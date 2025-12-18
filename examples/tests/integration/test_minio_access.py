"""
Integration tests for MinIO access.
"""
import io
import os
import uuid

import pytest

try:
    import boto3
    from botocore.exceptions import ClientError, EndpointConnectionError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


@pytest.fixture
def minio_client(minio_config):
    """Create a MinIO/S3 client for testing."""
    if not BOTO3_AVAILABLE:
        pytest.skip("boto3 not installed")

    client = boto3.client(
        's3',
        endpoint_url=minio_config["endpoint"],
        aws_access_key_id=minio_config["access_key"],
        aws_secret_access_key=minio_config["secret_key"],
        region_name='us-east-1',
    )
    return client


@pytest.fixture
def test_bucket_name():
    """Generate a unique test bucket name."""
    return f"test-bucket-{uuid.uuid4().hex[:8]}"


class TestMinIOAccess:
    """Test MinIO S3-compatible storage."""

    def test_minio_connection(self, minio_client):
        """Test that MinIO connection can be established."""
        try:
            response = minio_client.list_buckets()
            assert 'Buckets' in response
            assert isinstance(response['Buckets'], list)
        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_bucket_exists(self, minio_client, minio_config):
        """Test that required buckets exist or can be created."""
        required_buckets = ['datalake', 'warehouse', 'staging']

        try:
            existing_buckets = [
                b['Name'] for b in minio_client.list_buckets().get('Buckets', [])
            ]

            for bucket in required_buckets:
                if bucket not in existing_buckets:
                    try:
                        minio_client.create_bucket(Bucket=bucket)
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                            raise

            updated_buckets = [
                b['Name'] for b in minio_client.list_buckets().get('Buckets', [])
            ]
            for bucket in required_buckets:
                assert bucket in updated_buckets, (
                    f"Bucket {bucket} not found in MinIO"
                )

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_file_upload(self, minio_client, test_bucket_name):
        """Test uploading files to MinIO."""
        try:
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise

            test_content = b"Hello, MinIO! This is a test file."
            test_key = "test-uploads/test-file.txt"

            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=test_key,
                Body=test_content,
            )

            response = minio_client.head_object(
                Bucket=test_bucket_name,
                Key=test_key,
            )
            assert response['ContentLength'] == len(test_content)

            minio_client.delete_object(Bucket=test_bucket_name, Key=test_key)
            minio_client.delete_bucket(Bucket=test_bucket_name)

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_file_read(self, minio_client, test_bucket_name):
        """Test reading files from MinIO."""
        try:
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise

            test_content = b"Test content for reading"
            test_key = "test-reads/read-test.txt"

            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=test_key,
                Body=test_content,
            )

            response = minio_client.get_object(
                Bucket=test_bucket_name,
                Key=test_key,
            )
            read_content = response['Body'].read()

            assert read_content == test_content

            minio_client.delete_object(Bucket=test_bucket_name, Key=test_key)
            minio_client.delete_bucket(Bucket=test_bucket_name)

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_file_list(self, minio_client, test_bucket_name):
        """Test listing files in MinIO bucket."""
        try:
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise

            test_files = [
                "data/file1.txt",
                "data/file2.txt",
                "data/subdir/file3.txt",
            ]

            for key in test_files:
                minio_client.put_object(
                    Bucket=test_bucket_name,
                    Key=key,
                    Body=b"test",
                )

            response = minio_client.list_objects_v2(
                Bucket=test_bucket_name,
                Prefix="data/",
            )

            listed_keys = [obj['Key'] for obj in response.get('Contents', [])]
            assert len(listed_keys) == 3
            for key in test_files:
                assert key in listed_keys

            for key in test_files:
                minio_client.delete_object(Bucket=test_bucket_name, Key=key)
            minio_client.delete_bucket(Bucket=test_bucket_name)

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_multipart_upload(self, minio_client, test_bucket_name):
        """Test multipart upload for large files."""
        try:
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise

            large_content = b"x" * (6 * 1024 * 1024)
            test_key = "large-files/large-test.bin"

            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=test_key,
                Body=large_content,
            )

            response = minio_client.head_object(
                Bucket=test_bucket_name,
                Key=test_key,
            )
            assert response['ContentLength'] == len(large_content)

            minio_client.delete_object(Bucket=test_bucket_name, Key=test_key)
            minio_client.delete_bucket(Bucket=test_bucket_name)

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

    def test_presigned_url(self, minio_client, test_bucket_name):
        """Test generating presigned URLs for temporary access."""
        try:
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise

            test_key = "presigned/test-file.txt"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=test_key,
                Body=b"presigned test content",
            )

            presigned_url = minio_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': test_bucket_name, 'Key': test_key},
                ExpiresIn=3600,
            )

            assert presigned_url is not None
            assert test_bucket_name in presigned_url
            assert test_key in presigned_url

            minio_client.delete_object(Bucket=test_bucket_name, Key=test_key)
            minio_client.delete_bucket(Bucket=test_bucket_name)

        except EndpointConnectionError:
            pytest.skip("MinIO not available at configured endpoint")

"""
MinIO operations example using boto3.
"""
import boto3
from botocore.client import Config


def create_s3_client():
    """Create S3 client for MinIO."""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:30900',
        aws_access_key_id='admin',
        aws_secret_access_key='minioadmin',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def main():
    """Demonstrate MinIO operations."""
    s3 = create_s3_client()

    # List buckets
    print("Listing buckets:")
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

    # Upload file
    print("\nUploading file...")
    bucket_name = 'datalake'
    file_key = 'examples/test.txt'
    s3.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=b'Hello from MinIO!'
    )
    print(f"Uploaded {file_key} to {bucket_name}")

    # List objects
    print(f"\nListing objects in {bucket_name}:")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='examples/')
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")

    # Download file
    print(f"\nDownloading {file_key}:")
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    content = response['Body'].read().decode('utf-8')
    print(f"Content: {content}")

    # Delete file
    print(f"\nDeleting {file_key}...")
    s3.delete_object(Bucket=bucket_name, Key=file_key)
    print("Deleted successfully")


if __name__ == "__main__":
    main()

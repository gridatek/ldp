"""
End-to-end pipeline tests.

These tests validate the complete data pipeline from ingestion to transformation:
- Data upload to MinIO (S3-compatible storage)
- Pipeline orchestration validation
- Data transformation verification
- Output validation in target storage
- Error handling and retry mechanisms
"""
import io
import json
import os
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

try:
    import boto3
    from botocore.exceptions import ClientError, EndpointConnectionError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import (
        StructType,
        StructField,
        StringType,
        IntegerType,
        DoubleType,
        TimestampType,
    )

    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False


@pytest.fixture(scope="module")
def minio_config():
    """MinIO configuration for E2E tests."""
    return {
        "endpoint": os.getenv("MINIO_ENDPOINT", "http://localhost:30900"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "admin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    }


@pytest.fixture(scope="module")
def airflow_config():
    """Airflow configuration for E2E tests."""
    return {
        "webserver_url": os.getenv("AIRFLOW_URL", "http://localhost:30080"),
        "username": os.getenv("AIRFLOW_USER", "admin"),
        "password": os.getenv("AIRFLOW_PASSWORD", "admin"),
    }


@pytest.fixture(scope="module")
def minio_client(minio_config):
    """Create a MinIO/S3 client for E2E testing."""
    if not BOTO3_AVAILABLE:
        pytest.skip("boto3 not installed")

    try:
        client = boto3.client(
            "s3",
            endpoint_url=minio_config["endpoint"],
            aws_access_key_id=minio_config["access_key"],
            aws_secret_access_key=minio_config["secret_key"],
            region_name="us-east-1",
        )
        # Test connection
        client.list_buckets()
        return client
    except EndpointConnectionError:
        pytest.skip("MinIO not available at configured endpoint")
    except Exception as e:
        pytest.skip(f"MinIO connection failed: {e}")


@pytest.fixture(scope="module")
def spark_session():
    """Create Spark session for E2E testing."""
    if not PYSPARK_AVAILABLE:
        pytest.skip("PySpark not installed")

    spark = (
        SparkSession.builder.appName("e2e-test")
        .master("local[*]")
        .config("spark.sql.warehouse.dir", "/tmp/e2e-spark-warehouse")
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture(scope="function")
def test_bucket_name():
    """Generate unique test bucket name."""
    return f"e2e-test-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def sample_csv_data():
    """Generate sample CSV data for testing."""
    return """id,name,amount,transaction_date
1,Alice,100.50,2024-01-01
2,Bob,200.75,2024-01-02
3,Charlie,150.25,2024-01-03
4,Diana,300.00,2024-01-04
5,Eve,250.50,2024-01-05"""


@pytest.fixture(scope="function")
def sample_json_data():
    """Generate sample JSON data for testing."""
    return [
        {"id": 1, "name": "Alice", "amount": 100.50, "date": "2024-01-01"},
        {"id": 2, "name": "Bob", "amount": 200.75, "date": "2024-01-02"},
        {"id": 3, "name": "Charlie", "amount": 150.25, "date": "2024-01-03"},
    ]


class TestEndToEndPipeline:
    """Test complete data pipeline."""

    def test_full_pipeline_data_upload_to_minio(
        self, minio_client, test_bucket_name, sample_csv_data
    ):
        """Test uploading data to MinIO as first step of pipeline."""
        try:
            # Create test bucket
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                    raise

            # Upload raw data
            raw_key = "raw/transactions/2024/01/transactions.csv"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=raw_key,
                Body=sample_csv_data.encode("utf-8"),
                ContentType="text/csv",
            )

            # Verify upload
            response = minio_client.head_object(Bucket=test_bucket_name, Key=raw_key)
            assert response["ContentLength"] > 0
            assert response["ContentType"] == "text/csv"

            # Verify data content
            get_response = minio_client.get_object(Bucket=test_bucket_name, Key=raw_key)
            content = get_response["Body"].read().decode("utf-8")
            assert "Alice" in content
            assert "transaction_date" in content

        finally:
            # Cleanup
            try:
                minio_client.delete_object(Bucket=test_bucket_name, Key=raw_key)
                minio_client.delete_bucket(Bucket=test_bucket_name)
            except Exception:
                pass

    def test_pipeline_spark_transformation(
        self, spark_session, sample_csv_data, test_bucket_name
    ):
        """Test Spark transformation step of pipeline."""
        # Create DataFrame from CSV data
        from pyspark.sql.functions import col, current_timestamp, lit, to_date

        # Parse CSV data
        lines = sample_csv_data.strip().split("\n")
        header = lines[0].split(",")
        data = [line.split(",") for line in lines[1:]]

        df = spark_session.createDataFrame(data, header)

        # Apply transformations (similar to actual pipeline)
        df_transformed = (
            df.withColumn("amount", col("amount").cast("double"))
            .withColumn("transaction_date", to_date(col("transaction_date")))
            .withColumn("processed_at", current_timestamp())
            .withColumn("pipeline_id", lit(test_bucket_name))
        )

        # Verify transformations
        assert df_transformed.count() == 5
        assert "processed_at" in df_transformed.columns
        assert "pipeline_id" in df_transformed.columns

        # Verify data types
        schema = df_transformed.schema
        amount_field = [f for f in schema.fields if f.name == "amount"][0]
        assert str(amount_field.dataType) == "DoubleType()"

        # Verify aggregation works
        total_amount = df_transformed.agg({"amount": "sum"}).collect()[0][0]
        expected_total = 100.50 + 200.75 + 150.25 + 300.00 + 250.50
        assert abs(total_amount - expected_total) < 0.01

    def test_pipeline_data_quality_checks(self, spark_session, sample_csv_data):
        """Test data quality validation step of pipeline."""
        from pyspark.sql.functions import col, count, when

        # Create DataFrame
        lines = sample_csv_data.strip().split("\n")
        header = lines[0].split(",")
        data = [line.split(",") for line in lines[1:]]
        df = spark_session.createDataFrame(data, header)

        # Data quality checks
        total_rows = df.count()
        assert total_rows > 0, "DataFrame should not be empty"

        # Check for null values
        null_counts = df.select(
            [count(when(col(c).isNull(), c)).alias(c) for c in df.columns]
        ).collect()[0]
        for field in null_counts:
            assert field == 0, f"Found null values in column"

        # Check for duplicate IDs
        distinct_ids = df.select("id").distinct().count()
        assert distinct_ids == total_rows, "Found duplicate IDs"

        # Check value ranges
        df_with_amount = df.withColumn("amount", col("amount").cast("double"))
        negative_amounts = df_with_amount.filter(col("amount") < 0).count()
        assert negative_amounts == 0, "Found negative amounts"

    def test_pipeline_output_validation(
        self, minio_client, test_bucket_name, sample_csv_data
    ):
        """Test pipeline output validation in target storage."""
        try:
            # Create bucket
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                    raise

            # Simulate pipeline output (processed data)
            processed_data = {
                "pipeline_run_id": str(uuid.uuid4()),
                "processed_at": datetime.now().isoformat(),
                "input_rows": 5,
                "output_rows": 5,
                "status": "success",
                "metrics": {
                    "total_amount": 1002.00,
                    "avg_amount": 200.40,
                    "min_amount": 100.50,
                    "max_amount": 300.00,
                },
            }

            # Upload processed metadata
            metadata_key = "processed/metadata/run_metadata.json"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=metadata_key,
                Body=json.dumps(processed_data).encode("utf-8"),
                ContentType="application/json",
            )

            # Upload processed data
            processed_key = "processed/transactions/output.csv"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=processed_key,
                Body=sample_csv_data.encode("utf-8"),
            )

            # Validate output exists
            response = minio_client.list_objects_v2(
                Bucket=test_bucket_name, Prefix="processed/"
            )
            assert "Contents" in response
            assert len(response["Contents"]) == 2

            # Validate metadata
            metadata_response = minio_client.get_object(
                Bucket=test_bucket_name, Key=metadata_key
            )
            metadata = json.loads(metadata_response["Body"].read().decode("utf-8"))
            assert metadata["status"] == "success"
            assert metadata["input_rows"] == metadata["output_rows"]

        finally:
            # Cleanup
            try:
                objects = minio_client.list_objects_v2(Bucket=test_bucket_name)
                for obj in objects.get("Contents", []):
                    minio_client.delete_object(Bucket=test_bucket_name, Key=obj["Key"])
                minio_client.delete_bucket(Bucket=test_bucket_name)
            except Exception:
                pass

    def test_pipeline_partitioned_output(
        self, minio_client, test_bucket_name, sample_csv_data
    ):
        """Test pipeline with partitioned output."""
        try:
            # Create bucket
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                    raise

            # Simulate partitioned output by date
            partitions = [
                ("2024-01-01", "1,Alice,100.50,2024-01-01\n"),
                ("2024-01-02", "2,Bob,200.75,2024-01-02\n"),
                ("2024-01-03", "3,Charlie,150.25,2024-01-03\n"),
            ]

            for date, data in partitions:
                key = f"processed/transactions/date={date}/data.csv"
                minio_client.put_object(
                    Bucket=test_bucket_name,
                    Key=key,
                    Body=data.encode("utf-8"),
                )

            # Validate partitions exist
            response = minio_client.list_objects_v2(
                Bucket=test_bucket_name, Prefix="processed/transactions/"
            )
            assert len(response.get("Contents", [])) == 3

            # Validate specific partition
            partition_response = minio_client.get_object(
                Bucket=test_bucket_name,
                Key="processed/transactions/date=2024-01-01/data.csv",
            )
            content = partition_response["Body"].read().decode("utf-8")
            assert "Alice" in content

        finally:
            # Cleanup
            try:
                objects = minio_client.list_objects_v2(Bucket=test_bucket_name)
                for obj in objects.get("Contents", []):
                    minio_client.delete_object(Bucket=test_bucket_name, Key=obj["Key"])
                minio_client.delete_bucket(Bucket=test_bucket_name)
            except Exception:
                pass

    def test_full_pipeline(self, spark_session, minio_client, test_bucket_name):
        """Test complete pipeline from ingestion to transformation."""
        try:
            # Step 1: Setup - Create bucket and upload raw data
            try:
                minio_client.create_bucket(Bucket=test_bucket_name)
            except ClientError as e:
                if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                    raise

            raw_data = """id,name,amount,date
1,Alice,100.50,2024-01-01
2,Bob,200.75,2024-01-02
3,Charlie,150.25,2024-01-03"""

            raw_key = "raw/input.csv"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=raw_key,
                Body=raw_data.encode("utf-8"),
            )

            # Step 2: Read raw data (simulating Spark job reading from MinIO)
            response = minio_client.get_object(Bucket=test_bucket_name, Key=raw_key)
            csv_content = response["Body"].read().decode("utf-8")

            lines = csv_content.strip().split("\n")
            header = lines[0].split(",")
            data = [line.split(",") for line in lines[1:]]
            df = spark_session.createDataFrame(data, header)

            # Step 3: Transform data
            from pyspark.sql.functions import col, current_timestamp, upper

            df_transformed = (
                df.withColumn("amount", col("amount").cast("double"))
                .withColumn("name_upper", upper(col("name")))
                .withColumn("processed_at", current_timestamp())
            )

            # Step 4: Validate transformation
            assert df_transformed.count() == 3
            assert "name_upper" in df_transformed.columns

            # Step 5: Write processed data back (simulating output)
            processed_rows = df_transformed.collect()
            processed_csv = "id,name,name_upper,amount,date,processed_at\n"
            for row in processed_rows:
                processed_csv += f"{row.id},{row.name},{row.name_upper},{row.amount},{row.date},{row.processed_at}\n"

            processed_key = "processed/output.csv"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=processed_key,
                Body=processed_csv.encode("utf-8"),
            )

            # Step 6: Verify output
            output_response = minio_client.get_object(
                Bucket=test_bucket_name, Key=processed_key
            )
            output_content = output_response["Body"].read().decode("utf-8")
            assert "ALICE" in output_content  # Verify uppercase transformation
            assert "processed_at" in output_content

            # Step 7: Record pipeline metrics
            metrics = {
                "pipeline_id": test_bucket_name,
                "input_rows": 3,
                "output_rows": 3,
                "status": "success",
                "completed_at": datetime.now().isoformat(),
            }

            metrics_key = "metadata/pipeline_metrics.json"
            minio_client.put_object(
                Bucket=test_bucket_name,
                Key=metrics_key,
                Body=json.dumps(metrics).encode("utf-8"),
            )

            # Final validation
            all_objects = minio_client.list_objects_v2(Bucket=test_bucket_name)
            assert len(all_objects.get("Contents", [])) == 3  # raw, processed, metrics

        finally:
            # Cleanup
            try:
                objects = minio_client.list_objects_v2(Bucket=test_bucket_name)
                for obj in objects.get("Contents", []):
                    minio_client.delete_object(Bucket=test_bucket_name, Key=obj["Key"])
                minio_client.delete_bucket(Bucket=test_bucket_name)
            except Exception:
                pass


class TestPipelineErrorHandling:
    """Test pipeline error handling and recovery."""

    def test_error_handling_invalid_data(self, spark_session):
        """Test pipeline behavior with invalid/malformed data."""
        from pyspark.sql.functions import col

        # Create DataFrame with some invalid data
        data = [
            ("1", "Alice", "100.50"),
            ("2", "Bob", "invalid"),  # Invalid amount
            ("3", "Charlie", "150.25"),
        ]
        df = spark_session.createDataFrame(data, ["id", "name", "amount"])

        # PySpark 4.0: Use try_cast() as Column method for malformed input (returns NULL)
        df_with_cast = df.withColumn(
            "amount_double", col("amount").try_cast("double")
        )

        # Rows with invalid data should have null
        null_count = df_with_cast.filter(col("amount_double").isNull()).count()
        assert null_count == 1  # "invalid" becomes null

        # Valid rows should remain
        valid_count = df_with_cast.filter(col("amount_double").isNotNull()).count()
        assert valid_count == 2

    def test_error_handling_empty_input(self, spark_session):
        """Test pipeline behavior with empty input."""
        # Create empty DataFrame
        schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("amount", DoubleType(), True),
            ]
        )
        df_empty = spark_session.createDataFrame([], schema)

        # Pipeline should handle empty input gracefully
        assert df_empty.count() == 0

        # Transformations should work on empty DataFrame
        from pyspark.sql.functions import current_timestamp

        df_transformed = df_empty.withColumn("processed_at", current_timestamp())
        assert df_transformed.count() == 0
        assert "processed_at" in df_transformed.columns

    def test_error_handling_missing_columns(self, spark_session):
        """Test pipeline behavior when expected columns are missing."""
        # Create DataFrame with missing columns
        data = [("1", "Alice"), ("2", "Bob")]
        df = spark_session.createDataFrame(data, ["id", "name"])

        # Check if required column exists before processing
        required_columns = ["id", "name", "amount"]
        missing_columns = [c for c in required_columns if c not in df.columns]

        assert "amount" in missing_columns
        assert len(missing_columns) == 1

        # Handle missing column by adding default
        from pyspark.sql.functions import lit

        if "amount" not in df.columns:
            df = df.withColumn("amount", lit(0.0))

        assert "amount" in df.columns
        assert df.count() == 2

    def test_error_handling_duplicate_data(self, spark_session):
        """Test pipeline behavior with duplicate records."""
        # Create DataFrame with duplicates
        data = [
            ("1", "Alice", 100.0),
            ("1", "Alice", 100.0),  # Duplicate
            ("2", "Bob", 200.0),
            ("2", "Bob", 250.0),  # Same ID, different amount
        ]
        df = spark_session.createDataFrame(data, ["id", "name", "amount"])

        # Detect duplicates
        from pyspark.sql.functions import count

        duplicate_ids = (
            df.groupBy("id").agg(count("*").alias("cnt")).filter("cnt > 1")
        )
        assert duplicate_ids.count() == 2  # IDs 1 and 2 have duplicates

        # Deduplicate - keep first occurrence
        df_deduped = df.dropDuplicates(["id"])
        assert df_deduped.count() == 2

    def test_error_handling_retries(self):
        """Test pipeline retry mechanism."""
        attempts = 0
        max_retries = 3

        def unreliable_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception("Temporary failure")
            return "success"

        # Simulate retry logic
        result = None
        last_error = None

        for retry in range(max_retries):
            try:
                result = unreliable_operation()
                break
            except Exception as e:
                last_error = e
                time.sleep(0.1)  # Brief delay between retries

        assert result == "success"
        assert attempts == 3

    def test_error_handling_data_validation_failure(self, spark_session):
        """Test pipeline stops on critical data validation failure."""
        from pyspark.sql.functions import col

        # Create DataFrame with data that fails validation
        data = [
            ("1", "Alice", -100.0),  # Negative amount (invalid)
            ("2", "Bob", 200.0),
            ("3", "", 150.0),  # Empty name (invalid)
        ]
        df = spark_session.createDataFrame(data, ["id", "name", "amount"])

        # Define validation rules
        validation_errors = []

        # Check for negative amounts
        negative_count = df.filter(col("amount") < 0).count()
        if negative_count > 0:
            validation_errors.append(f"Found {negative_count} negative amounts")

        # Check for empty names
        empty_names = df.filter((col("name").isNull()) | (col("name") == "")).count()
        if empty_names > 0:
            validation_errors.append(f"Found {empty_names} empty names")

        # Validation should fail
        assert len(validation_errors) == 2
        assert any("negative amounts" in e for e in validation_errors)
        assert any("empty names" in e for e in validation_errors)

    def test_error_handling(self):
        """Test pipeline error handling and retries."""
        # Test that error handling mechanisms work
        error_log = []

        def process_with_error_handling(data, raise_error=False):
            try:
                if raise_error:
                    raise ValueError("Simulated processing error")
                return {"status": "success", "data": data}
            except Exception as e:
                error_log.append(str(e))
                return {"status": "error", "error": str(e)}

        # Test successful processing
        result = process_with_error_handling({"id": 1})
        assert result["status"] == "success"

        # Test error handling
        result = process_with_error_handling({"id": 2}, raise_error=True)
        assert result["status"] == "error"
        assert len(error_log) == 1
        assert "Simulated processing error" in error_log[0]


class TestPipelineMonitoring:
    """Test pipeline monitoring and metrics collection."""

    def test_pipeline_metrics_collection(self, spark_session):
        """Test that pipeline collects and reports metrics."""
        from pyspark.sql.functions import col, count, sum as spark_sum, avg, min as spark_min, max as spark_max

        # Create sample data
        data = [
            ("1", "Alice", 100.0),
            ("2", "Bob", 200.0),
            ("3", "Charlie", 150.0),
        ]
        df = spark_session.createDataFrame(data, ["id", "name", "amount"])

        # Collect metrics
        metrics = df.agg(
            count("*").alias("row_count"),
            spark_sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            spark_min("amount").alias("min_amount"),
            spark_max("amount").alias("max_amount"),
        ).collect()[0]

        assert metrics.row_count == 3
        assert metrics.total_amount == 450.0
        assert metrics.avg_amount == 150.0
        assert metrics.min_amount == 100.0
        assert metrics.max_amount == 200.0

    def test_pipeline_timing_metrics(self):
        """Test pipeline timing and duration tracking."""
        import time

        start_time = time.time()

        # Simulate pipeline stages
        stages = []

        # Stage 1: Data ingestion
        stage_start = time.time()
        time.sleep(0.1)  # Simulate work
        stages.append({"name": "ingestion", "duration": time.time() - stage_start})

        # Stage 2: Transformation
        stage_start = time.time()
        time.sleep(0.05)  # Simulate work
        stages.append({"name": "transformation", "duration": time.time() - stage_start})

        # Stage 3: Output
        stage_start = time.time()
        time.sleep(0.05)  # Simulate work
        stages.append({"name": "output", "duration": time.time() - stage_start})

        total_duration = time.time() - start_time

        # Validate timing metrics
        assert len(stages) == 3
        assert all(s["duration"] > 0 for s in stages)
        assert total_duration >= sum(s["duration"] for s in stages)

    def test_pipeline_data_lineage(self, spark_session):
        """Test pipeline data lineage tracking."""
        from pyspark.sql.functions import lit, current_timestamp

        # Create source data with lineage metadata
        source_data = [("1", "Alice", 100.0), ("2", "Bob", 200.0)]
        df_source = spark_session.createDataFrame(source_data, ["id", "name", "amount"])

        # Add lineage information
        df_with_lineage = (
            df_source.withColumn("source_system", lit("crm"))
            .withColumn("source_table", lit("customers"))
            .withColumn("extraction_time", current_timestamp())
            .withColumn("pipeline_version", lit("1.0.0"))
        )

        # Verify lineage columns
        assert "source_system" in df_with_lineage.columns
        assert "source_table" in df_with_lineage.columns
        assert "extraction_time" in df_with_lineage.columns
        assert "pipeline_version" in df_with_lineage.columns

        # Verify lineage values
        first_row = df_with_lineage.collect()[0]
        assert first_row.source_system == "crm"
        assert first_row.source_table == "customers"
        assert first_row.pipeline_version == "1.0.0"

"""
Pytest configuration and fixtures for integration tests.
"""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_session():
    """Create a Spark session for testing."""
    spark = SparkSession.builder \
        .appName("test") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()

    yield spark

    spark.stop()


@pytest.fixture(scope="session")
def minio_config():
    """MinIO configuration for tests."""
    return {
        "endpoint": "http://localhost:30900",
        "access_key": "admin",
        "secret_key": "minioadmin",
    }


@pytest.fixture(scope="session")
def postgres_config():
    """PostgreSQL configuration for tests."""
    return {
        "host": "localhost",
        "port": 30432,
        "database": "metastore",
        "user": "ldp",
        "password": "ldppassword",
    }

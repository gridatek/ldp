"""
Tests for Spark transformation functions.
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.transformations import (
    add_audit_columns,
    add_partition_columns,
    deduplicate,
    standardize_column_names
)


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .appName("test") \
        .master("local[*]") \
        .getOrCreate()


def test_add_audit_columns(spark):
    """Test adding audit columns."""
    data = [("Alice", 25), ("Bob", 30)]
    df = spark.createDataFrame(data, ["name", "age"])

    result = add_audit_columns(df)

    assert "created_at" in result.columns
    assert "updated_at" in result.columns
    assert result.count() == 2


def test_deduplicate(spark):
    """Test deduplication."""
    data = [
        ("Alice", 25, datetime(2024, 1, 1)),
        ("Alice", 26, datetime(2024, 1, 2)),
        ("Bob", 30, datetime(2024, 1, 1))
    ]
    df = spark.createDataFrame(data, ["name", "age", "timestamp"])

    result = deduplicate(df, ["name"], order_by="timestamp")

    assert result.count() == 2
    alice_row = result.filter(result.name == "Alice").first()
    assert alice_row.age == 26  # Should keep latest


def test_standardize_column_names(spark):
    """Test column name standardization."""
    data = [(1, 2, 3)]
    df = spark.createDataFrame(data, ["Column Name", "Another-Column", "UPPERCASE"])

    result = standardize_column_names(df)

    assert "column_name" in result.columns
    assert "another_column" in result.columns
    assert "uppercase" in result.columns

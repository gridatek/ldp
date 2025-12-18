"""
I/O helper functions for reading and writing data.
"""
from pyspark.sql import SparkSession, DataFrame
from typing import Dict, Any


class DataReader:
    """Helper class for reading data from various sources."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def read_csv(self, path: str, header: bool = True, **options) -> DataFrame:
        """Read CSV file."""
        return self.spark.read \
            .option("header", header) \
            .options(**options) \
            .csv(path)

    def read_parquet(self, path: str) -> DataFrame:
        """Read Parquet file."""
        return self.spark.read.parquet(path)

    def read_iceberg(self, table_name: str) -> DataFrame:
        """Read Iceberg table."""
        return self.spark.table(table_name)

    def read_json(self, path: str, **options) -> DataFrame:
        """Read JSON file."""
        return self.spark.read.options(**options).json(path)


class DataWriter:
    """Helper class for writing data to various destinations."""

    @staticmethod
    def write_parquet(df: DataFrame, path: str, mode: str = "overwrite",
                     partition_by: list = None):
        """Write DataFrame as Parquet."""
        writer = df.write.mode(mode)
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        writer.parquet(path)

    @staticmethod
    def write_iceberg(df: DataFrame, table_name: str, mode: str = "append"):
        """Write DataFrame to Iceberg table."""
        df.writeTo(table_name).using("iceberg").mode(mode).createOrReplace()

    @staticmethod
    def write_csv(df: DataFrame, path: str, mode: str = "overwrite",
                  header: bool = True, **options):
        """Write DataFrame as CSV."""
        df.write.mode(mode).option("header", header).options(**options).csv(path)

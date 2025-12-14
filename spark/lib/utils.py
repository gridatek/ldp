"""
Utility functions for Spark jobs.
"""
from pyspark.sql import SparkSession
from typing import Dict, Any


def get_iceberg_spark_session(app_name: str, configs: Dict[str, Any] = None) -> SparkSession:
    """
    Create a Spark session with Iceberg configuration.

    Args:
        app_name: Name of the Spark application
        configs: Additional Spark configurations

    Returns:
        Configured SparkSession
    """
    builder = SparkSession.builder.appName(app_name)

    # Default Iceberg configurations
    default_configs = {
        "spark.jars.packages": "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        "spark.sql.catalog.local": "org.apache.iceberg.spark.SparkCatalog",
        "spark.sql.catalog.local.type": "hadoop",
        "spark.sql.catalog.local.warehouse": "s3a://warehouse/",
        "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
        "spark.hadoop.fs.s3a.access.key": "admin",
        "spark.hadoop.fs.s3a.secret.key": "minioadmin",
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    }

    # Merge with custom configs
    if configs:
        default_configs.update(configs)

    # Apply configurations
    for key, value in default_configs.items():
        builder = builder.config(key, value)

    return builder.getOrCreate()


def read_from_s3(spark: SparkSession, path: str, format: str = "parquet", **options):
    """
    Read data from S3/MinIO.

    Args:
        spark: SparkSession
        path: S3 path (e.g., s3a://bucket/path)
        format: File format (parquet, csv, json, etc.)
        **options: Additional read options

    Returns:
        DataFrame
    """
    reader = spark.read.format(format)

    for key, value in options.items():
        reader = reader.option(key, value)

    return reader.load(path)


def write_to_iceberg(df, table_name: str, mode: str = "append"):
    """
    Write DataFrame to Iceberg table.

    Args:
        df: DataFrame to write
        table_name: Fully qualified table name (e.g., local.db.table)
        mode: Write mode (append, overwrite, etc.)
    """
    df.writeTo(table_name).using("iceberg").mode(mode).createOrReplace()

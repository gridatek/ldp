"""
Batch processing Spark job with Iceberg support.
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import argparse


def create_spark_session(app_name="BatchProcessing"):
    """Create and configure Spark session with Iceberg."""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()


def process_data(spark, input_path, output_table):
    """Process data and write to Iceberg table."""
    print(f"Reading data from {input_path}")

    # Read data (example with CSV)
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)

    # Add processing timestamp
    df_processed = df.withColumn("processed_at", current_timestamp())

    print(f"Writing {df_processed.count()} records to {output_table}")

    # Write to Iceberg table
    df_processed.writeTo(output_table) \
        .using("iceberg") \
        .createOrReplace()

    print(f"Successfully wrote data to {output_table}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Batch processing with Spark and Iceberg')
    parser.add_argument('--input', default='s3a://datalake/raw/', help='Input data path')
    parser.add_argument('--output', default='local.db.processed_data', help='Output Iceberg table')
    parser.add_argument('--date', help='Processing date (YYYY-MM-DD)')

    args = parser.parse_args()

    # Create Spark session
    spark = create_spark_session()

    try:
        # Process data
        input_path = f"{args.input}{args.date}/" if args.date else args.input
        process_data(spark, input_path, args.output)

        print("Batch processing completed successfully")
        return 0
    except Exception as e:
        print(f"Error during batch processing: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())

"""
Spark Structured Streaming job example.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


def create_spark_session():
    """Create Spark session for streaming."""
    return SparkSession.builder \
        .appName("StreamingJob") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()


def main():
    """Main streaming job."""
    spark = create_spark_session()

    # Define schema for incoming data
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("value", StringType(), True),
    ])

    # Read stream from a source (example: file source)
    df = spark.readStream \
        .format("csv") \
        .option("header", "true") \
        .schema(schema) \
        .load("s3a://datalake/streaming/")

    # Process the stream
    processed_df = df.withColumn("processed_at", current_timestamp())

    # Write stream to output
    query = processed_df.writeStream \
        .format("parquet") \
        .option("path", "s3a://datalake/processed/streaming/") \
        .option("checkpointLocation", "s3a://warehouse/checkpoints/streaming/") \
        .outputMode("append") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    main()

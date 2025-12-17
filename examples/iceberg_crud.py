"""
Iceberg CRUD operations example.
"""
from pyspark.sql import SparkSession
from datetime import datetime


def create_spark_session():
    """Create Spark session with Iceberg."""
    return SparkSession.builder \
        .appName("IcebergCRUD") \
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
        .getOrCreate()


def main():
    """Demonstrate Iceberg CRUD operations."""
    spark = create_spark_session()

    # Create database
    spark.sql("CREATE DATABASE IF NOT EXISTS local.demo")

    # Create table
    print("Creating Iceberg table...")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS local.demo.users (
            id BIGINT,
            name STRING,
            email STRING,
            created_at TIMESTAMP
        ) USING iceberg
    """)

    # Insert data
    print("Inserting data...")
    data = [
        (1, "Alice", "alice@example.com", datetime.now()),
        (2, "Bob", "bob@example.com", datetime.now()),
        (3, "Charlie", "charlie@example.com", datetime.now()),
    ]
    df = spark.createDataFrame(data, ["id", "name", "email", "created_at"])
    df.writeTo("local.demo.users").append()

    # Read data
    print("Reading data...")
    result = spark.table("local.demo.users")
    result.show()

    # Update data
    print("Updating data...")
    spark.sql("""
        UPDATE local.demo.users
        SET email = 'alice.new@example.com'
        WHERE id = 1
    """)

    # Read updated data
    print("After update:")
    spark.table("local.demo.users").show()

    # Delete data
    print("Deleting data...")
    spark.sql("DELETE FROM local.demo.users WHERE id = 3")

    # Read after delete
    print("After delete:")
    spark.table("local.demo.users").show()

    # Show table history
    print("Table history:")
    spark.sql("SELECT * FROM local.demo.users.history").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()

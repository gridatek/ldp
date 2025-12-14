"""
Simple Spark job example.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count


def main():
    """Simple Spark job."""
    # Create Spark session
    spark = SparkSession.builder \
        .appName("SimpleSparkJob") \
        .getOrCreate()

    # Create sample data
    data = [
        ("Alice", 25, "Engineering"),
        ("Bob", 30, "Sales"),
        ("Charlie", 35, "Engineering"),
        ("David", 28, "Sales"),
        ("Eve", 32, "Engineering"),
    ]

    # Create DataFrame
    df = spark.createDataFrame(data, ["name", "age", "department"])

    # Show data
    print("Sample Data:")
    df.show()

    # Perform aggregation
    print("Department Summary:")
    df.groupBy("department") \
        .agg(count("*").alias("count")) \
        .show()

    # Calculate average age by department
    print("Average Age by Department:")
    df.groupBy("department") \
        .avg("age") \
        .show()

    spark.stop()


if __name__ == "__main__":
    main()

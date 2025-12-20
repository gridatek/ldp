# Spark Directory

This directory contains Apache Spark job files and configurations for distributed data processing.

## Structure

```
spark/
├── jobs/              # Your Spark job scripts go here
└── README.md          # This file
```

## What is Spark?

Apache Spark is a unified analytics engine for large-scale data processing. It provides:

- **Fast processing**: In-memory computing
- **Distributed**: Processes data across multiple nodes
- **Rich APIs**: Python (PySpark), Scala, Java, SQL, R
- **Libraries**: SQL, Streaming, ML, Graph processing

## Adding Spark Jobs

### Option 1: Copy from Examples

Use tested job examples:

```bash
# Simple Spark job
cp examples/spark_job.py spark/jobs/

# Iceberg operations
cp examples/iceberg_crud.py spark/jobs/
```

### Option 2: Create Your Own

Create a new job file in `spark/jobs/`:

```python
"""
My Spark Job
Description: What this job does
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg


def create_spark_session():
    """Create Spark session with Iceberg support."""
    return SparkSession.builder \
        .appName("MySparkJob") \
        .config("spark.jars.packages",
                "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
        .config("spark.sql.extensions",
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.local",
                "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
        .getOrCreate()


def main():
    """Main job logic."""
    spark = create_spark_session()

    try:
        # Your data processing logic here
        df = spark.read.parquet("s3a://datalake/raw/data.parquet")

        # Transform
        result = df.groupBy("category") \
            .agg(count("*").alias("count"),
                 avg("amount").alias("avg_amount"))

        # Write to Iceberg table
        result.writeTo("local.analytics.summary") \
            .using("iceberg") \
            .createOrReplace()

        print(f"Processed {df.count()} records")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
```

## Running Spark Jobs

### Local Development

Submit jobs to your local Spark cluster:

```bash
# Using Makefile (recommended)
make spark-submit APP=spark/jobs/my_job.py

# Or directly with docker-compose
docker-compose exec spark-master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/jobs/my_job.py
```

### With Arguments

Pass arguments to your Spark job:

```bash
make spark-submit APP=spark/jobs/my_job.py ARGS="--date 2024-12-20 --env prod"
```

In your Python script:

```python
import sys

if __name__ == "__main__":
    # Parse arguments
    date = sys.argv[1] if len(sys.argv) > 1 else "2024-01-01"
    env = sys.argv[2] if len(sys.argv) > 2 else "dev"

    main(date, env)
```

### From Airflow

Use SparkSubmitOperator in your DAG:

```python
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

submit_job = SparkSubmitOperator(
    task_id='run_spark_job',
    application='/opt/spark/jobs/my_job.py',
    conn_id='spark_default',
    application_args=['--date', '{{ ds }}'],
    conf={
        'spark.jars.packages': 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0',
    },
)
```

## Spark Configuration

### Basic Configuration

All Spark jobs should include Iceberg support:

```python
spark = SparkSession.builder \
    .appName("MyJob") \
    .config("spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.local",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
    .getOrCreate()
```

### Memory Configuration

Adjust memory based on your data size:

```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
```

### S3/MinIO Configuration

For reading/writing to MinIO:

```python
spark = SparkSession.builder \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
```

## Common Spark Operations

### Reading Data

```python
# Parquet from S3/MinIO
df = spark.read.parquet("s3a://datalake/raw/data.parquet")

# CSV with schema inference
df = spark.read.csv("s3a://datalake/raw/data.csv", header=True, inferSchema=True)

# Iceberg table
df = spark.table("local.db.table_name")

# JSON
df = spark.read.json("s3a://datalake/raw/data.json")
```

### Writing Data

```python
# Write to Parquet
df.write.mode("overwrite").parquet("s3a://datalake/processed/output.parquet")

# Write to Iceberg table (append)
df.writeTo("local.db.table_name").append()

# Write to Iceberg table (replace)
df.writeTo("local.db.table_name").createOrReplace()

# Partitioned write
df.write.partitionBy("year", "month") \
    .parquet("s3a://datalake/processed/data/")
```

### Transformations

```python
from pyspark.sql.functions import col, when, lit, concat

# Filter
df_filtered = df.filter(col("age") > 18)

# Select and rename
df_selected = df.select(
    col("id"),
    col("name").alias("full_name"),
    col("age")
)

# Add columns
df_with_col = df.withColumn("status",
    when(col("age") >= 18, lit("adult"))
    .otherwise(lit("minor"))
)

# Join
df_joined = df1.join(df2, df1.id == df2.user_id, "left")

# Aggregate
df_agg = df.groupBy("department") \
    .agg(
        count("*").alias("count"),
        avg("salary").alias("avg_salary")
    )
```

### Working with Iceberg

```python
# Create table
spark.sql("""
    CREATE TABLE IF NOT EXISTS local.db.users (
        id BIGINT,
        name STRING,
        email STRING,
        created_at TIMESTAMP
    ) USING iceberg
    PARTITIONED BY (days(created_at))
""")

# Insert
df.writeTo("local.db.users").append()

# Update
spark.sql("""
    UPDATE local.db.users
    SET email = 'newemail@example.com'
    WHERE id = 123
""")

# Delete
spark.sql("DELETE FROM local.db.users WHERE id = 456")

# Time travel
df_historical = spark.read \
    .option("snapshot-id", "123456789") \
    .table("local.db.users")

# View history
spark.sql("SELECT * FROM local.db.users.history").show()
```

## Job Patterns

### Pattern 1: ETL Job

```python
def etl_job(date: str):
    """Extract, Transform, Load pattern."""
    spark = create_spark_session()

    # Extract
    raw_df = spark.read.parquet(f"s3a://datalake/raw/{date}/")

    # Transform
    clean_df = raw_df \
        .filter(col("value").isNotNull()) \
        .withColumn("processed_date", lit(date))

    # Load
    clean_df.writeTo(f"local.warehouse.cleaned_data").append()

    spark.stop()
```

### Pattern 2: Incremental Processing

```python
def incremental_process(last_processed_id: int):
    """Process only new records."""
    spark = create_spark_session()

    # Read only new records
    new_records = spark.table("local.raw.events") \
        .filter(col("id") > last_processed_id)

    if new_records.count() == 0:
        print("No new records to process")
        return

    # Process
    processed = new_records.transform(apply_business_logic)

    # Write
    processed.writeTo("local.processed.events").append()

    spark.stop()
```

### Pattern 3: Data Quality Checks

```python
def run_quality_checks(df):
    """Run data quality validations."""
    errors = []

    # Check for nulls
    null_count = df.filter(col("id").isNull()).count()
    if null_count > 0:
        errors.append(f"Found {null_count} null IDs")

    # Check for duplicates
    dup_count = df.groupBy("id").count() \
        .filter(col("count") > 1).count()
    if dup_count > 0:
        errors.append(f"Found {dup_count} duplicate IDs")

    # Check value ranges
    invalid_ages = df.filter((col("age") < 0) | (col("age") > 150)).count()
    if invalid_ages > 0:
        errors.append(f"Found {invalid_ages} invalid ages")

    if errors:
        raise ValueError(f"Data quality checks failed: {errors}")

    return True
```

## Best Practices

### 1. Always Stop Spark Session

Use try-finally to ensure cleanup:

```python
def main():
    spark = create_spark_session()
    try:
        # Your processing logic
        pass
    finally:
        spark.stop()
```

### 2. Use Appropriate File Formats

- **Parquet**: Default choice for analytics (columnar, compressed)
- **Iceberg**: For tables needing ACID, updates, or time travel
- **CSV**: Only for human-readable data or external systems
- **JSON**: For nested/semi-structured data

### 3. Partition Large Datasets

```python
# Partition by date for time-series data
df.write \
    .partitionBy("year", "month", "day") \
    .parquet("s3a://datalake/data/")
```

### 4. Cache Reused DataFrames

```python
# Cache if DataFrame is used multiple times
df = spark.read.parquet("s3a://datalake/data/")
df.cache()

# Use multiple times
df.filter(condition1).count()
df.filter(condition2).show()

# Unpersist when done
df.unpersist()
```

### 5. Broadcast Small Tables

```python
from pyspark.sql.functions import broadcast

# For joins with small dimension tables
result = large_df.join(broadcast(small_df), "key")
```

### 6. Handle Schema Evolution

With Iceberg, schemas can evolve safely:

```python
# Add column
spark.sql("ALTER TABLE local.db.users ADD COLUMN phone STRING")

# Rename column
spark.sql("ALTER TABLE local.db.users RENAME COLUMN email TO email_address")
```

## Monitoring and Debugging

### View Spark UI

Access Spark UI for monitoring:

- **Master UI**: http://localhost:8081
- **Worker UI**: http://localhost:8082
- **Application UI**: Available while job is running

### Check Logs

```bash
# View Spark master logs
make spark-logs

# Or directly
docker logs ldp-spark-master

# Worker logs
docker logs ldp-spark-worker
```

### Enable Debug Logging

```python
# In your job
spark.sparkContext.setLogLevel("DEBUG")
```

## Common Issues

### Out of Memory

Increase executor memory:

```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()
```

### Slow Shuffles

- Increase shuffle partitions
- Use broadcast joins for small tables
- Repartition data appropriately

```python
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

### Connection to MinIO Failed

Verify configuration:
- Endpoint: `http://minio:9000` (in Docker network)
- Credentials: `admin` / `minioadmin`
- Path style access: `true`

## Testing Spark Jobs

See `examples/tests/spark/` for testing patterns:

```bash
# Run Spark tests
pytest examples/tests/spark/
```

## Dependencies

Python packages for Spark workers are defined in:

```
docker/spark/requirements.txt
```

To add new dependencies:

1. Edit `docker/spark/requirements.txt`
2. Rebuild Spark images:
   ```bash
   docker-compose build spark-master spark-worker
   docker-compose up -d
   ```

## Learn More

- **Spark Documentation**: https://spark.apache.org/docs/latest/
- **PySpark API**: https://spark.apache.org/docs/latest/api/python/
- **Iceberg Spark**: https://iceberg.apache.org/docs/latest/spark-getting-started/
- **Getting Started Tutorial**: `docs/getting-started-tutorial.md`
- **Examples**: `examples/` directory

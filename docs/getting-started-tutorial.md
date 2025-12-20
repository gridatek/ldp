# Getting Started with LDP (Local Data Platform)

This tutorial will guide you through using the Local Data Platform (LDP) - a modern data platform built on Apache Spark, Apache Airflow, Apache Iceberg, and MinIO.

## What is LDP?

LDP is a local data platform that provides:
- **Apache Spark** for distributed data processing
- **Apache Airflow** for workflow orchestration
- **Apache Iceberg** for table management with ACID transactions
- **MinIO** for S3-compatible object storage
- **PostgreSQL** for metadata storage

## Prerequisites

Before you begin, ensure you have:
- **Docker Desktop** installed (Windows, macOS, or Linux)
- **Docker Compose** (included with Docker Desktop)
- Basic knowledge of Python and SQL
- Understanding of data pipelines

### Platform Support

LDP works on:
- ✅ **Windows** (Windows 10/11 with Docker Desktop)
- ✅ **Linux** (Ubuntu, Fedora, etc.)
- ✅ **macOS** (Intel and Apple Silicon)

**For Windows users**: Commands in this tutorial are shown for both Windows (PowerShell/Command Prompt) and Linux/macOS (Bash). Look for the 💻 Windows and 🐧 Linux/macOS icons.

## Starting the Platform

### 1. Start all services

**🐧 Linux/macOS:**
```bash
make up
```

**💻 Windows (PowerShell):**
```powershell
docker-compose up -d
```

**💻 Windows (Command Prompt):**
```cmd
docker-compose up -d
```

This will start all services: Airflow, Spark, MinIO, and PostgreSQL.

### 2. Verify services are running

**🐧 Linux/macOS:**
```bash
make status
```

**💻 Windows:**
```powershell
docker ps
```

You should see all containers running.

### 3. Access the web interfaces

- **Airflow UI**: http://localhost:8080 (username: `admin`, password: `admin`)
- **MinIO Console**: http://localhost:9001 (username: `admin`, password: `minioadmin`)
- **Spark Master**: http://localhost:8081

## Your First Data Pipeline

Let's walk through a complete data pipeline using the tested example code provided in the `examples/` directory.

**Important**: The `examples/` directory contains reference code that should **never be run directly**. Always copy examples to the appropriate location first:
- Spark jobs → `spark/jobs/`
- Airflow DAGs → `airflow/dags/`
- Scripts → `scripts/`

This keeps the examples clean as reference material and teaches you the proper workflow.

**Note for Windows users**: Replace forward slashes (`/`) with backslashes (`\`) in file paths, or use PowerShell which supports both.

### Example 1: Working with MinIO (Object Storage)

MinIO provides S3-compatible object storage for your data lake.

**Reference**: `examples/minio_operations.py`

```python
"""
MinIO operations example using boto3.
"""
import boto3
from botocore.client import Config


def create_s3_client():
    """Create S3 client for MinIO."""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:30900',
        aws_access_key_id='admin',
        aws_secret_access_key='minioadmin',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def main():
    """Demonstrate MinIO operations."""
    s3 = create_s3_client()

    # List buckets
    print("Listing buckets:")
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

    # Upload file
    print("\nUploading file...")
    bucket_name = 'datalake'
    file_key = 'examples/test.txt'
    s3.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=b'Hello from MinIO!'
    )
    print(f"Uploaded {file_key} to {bucket_name}")

    # List objects
    print(f"\nListing objects in {bucket_name}:")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='examples/')
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")

    # Download file
    print(f"\nDownloading {file_key}:")
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    content = response['Body'].read().decode('utf-8')
    print(f"Content: {content}")

    # Delete file
    print(f"\nDeleting {file_key}...")
    s3.delete_object(Bucket=bucket_name, Key=file_key)
    print("Deleted successfully")


if __name__ == "__main__":
    main()
```

**To run this example:**

1. First, copy it to your working directory:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/minio_operations.py scripts/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\minio_operations.py scripts\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\minio_operations.py scripts\
   ```

2. Then run it:
   ```bash
   python scripts/minio_operations.py
   ```
   *(Same command for all platforms)*

**Note**: Never run code directly from `examples/` - always copy it to the appropriate location first. This keeps the examples clean as reference material.

### Example 2: Processing Data with Spark

Spark allows you to process large datasets in a distributed manner.

**Reference**: `examples/spark_job.py`

```python
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
```

**To run this example:**

1. First, copy it to the Spark jobs directory:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/spark_job.py spark/jobs/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\spark_job.py spark\jobs\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\spark_job.py spark\jobs\
   ```

2. Then submit to the Spark cluster:

   **🐧 Linux/macOS:**
   ```bash
   make spark-submit APP=spark/jobs/spark_job.py
   ```

   **💻 Windows:**
   ```powershell
   docker-compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/spark_job.py
   ```

**Note**: Always copy examples to `spark/jobs/` before running, not from `examples/` directly.

### Example 3: Iceberg Tables (ACID Transactions)

Iceberg provides ACID transactions, schema evolution, and time travel for your data lake.

**Reference**: `examples/iceberg_crud.py`

This example demonstrates:
- Creating Iceberg tables
- Inserting data
- Updating records
- Deleting records
- Querying table history (time travel)

**Key features demonstrated:**

```python
# Create Iceberg table
spark.sql("""
    CREATE TABLE IF NOT EXISTS local.demo.users (
        id BIGINT,
        name STRING,
        email STRING,
        created_at TIMESTAMP
    ) USING iceberg
""")

# Insert data
df.writeTo("local.demo.users").append()

# Update records
spark.sql("""
    UPDATE local.demo.users
    SET email = 'alice.new@example.com'
    WHERE id = 1
""")

# Delete records
spark.sql("DELETE FROM local.demo.users WHERE id = 3")

# View table history (time travel)
spark.sql("SELECT * FROM local.demo.users.history").show()
```

**To run this example:**

1. First, copy it to the Spark jobs directory:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/iceberg_crud.py spark/jobs/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\iceberg_crud.py spark\jobs\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\iceberg_crud.py spark\jobs\
   ```

2. Then submit to the Spark cluster:

   **🐧 Linux/macOS:**
   ```bash
   make spark-submit APP=spark/jobs/iceberg_crud.py
   ```

   **💻 Windows:**
   ```powershell
   docker-compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/iceberg_crud.py
   ```

### Example 4: Airflow DAG (Workflow Orchestration)

Airflow orchestrates your data pipelines, scheduling and monitoring tasks.

**Reference**: `examples/simple_dag.py`

```python
"""
Simple Airflow DAG example.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def hello_world():
    """Simple Python function."""
    print("Hello from Local Data Platform!")
    return "Success"


with DAG(
    'simple_example',
    default_args={
        'owner': 'ldp',
        'start_date': datetime(2024, 1, 1),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A simple example DAG',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['example'],
) as dag:

    task1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    task2 = PythonOperator(
        task_id='hello_world',
        python_callable=hello_world,
    )

    task3 = BashOperator(
        task_id='finish',
        bash_command='echo "Pipeline completed!"',
    )

    task1 >> task2 >> task3
```

**To run this example:**

1. **First, copy** the DAG file to the Airflow DAGs folder:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/simple_dag.py airflow/dags/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\simple_dag.py airflow\dags\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\simple_dag.py airflow\dags\
   ```

2. Wait for Airflow to detect it (1-2 minutes)

3. Trigger the DAG from the Airflow UI or CLI:

   **🐧 Linux/macOS:**
   ```bash
   make airflow-trigger DAG=simple_example
   ```

   **💻 Windows:**
   ```powershell
   docker-compose exec airflow-webserver airflow dags trigger simple_example
   ```

**Important**: DAGs must be in `airflow/dags/` to be discovered by Airflow. Never reference `examples/` directly in your DAG paths.

## Production-Ready Examples

The `examples/dags/` directory contains more advanced, production-ready examples:

### Daily Data Ingestion

**Reference**: `examples/dags/data_ingestion/ingest_daily.py`

This DAG demonstrates:
- Ingesting data daily at 1 AM
- Using Airflow's S3Hook to interact with MinIO
- Proper error handling with retries
- Date-based partitioning

**Key concepts:**
```python
def upload_to_minio(**context):
    """Upload sample data to MinIO."""
    s3_hook = S3Hook(aws_conn_id='minio_default')

    # Use logical_date (Airflow 3.0 best practice)
    logical_date = context['logical_date'].strftime('%Y-%m-%d')
    s3_hook.load_string(
        string_data=f"Sample data for {logical_date}",
        key=f"raw/daily/{logical_date}/data.txt",
        bucket_name='datalake',
        replace=True
    )
```

**To use this example:**

1. **Copy to your DAGs directory:**

   **🐧 Linux/macOS:**
   ```bash
   cp examples/dags/data_ingestion/ingest_daily.py airflow/dags/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\dags\data_ingestion\ingest_daily.py airflow\dags\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\dags\data_ingestion\ingest_daily.py airflow\dags\
   ```

2. Wait for Airflow to detect it, then trigger from the UI

### Data Transformation Pipeline

**Reference**: `examples/dags/data_transformation/transform_pipeline.py`

This DAG demonstrates:
- Orchestrating Spark jobs with Airflow
- Using SparkSubmitOperator
- Task dependencies
- Passing parameters to Spark jobs

**Key concepts:**
```python
transform_raw_data = SparkSubmitOperator(
    task_id='transform_raw_data',
    application='/opt/spark/jobs/batch_processing.py',
    conn_id='spark_default',
    application_args=['--date', '{{ ds }}'],
    conf={
        'spark.jars.packages': 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0',
    },
)
```

**To use this example:**

1. **Copy to your DAGs directory:**

   **🐧 Linux/macOS:**
   ```bash
   cp examples/dags/data_transformation/transform_pipeline.py airflow/dags/
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\dags\data_transformation\transform_pipeline.py airflow\dags\
   ```

   **💻 Windows (Command Prompt):**
   ```cmd
   copy examples\dags\data_transformation\transform_pipeline.py airflow\dags\
   ```

2. Wait for Airflow to detect it, then trigger from the UI

## Building Your Own Pipeline

Now that you've seen the examples, here's how to build your own pipeline:

### Step 1: Design Your Data Flow

1. **Source**: Where is your data coming from? (files, APIs, databases)
2. **Storage**: Where will raw data be stored? (MinIO buckets)
3. **Processing**: What transformations are needed? (Spark jobs)
4. **Destination**: Where will processed data go? (Iceberg tables)
5. **Schedule**: How often should this run? (Airflow schedule)

### Step 2: Create Your Spark Job

1. Copy an example as a starting point:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/spark_job.py spark/jobs/my_job.py
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\spark_job.py spark\jobs\my_job.py
   ```

2. Edit `spark/jobs/my_job.py` with your transformations

3. Test it:

   **🐧 Linux/macOS:**
   ```bash
   make spark-submit APP=spark/jobs/my_job.py
   ```

   **💻 Windows:**
   ```powershell
   docker-compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/my_job.py
   ```

### Step 3: Create Your Airflow DAG

1. Copy an example as a starting point:

   **🐧 Linux/macOS:**
   ```bash
   cp examples/simple_dag.py airflow/dags/my_pipeline.py
   ```

   **💻 Windows (PowerShell):**
   ```powershell
   Copy-Item examples\simple_dag.py airflow\dags\my_pipeline.py
   ```

2. Edit `airflow/dags/my_pipeline.py` with your logic

3. Airflow will automatically detect it

4. Test and monitor in the Airflow UI

### Step 4: Monitor and Debug

- **Airflow UI**: Monitor task execution, view logs
- **Spark UI**: Monitor Spark job performance
- **MinIO Console**: Verify data files

## Common Use Cases

### Use Case 1: Batch Data Processing

1. Ingest data daily from external sources → MinIO
2. Process with Spark → transform and aggregate
3. Write to Iceberg tables → queryable data lake
4. Orchestrate with Airflow → schedule and monitor

**Example Flow:**
```
External API → Airflow (ingest) → MinIO (raw/)
→ Airflow (trigger Spark) → Spark Processing
→ Iceberg Table (processed/) → Analytics
```

### Use Case 2: Data Quality Pipeline

1. Read data from Iceberg tables
2. Run data quality checks with Spark
3. Write results back to quality tables
4. Alert on failures

See `examples/tests/spark/test_data_quality.py` for testing patterns.

### Use Case 3: Incremental Processing

1. Track last processed timestamp
2. Read only new data
3. Process incrementally
4. Update Iceberg tables (ACID safe)

## Best Practices

### 1. Never Run Code Directly from examples/
- **Always copy** example code to the proper location before running
- Spark jobs: Copy to `spark/jobs/`
- Airflow DAGs: Copy to `airflow/dags/`
- Scripts: Copy to `scripts/`
- This keeps examples clean as reference and prevents accidental modifications

### 2. Use Iceberg for All Tables
- ACID transactions prevent data corruption
- Schema evolution allows changes without breaking queries
- Time travel enables auditing and rollback

### 3. Organize Your Data in MinIO
```
datalake/
├── raw/           # Unprocessed data
├── staging/       # Intermediate processing
├── processed/     # Final clean data
└── archive/       # Historical data
```

### 4. Make Your DAGs Idempotent
- Tasks should produce the same result when re-run
- Use date parameters for partitioning
- Clean up before writing (or use upserts)

### 5. Use the Tested Examples
- All code in `examples/` is tested and working
- Copy and modify rather than starting from scratch
- Run tests: `make test`

## Troubleshooting

### Services won't start

**🐧 Linux/macOS:**
```bash
make down
make clean
make up
```

**💻 Windows:**
```powershell
docker-compose down
docker system prune -f
docker-compose up -d
```

### Can't connect to MinIO
- Check MinIO is running: `docker ps | grep minio`
- Verify endpoint: `http://localhost:9000` (API) or `http://localhost:9001` (Console)

### Airflow DAG not showing up

**🐧 Linux/macOS:**
- Check DAG file syntax: `make airflow-check`
- View Airflow logs: `make airflow-logs`

**💻 Windows:**
- Check syntax: `python airflow/dags/your_dag.py`
- View logs: `docker logs ldp-airflow-webserver`

### Spark job failing

**🐧 Linux/macOS:**
- Check Spark logs: `make spark-logs`

**💻 Windows:**
- Check logs: `docker logs ldp-spark-master`

**All platforms:**
- Verify Iceberg configuration in `config/iceberg/catalog.properties`

## Next Steps

1. **Run all examples**: Work through each example in order
2. **Explore the tests**: See `examples/tests/` for integration test patterns
3. **Read the docs**:
   - `docs/hive-vs-iceberg.md` - Understand why we use Iceberg
   - `docs/iceberg-hadoop-catalog.md` - Learn about catalog configuration
4. **Build your pipeline**: Start with a simple use case
5. **Join the community**: Contribute examples and improvements

## Additional Resources

- **Commands**:
  - Linux/macOS: Run `make help` to see all available commands
  - Windows: Use `docker-compose` commands directly or see commands in `Makefile`
- **Configuration Files**: See `config/` directory for all service configurations
- **Testing**: See `examples/tests/` for test examples
- **Production Guide**: See `docs/production-guide.md` for deployment guidance

## Platform-Specific Notes

### Windows Users

**File Paths:**
- Windows uses backslashes `\` for paths (e.g., `airflow\dags\`)
- PowerShell supports both `/` and `\`
- Always use forward slashes `/` inside Docker containers

**Common Commands:**
| Task | Linux/macOS | Windows |
|------|-------------|---------|
| Copy file | `cp source dest` | `Copy-Item source dest` or `copy source dest` |
| List files | `ls` | `dir` or `Get-ChildItem` |
| Start platform | `make up` | `docker-compose up -d` |
| Stop platform | `make down` | `docker-compose down` |
| View logs | `make logs` | `docker-compose logs` |

**Recommended Setup:**
- Use **PowerShell** (more powerful than Command Prompt)
- Or use **WSL (Windows Subsystem for Linux)** for full Linux compatibility
- Install **Docker Desktop for Windows**

### Linux/macOS Users

- Use the `Makefile` for convenient commands
- All `make` commands work out of the box
- Bash scripts in `scripts/` directory can be run directly

## Summary

You've learned how to:
- ✅ Start and access LDP services
- ✅ Work with MinIO for object storage
- ✅ Process data with Spark
- ✅ Manage tables with Iceberg (ACID, time travel)
- ✅ Orchestrate workflows with Airflow
- ✅ Use tested example code for your own pipelines

All the code in this tutorial is tested and ready to use. Start by running the examples, then modify them for your specific use cases.

Happy data engineering! 🚀

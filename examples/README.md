# Examples Directory

This directory contains **reference examples** and **template code** for working with LDP.

## Important: This Directory is Optional

**The `examples/` directory is for learning and reference only. You can:**
- ✅ **Copy examples** to the appropriate folders and modify them for your needs
- ✅ **Delete this entire directory** if you want to start fresh without examples
- ✅ **Keep it** as a reference library for tested code patterns

**The LDP platform does not require this directory to function.**

## Structure

```
examples/
├── dags/                          # Example Airflow DAGs
│   ├── data_ingestion/
│   │   └── ingest_daily.py       # Daily data ingestion to MinIO
│   └── data_transformation/
│       └── transform_pipeline.py  # Spark transformation pipeline
├── spark-jobs/                    # Example Spark jobs
├── tests/                         # Integration and E2E tests
│   ├── airflow/                  # Airflow DAG tests
│   ├── spark/                    # Spark job tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end pipeline tests
├── iceberg_crud.py               # Iceberg CRUD operations
├── minio_operations.py           # MinIO/S3 operations
├── spark_job.py                  # Simple Spark job
├── simple_dag.py                 # Simple Airflow DAG
└── README.md                     # This file
```

## How to Use These Examples

**Important**: Never run code directly from `examples/`. Always copy to the appropriate location first:

| Example Type | Copy To | Purpose |
|-------------|---------|---------|
| Spark jobs | `spark/jobs/` | Data processing jobs |
| Airflow DAGs | `airflow/dags/` | Workflow orchestration |
| Scripts | `scripts/` | Utility scripts |

## Quick Start

Follow these steps to try the examples:

### 1. MinIO Operations (Storage)

**Copy and run:**
```bash
# Copy to scripts directory
cp examples/minio_operations.py scripts/

# Run it
python scripts/minio_operations.py
```

**What it does:**
- Connects to MinIO (S3-compatible storage)
- Lists buckets
- Uploads/downloads files
- Demonstrates basic object storage operations

### 2. Simple Spark Job (Processing)

**Copy and run:**
```bash
# Copy to Spark jobs directory
cp examples/spark_job.py spark/jobs/

# Submit to Spark
make spark-submit APP=spark/jobs/spark_job.py
```

**What it does:**
- Creates a Spark DataFrame
- Performs aggregations
- Shows basic Spark operations

### 3. Iceberg CRUD (Table Management)

**Copy and run:**
```bash
# Copy to Spark jobs directory
cp examples/iceberg_crud.py spark/jobs/

# Submit to Spark
make spark-submit APP=spark/jobs/iceberg_crud.py
```

**What it does:**
- Creates Iceberg tables with ACID support
- Inserts, updates, and deletes data
- Demonstrates time travel (view table history)

### 4. Simple Airflow DAG (Orchestration)

```bash
# Copy DAG to Airflow
cp examples/simple_dag.py airflow/dags/

# Wait for Airflow to detect it (1-2 minutes)

# Trigger from UI or CLI
make airflow-trigger DAG=simple_example
```

**What it does:**
- Defines a simple 3-task workflow
- Shows task dependencies
- Demonstrates BashOperator and PythonOperator

## Production-Ready Examples

### Daily Data Ingestion

**File**: `dags/data_ingestion/ingest_daily.py`

**Features:**
- Scheduled to run daily at 1 AM
- Uses Airflow's S3Hook for MinIO
- Proper error handling with retries
- Date-based partitioning

**Use case:** Ingesting daily data from external sources into your data lake

**To use:**
```bash
# Copy to Airflow DAGs directory
cp examples/dags/data_ingestion/ingest_daily.py airflow/dags/

# Wait for Airflow to detect it
```

### Data Transformation Pipeline

**File**: `dags/data_transformation/transform_pipeline.py`

**Features:**
- Orchestrates Spark jobs with SparkSubmitOperator
- Task dependencies (start → transform → end)
- Passes date parameters to Spark jobs
- Includes Iceberg dependencies

**Use case:** Daily batch processing of raw data

**To use:**
```bash
# Copy to Airflow DAGs directory
cp examples/dags/data_transformation/transform_pipeline.py airflow/dags/

# Wait for Airflow to detect it
```

## Testing Examples

The `tests/` directory contains comprehensive testing patterns:

### Unit Tests

**Airflow DAG tests** (`tests/airflow/test_dags.py`):
- Validate DAG structure
- Check for cycles
- Verify task configurations

**Spark tests** (`tests/spark/`):
- Data transformation tests
- Data quality validation
- Schema validation

### Integration Tests

**Location**: `tests/integration/`

- **Iceberg tables** (`test_iceberg_tables.py`): Test Iceberg table operations
- **MinIO access** (`test_minio_access.py`): Test S3/MinIO connectivity
- **Airflow + Spark** (`test_airflow_spark.py`): Test full pipeline integration

### End-to-End Tests

**Location**: `tests/e2e/test_pipeline.py`

Tests complete data pipeline from ingestion to transformation.

**Run tests:**
```bash
# All tests
make test

# Specific test file
pytest examples/tests/integration/test_iceberg_tables.py
```

## Working with Examples

### Approach 1: Copy and Modify (Recommended)

Best for learning and building new features:

```bash
# 1. Copy the example
cp examples/simple_dag.py airflow/dags/my_first_dag.py

# 2. Edit the copied file
vim airflow/dags/my_first_dag.py

# 3. Run/deploy it
```

### Approach 2: Use as Reference Only

For building custom pipelines:

1. Read the example code in `examples/`
2. Understand the pattern
3. Write your own from scratch in the appropriate directory
4. Reference examples when stuck

### Approach 3: Start Fresh Without Examples

If you prefer to start with a clean slate:

```bash
# Remove the entire examples directory
rm -rf examples/

# The LDP platform will continue to work normally
# Build your own code in:
# - spark/jobs/
# - airflow/dags/
# - scripts/
```

## Example Code Patterns

### Pattern 1: Spark Session Creation

All Spark examples show how to create a properly configured Spark session:

```python
spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
    .getOrCreate()
```

### Pattern 2: MinIO Connection

All MinIO examples use boto3 with proper configuration:

```python
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:30900',
    aws_access_key_id='admin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)
```

### Pattern 3: Airflow Best Practices

All DAG examples follow Airflow 3.0+ best practices:

```python
with DAG(
    'dag_name',
    default_args={
        'owner': 'ldp',
        'start_date': datetime(2024, 1, 1),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    schedule='@daily',
    catchup=False,  # Don't backfill
    tags=['category'],  # For organization
) as dag:
    # Tasks here
```

### Pattern 4: Error Handling

Examples include proper error handling:

```python
try:
    # Your operation
    result = spark.table("my_table")
except Exception as e:
    logging.error(f"Failed to read table: {e}")
    raise
finally:
    spark.stop()
```

## Customizing Examples

### Change MinIO Endpoint

Update endpoint URLs based on your deployment:

- **Local**: `http://localhost:30900`
- **Docker network**: `http://minio:9000`
- **Kubernetes**: `http://minio.default.svc.cluster.local:9000`

### Change Catalog Configuration

Modify Iceberg catalog settings in `config/iceberg/catalog.properties`

### Change Schedules

Adjust DAG schedules:

```python
schedule='@daily'       # Once per day
schedule='@hourly'      # Once per hour
schedule='0 */6 * * *'  # Every 6 hours
schedule='0 2 * * *'    # Daily at 2 AM
```

## Common Modifications

### Add Authentication

For production, add proper authentication:

```python
# MinIO with temporary credentials
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('MINIO_ENDPOINT'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)
```

### Add Data Validation

Extend examples with data quality checks:

```python
# Example validation
if df.count() == 0:
    raise ValueError("DataFrame is empty!")

if df.filter(col("id").isNull()).count() > 0:
    raise ValueError("Found null IDs!")
```

### Add Monitoring

Add logging and metrics:

```python
import logging

logging.info(f"Processing {df.count()} records")
logging.info(f"Write completed to {table_name}")
```

## Best Practices

1. **Never run from examples/ directly** - Always copy to the appropriate folder first
2. **Use examples as templates** - Copy, then modify for your needs
3. **Keep examples/ as reference** - Or delete it if you prefer a clean start
4. **Test locally first** - Use `make spark-submit` or `python` to test
5. **Keep credentials separate** - Use environment variables
6. **Add error handling** - Don't let pipelines fail silently
7. **Make tasks idempotent** - Safe to re-run
8. **Use proper logging** - For debugging and monitoring

## Next Steps

1. **Run all examples** - Get familiar with each component
2. **Read the tutorial** - See `docs/getting-started-tutorial.md`
3. **Check the tests** - Learn testing patterns
4. **Build your pipeline** - Use examples as foundation

## Troubleshooting

### Import errors

Ensure packages are installed:
```bash
# For Spark jobs
cat docker/spark/requirements.txt

# For Airflow DAGs
cat docker/airflow/requirements.txt
```

### Connection errors

- Verify services are running: `make status`
- Check endpoints match your deployment
- Verify credentials

### Spark job failures

- Check logs: `make spark-logs`
- Verify Iceberg configuration
- Test locally first

## Learn More

- **Getting Started Tutorial**: `docs/getting-started-tutorial.md`
- **Iceberg vs Hive**: `docs/hive-vs-iceberg.md`
- **Production Guide**: `docs/production-guide.md`
- **Project Structure**: `docs/project-structure.md`

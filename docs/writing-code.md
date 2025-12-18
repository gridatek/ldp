# Where to Write Your Code

This guide explains exactly where to place your custom code in the LDP project.

## Quick Reference

| What You're Building | Where to Write Code |
|---------------------|-------------------|
| **Airflow workflows** | `airflow/dags/*.py` |
| **Spark data processing** | `spark/jobs/*.py` |
| **Reusable Spark functions** | `spark/lib/*.py` |
| **Interactive analysis** | `spark/notebooks/*.ipynb` |
| **SQL queries** | `spark/sql/*.sql` |
| **Custom Airflow operators** | `airflow/plugins/custom_operators/*.py` |
| **Input data files** | `data/raw/*` |
| **Configuration** | `config/env/.env` |

## Project Structure for Your Code

```
ldp/
├── airflow/
│   ├── dags/                      # ← Write your Airflow DAGs here
│   │   ├── your_pipeline.py
│   │   └── your_etl_workflow.py
│   │
│   └── plugins/                   # ← Custom Airflow operators
│       └── custom_operators/
│           └── your_operator.py
│
├── spark/
│   ├── jobs/                      # ← Write your Spark jobs here
│   │   ├── your_batch_job.py
│   │   └── your_streaming_job.py
│   │
│   ├── lib/                       # ← Reusable Spark utilities
│   │   ├── your_transformations.py
│   │   └── your_utils.py
│   │
│   ├── notebooks/                 # ← Jupyter notebooks
│   │   └── your_analysis.ipynb
│   │
│   └── sql/                       # ← SQL scripts
│       └── your_queries.sql
│
├── data/
│   ├── raw/                       # ← Input datasets
│   │   └── your_data.csv
│   │
│   ├── processed/                 # ← Output data
│   └── staging/                   # ← Temporary data
│
└── config/
    └── env/                       # ← Environment variables
        └── .env
```

## Starting from Scratch

The project directories are intentionally empty to give you a clean slate. Here's how to get started:

### Option 1: Start with Examples (Recommended for Learning)

Load the example code to see working implementations:

```bash
make load-examples
```

This copies example DAGs, Spark jobs, and libraries into your project directories. You can:
- Study the examples to understand the structure
- Modify them for your needs
- Delete them when ready to write your own

### Option 2: Start Fresh

Simply create new files in the appropriate directories:

```bash
# Create your first DAG
touch airflow/dags/my_pipeline.py

# Create your first Spark job
touch spark/jobs/my_data_processing.py
```

## Detailed Guide by Component

### 1. Airflow DAGs (`airflow/dags/`)

**When to use:** Orchestrating workflows, scheduling tasks, managing dependencies

**File naming:** Use descriptive names like `etl_pipeline.py`, `data_ingestion_daily.py`

**Example structure:**
```python
# airflow/dags/my_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def my_task():
    print("Processing data...")
    # Your logic here

with DAG(
    'my_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id='process_data',
        python_callable=my_task
    )
```

**Subdirectories:** You can organize DAGs in subdirectories:
```
airflow/dags/
├── ingestion/
│   ├── daily_load.py
│   └── hourly_sync.py
└── transformation/
    └── aggregate_metrics.py
```

---

### 2. Spark Jobs (`spark/jobs/`)

**When to use:** Data processing, transformations, analytics

**File naming:** Descriptive names like `process_sales.py`, `clean_user_data.py`

**Example structure:**
```python
# spark/jobs/process_sales.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum

def main():
    spark = SparkSession.builder \
        .appName("ProcessSales") \
        .getOrCreate()

    # Read data
    df = spark.read.csv("s3a://data/sales.csv", header=True)

    # Transform
    result = df.groupBy("region").agg(sum("revenue"))

    # Write
    result.write.mode("overwrite").parquet("s3a://output/sales_by_region")

    spark.stop()

if __name__ == "__main__":
    main()
```

---

### 3. Spark Libraries (`spark/lib/`)

**When to use:** Reusable functions, utilities, shared logic

**File naming:** Group related functions: `transformations.py`, `validators.py`, `io_helpers.py`

**Example structure:**
```python
# spark/lib/transformations.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, upper

def standardize_names(df: DataFrame, column: str) -> DataFrame:
    """Standardize name column to uppercase."""
    return df.withColumn(column, upper(col(column)))

def remove_nulls(df: DataFrame, columns: list) -> DataFrame:
    """Remove rows with nulls in specified columns."""
    for column in columns:
        df = df.filter(col(column).isNotNull())
    return df
```

**Usage in Spark jobs:**
```python
# spark/jobs/clean_data.py
from spark.lib.transformations import standardize_names, remove_nulls

df = spark.read.csv("data.csv")
df = standardize_names(df, "name")
df = remove_nulls(df, ["email", "phone"])
```

---

### 4. Jupyter Notebooks (`spark/notebooks/`)

**When to use:** Exploratory data analysis, prototyping, interactive development

**Access:**
```bash
# Get Jupyter URL and token
kubectl logs -n ldp deployment/jupyter
```

**Creating notebooks:**
1. Access Jupyter at `http://<minikube-ip>:30888`
2. Create new notebook in the `notebooks/` directory
3. Notebooks are persisted and appear in `spark/notebooks/`

---

### 5. SQL Scripts (`spark/sql/`)

**When to use:** Complex queries, table definitions, data transformations

**Example structure:**
```sql
-- spark/sql/create_tables.sql
CREATE TABLE IF NOT EXISTS sales (
    id BIGINT,
    date DATE,
    amount DECIMAL(10,2),
    region STRING
) USING iceberg
PARTITIONED BY (region);
```

**Usage in Spark:**
```python
spark.sql(open("spark/sql/create_tables.sql").read())
```

---

### 6. Custom Airflow Operators (`airflow/plugins/`)

**When to use:** Reusable custom operators for Airflow

**Example structure:**
```python
# airflow/plugins/custom_operators/iceberg_operator.py
from airflow.models import BaseOperator

class IcebergOperator(BaseOperator):
    def __init__(self, query: str, **kwargs):
        super().__init__(**kwargs)
        self.query = query

    def execute(self, context):
        # Execute Iceberg query
        pass
```

---

### 7. Data Files (`data/`)

**Directory structure:**
- `data/raw/` - Input datasets (CSV, JSON, Parquet, etc.)
- `data/processed/` - Transformed/cleaned data
- `data/staging/` - Temporary intermediate data

**Usage:**
```bash
# Add your datasets
cp ~/my_data.csv data/raw/

# Access in Spark
df = spark.read.csv("file:///opt/ldp/data/raw/my_data.csv")

# Or mount to MinIO and access via S3
aws s3 cp data/raw/my_data.csv s3://data/raw/ --endpoint-url http://minio:9000
```

---

### 8. Configuration (`config/env/`)

**Environment variables:**
```bash
# config/env/.env
AWS_ACCESS_KEY_ID=admin
AWS_SECRET_ACCESS_KEY=minioadmin
MINIO_ENDPOINT=http://minio:9000
DATABASE_URL=postgresql://user:pass@postgres:5432/db
```

**Usage in code:**
```python
import os
from dotenv import load_dotenv

load_dotenv('config/env/.env')

minio_endpoint = os.getenv('MINIO_ENDPOINT')
```

---

## Development Workflow

### 1. Create Your Code

```bash
# Create a new DAG
vim airflow/dags/my_etl.py

# Create a new Spark job
vim spark/jobs/process_data.py

# Add input data
cp ~/dataset.csv data/raw/
```

### 2. Test Locally

```bash
# Python syntax check
python -m py_compile airflow/dags/my_etl.py

# Run Spark job locally (if Spark installed)
spark-submit spark/jobs/process_data.py
```

### 3. Deploy to Platform

```bash
# Restart to load new DAGs
make stop && make start

# Or if platform is running, wait 30 seconds for Airflow to detect new DAGs
```

### 4. Verify

```bash
# Check Airflow UI for your DAG
open http://$(minikube ip):30080

# Check logs
make logs
kubectl logs -n ldp -l component=scheduler
```

---

## Best Practices

### Code Organization

1. **One DAG per file** - Easier to manage and debug
2. **Group related jobs** - Use subdirectories for organization
3. **Reuse code** - Put common logic in `spark/lib/`
4. **Clear naming** - Use descriptive file and function names

### File Naming Conventions

```
✓ Good:
  - etl_sales_daily.py
  - transform_user_events.py
  - ingest_api_data.py

✗ Avoid:
  - dag1.py
  - test.py
  - script.py
```

### Code Structure

```python
# Good structure
"""
Description of what this DAG does.
"""
from airflow import DAG
from datetime import datetime

# Constants
DEFAULT_ARGS = {
    'owner': 'data-team',
    'retries': 2,
}

# Helper functions
def process_data():
    """Process the data."""
    pass

# DAG definition
with DAG('my_pipeline', default_args=DEFAULT_ARGS) as dag:
    # Tasks here
    pass
```

### Testing

```bash
# Unit tests for Spark
pytest spark/tests/

# Unit tests for Airflow
pytest airflow/tests/

# Integration tests
pytest tests/integration/
```

---

## Common Patterns

### Pattern 1: ETL Pipeline

```
airflow/dags/etl_pipeline.py        # Orchestration
spark/jobs/extract.py               # Extract data
spark/jobs/transform.py             # Transform data
spark/jobs/load.py                  # Load to destination
spark/lib/validators.py             # Data quality checks
```

### Pattern 2: Scheduled Batch Processing

```
airflow/dags/nightly_batch.py       # Scheduled DAG
spark/jobs/aggregate_metrics.py     # Batch processing
spark/sql/create_views.sql          # SQL transformations
```

### Pattern 3: Data Quality Pipeline

```
airflow/dags/data_quality.py        # Quality checks orchestration
spark/lib/data_quality.py           # Quality check functions
spark/lib/metrics.py                # Metrics calculation
```

---

## Examples

The `examples/` directory contains reference implementations:

```
examples/
├── simple_dag.py                   # Basic Airflow DAG
├── spark_job.py                    # Simple Spark job
├── iceberg_crud.py                 # Iceberg operations
├── minio_operations.py             # MinIO/S3 operations
├── dags/                           # Complete DAG examples
├── spark-jobs/                     # Complete Spark job examples
└── spark-lib/                      # Utility library examples
```

Load examples to study:
```bash
make load-examples
```

---

## Troubleshooting

### DAG not appearing in Airflow UI

1. **Wait 30 seconds** - Airflow scans for new DAGs every 30 seconds
2. **Check syntax** - `python -m py_compile airflow/dags/your_dag.py`
3. **Check logs** - `kubectl logs -n ldp -l component=scheduler`
4. **Verify location** - DAG must be in `airflow/dags/` or subdirectory

### Spark job not running

1. **Check imports** - Ensure `spark/lib/` is in Python path
2. **Verify Spark session** - Check SparkSession configuration
3. **Check resources** - Ensure sufficient memory/CPU
4. **View logs** - `kubectl logs -n ldp -l app=spark-master`

### Import errors

```python
# Wrong - won't work
from lib.utils import my_function

# Correct - use full path
from spark.lib.utils import my_function
```

---

## Next Steps

1. **Start with examples** - `make load-examples`
2. **Study the code** - Understand patterns and structure
3. **Modify examples** - Adapt to your needs
4. **Write your own** - Create custom DAGs and jobs
5. **Test thoroughly** - Use unit and integration tests
6. **Document** - Add comments and docstrings

## Additional Resources

- [Setup Guide](setup-guide.md) - Platform installation
- [Project Structure](project-structure.md) - Full directory layout
- [Troubleshooting](troubleshooting.md) - Common issues
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Spark Documentation](https://spark.apache.org/docs/latest/)
- [Iceberg Documentation](https://iceberg.apache.org/docs/latest/)

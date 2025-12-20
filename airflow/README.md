# Airflow Directory

This directory contains Apache Airflow configuration and DAG files for workflow orchestration.

## Structure

```
airflow/
├── dags/              # Your Airflow DAG files go here
├── logs/              # Airflow execution logs (auto-generated)
├── plugins/           # Custom Airflow plugins
└── README.md          # This file
```

## What is Airflow?

Apache Airflow is a platform to programmatically author, schedule, and monitor workflows (DAGs - Directed Acyclic Graphs).

## Adding DAGs

### Option 1: Copy from Examples

Copy tested DAG examples to this directory:

```bash
# Simple example
cp examples/simple_dag.py airflow/dags/

# Production examples
cp examples/dags/data_ingestion/ingest_daily.py airflow/dags/
cp examples/dags/data_transformation/transform_pipeline.py airflow/dags/
```

### Option 2: Create Your Own

Create a new DAG file in `airflow/dags/`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    'my_pipeline',
    default_args={
        'owner': 'ldp',
        'start_date': datetime(2024, 1, 1),
        'retries': 1,
    },
    description='My data pipeline',
    schedule='@daily',
    catchup=False,
) as dag:

    task = BashOperator(
        task_id='my_task',
        bash_command='echo "Hello LDP!"',
    )
```

## DAG Best Practices

1. **Use `catchup=False`** - Don't backfill historical runs automatically
2. **Set proper retries** - Allow tasks to retry on transient failures
3. **Tag your DAGs** - Use tags for organization: `tags=['ingestion', 'daily']`
4. **Use logical_date** - Instead of deprecated `execution_date` (Airflow 3.0+)
5. **Make tasks idempotent** - Tasks should be safe to re-run

## Useful Commands

```bash
# Trigger a DAG
make airflow-trigger DAG=my_pipeline

# List all DAGs
make airflow-dags

# Check DAG for errors
make airflow-check

# View logs
make airflow-logs
```

## Accessing Airflow UI

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

## Example DAGs

See the `examples/` directory for tested, production-ready DAG examples:

- `examples/simple_dag.py` - Basic DAG structure
- `examples/dags/data_ingestion/ingest_daily.py` - Daily data ingestion
- `examples/dags/data_transformation/transform_pipeline.py` - Spark transformation pipeline

## Common Issues

### DAG not appearing in UI

1. Check for Python syntax errors: `python airflow/dags/your_dag.py`
2. Wait 1-2 minutes for Airflow to scan for new DAGs
3. Check Airflow logs: `make airflow-logs`

### Import errors

Ensure all required packages are in `docker/airflow/requirements.txt`

## Learn More

- [Airflow Documentation](https://airflow.apache.org/docs/)
- Tutorial: `docs/getting-started-tutorial.md`
- Production Guide: `docs/production-guide.md`

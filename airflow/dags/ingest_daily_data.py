"""
Daily data ingestion DAG that uploads data to MinIO.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'ldp',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def upload_to_minio(**context):
    """Upload data to MinIO storage."""
    execution_date = context['ds']
    print(f"Uploading data for date: {execution_date}")
    # Placeholder for actual MinIO upload logic
    return f"Data uploaded for {execution_date}"


with DAG(
    'ingest_daily_data',
    default_args=default_args,
    description='Daily data ingestion to MinIO',
    schedule='0 1 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ingestion', 'minio', 'data'],
) as dag:

    start_task = BashOperator(
        task_id='start',
        bash_command='echo "Starting daily data ingestion"',
    )

    upload_task = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_to_minio,
    )

    end_task = BashOperator(
        task_id='end',
        bash_command='echo "Daily data ingestion completed"',
    )

    start_task >> upload_task >> end_task

"""
Daily data ingestion DAG.
Ingests data from various sources into MinIO.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

default_args = {
    'owner': 'ldp',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def upload_to_minio(**context):
    """Upload sample data to MinIO."""
    s3_hook = S3Hook(aws_conn_id='minio_default')

    # Example: Upload a file to MinIO
    execution_date = context['execution_date'].strftime('%Y-%m-%d')
    s3_hook.load_string(
        string_data=f"Sample data for {execution_date}",
        key=f"raw/daily/{execution_date}/data.txt",
        bucket_name='datalake',
        replace=True
    )
    print(f"Uploaded data for {execution_date} to MinIO")


with DAG(
    'ingest_daily_data',
    default_args=default_args,
    description='Daily data ingestion to MinIO',
    schedule='0 1 * * *',  # Run daily at 1 AM
    catchup=False,
    tags=['ingestion', 'daily', 'minio'],
) as dag:

    ingest_task = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_to_minio,
    )

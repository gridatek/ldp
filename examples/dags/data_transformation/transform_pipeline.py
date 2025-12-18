"""
Data transformation pipeline using Spark and Iceberg.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'ldp',
    'depends_on_past': True,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'transform_pipeline',
    default_args=default_args,
    description='Transform raw data using Spark',
    schedule='0 2 * * *',  # Run daily at 2 AM
    catchup=False,
    tags=['transformation', 'spark', 'iceberg'],
) as dag:

    start = BashOperator(
        task_id='start',
        bash_command='echo "Starting transformation pipeline"',
    )

    transform_raw_data = SparkSubmitOperator(
        task_id='transform_raw_data',
        application='/opt/spark/jobs/batch_processing.py',
        conn_id='spark_default',
        application_args=['--date', '{{ ds }}'],
        conf={
            'spark.jars.packages': 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0',
        },
    )

    end = BashOperator(
        task_id='end',
        bash_command='echo "Transformation completed"',
    )

    start >> transform_raw_data >> end

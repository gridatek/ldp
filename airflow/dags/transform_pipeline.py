"""
Data transformation pipeline DAG using Spark.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'ldp',
    'depends_on_past': True,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'transform_pipeline',
    default_args=default_args,
    description='Data transformation using Spark',
    schedule='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['transformation', 'spark', 'etl'],
) as dag:

    start_task = BashOperator(
        task_id='start',
        bash_command='echo "Starting data transformation pipeline"',
    )

    transform_job = SparkSubmitOperator(
        task_id='run_transformation',
        application='/opt/spark/jobs/batch_processing.py',
        conn_id='spark_default',
        conf={
            'spark.jars.packages': 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,'
                                  'org.apache.hadoop:hadoop-aws:3.3.4',
            'spark.sql.catalog.local': 'org.apache.iceberg.spark.SparkCatalog',
            'spark.sql.catalog.local.type': 'hadoop',
            'spark.sql.catalog.local.warehouse': 's3a://warehouse/',
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'admin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin',
            'spark.hadoop.fs.s3a.path.style.access': 'true',
        },
        verbose=True,
    )

    end_task = BashOperator(
        task_id='end',
        bash_command='echo "Data transformation pipeline completed"',
    )

    start_task >> transform_job >> end_task

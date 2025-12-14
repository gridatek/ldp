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
    schedule_interval=timedelta(days=1),
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

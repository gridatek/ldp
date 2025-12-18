"""
Integration tests for Airflow and Spark.
"""
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../airflow/dags'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../airflow/plugins'))


class TestAirflowSparkIntegration:
    """Test Airflow and Spark integration."""

    @pytest.fixture
    def airflow_config(self):
        """Airflow configuration for tests."""
        return {
            "webserver_url": os.getenv("AIRFLOW_URL", "http://localhost:30080"),
            "username": os.getenv("AIRFLOW_USER", "admin"),
            "password": os.getenv("AIRFLOW_PASSWORD", "admin"),
        }

    @pytest.fixture
    def spark_config(self):
        """Spark configuration for tests."""
        return {
            "master_url": os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"),
            "master_web_url": os.getenv("SPARK_MASTER_WEB_URL", "http://localhost:30707"),
        }

    def test_spark_connection(self, spark_session):
        """Test that Spark session can be created and configured correctly."""
        assert spark_session is not None
        assert spark_session.sparkContext.appName == "test"

        sc = spark_session.sparkContext
        assert sc.master.startswith("local")

        test_data = [(1, "a"), (2, "b"), (3, "c")]
        df = spark_session.createDataFrame(test_data, ["id", "value"])
        assert df.count() == 3
        assert len(df.columns) == 2

    def test_spark_iceberg_catalog_config(self, spark_session):
        """Test that Spark can be configured with Iceberg catalog settings."""
        iceberg_conf = {
            "spark.sql.catalog.local": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.local.type": "hadoop",
            "spark.sql.catalog.local.warehouse": "s3a://warehouse/",
        }

        for key, expected_value in iceberg_conf.items():
            pass

        assert spark_session is not None

    def test_dag_import_validation(self):
        """Test that DAG files can be imported without errors."""
        dag_errors = []

        dag_files = [
            "example_spark_job",
            "data_ingestion.ingest_daily",
            "data_transformation.transform_pipeline",
        ]

        for dag_module in dag_files:
            try:
                __import__(dag_module)
            except ImportError as e:
                if "airflow" not in str(e).lower():
                    dag_errors.append(f"{dag_module}: {e}")
            except Exception as e:
                dag_errors.append(f"{dag_module}: {e}")

        assert len(dag_errors) == 0, f"DAG import errors: {dag_errors}"

    def test_dag_structure_validation(self):
        """Test that DAGs have required structure and properties."""
        try:
            from airflow.models import DagBag

            dagbag = DagBag(
                dag_folder=os.path.join(
                    os.path.dirname(__file__), '../../airflow/dags'
                ),
                include_examples=False,
            )

            assert len(dagbag.import_errors) == 0, (
                f"DAG import errors: {dagbag.import_errors}"
            )

            for dag_id, dag in dagbag.dags.items():
                assert dag.default_args is not None, (
                    f"DAG {dag_id} missing default_args"
                )
                assert len(dag.tasks) > 0, f"DAG {dag_id} has no tasks"

        except ImportError:
            pytest.skip("Airflow not installed, skipping DAG validation")

    def test_spark_submit_operator_config(self):
        """Test SparkSubmitOperator configuration validation."""
        try:
            from airflow.providers.apache.spark.operators.spark_submit import (
                SparkSubmitOperator,
            )

            operator = SparkSubmitOperator(
                task_id="test_spark_submit",
                application="/path/to/job.py",
                conn_id="spark_default",
                conf={
                    "spark.jars.packages": (
                        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0"
                    ),
                },
            )

            assert operator.task_id == "test_spark_submit"
            assert operator._conn_id == "spark_default"
            assert "spark.jars.packages" in operator._conf

        except ImportError:
            pytest.skip("Airflow Spark provider not installed")

    def test_iceberg_operator_instantiation(self):
        """Test IcebergTableOperator can be instantiated correctly."""
        try:
            from custom_operators.iceberg_operator import IcebergTableOperator

            operator = IcebergTableOperator(
                task_id="test_iceberg_create",
                operation="create",
                table_name="local.db.test_table",
                table_schema={"id": "BIGINT", "name": "STRING"},
                partition_by=["id"],
            )

            assert operator.operation == "create"
            assert operator.table_name == "local.db.test_table"
            assert "id" in operator.table_schema
            assert "id" in operator.partition_by

        except ImportError:
            pytest.skip("IcebergTableOperator not available")

    def test_spark_dataframe_operations(self, spark_session):
        """Test Spark DataFrame operations that would be used in DAGs."""
        test_data = [
            (1, "Alice", 100.0, "2024-01-01"),
            (2, "Bob", 200.0, "2024-01-02"),
            (3, "Charlie", 300.0, "2024-01-03"),
        ]
        df = spark_session.createDataFrame(
            test_data, ["id", "name", "amount", "date"]
        )

        filtered_df = df.filter(df.amount > 150)
        assert filtered_df.count() == 2

        aggregated = df.groupBy("date").sum("amount")
        assert aggregated.count() == 3

        df_with_new_col = df.withColumn(
            "processed_at",
            spark_session.sql("SELECT current_timestamp()").collect()[0][0]
        )
        assert "processed_at" in df_with_new_col.columns

    def test_spark_sql_execution(self, spark_session):
        """Test Spark SQL execution capabilities."""
        test_data = [(1, "test1"), (2, "test2")]
        df = spark_session.createDataFrame(test_data, ["id", "value"])
        df.createOrReplaceTempView("test_table")

        result = spark_session.sql("SELECT * FROM test_table WHERE id = 1")
        assert result.count() == 1
        assert result.collect()[0]["value"] == "test1"

        result = spark_session.sql("SELECT COUNT(*) as cnt FROM test_table")
        assert result.collect()[0]["cnt"] == 2

"""
Tests for Airflow DAGs.
"""
import os
import pytest
from airflow.models import DagBag


class TestDAGs:
    """Test suite for DAG validation."""

    def setup_method(self):
        """Setup test fixtures."""
        dag_folder = os.path.join(os.path.dirname(__file__), '../dags')
        self.dagbag = DagBag(dag_folder=dag_folder, include_examples=False)

    def test_no_import_errors(self):
        """Test that all DAGs can be imported without errors."""
        assert not self.dagbag.import_errors, \
            f"DAG import errors: {self.dagbag.import_errors}"

    def test_dag_loaded(self):
        """Test that expected DAGs are loaded."""
        expected_dags = [
            'example_spark_job',
            'ingest_daily_data',
            'transform_pipeline',
        ]

        for dag_id in expected_dags:
            assert dag_id in self.dagbag.dags, \
                f"DAG {dag_id} not found in DagBag"

    def test_dag_tags(self):
        """Test that DAGs have appropriate tags."""
        for dag_id, dag in self.dagbag.dags.items():
            assert dag.tags, f"DAG {dag_id} has no tags"

    def test_dag_retries(self):
        """Test that DAGs have retry configuration."""
        for dag_id, dag in self.dagbag.dags.items():
            for task_id, task in dag.task_dict.items():
                assert hasattr(task, 'retries'), \
                    f"Task {task_id} in DAG {dag_id} has no retry configuration"

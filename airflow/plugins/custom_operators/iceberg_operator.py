"""
Custom Airflow operator for Iceberg table operations.
"""
import json
import os
import tempfile
from typing import Any, Dict, List, Optional

from airflow.models import BaseOperator
from airflow.providers.apache.spark.hooks.spark_submit import SparkSubmitHook


class IcebergTableOperator(BaseOperator):
    """
    Operator to perform Iceberg table operations.

    :param operation: Operation to perform (create, drop, snapshot, etc.)
    :param table_name: Name of the Iceberg table (format: catalog.database.table)
    :param spark_conn_id: Spark connection ID
    :param table_schema: Schema for table creation (if operation is 'create')
        Example: {"id": "BIGINT", "name": "STRING", "created_at": "TIMESTAMP"}
    :param partition_by: List of columns to partition by (optional)
    :param table_properties: Additional Iceberg table properties (optional)
    :param warehouse_path: S3/MinIO warehouse path (default: s3a://warehouse/)
    :param s3_endpoint: S3/MinIO endpoint URL
    :param s3_access_key: S3/MinIO access key
    :param s3_secret_key: S3/MinIO secret key
    """

    template_fields = ['table_name', 'operation', 'warehouse_path']

    def __init__(
        self,
        operation: str,
        table_name: str,
        spark_conn_id: str = 'spark_default',
        table_schema: Optional[Dict[str, str]] = None,
        partition_by: Optional[List[str]] = None,
        table_properties: Optional[Dict[str, str]] = None,
        warehouse_path: str = 's3a://warehouse/',
        s3_endpoint: str = 'http://minio:9000',
        s3_access_key: str = 'admin',
        s3_secret_key: str = 'minioadmin',
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.operation = operation
        self.table_name = table_name
        self.spark_conn_id = spark_conn_id
        self.table_schema = table_schema or {}
        self.partition_by = partition_by or []
        self.table_properties = table_properties or {}
        self.warehouse_path = warehouse_path
        self.s3_endpoint = s3_endpoint
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key

    def _get_spark_conf(self) -> Dict[str, str]:
        """Get Spark configuration for Iceberg."""
        return {
            'spark.jars.packages': 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,'
                                   'org.apache.hadoop:hadoop-aws:3.3.4',
            'spark.sql.extensions': 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions',
            'spark.sql.catalog.spark_catalog': 'org.apache.iceberg.spark.SparkSessionCatalog',
            'spark.sql.catalog.spark_catalog.type': 'hive',
            'spark.sql.catalog.local': 'org.apache.iceberg.spark.SparkCatalog',
            'spark.sql.catalog.local.type': 'hadoop',
            'spark.sql.catalog.local.warehouse': self.warehouse_path,
            'spark.hadoop.fs.s3a.endpoint': self.s3_endpoint,
            'spark.hadoop.fs.s3a.access.key': self.s3_access_key,
            'spark.hadoop.fs.s3a.secret.key': self.s3_secret_key,
            'spark.hadoop.fs.s3a.path.style.access': 'true',
            'spark.hadoop.fs.s3a.impl': 'org.apache.hadoop.fs.s3a.S3AFileSystem',
        }

    def _submit_spark_sql(self, sql_statement: str) -> None:
        """Submit a Spark SQL statement via SparkSubmitHook."""
        script_content = f'''
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("IcebergOperation").getOrCreate()

sql = """{sql_statement}"""
spark.sql(sql)

spark.stop()
'''
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as script_file:
            script_file.write(script_content)
            script_path = script_file.name

        try:
            hook = SparkSubmitHook(
                conn_id=self.spark_conn_id,
                conf=self._get_spark_conf(),
            )
            hook.submit(application=script_path)
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)

    def execute(self, context: Any) -> str:
        """Execute the Iceberg operation."""
        self.log.info(f"Executing {self.operation} on table {self.table_name}")

        if self.operation == 'create':
            return self._create_table()
        elif self.operation == 'drop':
            return self._drop_table()
        elif self.operation == 'snapshot':
            return self._create_snapshot()
        else:
            raise ValueError(f"Unsupported operation: {self.operation}")

    def _create_table(self) -> str:
        """Create an Iceberg table."""
        self.log.info(f"Creating Iceberg table {self.table_name}")

        if not self.table_schema:
            raise ValueError("table_schema is required for create operation")

        columns = ", ".join(
            f"{col_name} {col_type}"
            for col_name, col_type in self.table_schema.items()
        )

        sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns}) USING iceberg"

        if self.partition_by:
            partition_cols = ", ".join(self.partition_by)
            sql += f" PARTITIONED BY ({partition_cols})"

        if self.table_properties:
            props = ", ".join(
                f"'{k}' = '{v}'" for k, v in self.table_properties.items()
            )
            sql += f" TBLPROPERTIES ({props})"

        self.log.info(f"Executing SQL: {sql}")
        self._submit_spark_sql(sql)

        return f"Created table {self.table_name}"

    def _drop_table(self) -> str:
        """Drop an Iceberg table."""
        self.log.info(f"Dropping Iceberg table {self.table_name}")

        sql = f"DROP TABLE IF EXISTS {self.table_name} PURGE"

        self.log.info(f"Executing SQL: {sql}")
        self._submit_spark_sql(sql)

        return f"Dropped table {self.table_name}"

    def _create_snapshot(self) -> str:
        """Create a snapshot of an Iceberg table using a write operation."""
        self.log.info(f"Creating snapshot for table {self.table_name}")

        sql = f"CALL local.system.create_changelog_view(table => '{self.table_name}')"

        self.log.info(f"Executing snapshot procedure for table {self.table_name}")
        self._submit_spark_sql(sql)

        return f"Created snapshot for table {self.table_name}"

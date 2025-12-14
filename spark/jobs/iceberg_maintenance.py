"""
Iceberg table maintenance operations.
"""
from pyspark.sql import SparkSession
import argparse


def create_spark_session():
    """Create Spark session with Iceberg."""
    return SparkSession.builder \
        .appName("IcebergMaintenance") \
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/") \
        .getOrCreate()


def expire_snapshots(spark, table_name, older_than_days=7):
    """Expire old snapshots from Iceberg table."""
    print(f"Expiring snapshots older than {older_than_days} days for {table_name}")

    spark.sql(f"""
        CALL local.system.expire_snapshots(
            table => '{table_name}',
            older_than => TIMESTAMP '{older_than_days} days ago'
        )
    """)

    print(f"Snapshots expired for {table_name}")


def remove_orphan_files(spark, table_name):
    """Remove orphan files from Iceberg table."""
    print(f"Removing orphan files for {table_name}")

    spark.sql(f"""
        CALL local.system.remove_orphan_files(
            table => '{table_name}'
        )
    """)

    print(f"Orphan files removed for {table_name}")


def compact_table(spark, table_name):
    """Compact small files in Iceberg table."""
    print(f"Compacting table {table_name}")

    spark.sql(f"""
        CALL local.system.rewrite_data_files(
            table => '{table_name}'
        )
    """)

    print(f"Table {table_name} compacted")


def main():
    """Main maintenance function."""
    parser = argparse.ArgumentParser(description='Iceberg table maintenance')
    parser.add_argument('--table', required=True, help='Table name (e.g., local.db.table_name)')
    parser.add_argument('--operation', required=True,
                       choices=['expire_snapshots', 'remove_orphans', 'compact'],
                       help='Maintenance operation')
    parser.add_argument('--days', type=int, default=7, help='Days for snapshot expiration')

    args = parser.parse_args()

    spark = create_spark_session()

    try:
        if args.operation == 'expire_snapshots':
            expire_snapshots(spark, args.table, args.days)
        elif args.operation == 'remove_orphans':
            remove_orphan_files(spark, args.table)
        elif args.operation == 'compact':
            compact_table(spark, args.table)

        print("Maintenance operation completed successfully")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

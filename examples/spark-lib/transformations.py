"""
Common data transformation functions.
"""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, current_timestamp, to_date, year, month, dayofmonth


def add_audit_columns(df: DataFrame) -> DataFrame:
    """
    Add audit columns to DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with audit columns
    """
    return df \
        .withColumn("created_at", current_timestamp()) \
        .withColumn("updated_at", current_timestamp())


def add_partition_columns(df: DataFrame, date_col: str = "created_at") -> DataFrame:
    """
    Add partition columns based on a date column.

    Args:
        df: Input DataFrame
        date_col: Name of the date column

    Returns:
        DataFrame with partition columns
    """
    return df \
        .withColumn("year", year(col(date_col))) \
        .withColumn("month", month(col(date_col))) \
        .withColumn("day", dayofmonth(col(date_col)))


def deduplicate(df: DataFrame, key_columns: list, order_by: str = None) -> DataFrame:
    """
    Deduplicate DataFrame based on key columns.

    Args:
        df: Input DataFrame
        key_columns: List of columns to use for deduplication
        order_by: Column to order by (keeps latest record)

    Returns:
        Deduplicated DataFrame
    """
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number, desc

    if order_by:
        window_spec = Window.partitionBy(*key_columns).orderBy(desc(order_by))
    else:
        window_spec = Window.partitionBy(*key_columns).orderBy(lit(1))

    return df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")


def standardize_column_names(df: DataFrame) -> DataFrame:
    """
    Standardize column names to lowercase with underscores.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with standardized column names
    """
    import re

    for col_name in df.columns:
        # Convert to lowercase and replace spaces/special chars with underscores
        new_name = re.sub(r'[^a-zA-Z0-9]', '_', col_name).lower()
        df = df.withColumnRenamed(col_name, new_name)

    return df

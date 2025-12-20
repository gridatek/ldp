# Tests Directory

This directory contains test suites for validating LDP components and pipelines.

## Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for service interactions
├── e2e/               # End-to-end pipeline tests
├── conftest.py        # Pytest configuration and fixtures
└── README.md          # This file
```

## Testing Framework

LDP uses **pytest** as the primary testing framework.

### Installation

```bash
pip install pytest pytest-cov
```

### Running Tests

```bash
# Run all tests
make test

# Or directly with pytest
pytest tests/

# Run specific test file
pytest tests/integration/test_iceberg.py

# Run with coverage
pytest --cov=. tests/

# Run tests matching pattern
pytest -k "test_iceberg"

# Verbose output
pytest -v tests/
```

## Test Categories

### Unit Tests

**Location**: `tests/unit/`

Test individual functions and components in isolation.

**Example:**

```python
"""
Unit tests for data transformations
"""
import pytest
from pyspark.sql import SparkSession
from spark.jobs.transformations import clean_data


@pytest.fixture
def spark():
    """Create Spark session for testing."""
    spark = SparkSession.builder \
        .appName("test") \
        .master("local[*]") \
        .getOrCreate()
    yield spark
    spark.stop()


def test_clean_data_removes_nulls(spark):
    """Test that clean_data removes null values."""
    # Arrange
    data = [
        (1, "Alice", "alice@example.com"),
        (2, None, "bob@example.com"),
        (3, "Charlie", None),
    ]
    df = spark.createDataFrame(data, ["id", "name", "email"])

    # Act
    result = clean_data(df)

    # Assert
    assert result.count() == 1
    assert result.filter("name IS NOT NULL").count() == 1
    assert result.filter("email IS NOT NULL").count() == 1
```

**Best practices:**
- Test one thing per test
- Use descriptive names: `test_<what>_<condition>_<expected>`
- Use arrange-act-assert pattern
- Keep tests fast (no external dependencies)

### Integration Tests

**Location**: `tests/integration/`

Test interactions between multiple components.

**Example:**

```python
"""
Integration tests for Iceberg table operations
"""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="module")
def spark_with_iceberg():
    """Create Spark session with Iceberg configuration."""
    spark = SparkSession.builder \
        .appName("integration-test") \
        .config("spark.jars.packages",
                "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
        .config("spark.sql.extensions",
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.test",
                "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.test.type", "hadoop") \
        .config("spark.sql.catalog.test.warehouse",
                "/tmp/test-warehouse") \
        .getOrCreate()
    yield spark
    spark.stop()


def test_create_and_query_iceberg_table(spark_with_iceberg):
    """Test creating and querying an Iceberg table."""
    spark = spark_with_iceberg

    # Create table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS test.db.users (
            id BIGINT,
            name STRING
        ) USING iceberg
    """)

    # Insert data
    data = [(1, "Alice"), (2, "Bob")]
    df = spark.createDataFrame(data, ["id", "name"])
    df.writeTo("test.db.users").append()

    # Query
    result = spark.table("test.db.users")

    # Assert
    assert result.count() == 2
    assert result.filter("id = 1").first()["name"] == "Alice"

    # Cleanup
    spark.sql("DROP TABLE IF EXISTS test.db.users")
```

**Examples included:**
- `test_iceberg_tables.py` - Iceberg CRUD operations
- `test_minio_access.py` - MinIO connectivity and operations
- `test_airflow_spark.py` - Airflow + Spark integration

### End-to-End Tests

**Location**: `tests/e2e/`

Test complete pipelines from start to finish.

**Example:**

```python
"""
End-to-end pipeline test
"""
import pytest
from datetime import datetime


def test_complete_data_pipeline(spark, minio_client):
    """Test complete data pipeline: ingest → transform → load."""
    # 1. Ingest: Upload raw data to MinIO
    test_data = "user_id,name,age\n1,Alice,25\n2,Bob,30"
    minio_client.put_object(
        Bucket="datalake",
        Key="raw/users.csv",
        Body=test_data.encode()
    )

    # 2. Transform: Process with Spark
    df = spark.read.csv("s3a://datalake/raw/users.csv", header=True)
    transformed = df.filter(df.age >= 18)

    # 3. Load: Write to Iceberg table
    transformed.writeTo("test.analytics.users").createOrReplace()

    # 4. Verify: Query final table
    result = spark.table("test.analytics.users")

    assert result.count() == 2
    assert all(row.age >= 18 for row in result.collect())

    # Cleanup
    spark.sql("DROP TABLE IF EXISTS test.analytics.users")
    minio_client.delete_object(Bucket="datalake", Key="raw/users.csv")
```

**Use cases:**
- Verify complete workflows
- Test data quality end-to-end
- Validate error handling
- Check monitoring and alerts

## Pytest Configuration

### conftest.py

Shared fixtures and configuration:

```python
"""
Pytest configuration and shared fixtures
"""
import pytest
from pyspark.sql import SparkSession
import boto3


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for all tests."""
    spark = SparkSession.builder \
        .appName("ldp-tests") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    yield spark

    spark.stop()


@pytest.fixture(scope="session")
def minio_client():
    """Create MinIO client for tests."""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='admin',
        aws_secret_access_key='minioadmin'
    )


@pytest.fixture
def clean_database(spark):
    """Clean test database before and after tests."""
    # Setup: Drop all test tables
    spark.sql("DROP DATABASE IF EXISTS test_db CASCADE")
    spark.sql("CREATE DATABASE IF NOT EXISTS test_db")

    yield

    # Teardown: Clean up
    spark.sql("DROP DATABASE IF EXISTS test_db CASCADE")
```

### pytest.ini

Project-level pytest configuration:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

## Test Data

### Using Fixtures

Create reusable test data:

```python
@pytest.fixture
def sample_users_df(spark):
    """Sample users DataFrame."""
    data = [
        (1, "Alice", 25, "Engineering"),
        (2, "Bob", 30, "Sales"),
        (3, "Charlie", 35, "Engineering"),
    ]
    return spark.createDataFrame(data, ["id", "name", "age", "department"])


def test_filter_by_department(sample_users_df):
    """Test filtering by department."""
    result = sample_users_df.filter("department = 'Engineering'")
    assert result.count() == 2
```

### Test Data Files

Store test data in `tests/data/`:

```
tests/data/
├── sample_users.csv
├── sample_events.json
└── sample_transactions.parquet
```

Load in tests:

```python
def test_read_csv(spark):
    """Test reading CSV file."""
    df = spark.read.csv("tests/data/sample_users.csv", header=True)
    assert df.count() > 0
```

## Markers

Use markers to categorize tests:

```python
import pytest


@pytest.mark.slow
def test_large_dataset_processing(spark):
    """Test processing large dataset (marked as slow)."""
    # This test takes a long time
    pass


@pytest.mark.integration
def test_minio_connection():
    """Test MinIO connectivity (marked as integration)."""
    pass


@pytest.mark.e2e
def test_full_pipeline():
    """Test complete pipeline (marked as e2e)."""
    pass
```

Run specific markers:

```bash
# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run integration and e2e tests
pytest -m "integration or e2e"
```

## Testing Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange: Set up test data and conditions
    data = [1, 2, 3]
    expected = 6

    # Act: Execute the code being tested
    result = sum(data)

    # Assert: Verify the result
    assert result == expected
```

### 2. Descriptive Test Names

```python
# Good
def test_clean_data_removes_null_emails():
    pass

# Bad
def test_clean():
    pass
```

### 3. One Assertion per Test (when possible)

```python
# Good
def test_user_has_valid_email():
    user = create_user()
    assert "@" in user.email

def test_user_has_valid_name():
    user = create_user()
    assert len(user.name) > 0

# Less ideal
def test_user_validation():
    user = create_user()
    assert "@" in user.email
    assert len(user.name) > 0
```

### 4. Use Fixtures for Setup/Teardown

```python
@pytest.fixture
def test_table(spark):
    """Create test table, clean up after."""
    # Setup
    spark.sql("CREATE TABLE test.users (id INT, name STRING)")

    yield "test.users"

    # Teardown
    spark.sql("DROP TABLE IF EXISTS test.users")


def test_insert_data(test_table):
    """Test using the fixture."""
    # Table is created automatically
    # Will be cleaned up automatically
    pass
```

### 5. Isolate Tests

Tests should not depend on each other:

```python
# Bad - depends on test order
def test_create_user():
    global user
    user = User("Alice")

def test_user_name():
    assert user.name == "Alice"  # Fails if test_create_user didn't run

# Good - self-contained
def test_create_user():
    user = User("Alice")
    assert user.name == "Alice"

def test_user_name():
    user = User("Alice")
    assert user.name == "Alice"
```

### 6. Test Edge Cases

```python
def test_divide_by_zero():
    """Test edge case: division by zero."""
    with pytest.raises(ZeroDivisionError):
        result = 10 / 0


def test_empty_dataframe(spark):
    """Test edge case: empty DataFrame."""
    df = spark.createDataFrame([], schema="id INT, name STRING")
    result = process_data(df)
    assert result.count() == 0
```

## Coverage

### Generate Coverage Reports

```bash
# Run tests with coverage
pytest --cov=spark --cov=airflow --cov-report=html tests/

# View report
open htmlcov/index.html
```

### Coverage Configuration

In `pytest.ini`:

```ini
[coverage:run]
source = spark,airflow
omit =
    */tests/*
    */venv/*
    */__pycache__/*
```

## Continuous Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Example Tests

### Test Airflow DAG

```python
"""
Test Airflow DAG validation
"""
from airflow.models import DagBag


def test_dag_loads_with_no_errors():
    """Test that all DAGs load without errors."""
    dag_bag = DagBag(include_examples=False)
    assert len(dag_bag.import_errors) == 0


def test_simple_dag_has_correct_tasks():
    """Test simple_dag has expected tasks."""
    dag_bag = DagBag(include_examples=False)
    dag = dag_bag.get_dag('simple_example')

    assert dag is not None
    assert len(dag.tasks) == 3

    task_ids = [task.task_id for task in dag.tasks]
    assert 'print_date' in task_ids
    assert 'hello_world' in task_ids
    assert 'finish' in task_ids
```

### Test Spark Transformation

```python
"""
Test Spark data transformations
"""
from pyspark.sql import SparkSession


def test_filter_adults(spark):
    """Test filtering users by age."""
    data = [(1, "Alice", 25), (2, "Bob", 17), (3, "Charlie", 30)]
    df = spark.createDataFrame(data, ["id", "name", "age"])

    result = df.filter(df.age >= 18)

    assert result.count() == 2
    ages = [row.age for row in result.collect()]
    assert all(age >= 18 for age in ages)
```

### Test Data Quality

```python
"""
Test data quality checks
"""
def test_no_null_ids(sample_df):
    """Test that there are no null IDs."""
    null_count = sample_df.filter("id IS NULL").count()
    assert null_count == 0


def test_no_duplicate_ids(sample_df):
    """Test that IDs are unique."""
    total_count = sample_df.count()
    distinct_count = sample_df.select("id").distinct().count()
    assert total_count == distinct_count


def test_email_format(sample_df):
    """Test that emails contain @."""
    invalid_emails = sample_df.filter(~sample_df.email.contains("@")).count()
    assert invalid_emails == 0
```

## Troubleshooting

### Tests Fail Locally

```bash
# Clean pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements-test.txt
```

### Spark Tests Hang

- Reduce executor memory in test fixtures
- Use `master("local[1]")` for single-threaded testing
- Ensure `spark.stop()` is called

### MinIO Connection Fails

- Verify MinIO is running: `docker ps | grep minio`
- Check endpoint URL matches your setup
- Verify credentials

## Learn More

- **Pytest Documentation**: https://docs.pytest.org/
- **Testing Best Practices**: https://testdriven.io/blog/testing-best-practices/
- **PySpark Testing**: https://spark.apache.org/docs/latest/api/python/user_guide/testing.html
- **Example Tests**: `examples/tests/` directory
- **CI Configuration**: `.github/workflows/` directory

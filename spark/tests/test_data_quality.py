"""
Tests for Data Quality Validation Framework.
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.data_quality import (
    DataQualityValidator,
    ValidationRule,
    ValidationSeverity,
    ValidationStatus,
    DataQualityProfile,
    validate_dataframe,
)


@pytest.fixture(scope="module")
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .appName("data-quality-test") \
        .master("local[*]") \
        .getOrCreate()


@pytest.fixture
def sample_df(spark):
    """Create sample DataFrame for testing."""
    data = [
        (1, "Alice", "alice@example.com", 100.0, "active"),
        (2, "Bob", "bob@example.com", 200.0, "active"),
        (3, "Charlie", "charlie@example.com", 150.0, "inactive"),
        (4, "Diana", "diana@example.com", 300.0, "active"),
        (5, "Eve", "eve@example.com", 250.0, "pending"),
    ]
    return spark.createDataFrame(data, ["id", "name", "email", "amount", "status"])


@pytest.fixture
def df_with_nulls(spark):
    """Create DataFrame with null values."""
    data = [
        (1, "Alice", 100.0),
        (2, None, 200.0),
        (3, "Charlie", None),
        (4, "Diana", 300.0),
    ]
    return spark.createDataFrame(data, ["id", "name", "amount"])


@pytest.fixture
def df_with_duplicates(spark):
    """Create DataFrame with duplicate values."""
    data = [
        (1, "Alice", 100.0),
        (1, "Alice", 100.0),
        (2, "Bob", 200.0),
        (3, "Charlie", 150.0),
        (3, "Charlie", 150.0),
    ]
    return spark.createDataFrame(data, ["id", "name", "amount"])


class TestValidationRules:
    """Test individual validation rules."""

    def test_not_null_pass(self, sample_df):
        """Test not_null rule passes when no nulls."""
        rule = ValidationRule.not_null("name")
        result = rule.execute(sample_df)
        assert result.passed
        assert result.failed_count == 0

    def test_not_null_fail(self, df_with_nulls):
        """Test not_null rule fails when nulls present."""
        rule = ValidationRule.not_null("name")
        result = rule.execute(df_with_nulls)
        assert not result.passed
        assert result.failed_count == 1

    def test_not_null_with_threshold(self, df_with_nulls):
        """Test not_null rule with threshold."""
        # 1 out of 4 = 25% null, threshold of 30% should pass
        rule = ValidationRule.not_null("name", threshold=0.30)
        result = rule.execute(df_with_nulls)
        assert result.passed

    def test_unique_pass(self, sample_df):
        """Test unique rule passes when all values unique."""
        rule = ValidationRule.unique("id")
        result = rule.execute(sample_df)
        assert result.passed
        assert result.failed_count == 0

    def test_unique_fail(self, df_with_duplicates):
        """Test unique rule fails with duplicates."""
        rule = ValidationRule.unique("id")
        result = rule.execute(df_with_duplicates)
        assert not result.passed
        assert result.failed_count > 0

    def test_in_range_pass(self, sample_df):
        """Test in_range rule passes when values in range."""
        rule = ValidationRule.in_range("amount", min_val=0, max_val=500)
        result = rule.execute(sample_df)
        assert result.passed

    def test_in_range_fail(self, sample_df):
        """Test in_range rule fails when values out of range."""
        rule = ValidationRule.in_range("amount", min_val=0, max_val=200)
        result = rule.execute(sample_df)
        assert not result.passed
        assert result.failed_count > 0

    def test_not_empty_pass(self, sample_df):
        """Test not_empty rule passes when no empty strings."""
        rule = ValidationRule.not_empty("name")
        result = rule.execute(sample_df)
        assert result.passed

    def test_not_empty_fail(self, spark):
        """Test not_empty rule fails with empty strings."""
        data = [(1, "Alice"), (2, ""), (3, "Charlie")]
        df = spark.createDataFrame(data, ["id", "name"])
        rule = ValidationRule.not_empty("name")
        result = rule.execute(df)
        assert not result.passed
        assert result.failed_count == 1

    def test_matches_pattern_pass(self, sample_df):
        """Test matches_pattern rule with email pattern."""
        rule = ValidationRule.matches_pattern("email", r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        result = rule.execute(sample_df)
        assert result.passed

    def test_matches_pattern_fail(self, spark):
        """Test matches_pattern rule fails with invalid pattern."""
        data = [(1, "valid@email.com"), (2, "invalid-email"), (3, "another@test.com")]
        df = spark.createDataFrame(data, ["id", "email"])
        rule = ValidationRule.matches_pattern("email", r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        result = rule.execute(df)
        assert not result.passed
        assert result.failed_count == 1

    def test_in_set_pass(self, sample_df):
        """Test in_set rule passes when values in set."""
        rule = ValidationRule.in_set("status", {"active", "inactive", "pending"})
        result = rule.execute(sample_df)
        assert result.passed

    def test_in_set_fail(self, spark):
        """Test in_set rule fails with invalid values."""
        data = [(1, "active"), (2, "unknown"), (3, "inactive")]
        df = spark.createDataFrame(data, ["id", "status"])
        rule = ValidationRule.in_set("status", {"active", "inactive"})
        result = rule.execute(df)
        assert not result.passed
        assert result.failed_count == 1

    def test_row_count_pass(self, sample_df):
        """Test row_count rule passes within range."""
        rule = ValidationRule.row_count(min_count=3, max_count=10)
        result = rule.execute(sample_df)
        assert result.passed

    def test_row_count_fail_min(self, sample_df):
        """Test row_count rule fails when below minimum."""
        rule = ValidationRule.row_count(min_count=10)
        result = rule.execute(sample_df)
        assert not result.passed

    def test_row_count_exact(self, sample_df):
        """Test row_count rule with exact count."""
        rule = ValidationRule.row_count(exact_count=5)
        result = rule.execute(sample_df)
        assert result.passed

    def test_column_exists_pass(self, sample_df):
        """Test column_exists rule passes when columns exist."""
        rule = ValidationRule.column_exists(["id", "name", "email"])
        result = rule.execute(sample_df)
        assert result.passed

    def test_column_exists_fail(self, sample_df):
        """Test column_exists rule fails when columns missing."""
        rule = ValidationRule.column_exists(["id", "name", "nonexistent"])
        result = rule.execute(sample_df)
        assert not result.passed
        assert "nonexistent" in result.details["missing_columns"]

    def test_no_duplicates_pass(self, sample_df):
        """Test no_duplicates rule passes when no duplicates."""
        rule = ValidationRule.no_duplicates(["id"])
        result = rule.execute(sample_df)
        assert result.passed

    def test_no_duplicates_fail(self, df_with_duplicates):
        """Test no_duplicates rule fails with duplicates."""
        rule = ValidationRule.no_duplicates(["id", "name"])
        result = rule.execute(df_with_duplicates)
        assert not result.passed

    def test_custom_rule(self, sample_df):
        """Test custom validation rule."""
        rule = ValidationRule.custom(
            name="check_positive_amounts",
            check_fn=lambda df: df.filter(df.amount > 0).count() == df.count(),
            message="All amounts should be positive",
        )
        result = rule.execute(sample_df)
        assert result.passed


class TestDataQualityValidator:
    """Test DataQualityValidator class."""

    def test_multiple_rules(self, sample_df):
        """Test validator with multiple rules."""
        validator = DataQualityValidator(sample_df, "test_df")
        validator.add_rule(ValidationRule.not_null("id"))
        validator.add_rule(ValidationRule.unique("id"))
        validator.add_rule(ValidationRule.in_range("amount", min_val=0, max_val=500))

        report = validator.validate()
        assert report.is_valid
        assert report.passed_count == 3
        assert report.failed_count == 0

    def test_validator_with_failures(self, df_with_nulls):
        """Test validator reports failures correctly."""
        validator = DataQualityValidator(df_with_nulls, "test_df")
        validator.add_rule(ValidationRule.not_null("name"))
        validator.add_rule(ValidationRule.not_null("amount"))

        report = validator.validate()
        assert not report.is_valid
        assert len(report.errors) == 2

    def test_fail_fast_mode(self, df_with_nulls):
        """Test fail_fast mode stops on first failure."""
        validator = DataQualityValidator(df_with_nulls, "test_df", fail_fast=True)
        validator.add_rule(ValidationRule.not_null("name"))
        validator.add_rule(ValidationRule.not_null("id"))  # Would pass

        report = validator.validate()
        # Should only have one result due to fail_fast
        assert len(report.results) == 1
        assert not report.is_valid

    def test_warning_severity(self, df_with_nulls):
        """Test warning severity doesn't fail validation."""
        validator = DataQualityValidator(df_with_nulls, "test_df")
        validator.add_rule(ValidationRule.not_null("name", severity=ValidationSeverity.WARNING))

        report = validator.validate()
        assert report.is_valid  # Warning doesn't fail
        assert len(report.warnings) == 1

    def test_report_to_dict(self, sample_df):
        """Test report serialization to dictionary."""
        validator = DataQualityValidator(sample_df, "test_df")
        validator.add_rule(ValidationRule.not_null("id"))

        report = validator.validate()
        report_dict = report.to_dict()

        assert "timestamp" in report_dict
        assert report_dict["dataframe_name"] == "test_df"
        assert report_dict["is_valid"] is True
        assert len(report_dict["results"]) == 1

    def test_add_rules_chain(self, sample_df):
        """Test chaining add_rule calls."""
        validator = (
            DataQualityValidator(sample_df, "test_df")
            .add_rule(ValidationRule.not_null("id"))
            .add_rule(ValidationRule.unique("id"))
        )

        report = validator.validate()
        assert len(report.results) == 2


class TestDataQualityProfile:
    """Test DataQualityProfile class."""

    def test_profile_generation(self, sample_df):
        """Test profile generation."""
        profile = DataQualityProfile.profile(sample_df)

        assert profile["total_rows"] == 5
        assert profile["total_columns"] == 5
        assert "id" in profile["columns"]
        assert "name" in profile["columns"]

    def test_profile_numeric_stats(self, sample_df):
        """Test numeric column statistics in profile."""
        profile = DataQualityProfile.profile(sample_df)

        amount_profile = profile["columns"]["amount"]
        assert amount_profile["data_type"] == "DoubleType()"
        assert "min" in amount_profile
        assert "max" in amount_profile
        assert "avg" in amount_profile

    def test_profile_string_stats(self, sample_df):
        """Test string column statistics in profile."""
        profile = DataQualityProfile.profile(sample_df)

        name_profile = profile["columns"]["name"]
        assert name_profile["data_type"] == "StringType()"
        assert "min_length" in name_profile
        assert "max_length" in name_profile

    def test_profile_null_count(self, df_with_nulls):
        """Test null count in profile."""
        profile = DataQualityProfile.profile(df_with_nulls)

        name_profile = profile["columns"]["name"]
        assert name_profile["null_count"] == 1
        assert name_profile["null_percentage"] == 25.0


class TestValidateDataframeFunction:
    """Test convenience function."""

    def test_validate_dataframe_success(self, sample_df):
        """Test validate_dataframe function success."""
        rules = [
            ValidationRule.not_null("id"),
            ValidationRule.unique("id"),
        ]
        report = validate_dataframe(sample_df, rules, "test_df", fail_on_error=True)
        assert report.is_valid

    def test_validate_dataframe_failure(self, df_with_nulls):
        """Test validate_dataframe function raises on failure."""
        rules = [ValidationRule.not_null("name")]

        with pytest.raises(ValueError) as excinfo:
            validate_dataframe(df_with_nulls, rules, "test_df", fail_on_error=True)

        assert "Data quality validation failed" in str(excinfo.value)

    def test_validate_dataframe_no_fail(self, df_with_nulls):
        """Test validate_dataframe doesn't raise when fail_on_error=False."""
        rules = [ValidationRule.not_null("name")]
        report = validate_dataframe(df_with_nulls, rules, "test_df", fail_on_error=False)
        assert not report.is_valid  # Returns report but doesn't raise

"""
Data Quality Validation Framework.

This module provides a comprehensive data quality validation framework for
validating DataFrames in data pipelines. It supports various validation rules
including null checks, uniqueness, range validation, pattern matching, and
referential integrity.

Usage:
    from lib.data_quality import DataQualityValidator, ValidationRule

    validator = DataQualityValidator(df)
    validator.add_rule(ValidationRule.not_null("id"))
    validator.add_rule(ValidationRule.unique("email"))
    validator.add_rule(ValidationRule.in_range("amount", min_val=0, max_val=10000))

    results = validator.validate()
    if not results.is_valid:
        for error in results.errors:
            print(f"Validation failed: {error}")
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    count,
    isnan,
    isnull,
    length,
    lit,
    regexp_extract,
    sum as spark_sum,
    when,
)


class ValidationSeverity(Enum):
    """Severity levels for validation rules."""

    ERROR = "error"  # Fails validation
    WARNING = "warning"  # Logs warning but passes
    INFO = "info"  # Informational only


class ValidationStatus(Enum):
    """Status of a validation check."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a single validation rule."""

    rule_name: str
    column: Optional[str]
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    failed_count: int = 0
    total_count: int = 0

    @property
    def passed(self) -> bool:
        return self.status == ValidationStatus.PASSED

    @property
    def failure_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.failed_count / self.total_count


@dataclass
class ValidationReport:
    """Complete validation report for a DataFrame."""

    timestamp: datetime
    dataframe_name: str
    total_rows: int
    results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if all ERROR severity rules passed."""
        return all(
            r.passed or r.severity != ValidationSeverity.ERROR for r in self.results
        )

    @property
    def errors(self) -> List[ValidationResult]:
        """Get all failed ERROR severity results."""
        return [
            r
            for r in self.results
            if not r.passed and r.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self) -> List[ValidationResult]:
        """Get all failed WARNING severity results."""
        return [
            r
            for r in self.results
            if not r.passed and r.severity == ValidationSeverity.WARNING
        ]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "dataframe_name": self.dataframe_name,
            "total_rows": self.total_rows,
            "is_valid": self.is_valid,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "results": [
                {
                    "rule_name": r.rule_name,
                    "column": r.column,
                    "status": r.status.value,
                    "severity": r.severity.value,
                    "message": r.message,
                    "details": r.details,
                    "failed_count": r.failed_count,
                    "total_count": r.total_count,
                    "failure_rate": r.failure_rate,
                }
                for r in self.results
            ],
            "metadata": self.metadata,
        }


class ValidationRule:
    """Factory class for creating validation rules."""

    def __init__(
        self,
        name: str,
        check_fn: Callable[[DataFrame], ValidationResult],
        column: Optional[str] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        self.name = name
        self.check_fn = check_fn
        self.column = column
        self.severity = severity

    def execute(self, df: DataFrame) -> ValidationResult:
        """Execute the validation rule."""
        result = self.check_fn(df)
        result.severity = self.severity
        return result

    @staticmethod
    def not_null(
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        threshold: float = 0.0,
    ) -> "ValidationRule":
        """Create a rule to check for null values in a column."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            null_count = df.filter(col(column).isNull() | isnan(column)).count()
            failure_rate = null_count / total if total > 0 else 0

            passed = failure_rate <= threshold
            return ValidationResult(
                rule_name="not_null",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {null_count} null values ({failure_rate:.2%})",
                details={"null_count": null_count, "threshold": threshold},
                failed_count=null_count,
                total_count=total,
            )

        return ValidationRule(f"not_null_{column}", check, column, severity)

    @staticmethod
    def unique(
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check for unique values in a column."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            distinct_count = df.select(column).distinct().count()
            duplicate_count = total - distinct_count

            passed = duplicate_count == 0
            return ValidationResult(
                rule_name="unique",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {duplicate_count} duplicate values",
                details={
                    "distinct_count": distinct_count,
                    "duplicate_count": duplicate_count,
                },
                failed_count=duplicate_count,
                total_count=total,
            )

        return ValidationRule(f"unique_{column}", check, column, severity)

    @staticmethod
    def in_range(
        column: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check if values are within a range."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            conditions = []

            if min_val is not None:
                conditions.append(col(column) < min_val)
            if max_val is not None:
                conditions.append(col(column) > max_val)

            if not conditions:
                return ValidationResult(
                    rule_name="in_range",
                    column=column,
                    status=ValidationStatus.SKIPPED,
                    severity=severity,
                    message="No range specified",
                    details={},
                    failed_count=0,
                    total_count=total,
                )

            out_of_range = df.filter(
                conditions[0] if len(conditions) == 1 else conditions[0] | conditions[1]
            ).count()

            passed = out_of_range == 0
            return ValidationResult(
                rule_name="in_range",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {out_of_range} values outside range [{min_val}, {max_val}]",
                details={"min": min_val, "max": max_val, "out_of_range": out_of_range},
                failed_count=out_of_range,
                total_count=total,
            )

        return ValidationRule(f"in_range_{column}", check, column, severity)

    @staticmethod
    def not_empty(
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check for empty strings."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            empty_count = df.filter(
                (col(column).isNull()) | (col(column) == "") | (length(col(column)) == 0)
            ).count()

            passed = empty_count == 0
            return ValidationResult(
                rule_name="not_empty",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {empty_count} empty values",
                details={"empty_count": empty_count},
                failed_count=empty_count,
                total_count=total,
            )

        return ValidationRule(f"not_empty_{column}", check, column, severity)

    @staticmethod
    def matches_pattern(
        column: str,
        pattern: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check if values match a regex pattern."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            # Extract matching values
            matched = df.filter(
                regexp_extract(col(column), pattern, 0) != ""
            ).count()
            non_matching = total - matched

            passed = non_matching == 0
            return ValidationResult(
                rule_name="matches_pattern",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {non_matching} values not matching pattern '{pattern}'",
                details={"pattern": pattern, "non_matching": non_matching},
                failed_count=non_matching,
                total_count=total,
            )

        return ValidationRule(f"matches_pattern_{column}", check, column, severity)

    @staticmethod
    def in_set(
        column: str,
        valid_values: Set[Any],
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check if values are in a set of valid values."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            valid_count = df.filter(col(column).isin(list(valid_values))).count()
            invalid_count = total - valid_count

            passed = invalid_count == 0
            return ValidationResult(
                rule_name="in_set",
                column=column,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Column '{column}' has {invalid_count} values not in valid set",
                details={
                    "valid_values": list(valid_values),
                    "invalid_count": invalid_count,
                },
                failed_count=invalid_count,
                total_count=total,
            )

        return ValidationRule(f"in_set_{column}", check, column, severity)

    @staticmethod
    def row_count(
        min_count: Optional[int] = None,
        max_count: Optional[int] = None,
        exact_count: Optional[int] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to validate row count."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            passed = True
            message_parts = []

            if exact_count is not None:
                passed = total == exact_count
                message_parts.append(f"expected exactly {exact_count}")
            else:
                if min_count is not None and total < min_count:
                    passed = False
                    message_parts.append(f"minimum {min_count}")
                if max_count is not None and total > max_count:
                    passed = False
                    message_parts.append(f"maximum {max_count}")

            return ValidationResult(
                rule_name="row_count",
                column=None,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Row count is {total}, {', '.join(message_parts) if message_parts else 'within limits'}",
                details={
                    "actual_count": total,
                    "min_count": min_count,
                    "max_count": max_count,
                    "exact_count": exact_count,
                },
                failed_count=0 if passed else 1,
                total_count=1,
            )

        return ValidationRule("row_count", check, None, severity)

    @staticmethod
    def column_exists(
        columns: List[str],
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check if required columns exist."""

        def check(df: DataFrame) -> ValidationResult:
            existing_columns = set(df.columns)
            missing_columns = [c for c in columns if c not in existing_columns]

            passed = len(missing_columns) == 0
            return ValidationResult(
                rule_name="column_exists",
                column=None,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Missing columns: {missing_columns}" if missing_columns else "All required columns present",
                details={
                    "required_columns": columns,
                    "missing_columns": missing_columns,
                },
                failed_count=len(missing_columns),
                total_count=len(columns),
            )

        return ValidationRule("column_exists", check, None, severity)

    @staticmethod
    def no_duplicates(
        columns: List[str],
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a rule to check for duplicate rows based on columns."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            distinct = df.select(columns).distinct().count()
            duplicates = total - distinct

            passed = duplicates == 0
            return ValidationResult(
                rule_name="no_duplicates",
                column=",".join(columns),
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=f"Found {duplicates} duplicate rows based on columns {columns}",
                details={"columns": columns, "duplicate_count": duplicates},
                failed_count=duplicates,
                total_count=total,
            )

        return ValidationRule("no_duplicates", check, ",".join(columns), severity)

    @staticmethod
    def custom(
        name: str,
        check_fn: Callable[[DataFrame], bool],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationRule":
        """Create a custom validation rule."""

        def check(df: DataFrame) -> ValidationResult:
            total = df.count()
            passed = check_fn(df)
            return ValidationResult(
                rule_name=name,
                column=None,
                status=ValidationStatus.PASSED if passed else ValidationStatus.FAILED,
                severity=severity,
                message=message,
                details={},
                failed_count=0 if passed else 1,
                total_count=1,
            )

        return ValidationRule(name, check, None, severity)


class DataQualityValidator:
    """Main validator class for executing data quality checks."""

    def __init__(
        self,
        df: DataFrame,
        name: str = "unnamed_dataframe",
        fail_fast: bool = False,
    ):
        """
        Initialize the validator.

        Args:
            df: The DataFrame to validate
            name: Name of the DataFrame for reporting
            fail_fast: If True, stop on first failure
        """
        self.df = df
        self.name = name
        self.fail_fast = fail_fast
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> "DataQualityValidator":
        """Add a validation rule."""
        self.rules.append(rule)
        return self

    def add_rules(self, rules: List[ValidationRule]) -> "DataQualityValidator":
        """Add multiple validation rules."""
        self.rules.extend(rules)
        return self

    def validate(self) -> ValidationReport:
        """Execute all validation rules and return a report."""
        total_rows = self.df.count()
        results: List[ValidationResult] = []

        for rule in self.rules:
            try:
                result = rule.execute(self.df)
                results.append(result)

                if (
                    self.fail_fast
                    and not result.passed
                    and result.severity == ValidationSeverity.ERROR
                ):
                    break
            except Exception as e:
                results.append(
                    ValidationResult(
                        rule_name=rule.name,
                        column=rule.column,
                        status=ValidationStatus.FAILED,
                        severity=rule.severity,
                        message=f"Rule execution failed: {str(e)}",
                        details={"error": str(e)},
                    )
                )

        return ValidationReport(
            timestamp=datetime.now(),
            dataframe_name=self.name,
            total_rows=total_rows,
            results=results,
        )

    def clear_rules(self) -> "DataQualityValidator":
        """Clear all validation rules."""
        self.rules = []
        return self


class DataQualityProfile:
    """Generate a data quality profile for a DataFrame."""

    @staticmethod
    def profile(df: DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive data quality profile.

        Args:
            df: The DataFrame to profile

        Returns:
            Dictionary containing profile information
        """
        from pyspark.sql.functions import approx_count_distinct, avg, max as spark_max
        from pyspark.sql.functions import min as spark_min, stddev

        total_rows = df.count()
        columns = df.columns
        schema = df.schema

        profile = {
            "total_rows": total_rows,
            "total_columns": len(columns),
            "columns": {},
        }

        for column in columns:
            col_type = str(schema[column].dataType)
            col_profile = {
                "data_type": col_type,
                "nullable": schema[column].nullable,
            }

            # Null count
            null_count = df.filter(col(column).isNull()).count()
            col_profile["null_count"] = null_count
            col_profile["null_percentage"] = (
                null_count / total_rows * 100 if total_rows > 0 else 0
            )

            # Distinct count (approximate for performance)
            col_profile["approx_distinct_count"] = df.select(
                approx_count_distinct(column)
            ).collect()[0][0]

            # Numeric statistics
            if "Int" in col_type or "Double" in col_type or "Float" in col_type:
                stats = df.select(
                    spark_min(column).alias("min"),
                    spark_max(column).alias("max"),
                    avg(column).alias("avg"),
                    stddev(column).alias("stddev"),
                ).collect()[0]

                col_profile["min"] = stats["min"]
                col_profile["max"] = stats["max"]
                col_profile["avg"] = stats["avg"]
                col_profile["stddev"] = stats["stddev"]

            # String statistics
            if "String" in col_type:
                length_stats = df.select(
                    spark_min(length(column)).alias("min_length"),
                    spark_max(length(column)).alias("max_length"),
                    avg(length(column)).alias("avg_length"),
                ).collect()[0]

                col_profile["min_length"] = length_stats["min_length"]
                col_profile["max_length"] = length_stats["max_length"]
                col_profile["avg_length"] = length_stats["avg_length"]

                # Empty string count
                empty_count = df.filter(col(column) == "").count()
                col_profile["empty_count"] = empty_count

            profile["columns"][column] = col_profile

        return profile


def validate_dataframe(
    df: DataFrame,
    rules: List[ValidationRule],
    name: str = "dataframe",
    fail_on_error: bool = True,
) -> ValidationReport:
    """
    Convenience function to validate a DataFrame with rules.

    Args:
        df: DataFrame to validate
        rules: List of validation rules
        name: Name of the DataFrame
        fail_on_error: If True, raise exception on validation failure

    Returns:
        ValidationReport

    Raises:
        ValueError: If fail_on_error is True and validation fails
    """
    validator = DataQualityValidator(df, name)
    validator.add_rules(rules)
    report = validator.validate()

    if fail_on_error and not report.is_valid:
        error_messages = [f"{e.rule_name}: {e.message}" for e in report.errors]
        raise ValueError(f"Data quality validation failed:\n" + "\n".join(error_messages))

    return report

"""Validators for null/not-null checks."""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToBeNullValidator(Validator):
    """Validator for to_be_null operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are null.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget specifying field
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_null only works with column targets")

        field_name = expectation.target.field_name
        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)
            if value is not None:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "reason": f"Expected null, got {value}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )


class ToNotBeNullValidator(Validator):
    """Validator for to_not_be_null operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are not null.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget specifying field
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_not_be_null only works with column targets")

        field_name = expectation.target.field_name
        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)
            if value is None:
                failed += 1
                failures.append(
                    {"record": str(record), "field": field_name, "reason": "Expected not null"}
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

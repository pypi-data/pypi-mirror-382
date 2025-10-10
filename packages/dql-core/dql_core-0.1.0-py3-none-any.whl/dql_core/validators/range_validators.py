"""Validators for range checks."""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToBeBetweenValidator(Validator):
    """Validator for to_be_between operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are within a range.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToBeBetween operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget, ToBeBetween

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_between only works with column targets")

        if not isinstance(expectation.operator, ToBeBetween):
            raise ValidationError("Expected ToBeBetween operator")

        field_name = expectation.target.field_name
        min_value = expectation.operator.min_value
        max_value = expectation.operator.max_value

        if min_value > max_value:
            raise ValidationError(f"min_value ({min_value}) must be <= max_value ({max_value})")

        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            try:
                if not (min_value <= value <= max_value):
                    failed += 1
                    failures.append(
                        {
                            "record": str(record),
                            "field": field_name,
                            "value": value,
                            "min": min_value,
                            "max": max_value,
                            "reason": f"Value {value} is not between {min_value} and {max_value}",
                        }
                    )
            except TypeError as e:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "reason": f"Cannot compare value {value} with range: {e}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

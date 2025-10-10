"""Validators for uniqueness checks."""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToBeUniqueValidator(Validator):
    """Validator for to_be_unique operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are unique across all records.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToBeUnique operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget, ToBeUnique

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_unique only works with column targets")

        if not isinstance(expectation.operator, ToBeUnique):
            raise ValidationError("Expected ToBeUnique operator")

        field_name = expectation.target.field_name

        seen_values = {}
        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)

            # Skip null values (nulls are not considered duplicates)
            if value is None:
                continue

            # Check if we've seen this value before
            if value in seen_values:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "first_occurrence": seen_values[value],
                        "reason": f"Duplicate value '{value}' found",
                    }
                )
            else:
                seen_values[value] = str(record)

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

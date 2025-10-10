"""Validators for enum/set membership checks."""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToBeInValidator(Validator):
    """Validator for to_be_in operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are in a set of allowed values.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToBeIn operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget, ToBeIn

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_in only works with column targets")

        if not isinstance(expectation.operator, ToBeIn):
            raise ValidationError("Expected ToBeIn operator")

        field_name = expectation.target.field_name
        allowed_values = expectation.operator.values

        if not allowed_values:
            raise ValidationError("to_be_in requires at least one allowed value")

        # Convert to set for O(1) lookup
        allowed_set = set(allowed_values)

        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            if value not in allowed_set:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "allowed_values": list(allowed_values),
                        "reason": f"Value '{value}' is not in allowed set {list(allowed_values)}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

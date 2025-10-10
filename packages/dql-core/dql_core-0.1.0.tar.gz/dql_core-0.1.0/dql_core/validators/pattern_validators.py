"""Validators for pattern matching."""

import re
from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToMatchPatternValidator(Validator):
    """Validator for to_match_pattern operator."""

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values match a regex pattern.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToMatchPattern operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status
        """
        from dql_parser.ast_nodes import ColumnTarget, ToMatchPattern

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_match_pattern only works with column targets")

        if not isinstance(expectation.operator, ToMatchPattern):
            raise ValidationError("Expected ToMatchPattern operator")

        field_name = expectation.target.field_name
        pattern = expectation.operator.pattern

        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern '{pattern}': {e}")

        total = 0
        failed = 0
        failures = []

        for record in records:
            total += 1
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            value_str = str(value)
            if not regex.match(value_str):
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "pattern": pattern,
                        "reason": f"Value '{value}' does not match pattern '{pattern}'",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

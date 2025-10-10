"""Abstract validation executor."""

import time
from abc import ABC, abstractmethod
from typing import Any, Iterable

from dql_core.results import ValidationRunResult, ExpectationResult, ValidationResult
from dql_core.exceptions import ExecutorError
from dql_core.validators import default_registry


class ValidationExecutor(ABC):
    """Abstract base class for validation executors.

    Framework-specific implementations must subclass and implement
    abstract methods for data access.
    """

    def __init__(self, validator_registry=None):
        """Initialize executor with validator registry.

        Args:
            validator_registry: ValidatorRegistry to use (defaults to default_registry)
        """
        self.validator_registry = validator_registry or default_registry

    @abstractmethod
    def get_records(self, model_name: str) -> Iterable[Any]:
        """Retrieve records for the specified model.

        Args:
            model_name: Name of the model/table to query

        Returns:
            Iterable of records (QuerySet, list, generator, etc.)

        Raises:
            ExecutorError: If model not found or query fails
        """
        pass

    @abstractmethod
    def filter_records(self, records: Iterable[Any], condition: Any) -> Iterable[Any]:
        """Filter records based on condition.

        Args:
            records: Records to filter
            condition: Filtering condition (framework-specific AST node)

        Returns:
            Filtered records

        Raises:
            ExecutorError: If filtering fails
        """
        pass

    @abstractmethod
    def count_records(self, records: Iterable[Any]) -> int:
        """Count records in iterable.

        Args:
            records: Records to count

        Returns:
            Number of records

        Raises:
            ExecutorError: If counting fails
        """
        pass

    @abstractmethod
    def get_field_value(self, record: Any, field_name: str) -> Any:
        """Get field value from record.

        Args:
            record: Single record object
            field_name: Name of field to retrieve

        Returns:
            Field value

        Raises:
            ExecutorError: If field doesn't exist or access fails
        """
        pass

    def execute(self, ast: Any) -> ValidationRunResult:
        """Execute validation from DQL AST.

        This is a concrete method that orchestrates validation using
        the abstract methods above.

        Args:
            ast: DQL File AST from parser

        Returns:
            ValidationRunResult with all expectation results

        Raises:
            ExecutorError: If execution fails
        """
        from dql_parser.ast_nodes import DQLFile, RowTarget

        if not isinstance(ast, DQLFile):
            raise ExecutorError("Expected DQLFile AST node")

        start_time = time.time()
        expectation_results = []
        overall_passed = True

        for from_block in ast.from_blocks:
            model_name = from_block.model_name

            try:
                # Get all records for this model
                records = self.get_records(model_name)
            except Exception as e:
                raise ExecutorError(f"Failed to get records for model '{model_name}': {e}")

            for expectation in from_block.expectations:
                try:
                    # Handle row-level filtering if needed
                    if isinstance(expectation.target, RowTarget):
                        if expectation.target.condition:
                            records = self.filter_records(records, expectation.target.condition)

                    # Get operator name from expectation.operator class
                    operator_type = type(expectation.operator).__name__
                    # Convert class name to operator name (ToBeNull -> to_be_null)
                    operator_name = self._class_name_to_operator(operator_type)

                    # Get validator for this operator
                    validator_class = self.validator_registry.get(operator_name)
                    validator = validator_class()

                    # Execute validation
                    validation_result = validator.validate(records, expectation, self)

                    # Create expectation result
                    expectation_result = ExpectationResult(
                        expectation=expectation,
                        passed=validation_result.passed,
                        validation_result=validation_result,
                        severity=expectation.severity,
                        model_name=model_name,
                    )

                    expectation_results.append(expectation_result)

                    if not validation_result.passed:
                        overall_passed = False

                except Exception as e:
                    # Catch validation errors and create failed result
                    validation_result = ValidationResult(
                        passed=False,
                        total_records=0,
                        failed_records=0,
                        failures=[{"error": str(e)}],
                    )
                    expectation_result = ExpectationResult(
                        expectation=expectation,
                        passed=False,
                        validation_result=validation_result,
                        severity=expectation.severity,
                        model_name=model_name,
                    )
                    expectation_results.append(expectation_result)
                    overall_passed = False

        duration = time.time() - start_time

        return ValidationRunResult(
            overall_passed=overall_passed,
            expectation_results=expectation_results,
            duration=duration,
        )

    def _class_name_to_operator(self, class_name: str) -> str:
        """Convert operator class name to operator name.

        Args:
            class_name: Class name (e.g., 'ToBeNull')

        Returns:
            Operator name (e.g., 'to_be_null')
        """
        # Convert PascalCase to snake_case
        import re

        # Insert underscore before capitals
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        # Handle consecutive capitals
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()

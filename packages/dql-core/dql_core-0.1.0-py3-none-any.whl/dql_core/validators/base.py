"""Abstract base class for validators."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dql_core.executor import ValidationExecutor

from dql_core.results import ValidationResult


class Validator(ABC):
    """Abstract base class for all DQL validators.

    Framework-specific implementations should subclass this and implement
    the validate() method to check records against expectations.
    """

    @abstractmethod
    def validate(
        self, records: Iterable[Any], expectation: Any, executor: "ValidationExecutor"
    ) -> ValidationResult:
        """Validate records against an expectation.

        Args:
            records: Iterable of records to validate
            expectation: ExpectationNode AST with operator and arguments
            executor: ValidationExecutor for data access helpers

        Returns:
            ValidationResult with pass/fail status and failure details

        Raises:
            ValidationError: If validation cannot be performed
        """
        pass

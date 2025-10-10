"""Abstract base classes for cleaners."""

from abc import ABC, abstractmethod
from typing import Any, Callable

from dql_core.results import CleanerResult
from dql_core.exceptions import CleanerError


class Cleaner(ABC):
    """Abstract base class for cleaners.

    Cleaners are functions that modify records when validation fails.
    """

    @abstractmethod
    def clean(self, record: Any, context: dict) -> CleanerResult:
        """Execute cleaning logic on a record.

        Args:
            record: Record to clean
            context: Context dict with execution info

        Returns:
            CleanerResult with success status and modifications

        Raises:
            CleanerError: If cleaning fails
        """
        pass


class CleanerExecutor(ABC):
    """Abstract cleaner executor with transaction management."""

    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin a transaction for cleaner execution.

        Raises:
            CleanerError: If transaction cannot be started
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction.

        Raises:
            CleanerError: If commit fails
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction.

        Raises:
            CleanerError: If rollback fails
        """
        pass

    @abstractmethod
    def save_record(self, record: Any) -> None:
        """Save modified record (framework-specific).

        Args:
            record: Record to save

        Raises:
            CleanerError: If save fails
        """
        pass

    def execute_cleaner(self, cleaner_func: Callable, record: Any, context: dict) -> CleanerResult:
        """Execute cleaner with transaction safety.

        This is a concrete method using template method pattern.

        Args:
            cleaner_func: Cleaner function to execute
            record: Record to clean
            context: Execution context

        Returns:
            CleanerResult with success status
        """
        try:
            self.begin_transaction()
            result = cleaner_func(record, context)
            if result.modified:
                self.save_record(record)
            self.commit()
            return result
        except Exception as e:
            self.rollback()
            return CleanerResult(success=False, modified=False, error=str(e))

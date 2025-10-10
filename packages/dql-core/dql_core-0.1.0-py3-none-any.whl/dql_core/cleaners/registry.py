"""Cleaner registry for looking up cleaners by name."""

from typing import Callable, Dict

from dql_core.exceptions import CleanerError


class CleanerRegistry:
    """Registry for mapping cleaner names to cleaner functions."""

    def __init__(self):
        """Initialize empty cleaner registry."""
        self._cleaners: Dict[str, Callable] = {}

    def register(self, name: str, cleaner_func: Callable) -> None:
        """Register a cleaner function.

        Args:
            name: Name of cleaner (e.g., 'trim_whitespace', 'uppercase')
            cleaner_func: Function that performs cleaning

        Raises:
            CleanerError: If cleaner name is already registered
        """
        if name in self._cleaners:
            raise CleanerError(f"Cleaner '{name}' is already registered")
        self._cleaners[name] = cleaner_func

    def get(self, name: str) -> Callable:
        """Get cleaner function by name.

        Args:
            name: Name of cleaner to look up

        Returns:
            Cleaner function

        Raises:
            CleanerError: If no cleaner is registered for name
        """
        if name not in self._cleaners:
            raise CleanerError(f"No cleaner registered with name '{name}'")
        return self._cleaners[name]

    def has(self, name: str) -> bool:
        """Check if a cleaner is registered.

        Args:
            name: Name of cleaner to check

        Returns:
            True if cleaner is registered, False otherwise
        """
        return name in self._cleaners

    def list_cleaners(self) -> list:
        """Get list of all registered cleaner names.

        Returns:
            List of cleaner names
        """
        return list(self._cleaners.keys())


# Global default registry
default_cleaner_registry = CleanerRegistry()

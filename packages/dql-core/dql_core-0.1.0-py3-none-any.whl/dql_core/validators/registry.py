"""Validator registry for looking up validators by operator type."""

from typing import Dict, Type

from dql_core.validators.base import Validator
from dql_core.exceptions import ValidationError


class ValidatorRegistry:
    """Registry for mapping operator types to validator implementations."""

    def __init__(self):
        """Initialize empty validator registry."""
        self._validators: Dict[str, Type[Validator]] = {}

    def register(self, operator_name: str, validator_class: Type[Validator]) -> None:
        """Register a validator for an operator type.

        Args:
            operator_name: Name of operator (e.g., 'to_be_null', 'to_match_pattern')
            validator_class: Validator class to handle this operator

        Raises:
            ValidationError: If operator is already registered
        """
        if operator_name in self._validators:
            raise ValidationError(f"Validator for operator '{operator_name}' is already registered")
        self._validators[operator_name] = validator_class

    def get(self, operator_name: str) -> Type[Validator]:
        """Get validator class for an operator.

        Args:
            operator_name: Name of operator to look up

        Returns:
            Validator class for the operator

        Raises:
            ValidationError: If no validator is registered for operator
        """
        if operator_name not in self._validators:
            raise ValidationError(f"No validator registered for operator '{operator_name}'")
        return self._validators[operator_name]

    def has(self, operator_name: str) -> bool:
        """Check if a validator is registered for an operator.

        Args:
            operator_name: Name of operator to check

        Returns:
            True if validator is registered, False otherwise
        """
        return operator_name in self._validators

    def list_operators(self) -> list:
        """Get list of all registered operators.

        Returns:
            List of operator names
        """
        return list(self._validators.keys())


# Global default registry
default_registry = ValidatorRegistry()

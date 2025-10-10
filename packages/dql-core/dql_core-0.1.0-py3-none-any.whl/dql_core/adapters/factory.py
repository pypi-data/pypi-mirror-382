"""Factory for creating API adapters."""

from typing import Any, Dict, Type

from dql_core.adapters.base import ExternalAPIAdapter
from dql_core.exceptions import AdapterError


class APIAdapterFactory:
    """Factory for creating external API adapters."""

    def __init__(self):
        """Initialize factory with empty adapter registry."""
        self._adapters: Dict[str, Type[ExternalAPIAdapter]] = {}

    def register(self, adapter_type: str, adapter_class: Type[ExternalAPIAdapter]) -> None:
        """Register an adapter type.

        Args:
            adapter_type: Name of adapter type (e.g., 'rest', 'soap')
            adapter_class: Adapter class to instantiate

        Raises:
            AdapterError: If adapter type is already registered
        """
        if adapter_type in self._adapters:
            raise AdapterError(f"Adapter type '{adapter_type}' is already registered")
        self._adapters[adapter_type] = adapter_class

    def create(self, adapter_type: str, config: Dict[str, Any] = None) -> ExternalAPIAdapter:
        """Create an adapter instance.

        Args:
            adapter_type: Type of adapter to create
            config: Configuration for the adapter

        Returns:
            Configured adapter instance

        Raises:
            AdapterError: If adapter type is not registered
        """
        if adapter_type not in self._adapters:
            raise AdapterError(f"No adapter registered for type '{adapter_type}'")

        adapter_class = self._adapters[adapter_type]
        adapter = adapter_class(config)
        adapter.validate_config()
        return adapter

    def list_types(self) -> list:
        """Get list of registered adapter types.

        Returns:
            List of adapter type names
        """
        return list(self._adapters.keys())


# Global default factory
default_adapter_factory = APIAdapterFactory()

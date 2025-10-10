"""Abstract base class for external API adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from dql_core.exceptions import AdapterError


class ExternalAPIAdapter(ABC):
    """Abstract base class for external API adapters.

    Subclass this to create adapters for specific external APIs
    (e.g., REST APIs, SOAP services, etc.)
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize adapter with configuration.

        Args:
            config: Configuration dict for the adapter
        """
        self.config = config or {}

    @abstractmethod
    def call(self, **kwargs) -> dict:
        """Make API call with given parameters.

        Args:
            **kwargs: API-specific parameters

        Returns:
            Response data as dictionary

        Raises:
            AdapterError: If API call fails
        """
        pass

    def validate_config(self) -> None:
        """Validate adapter configuration.

        Raises:
            AdapterError: If configuration is invalid
        """
        pass

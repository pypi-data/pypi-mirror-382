"""Decorators for cleaner registration."""

from typing import Callable

from dql_core.cleaners.registry import default_cleaner_registry


def register_cleaner(name: str, registry=None):
    """Decorator to register a cleaner function.

    Args:
        name: Name to register cleaner under
        registry: CleanerRegistry to use (defaults to default_cleaner_registry)

    Returns:
        Decorator function

    Example:
        @register_cleaner('trim_whitespace')
        def trim_whitespace(record, context):
            # cleaning logic
            return CleanerResult(success=True, modified=True)
    """
    reg = registry or default_cleaner_registry

    def decorator(func: Callable) -> Callable:
        reg.register(name, func)
        return func

    return decorator

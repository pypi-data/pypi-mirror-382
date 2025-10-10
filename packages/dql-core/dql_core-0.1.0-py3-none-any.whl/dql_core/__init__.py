"""dql-core: Framework-agnostic validation engine for Data Quality Language (DQL)."""

__version__ = "0.1.0"

# Core executor
from dql_core.executor import ValidationExecutor

# Results
from dql_core.results import (
    ValidationResult,
    ExpectationResult,
    CleanerResult,
    ValidationRunResult,
)

# Exceptions
from dql_core.exceptions import (
    DQLCoreError,
    ValidationError,
    CleanerError,
    ExecutorError,
    AdapterError,
)

# Validators
from dql_core.validators import (
    Validator,
    ValidatorRegistry,
    default_registry,
    ToBeNullValidator,
    ToNotBeNullValidator,
    ToMatchPatternValidator,
    ToBeBetweenValidator,
    ToBeInValidator,
    ToBeUniqueValidator,
)

# Cleaners
from dql_core.cleaners import (
    Cleaner,
    CleanerExecutor,
    CleanerRegistry,
    default_cleaner_registry,
    register_cleaner,
)

# Adapters
from dql_core.adapters import (
    ExternalAPIAdapter,
    APIAdapterFactory,
    default_adapter_factory,
    RateLimiter,
    retry_with_backoff,
)

__all__ = [
    "__version__",
    # Executor
    "ValidationExecutor",
    # Results
    "ValidationResult",
    "ExpectationResult",
    "CleanerResult",
    "ValidationRunResult",
    # Exceptions
    "DQLCoreError",
    "ValidationError",
    "CleanerError",
    "ExecutorError",
    "AdapterError",
    # Validators
    "Validator",
    "ValidatorRegistry",
    "default_registry",
    "ToBeNullValidator",
    "ToNotBeNullValidator",
    "ToMatchPatternValidator",
    "ToBeBetweenValidator",
    "ToBeInValidator",
    "ToBeUniqueValidator",
    # Cleaners
    "Cleaner",
    "CleanerExecutor",
    "CleanerRegistry",
    "default_cleaner_registry",
    "register_cleaner",
    # Adapters
    "ExternalAPIAdapter",
    "APIAdapterFactory",
    "default_adapter_factory",
    "RateLimiter",
    "retry_with_backoff",
]

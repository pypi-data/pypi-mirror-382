"""Exception hierarchy for dql-core package."""


class DQLCoreError(Exception):
    """Base exception for all dql-core errors."""

    pass


class ValidationError(DQLCoreError):
    """Raised when validation fails or encounters an error.

    This exception is raised when:
    - A validation rule execution encounters an error
    - Invalid validation configuration is detected
    - Required data for validation is missing
    """

    pass


class CleanerError(DQLCoreError):
    """Raised when cleaner execution encounters an error.

    This exception is raised when:
    - A cleaner function fails during execution
    - Transaction management fails
    - Record modification fails
    - Invalid cleaner configuration is detected
    """

    pass


class ExecutorError(DQLCoreError):
    """Raised when executor encounters an error.

    This exception is raised when:
    - Data access methods fail
    - Model/table not found
    - Invalid executor configuration
    - Execution orchestration fails
    """

    pass


class AdapterError(DQLCoreError):
    """Raised when external API adapter encounters an error.

    This exception is raised when:
    - External API call fails
    - Rate limiting is exceeded
    - Invalid adapter configuration
    - Network errors occur
    """

    pass

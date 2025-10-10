"""Result dataclasses for validation and cleaner execution."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    """Result of validating records against an expectation.

    Attributes:
        passed: Whether all records passed validation
        total_records: Total number of records validated
        failed_records: Number of records that failed
        failures: List of failure details (record info, reason)
    """

    passed: bool
    total_records: int
    failed_records: int
    failures: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExpectationResult:
    """Result of executing a single expectation.

    Attributes:
        expectation: The expectation AST node that was executed
        passed: Whether the expectation passed
        validation_result: The validation result details
        severity: Severity level (critical, warning, info)
        model_name: Name of the model/table validated
    """

    expectation: Any  # ExpectationNode from dql_parser
    passed: bool
    validation_result: ValidationResult
    severity: Optional[str] = None
    model_name: str = ""


@dataclass
class CleanerResult:
    """Result of executing a cleaner function.

    Attributes:
        success: Whether the cleaner executed successfully
        modified: Whether the record was modified
        before_value: Value before cleaning (optional)
        after_value: Value after cleaning (optional)
        error: Error message if cleaner failed
    """

    success: bool
    modified: bool
    before_value: Any = None
    after_value: Any = None
    error: Optional[str] = None


@dataclass
class ValidationRunResult:
    """Result of executing a complete DQL validation run.

    Attributes:
        overall_passed: Whether all expectations passed
        expectation_results: List of results for each expectation
        duration: Duration of validation run in seconds
        total_expectations: Total number of expectations executed
        passed_expectations: Number of expectations that passed
        failed_expectations: Number of expectations that failed
    """

    overall_passed: bool
    expectation_results: List[ExpectationResult]
    duration: float
    total_expectations: int = 0
    passed_expectations: int = 0
    failed_expectations: int = 0

    def __post_init__(self):
        """Calculate aggregate counts from expectation results."""
        self.total_expectations = len(self.expectation_results)
        self.passed_expectations = sum(1 for r in self.expectation_results if r.passed)
        self.failed_expectations = self.total_expectations - self.passed_expectations

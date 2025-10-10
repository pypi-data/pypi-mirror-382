"""Validators for DQL operators."""

from dql_core.validators.base import Validator
from dql_core.validators.registry import ValidatorRegistry, default_registry
from dql_core.validators.null_validators import ToBeNullValidator, ToNotBeNullValidator
from dql_core.validators.pattern_validators import ToMatchPatternValidator
from dql_core.validators.range_validators import ToBeBetweenValidator
from dql_core.validators.enum_validators import ToBeInValidator
from dql_core.validators.uniqueness_validators import ToBeUniqueValidator

__all__ = [
    "Validator",
    "ValidatorRegistry",
    "default_registry",
    "ToBeNullValidator",
    "ToNotBeNullValidator",
    "ToMatchPatternValidator",
    "ToBeBetweenValidator",
    "ToBeInValidator",
    "ToBeUniqueValidator",
]

# Register default validators
default_registry.register("to_be_null", ToBeNullValidator)
default_registry.register("to_not_be_null", ToNotBeNullValidator)
default_registry.register("to_match_pattern", ToMatchPatternValidator)
default_registry.register("to_be_between", ToBeBetweenValidator)
default_registry.register("to_be_in", ToBeInValidator)
default_registry.register("to_be_unique", ToBeUniqueValidator)

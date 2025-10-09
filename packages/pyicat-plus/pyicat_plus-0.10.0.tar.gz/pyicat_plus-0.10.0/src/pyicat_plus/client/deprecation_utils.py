import warnings
from functools import wraps
from typing import Any


def deprecated_property(property_method):
    """Decorator to mark properties as deprecated with a warning."""

    @wraps(property_method)
    def deprecated_method(self):
        warnings.warn(
            f"Property '{property_method.__name__}' is deprecated and may be removed in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        return property_method(self)

    return property(deprecated_method)


def deprecated_argument(
    new_name: str, new_value: Any, deprecated_name: str, deprecated_value: Any
) -> Any:
    """Function to handle new and deprecated function argument."""
    if deprecated_value is not None:
        if new_value is not None:
            raise ValueError(
                f"Argument '{deprecated_name}' is replaced by '{new_name}'."
            )
        new_value = deprecated_value
        warnings.warn(
            f"Argument '{deprecated_name}' is deprecated and may be removed in future versions. Use '{new_name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    return new_value


def deprecated_method(func):
    """Decorator to mark methods as deprecated with a warning."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"Method '{func.__name__}' is deprecated and may be removed in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


def warn_deprecated_module(
    message: str = "This module is deprecated and may be removed in future versions.",
):
    warnings.warn(message, ImportWarning, stacklevel=2)

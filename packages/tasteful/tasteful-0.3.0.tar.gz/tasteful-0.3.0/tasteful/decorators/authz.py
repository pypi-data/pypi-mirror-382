"""Decorators for authorization in Tasteful applications."""

import inspect

from functools import wraps
from typing import Any, Callable, List


def requires(permissions: List[str] = []) -> Callable:
    """Indicate permissions needed to perfom the action."""

    def decorator(func: Callable) -> Callable:
        setattr(func, "_required_permissions", permissions)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

        return wrapper

    return decorator

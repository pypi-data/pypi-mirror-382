"""Decorators for authentication in Tasteful applications."""

from functools import wraps
from typing import Callable


def public(func: Callable) -> Callable:
    """Mark a route as public.

    It bypass authentication requirements.
    """
    # Set a marker attribute on the function
    setattr(func, "_is_public_route", True)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper

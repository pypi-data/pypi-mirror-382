from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable

from .result import Result


def returns_result[**P, T](fn: Callable[P, T]) -> Callable[P, Result[T]]:
    """
    Decorator that wraps a function to return a Result[T] instead of T.
    Automatically catches exceptions and converts them to Result.err().

    Example:
        @returns_result
        def divide(a: int, b: int) -> float:
            return a / b

        result = divide(10, 2)  # Returns Result.ok(5.0)
        result = divide(10, 0)  # Returns Result.err(ZeroDivisionError)
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T]:
        try:
            value = fn(*args, **kwargs)
            return Result.ok(value)
        except Exception as e:
            return Result.err(e)

    return wrapper


def async_returns_result[**P, T](fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[Result[T]]]:
    """
    Decorator that wraps an async function to return a Result[T] instead of T.
    Automatically catches exceptions and converts them to Result.err().

    Example:
        @async_returns_result
        async def fetch_data(url: str) -> dict:
            response = await http_client.get(url)
            return response.json()

        result = await fetch_data("https://api.example.com")  # Returns Result[dict]
    """

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T]:
        try:
            value = await fn(*args, **kwargs)
            return Result.ok(value)
        except Exception as e:
            return Result.err(e)

    return wrapper

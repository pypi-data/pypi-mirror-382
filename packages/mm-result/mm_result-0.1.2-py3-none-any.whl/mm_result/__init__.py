"""
mm-result: Functional error handling for Python using Result types.

A Result[T] represents either a successful value (Ok) or an error (Err).
This enables functional programming patterns for error handling without exceptions.

Basic usage:
    from mm_result import Result

    def divide(a: int, b: int) -> Result[float]:
        if b == 0:
            return Result.err("Division by zero")
        return Result.ok(a / b)

    result = divide(10, 2)
    if result.is_ok():
        print(f"Success: {result.unwrap()}")
    else:
        print(f"Error: {result.unwrap_err()}")

Optional Pydantic integration:
    Install with: pip install mm-result[pydantic]

    from pydantic import BaseModel
    from mm_result import Result

    class MyModel(BaseModel):
        result_field: Result[int]
"""

from .decorators import async_returns_result, returns_result
from .result import (
    ErrResult,
    OkResult,
    Result,
    UnwrapErrError,
    UnwrapError,
    is_err,
    is_ok,
)

__all__ = [
    "ErrResult",
    "OkResult",
    "Result",
    "UnwrapErrError",
    "UnwrapError",
    "async_returns_result",
    "is_err",
    "is_ok",
    "returns_result",
]

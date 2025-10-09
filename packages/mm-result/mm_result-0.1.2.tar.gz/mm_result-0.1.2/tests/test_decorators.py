import pytest

from mm_result import async_returns_result, returns_result


class TestDecorators:
    def test_returns_result_success(self):
        @returns_result
        def divide(a: int, b: int) -> float:
            return a / b

        result = divide(10, 2)
        assert result.is_ok()
        assert result.unwrap() == 5.0

    def test_returns_result_error(self):
        @returns_result
        def divide(a: int, b: int) -> float:
            return a / b

        result = divide(10, 0)
        assert result.is_err()
        assert result.error is not None
        assert "ZeroDivisionError" in result.error
        assert result.extra is not None
        assert isinstance(result.extra["exception"], ZeroDivisionError)

    def test_returns_result_preserves_metadata(self):
        @returns_result
        def example_function(x: int) -> int:
            """Example docstring."""
            return x * 2

        assert example_function.__name__ == "example_function"
        assert example_function.__doc__ == "Example docstring."

    def test_returns_result_with_args_kwargs(self):
        @returns_result
        def complex_function(a: int, b: int, *, multiplier: int = 1) -> int:
            return (a + b) * multiplier

        result = complex_function(5, 3, multiplier=2)
        assert result.is_ok()
        assert result.unwrap() == 16


@pytest.mark.asyncio
class TestAsyncDecorators:
    async def test_async_returns_result_success(self):
        @async_returns_result
        async def async_divide(a: int, b: int) -> float:
            return a / b

        result = await async_divide(10, 2)
        assert result.is_ok()
        assert result.unwrap() == 5.0

    async def test_async_returns_result_error(self):
        @async_returns_result
        async def async_divide(a: int, b: int) -> float:
            return a / b

        result = await async_divide(10, 0)
        assert result.is_err()
        assert result.error is not None
        assert "ZeroDivisionError" in result.error
        assert result.extra is not None
        assert isinstance(result.extra["exception"], ZeroDivisionError)

    async def test_async_returns_result_preserves_metadata(self):
        @async_returns_result
        async def async_example(x: int) -> int:
            """Async example docstring."""
            return x * 2

        assert async_example.__name__ == "async_example"
        assert async_example.__doc__ == "Async example docstring."

    async def test_async_returns_result_with_args_kwargs(self):
        @async_returns_result
        async def async_complex(a: int, b: int, *, multiplier: int = 1) -> int:
            return (a + b) * multiplier

        result = await async_complex(5, 3, multiplier=2)
        assert result.is_ok()
        assert result.unwrap() == 16

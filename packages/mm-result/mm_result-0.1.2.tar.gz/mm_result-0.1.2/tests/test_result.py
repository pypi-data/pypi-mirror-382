import pytest

from mm_result import Result, UnwrapErrError, UnwrapError


class TestResultCreation:
    def test_ok_creation(self):
        result = Result.ok(42)
        assert result.is_ok()
        assert not result.is_err()
        assert result.value == 42
        assert result.error is None
        assert result.extra is None

    def test_ok_with_extra(self):
        extra = {"key": "value"}
        result = Result.ok(42, extra=extra)
        assert result.is_ok()
        assert result.extra == extra

    def test_ok_with_none_value(self):
        result = Result.ok(None)
        assert result.is_ok()
        assert result.value is None

    def test_err_string(self):
        result = Result.err("error message")
        assert result.is_err()
        assert not result.is_ok()
        assert result.error == "error message"
        assert result.value is None
        assert result.extra is None

    def test_err_exception(self):
        exc = ValueError("bad value")
        result = Result.err(exc)
        assert result.is_err()
        assert result.error == "ValueError: bad value"
        assert result.extra is not None
        assert result.extra["exception"] is exc

    def test_err_tuple(self):
        exc = ValueError("bad value")
        result = Result.err(("custom_error", exc))
        assert result.is_err()
        assert result.error == "custom_error"
        assert result.extra is not None
        assert result.extra["exception"] is exc

    def test_err_user_exception_priority(self):
        exc = ValueError("test")
        user_exc = "custom_exception"
        result = Result.err(exc, extra={"exception": user_exc})
        assert result.extra is not None
        assert result.extra["exception"] == user_exc

    def test_err_traceback_capture(self):
        def raise_error():
            raise ValueError("with traceback")

        try:
            raise_error()
        except Exception as e:
            result = Result.err(e)
            assert result.extra is not None
            assert "traceback" in result.extra
            assert isinstance(result.extra["traceback"], str)

    def test_err_user_traceback_priority(self):
        def raise_error():
            raise ValueError("test")

        try:
            raise_error()
        except Exception as e:
            result = Result.err(e, extra={"traceback": "user_trace"})
            assert result.extra is not None
            assert result.extra["traceback"] == "user_trace"


class TestResultMethods:
    def test_unwrap_success(self):
        result = Result.ok(42)
        assert result.unwrap() == 42

    def test_unwrap_error(self):
        result = Result.err("test error")
        with pytest.raises(UnwrapError, match="Called unwrap\\(\\) on a failure value: test error"):
            result.unwrap()

    def test_unwrap_custom_message(self):
        result = Result.err("test error")
        with pytest.raises(UnwrapError, match="Custom message: test error"):
            result.unwrap("Custom message")

    def test_unwrap_or(self):
        assert Result.ok(42).unwrap_or(0) == 42
        assert Result.err("error").unwrap_or(0) == 0

    def test_unwrap_error_success(self):
        result = Result.err("test error")
        assert result.unwrap_err() == "test error"

    def test_unwrap_error_on_success(self):
        result = Result.ok(42)
        with pytest.raises(UnwrapErrError, match="Called unwrap_err\\(\\) on a success value"):
            result.unwrap_err()

    def test_value_or_error(self):
        assert Result.ok(42).value_or_error() == 42
        assert Result.err("error").value_or_error() == "error"


class TestResultTransformations:
    def test_map_success(self):
        result = Result.ok(42)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_ok()
        assert mapped.unwrap() == 84

    def test_map_error_passthrough(self):
        result = Result.err("error")
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_err()
        assert mapped.error == "error"

    def test_map_exception_handling(self):
        result = Result.ok(42)
        mapped = result.map(lambda _: 1 / 0)  # Will raise ZeroDivisionError
        assert mapped.is_err()
        assert mapped.error == "map_exception"
        assert mapped.extra is not None
        assert isinstance(mapped.extra["exception"], ZeroDivisionError)

    def test_chain_success(self):
        result = Result.ok(42)
        chained = result.chain(lambda x: Result.ok(x * 2))
        assert chained.is_ok()
        assert chained.unwrap() == 84

    def test_chain_error_passthrough(self):
        result = Result.err("error")
        chained = result.chain(lambda x: Result.ok(x * 2))
        assert chained.is_err()
        assert chained.error == "error"

    def test_chain_exception_handling(self):
        result = Result.ok(42)
        chained = result.chain(lambda _: 1 / 0)  # type: ignore[arg-type]  # Will raise ZeroDivisionError
        assert chained.is_err()
        assert chained.error == "chain_exception"
        assert chained.extra is not None
        assert isinstance(chained.extra["exception"], ZeroDivisionError)


@pytest.mark.asyncio
class TestAsyncMethods:
    async def test_map_async_success(self):
        result = Result.ok(42)

        async def async_double(x):
            return x * 2

        mapped = await result.map_async(async_double)
        assert mapped.is_ok()
        assert mapped.unwrap() == 84

    async def test_chain_async_success(self):
        result = Result.ok(42)

        async def async_transform(x):
            return Result.ok(x * 2)

        chained = await result.chain_async(async_transform)
        assert chained.is_ok()
        assert chained.unwrap() == 84


class TestResultUtilities:
    def test_to_dict(self):
        # Success case
        result = Result.ok(42, extra={"key": "value"})
        expected = {"value": 42, "error": None, "extra": {"key": "value"}}
        assert result.to_dict() == expected

        # Error case
        result = Result.err("error", extra={"key": "value"})
        expected = {"value": None, "error": "error", "extra": {"key": "value"}}
        assert result.to_dict() == expected

    def test_to_dict_safe_exception(self):
        # Test with exception - should convert exception to string
        exc = ValueError("test error")
        result = Result.err(exc)

        # Default behavior - keeps original exception object
        default_dict = result.to_dict()
        assert default_dict["extra"]["exception"] is exc

        # Safe exception mode - converts exception to string
        safe_dict = result.to_dict(safe_exception=True)
        assert safe_dict["extra"]["exception"] == "test error"

        # Should be JSON serializable now
        import json

        json_str = json.dumps(safe_dict)
        assert json_str is not None

        # Test with traceback if present
        try:
            raise ValueError("test with traceback")  # noqa: TRY301
        except ValueError as e:
            result_with_tb = Result.err(e)

            # Default should have traceback
            default_with_tb = result_with_tb.to_dict()
            assert "traceback" in default_with_tb["extra"]

            # Safe mode should remove traceback
            safe_with_tb = result_with_tb.to_dict(safe_exception=True)
            assert "traceback" not in safe_with_tb["extra"]

        # Test with no extra - should work fine
        result_no_extra = Result.ok(42)
        assert result_no_extra.to_dict(safe_exception=True) == {"value": 42, "error": None, "extra": None}

        # Test with extra but no exception/traceback - should preserve other data
        result_other_extra = Result.err("error", extra={"custom": "data", "number": 123})
        safe_other = result_other_extra.to_dict(safe_exception=True)
        assert safe_other["extra"] == {"custom": "data", "number": 123}

    def test_repr(self):
        # Success with None value should show value
        result = Result.ok(None)
        assert repr(result) == "Result(value=None)"

        # Success with value
        result = Result.ok(42)
        assert repr(result) == "Result(value=42)"

        # Error
        result = Result.err("error")
        assert repr(result) == "Result(error='error')"

        # Error with extra
        result = Result.err("error", extra={"key": "value"})
        assert repr(result) == "Result(error='error', extra={'key': 'value'})"

    def test_equality(self):
        # Same ok results
        assert Result.ok(42) == Result.ok(42)
        assert Result.ok(42, extra={"a": 1}) == Result.ok(42, extra={"a": 1})

        # Different ok results
        assert Result.ok(42) != Result.ok(43)
        assert Result.ok(42, extra={"a": 1}) != Result.ok(42, extra={"a": 2})

        # Same error results
        assert Result.err("error") == Result.err("error")

        # Different error results
        assert Result.err("error1") != Result.err("error2")

        # Ok vs Error
        assert Result.ok(42) != Result.err("error")

        # Different types
        assert Result.ok(42) != 42
        assert Result.ok(42) != "not a result"

    def test_hash(self):
        # Should be hashable
        result_set = {Result.ok(42), Result.err("error")}
        assert len(result_set) == 2

        # Same results should have same hash
        r1 = Result.ok(42, extra={"a": 1})
        r2 = Result.ok(42, extra={"a": 1})
        assert hash(r1) == hash(r2)


class TestResultCopying:
    def test_with_value(self):
        original = Result.ok(42, extra={"key": "value"})
        new_result = original.with_value("new_value")
        assert new_result.unwrap() == "new_value"
        assert new_result.extra == {"key": "value"}  # Extra preserved

    def test_with_error(self):
        original = Result.ok(42, extra={"key": "value"})
        new_result = original.with_error("new_error")
        assert new_result.is_err()
        assert new_result.error == "new_error"
        assert new_result.extra == {"key": "value"}  # Extra preserved


class TestDirectInstantiation:
    def test_direct_instantiation_blocked(self):
        with pytest.raises(RuntimeError, match="Result is not intended to be instantiated directly"):
            Result()


def test_pydantic_integration():
    """Test pydantic integration if available."""
    try:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            result_field: Result[int]

        # Test serialization
        model = TestModel(result_field=Result.ok(42))
        data = model.model_dump()
        expected = {"result_field": {"value": 42, "error": None, "extra": None}}
        assert data == expected

        # Test deserialization
        model2 = TestModel.model_validate({"result_field": {"value": 123, "error": None, "extra": None}})
        assert model2.result_field.is_ok()
        assert model2.result_field.unwrap() == 123

    except ImportError:
        pytest.skip("Pydantic not available")

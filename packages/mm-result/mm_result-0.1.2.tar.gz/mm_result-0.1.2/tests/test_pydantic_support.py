"""Tests for Pydantic integration."""

import pytest

from mm_result import Result

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

pytestmark = pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")


if PYDANTIC_AVAILABLE:

    class SampleModel(BaseModel):  # type: ignore[misc]
        result_field: Result[int]


class TestPydanticIntegration:
    def test_ok_result_serialization(self):
        model = SampleModel(result_field=Result.ok(42))
        data = model.model_dump()
        expected = {"result_field": {"value": 42, "error": None, "extra": None}}
        assert data == expected

    def test_ok_result_deserialization(self):
        model = SampleModel.model_validate({"result_field": {"value": 123, "error": None, "extra": None}})
        assert model.result_field.is_ok()
        assert model.result_field.unwrap() == 123

    def test_err_result_serialization(self):
        model = SampleModel(result_field=Result.err("something went wrong"))
        data = model.model_dump()
        expected = {"result_field": {"value": None, "error": "something went wrong", "extra": None}}
        assert data == expected

    def test_err_result_deserialization(self):
        model = SampleModel.model_validate({"result_field": {"value": None, "error": "failed", "extra": None}})
        assert model.result_field.is_err()
        assert model.result_field.unwrap_err() == "failed"

    def test_result_with_extra_serialization(self):
        model = SampleModel(result_field=Result.ok(42, extra={"metadata": "test", "count": 5}))
        data = model.model_dump()
        expected = {"result_field": {"value": 42, "error": None, "extra": {"metadata": "test", "count": 5}}}
        assert data == expected

    def test_result_with_extra_deserialization(self):
        model = SampleModel.model_validate({"result_field": {"value": 100, "error": None, "extra": {"key": "value"}}})
        assert model.result_field.is_ok()
        assert model.result_field.unwrap() == 100
        assert model.result_field.extra == {"key": "value"}

    def test_safe_exception_serialization(self):
        try:
            raise ValueError("test error")  # noqa: TRY301
        except ValueError as e:
            result = Result.err(e)

        model = SampleModel(result_field=result)
        data = model.model_dump()

        assert data["result_field"]["error"] == "ValueError: test error"
        assert data["result_field"]["value"] is None
        assert "exception" in data["result_field"]["extra"]
        assert isinstance(data["result_field"]["extra"]["exception"], str)
        assert "traceback" not in data["result_field"]["extra"]

    def test_result_instance_passthrough(self):
        original = Result.ok(42)
        model = SampleModel(result_field=original)
        assert model.result_field is original

    def test_invalid_value_raises_type_error(self):
        with pytest.raises(TypeError, match="Invalid value for Result"):
            SampleModel.model_validate({"result_field": "not a valid result"})

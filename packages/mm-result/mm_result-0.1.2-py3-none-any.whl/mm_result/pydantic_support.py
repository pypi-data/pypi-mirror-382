"""Pydantic integration for Result type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

if TYPE_CHECKING:
    from .result import Result


def add_pydantic_support(result_class: type[Result[Any]]) -> None:
    """Add Pydantic schema validation and serialization to Result class."""

    def __get_pydantic_core_schema__(  # noqa: N807
        cls: type[Result[Any]], _source_type: type[Any], _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,  # type: ignore[attr-defined]
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.to_dict(safe_exception=True)),
        )

    def _validate(cls: type[Result[Any]], value: object) -> Result[Any]:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls._create(
                value=value.get("value"),
                error=value.get("error"),
                extra=value.get("extra"),
            )
        raise TypeError(f"Invalid value for Result: {value}")

    result_class.__get_pydantic_core_schema__ = classmethod(__get_pydantic_core_schema__)  # type: ignore[attr-defined]
    result_class._validate = classmethod(_validate)  # type: ignore[attr-defined]  # noqa: SLF001

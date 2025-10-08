from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar
from uuid import UUID


class ExtendedJSONEncoder(json.JSONEncoder):
    """JSON encoder with extended type support for common Python objects.

    Supports built-in Python types, dataclasses, enums, exceptions, and custom registered types.
    Automatically registers pydantic BaseModel if available.
    All type handlers are unified in a single registration system for consistency and performance.
    """

    _type_handlers: ClassVar[dict[type[Any], Callable[[Any], Any]]] = {
        # Order matters: more specific types first
        datetime: lambda obj: obj.isoformat(),  # Must be before date (inheritance)
        date: lambda obj: obj.isoformat(),
        UUID: str,
        Decimal: str,
        Path: str,
        set: list,
        frozenset: list,
        bytes: lambda obj: obj.decode("latin-1"),
        complex: lambda obj: {"real": obj.real, "imag": obj.imag},
        Enum: lambda obj: obj.value,
        Exception: str,
    }

    @classmethod
    def register(cls, type_: type[Any], serializer: Callable[[Any], Any]) -> None:
        """Register a custom type with its serialization function.

        Args:
            type_: The type to register
            serializer: Function that converts objects of this type to JSON-serializable data

        Raises:
            ValueError: If type_ is a built-in JSON type
        """
        if type_ in (str, int, float, bool, list, dict, type(None)):
            raise ValueError(f"Cannot override built-in JSON type: {type_.__name__}")
        cls._type_handlers[type_] = serializer

    def default(self, obj: Any) -> Any:  # noqa: ANN401
        # Check registered type handlers first
        for type_, handler in self._type_handlers.items():
            if isinstance(obj, type_):
                return handler(obj)

        # Special case: dataclasses (requires is_dataclass check, not isinstance)
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)  # Don't need recursive serialization

        return super().default(obj)


def json_dumps(data: Any, type_handlers: dict[type[Any], Callable[[Any], Any]] | None = None, **kwargs: Any) -> str:  # noqa: ANN401
    """Serialize object to JSON with extended type support.

    Unlike standard json.dumps, uses ExtendedJSONEncoder which automatically handles
    UUID, Decimal, Path, datetime, dataclasses, enums, pydantic models, and other Python types.

    Args:
        data: Object to serialize to JSON
        type_handlers: Optional additional type handlers for this call only.
                      These handlers take precedence over default ones.
        **kwargs: Additional arguments passed to json.dumps

    Returns:
        JSON string representation
    """
    if type_handlers:
        # Type narrowing for mypy
        handlers: dict[type[Any], Callable[[Any], Any]] = type_handlers

        class TemporaryEncoder(ExtendedJSONEncoder):
            _type_handlers: ClassVar[dict[type[Any], Callable[[Any], Any]]] = {
                **ExtendedJSONEncoder._type_handlers,  # noqa: SLF001
                **handlers,
            }

        encoder_cls: type[json.JSONEncoder] = TemporaryEncoder
    else:
        encoder_cls = ExtendedJSONEncoder

    return json.dumps(data, cls=encoder_cls, **kwargs)


def _auto_register_optional_types() -> None:
    """Register handlers for optional dependencies if available."""
    # Pydantic models
    try:
        from pydantic import BaseModel  # type: ignore[import-not-found]  # noqa: PLC0415

        ExtendedJSONEncoder.register(BaseModel, lambda obj: obj.model_dump())
    except ImportError:
        pass


# Auto-register optional types when module is imported
_auto_register_optional_types()

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

import pytest

from mm_std.json_utils import ExtendedJSONEncoder, json_dumps


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class Person:
    name: str
    age: int
    birth_date: date


@dataclass
class Address:
    street: str
    city: str


class CustomType:
    def __init__(self, value: str) -> None:
        self.value = value


def assert_json_serializes_to(obj, expected_json_string):
    result = json.dumps(obj, cls=ExtendedJSONEncoder)
    assert result == expected_json_string


def assert_json_deserializes_to(obj, expected_dict):
    result = json.loads(json.dumps(obj, cls=ExtendedJSONEncoder))
    assert result == expected_dict


class TestExtendedJSONEncoder:
    def test_builtin_types_unchanged(self):
        data = {"str": "hello", "int": 42, "float": 3.14, "bool": True, "list": [1, 2], "dict": {"nested": "value"}, "null": None}
        result = json.dumps(data, cls=ExtendedJSONEncoder)
        expected = json.dumps(data)
        assert result == expected

    @pytest.mark.parametrize(
        "obj,expected",
        [
            (datetime(2023, 6, 15, 14, 30, 45), '"2023-06-15T14:30:45"'),
            (date(2023, 6, 15), '"2023-06-15"'),
            (UUID("12345678-1234-5678-1234-567812345678"), '"12345678-1234-5678-1234-567812345678"'),
            (Decimal("123.456"), '"123.456"'),
            (Path("/home/user/file.txt"), '"/home/user/file.txt"'),
            (b"hello world", '"hello world"'),
            (Color.RED, '"red"'),
            (ValueError("Something went wrong"), '"Something went wrong"'),
        ],
    )
    def test_basic_type_serialization(self, obj, expected):
        assert_json_serializes_to(obj, expected)

    @pytest.mark.parametrize(
        "collection,expected_sorted",
        [
            ({1, 2, 3}, [1, 2, 3]),
            (frozenset({1, 2, 3}), [1, 2, 3]),
        ],
    )
    def test_set_serialization(self, collection, expected_sorted):
        result = json.loads(json.dumps(collection, cls=ExtendedJSONEncoder))
        assert sorted(result) == expected_sorted

    def test_complex_number_serialization(self):
        complex_obj = complex(3, 4)
        assert_json_deserializes_to(complex_obj, {"real": 3.0, "imag": 4.0})

    def test_dataclass_serialization(self):
        person = Person("Alice", 30, date(1993, 6, 15))
        expected = {"name": "Alice", "age": 30, "birth_date": "1993-06-15"}
        assert_json_deserializes_to(person, expected)

    def test_nested_dataclass_serialization(self):
        person = Person("Bob", 25, date(1998, 12, 25))
        data = {"person": person, "uuid": UUID("12345678-1234-5678-1234-567812345678")}
        expected = {
            "person": {"name": "Bob", "age": 25, "birth_date": "1998-12-25"},
            "uuid": "12345678-1234-5678-1234-567812345678",
        }
        assert_json_deserializes_to(data, expected)


class TestExtendedJSONEncoderRegistration:
    def test_register_custom_type(self):
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"custom:{obj.value}")
        custom_obj = CustomType("test")
        assert_json_serializes_to(custom_obj, '"custom:test"')

    @pytest.mark.parametrize("builtin_type", [str, int, float, bool, list, dict, type(None)])
    def test_register_builtin_type_raises_error(self, builtin_type):
        with pytest.raises(ValueError, match=f"Cannot override built-in JSON type: {builtin_type.__name__}"):
            ExtendedJSONEncoder.register(builtin_type, lambda obj: obj)

    def test_register_override_existing_handler(self):
        # Register initial handler
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"first:{obj.value}")
        custom_obj = CustomType("test")
        assert_json_serializes_to(custom_obj, '"first:test"')

        # Override with new handler
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"second:{obj.value}")
        assert_json_serializes_to(custom_obj, '"second:test"')


class TestJsonDumps:
    def test_basic_usage_without_type_handlers(self):
        data = {"date": date(2023, 6, 15), "uuid": UUID("12345678-1234-5678-1234-567812345678")}
        expected = {"date": "2023-06-15", "uuid": "12345678-1234-5678-1234-567812345678"}
        result = json.loads(json_dumps(data))
        assert result == expected

    def test_with_additional_type_handlers(self):
        custom_obj = CustomType("test_value")
        data = {"custom": custom_obj, "date": date(2023, 6, 15)}
        type_handlers = {CustomType: lambda obj: f"handled:{obj.value}"}
        expected = {"custom": "handled:test_value", "date": "2023-06-15"}
        result = json.loads(json_dumps(data, type_handlers=type_handlers))
        assert result == expected

    def test_type_handlers_override_default(self):
        data = {"date": date(2023, 6, 15)}
        type_handlers = {date: lambda obj: f"custom_date:{obj.isoformat()}"}
        expected = {"date": "custom_date:2023-06-15"}
        result = json.loads(json_dumps(data, type_handlers=type_handlers))
        assert result == expected

    @pytest.mark.parametrize(
        "kwargs,assertion",
        [
            ({"indent": 2}, lambda result: "\n" in result),
            ({"ensure_ascii": True}, lambda _: "\\u" in json_dumps({"msg": "hello 世界"}, ensure_ascii=True)),
            ({"ensure_ascii": False}, lambda _: "世界" in json_dumps({"msg": "hello 世界"}, ensure_ascii=False)),
        ],
    )
    def test_kwargs_passed_to_json_dumps(self, kwargs, assertion):
        data = {"name": "test", "value": 42}
        result = json_dumps(data, **kwargs)
        assert assertion(result)

    @pytest.mark.parametrize(
        "type_handlers",
        [
            {},
            None,
        ],
    )
    def test_empty_and_none_type_handlers(self, type_handlers):
        data = {"date": date(2023, 6, 15)}
        result = json_dumps(data, type_handlers=type_handlers)
        expected = json_dumps(data)
        assert result == expected

    def test_complex_nested_structure_with_custom_handlers(self):
        address = Address("123 Main St", "New York")
        person = Person("Alice", 30, date(1993, 6, 15))
        custom = CustomType("special")

        data = {
            "timestamp": datetime(2023, 6, 15, 14, 30),
            "person": person,
            "address": address,
            "custom": custom,
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "tags": {"important", "test"},
        }

        type_handlers = {
            CustomType: lambda obj: {"type": "custom", "value": obj.value},
            Address: lambda obj: f"{obj.street}, {obj.city}",
        }

        result = json.loads(json_dumps(data, type_handlers=type_handlers))

        expected = {
            "timestamp": "2023-06-15T14:30:00",
            "person": {"name": "Alice", "age": 30, "birth_date": "1993-06-15"},
            "address": "123 Main St, New York",
            "custom": {"type": "custom", "value": "special"},
            "id": "12345678-1234-5678-1234-567812345678",
            "tags": ["important", "test"],
        }

        # Check tags separately due to set ordering
        assert sorted(result["tags"]) == sorted(expected["tags"])
        result_without_tags = {k: v for k, v in result.items() if k != "tags"}
        expected_without_tags = {k: v for k, v in expected.items() if k != "tags"}
        assert result_without_tags == expected_without_tags

from collections import OrderedDict, defaultdict
from decimal import Decimal

import pytest

from mm_std import replace_empty_dict_entries


@pytest.fixture
def sample_data():
    return {"a": 1, "b": None, "c": "hello", "d": "", "e": 0, "f": False}


@pytest.fixture
def complex_data():
    return {
        "none": None,
        "empty_str": "",
        "zero_int": 0,
        "zero_float": 0.0,
        "zero_decimal": Decimal(0),
        "false": False,
        "keep_this": "value",
        "keep_true": True,
        "keep_one": 1,
    }


class TestReplaceEmptyDictEntries:
    def test_basic_none_removal(self, sample_data):
        result = replace_empty_dict_entries(sample_data)
        assert result == {"a": 1, "c": "hello", "e": 0, "f": False}  # empty string removed by default
        assert type(result) is dict

    def test_none_replacement_with_defaults(self, sample_data):
        defaults = {"b": 42}
        result = replace_empty_dict_entries(sample_data, defaults)
        assert result == {"a": 1, "b": 42, "c": "hello", "e": 0, "f": False}  # empty string removed by default

    @pytest.mark.parametrize(
        "treat_empty_string_as_empty,expected_keys",
        [
            (True, {"a", "c", "e", "f"}),  # default behavior - empty strings removed
            (False, {"a", "c", "d", "e", "f"}),  # empty strings kept
        ],
    )
    def test_empty_string_handling(self, sample_data, treat_empty_string_as_empty, expected_keys):
        result = replace_empty_dict_entries(sample_data, treat_empty_string_as_empty=treat_empty_string_as_empty)
        assert set(result.keys()) == expected_keys

    def test_empty_string_with_defaults(self, sample_data):
        defaults = {"d": "default_value"}
        result = replace_empty_dict_entries(sample_data, defaults)
        assert result["d"] == "default_value"

    @pytest.mark.parametrize(
        "treat_zero_as_empty,expected_has_zero",
        [
            (False, True),  # default - zeros kept
            (True, False),  # zeros removed
        ],
    )
    def test_zero_handling(self, treat_zero_as_empty, expected_has_zero):
        data = {"a": 1, "b": 0, "c": 0.0, "d": Decimal(0)}
        result = replace_empty_dict_entries(data, treat_zero_as_empty=treat_zero_as_empty)

        if expected_has_zero:
            assert "b" in result and "c" in result and "d" in result
        else:
            assert "b" not in result and "c" not in result and "d" not in result

    def test_zero_with_defaults(self):
        data = {"a": 1, "b": 0, "c": 0.0, "d": Decimal(0)}
        defaults = {"b": 10, "c": 3.14, "d": Decimal(100)}
        result = replace_empty_dict_entries(data, defaults, treat_zero_as_empty=True)
        assert result == {"a": 1, "b": 10, "c": 3.14, "d": Decimal(100)}

    @pytest.mark.parametrize(
        "treat_false_as_empty,expected_has_false",
        [
            (False, True),  # default - False kept
            (True, False),  # False removed
        ],
    )
    def test_false_handling(self, treat_false_as_empty, expected_has_false):
        data = {"a": True, "b": False, "c": "hello"}
        result = replace_empty_dict_entries(data, treat_false_as_empty=treat_false_as_empty)

        if expected_has_false:
            assert result["b"] is False
        else:
            assert "b" not in result

    def test_false_with_defaults(self):
        data = {"a": True, "b": False, "c": "hello"}
        result = replace_empty_dict_entries(data, {"b": True}, treat_false_as_empty=True)
        assert result == {"a": True, "b": True, "c": "hello"}

    def test_bool_vs_int_precedence(self):
        data = {"a": False, "b": 0, "c": True, "d": 1}
        defaults = {"a": "false_default", "b": "zero_default"}
        result = replace_empty_dict_entries(data, defaults, treat_zero_as_empty=True, treat_false_as_empty=True)
        assert result == {"a": "false_default", "b": "zero_default", "c": True, "d": 1}

    @pytest.mark.parametrize(
        "dict_type,expected_type",
        [
            (dict, dict),
            (lambda d: defaultdict(list, d), defaultdict),
            (lambda d: OrderedDict(d.items()), OrderedDict),
        ],
    )
    def test_type_preservation(self, sample_data, dict_type, expected_type):
        data = dict_type(sample_data)
        result = replace_empty_dict_entries(data)
        assert isinstance(result, expected_type)

    def test_defaultdict_factory_preservation(self):
        data = defaultdict(list, {"a": [1, 2], "b": None, "c": []})
        result = replace_empty_dict_entries(data)

        assert isinstance(result, defaultdict)
        assert result.default_factory is list
        assert result == {"a": [1, 2], "c": []}

        # Test that default_factory still works
        result["new_key"].append("test")  # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]
        assert result["new_key"] == ["test"]

    def test_ordered_dict_order_preservation(self):
        data = OrderedDict([("a", 1), ("b", None), ("c", 2)])
        result = replace_empty_dict_entries(data)

        assert type(result) is OrderedDict
        assert list(result.keys()) == ["a", "c"]
        assert result == OrderedDict([("a", 1), ("c", 2)])

    def test_all_flags_combined(self, complex_data):
        result = replace_empty_dict_entries(
            complex_data, treat_zero_as_empty=True, treat_false_as_empty=True, treat_empty_string_as_empty=True
        )
        assert result == {"keep_this": "value", "keep_true": True, "keep_one": 1}

    @pytest.mark.parametrize(
        "input_dict,expected",
        [
            ({}, {}),
            ({"a": 1, "b": "hello", "c": True}, {"a": 1, "b": "hello", "c": True}),
        ],
    )
    def test_edge_cases(self, input_dict, expected):
        result = replace_empty_dict_entries(input_dict)
        assert result == expected
        assert result is not input_dict  # Should be a new instance

    def test_partial_defaults(self):
        data = {"a": None, "b": None, "c": 1}
        defaults = {"a": "replaced"}
        result = replace_empty_dict_entries(data, defaults)
        assert result == {"a": "replaced", "c": 1}

    @pytest.mark.parametrize(
        "value,treat_zero_as_empty,should_be_removed",
        [
            (-0.0, True, True),
            (+0.0, True, True),
            (Decimal("0.00"), True, True),
            (0.0000001, True, False),
            (-1, True, False),
        ],
    )
    def test_numeric_edge_cases(self, value, treat_zero_as_empty, should_be_removed):
        data = {"test_key": value}
        result = replace_empty_dict_entries(data, treat_zero_as_empty=treat_zero_as_empty)

        if should_be_removed:
            assert "test_key" not in result
        else:
            assert "test_key" in result

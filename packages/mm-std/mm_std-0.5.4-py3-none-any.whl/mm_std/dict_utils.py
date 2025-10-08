from collections import OrderedDict, defaultdict
from collections.abc import Mapping, MutableMapping
from decimal import Decimal
from typing import TypeVar, overload

K = TypeVar("K")
V = TypeVar("V")


@overload
def replace_empty_dict_entries(
    data: defaultdict[K, V],
    defaults: Mapping[K, V] | None = None,
    treat_zero_as_empty: bool = False,
    treat_false_as_empty: bool = False,
    treat_empty_string_as_empty: bool = True,
) -> defaultdict[K, V]: ...


@overload
def replace_empty_dict_entries(
    data: OrderedDict[K, V],
    defaults: Mapping[K, V] | None = None,
    treat_zero_as_empty: bool = False,
    treat_false_as_empty: bool = False,
    treat_empty_string_as_empty: bool = True,
) -> OrderedDict[K, V]: ...


@overload
def replace_empty_dict_entries(
    data: dict[K, V],
    defaults: Mapping[K, V] | None = None,
    treat_zero_as_empty: bool = False,
    treat_false_as_empty: bool = False,
    treat_empty_string_as_empty: bool = True,
) -> dict[K, V]: ...


def replace_empty_dict_entries(
    data: MutableMapping[K, V],
    defaults: Mapping[K, V] | None = None,
    treat_zero_as_empty: bool = False,
    treat_false_as_empty: bool = False,
    treat_empty_string_as_empty: bool = True,
) -> MutableMapping[K, V]:
    """
    Replace empty entries in a dictionary with defaults or remove them entirely.

    Preserves the exact type of the input mapping:
    - dict[str, int] → dict[str, int]
    - defaultdict[str, float] → defaultdict[str, float]
    - OrderedDict[str, str] → OrderedDict[str, str]

    Args:
        data: The dictionary to process
        defaults: Default values to use for empty entries. If None or key not found, empty entries are removed
        treat_zero_as_empty: Treat 0 as empty value
        treat_false_as_empty: Treat False as empty value
        treat_empty_string_as_empty: Treat "" as empty value

    Returns:
        New dictionary of the same concrete type with empty entries replaced or removed
    """
    if defaults is None:
        defaults = {}

    if isinstance(data, defaultdict):
        result: MutableMapping[K, V] = defaultdict(data.default_factory)
    else:
        result = data.__class__()

    for key, value in data.items():
        should_replace = (
            value is None
            or (treat_false_as_empty and value is False)
            or (treat_empty_string_as_empty and isinstance(value, str) and value == "")
            or (treat_zero_as_empty and isinstance(value, (int, float, Decimal)) and not isinstance(value, bool) and value == 0)
        )

        if should_replace:
            if key in defaults:
                new_value = defaults[key]
            else:
                continue  # Skip the key if no default is available
        else:
            new_value = value

        result[key] = new_value
    return result

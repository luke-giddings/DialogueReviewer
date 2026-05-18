"""
Utilities to help when narrowing type checking.
"""

from typing import Protocol, TypeIs, cast, runtime_checkable


def is_dict_str_str(test_dict: object) -> TypeIs[dict[str, str]]:
    """Return True if the type is dict with string keys and string values."""
    if not isinstance(test_dict, dict):
        return False
    items = cast(dict[object, object], test_dict).items()
    return all(isinstance(k, str) and isinstance(v, str) for k, v in items)


def is_dict_str_obj(test_dict: object) -> TypeIs[dict[str, object]]:
    """Return True if the type is dict with string keys. Value types are not checked."""
    if not isinstance(test_dict, dict):
        return False
    items = cast(dict[object, object], test_dict).items()
    return all(isinstance(k, str) for k, _ in items)


def is_list_obj(test_list: object) -> TypeIs[list[object]]:
    """Return True if the type is list. Element types are not checked."""
    return isinstance(test_list, list)


def is_list_str(test_list: object) -> TypeIs[list[str]]:
    """Return True if the type is list of strings."""
    if not isinstance(test_list, list):
        return False
    test_list = cast(list[object], test_list)
    return all(isinstance(k, str) for k in test_list)


@runtime_checkable
class HasFields(Protocol):
    """Protocol to allow us to do strict type checking with objects that have _fields attributes."""

    _fields: tuple[str, ...]


def get_fields(obj: HasFields) -> tuple[str, ...]:
    """This function is to get around Pylance complaining about using protected members outside their class."""
    return obj._fields  # pyright: ignore[reportPrivateUsage]

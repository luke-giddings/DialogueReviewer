"""
Utilities to help when narrowing type checking.
"""

from typing import Any, TypeIs, cast


def is_dict_str_str(test_dict: Any) -> TypeIs[dict[str, str]]:
    """Return True if the type is dict with string keys and string values."""
    if not isinstance(test_dict, dict):
        return False
    items = cast(dict[Any, Any], test_dict).items()
    return all(isinstance(k, str) and isinstance(v, str) for k, v in items)


def is_dict_str_any(test_dict: Any) -> TypeIs[dict[str, Any]]:
    """Return True if the type is dict with string keys. Value's type is not checked."""
    if not isinstance(test_dict, dict):
        return False
    items = cast(dict[Any, Any], test_dict).items()
    return all(isinstance(k, str) for k, _ in items)


def is_list_any(test_list: Any) -> TypeIs[list[Any]]:
    """Return True if the type is list. Element's type is not checked."""
    return isinstance(test_list, list)


def is_list_str(test_list: Any) -> TypeIs[list[str]]:
    """Return True if the type is list of strings."""
    if not isinstance(test_list, list):
        return False
    test_list = cast(list[Any], test_list)
    return all(isinstance(k, str) for k in test_list)

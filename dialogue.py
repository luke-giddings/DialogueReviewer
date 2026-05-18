"""
DialogueLine dataclass with the validators and converters to create them.
Importer to load in the dialogue lines.  You can load from a file (json, xlsx or csv) or from Gridly's database.

Usage: Create a DialogueImporter class and then call from_gridly() or from_file().

TODO: Describe the scheme.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NamedTuple, Protocol, TypedDict, TypeIs, cast, get_type_hints

import pandas as pd

import _type_helpers
from _gridly_socket import GridlySocket

logger = logging.getLogger(__name__)
GRIDLY_COLUMN_CHARACTER: Final[str] = "column_CharacterName"
GRIDLY_COLUMN_LANG_PREFIX: Final[set[str]] = {"src_", "tg_"}


@dataclass
class DialogueLine:
    """
    A single dialogue line containing all the information associated with it:
        Character speaking, translations and path information.
    """

    character: str = ""
    translations: dict[str, str] = field(default_factory=dict[str, str])  # Lang -> Text

    # Path Info
    id: str = ""
    game_area: str = ""
    chapter: str = ""
    scene: str = ""
    game_feature: str = ""

    @classmethod
    def from_tuple(cls, tuple_line: _DialogueRowTuple) -> DialogueLine:
        """
        Create a dialogue line from a _DialogueRowTuple.
        Args:
            tuple_line: The tuple to convert.
        Returns:
            The new dialogue line.
        """
        translations: dict[str, str] = {}
        for named_field in tuple_line._fields:
            if named_field.startswith("text_"):
                lang_id = named_field[len("text_") :]
                translations[lang_id] = getattr(tuple_line, named_field)

        return cls(
            character=tuple_line.character,
            translations=translations,
            id=tuple_line.id,
            game_area=tuple_line.game_area,
            chapter=tuple_line.chapter,
            scene=tuple_line.scene,
            game_feature=tuple_line.game_feature,
        )

    @classmethod
    def from_dict(cls, dict_line: _DialogueRowDict) -> DialogueLine:
        """
        Create a dialogue line from a dictionary.
        Args:
            dict_line: The dictionary to convert.
        Returns:
            The new dialogue line.
        """
        return cls(
            character=dict_line["character"],
            translations=dict(dict_line["translations"]),
            id=dict_line["id"],
            game_area=dict_line["game_area"],
            chapter=dict_line["chapter"],
            scene=dict_line["scene"],
            game_feature=dict_line["game_feature"],
        )


class DialogueImporter:
    """
    Currently a stateless class that wraps all the ways to load the dialogue lines.
    """

    def from_gridly(self, view_id: str, api_key: str) -> list[DialogueLine]:
        """
        Load dialogue lines from a Gridly View.
        Args:
            view_id: The Gridly View ID that you want to get the records from.
            api_key: The Gridly API Key that will allow you access to Gridly.
        Returns:
            A list containing all the valid dialogue lines. This is empty if an error occurs.
        """
        results: list[DialogueLine] = []
        socket: GridlySocket = GridlySocket(view_id, api_key)
        gridly_results = socket.retrieve_all_records()
        if not gridly_results[0] or gridly_results[1] is None:
            return results

        for gridly_line in gridly_results[1]:
            if not _type_helpers.is_dict_str_obj(gridly_line):
                continue

            # convert gridly results into a dict
            new_dialogue_line: dict[str, object] = {}
            translations = dict[str, str]()
            new_dialogue_line["translations"] = translations
            all_characters: list[str] = []

            if "id" in gridly_line:
                new_dialogue_line["id"] = gridly_line["id"]
            if "path" in gridly_line and isinstance(gridly_line["path"], str):
                new_dialogue_line = _extract_from_gridly_path(gridly_line["path"], new_dialogue_line)
            if "cells" in gridly_line:
                cells = gridly_line["cells"]
                if _type_helpers.is_list_obj(cells):
                    for cell in cells:
                        if not _type_helpers.is_dict_str_obj(cell):
                            continue
                        if "columnId" in cell and "value" in cell and isinstance(cell["columnId"], str):
                            for lang_prefix in GRIDLY_COLUMN_LANG_PREFIX:
                                if cell["columnId"].startswith(lang_prefix) and isinstance(cell["value"], str):
                                    language = cell["columnId"][len(lang_prefix) :]
                                    translations[language] = cell["value"]
                            if cell["columnId"] == GRIDLY_COLUMN_CHARACTER:
                                cell_value = cell["value"]
                                if _type_helpers.is_list_str(cell_value):
                                    all_characters = cell_value

            for character in all_characters:
                char_converted_data: _DialogueRowDict = cast(
                    _DialogueRowDict, {**new_dialogue_line, "character": character}
                )
                if _is_valid_from_dict(char_converted_data):
                    line = DialogueLine.from_dict(char_converted_data)
                    _log_missing_unknown_lines(
                        char_converted_data, True, char_converted_data["id"], _get_broken_fields_from_dict
                    )
                    results.append(line)
                else:
                    _log_missing_unknown_lines(char_converted_data, False, "Unknown ID", _get_broken_fields_from_dict)

        return results

    def from_file(self, path: Path) -> list[DialogueLine]:
        """
        Load the dialogue lines from a given file.
        Supported types: csv, xlsx and json.
        Args:
            path: The path to the file location.
        Returns:
            A list containing all the valid dialogue lines. This is empty if an error occurs.
        """
        suffix = path.suffix.lower()
        match suffix:
            case ".csv":
                return _from_csv(path)
            case ".xlsx":
                return _from_xlsx(path)
            case ".json":
                return _from_json(path)
            case _:
                raise ValueError(f"Unsupported file extension: {suffix}")


class _DialogueRowTuple(NamedTuple):
    """Expected shape of a row from DataFrame.itertuples() (CSV/XLSX path)."""

    id: str
    character: str
    game_area: str
    chapter: str
    scene: str
    game_feature: str


_DIALOGUE_ROW_TUPLE_VAR_TYPES = get_type_hints(_DialogueRowTuple)
_DIALOGUE_ROW_TUPLE_MANUAL_VERIFY_VARS: set[str] = set()


class _DialogueRowDict(TypedDict):
    """Expected shape of a row from JSON or Gridly input."""

    id: str
    character: str
    game_area: str
    chapter: str
    scene: str
    game_feature: str
    translations: dict[str, str]


_DIALOGUE_ROW_DICT_VAR_TYPES = get_type_hints(_DialogueRowDict)
_DIALOGUE_ROW_DICT_MANUAL_VERIFY_VARS = {"translations"}


def _from_csv(path: Path) -> list[DialogueLine]:
    """Load dialogue lines from a csv file."""
    file = pd.read_csv(path)
    return _from_dataframe(file)


def _from_xlsx(path: Path) -> list[DialogueLine]:
    """Load dialogue lines from an excel file."""
    file: pd.DataFrame = pd.read_excel(path)  # pyright: ignore[reportUnknownMemberType] (pandas-stubs leaves an Unknown in the sig)
    return _from_dataframe(file)


def _from_json(path: Path) -> list[DialogueLine]:
    """Load dialogue lines from a json file."""
    results: list[DialogueLine] = []
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
        if not _type_helpers.is_list_obj(data):
            logger.error("Expected JSON array at top level, got %s", type(data).__name__)
            return []
        for json_line in data:
            if not _is_valid_from_dict(json_line):
                _log_missing_unknown_lines(json_line, False, "Unknown ID", _get_broken_fields_from_dict)
                continue
            line = DialogueLine.from_dict(json_line)
            _log_missing_unknown_lines(json_line, True, json_line["id"], _get_broken_fields_from_dict)
            results.append(line)
    return results


def _from_dataframe(dataframe: pd.DataFrame) -> list[DialogueLine]:
    """
    Convert all the dialogue lines within a data frame.
    Args:
        dataframe: The DataFrame to convert.
    Returns:
        A list of the new dialogue lines.
    """
    result: list[DialogueLine] = []

    for dialogue_row in dataframe.itertuples(index=False):
        if not _is_valid_from_tuple(dialogue_row):
            _log_missing_unknown_lines(dialogue_row, False, "Unknown ID", _get_broken_fields_from_tuple)
            continue
        line = DialogueLine.from_tuple(dialogue_row)
        _log_missing_unknown_lines(dialogue_row, True, dialogue_row.id, _get_broken_fields_from_tuple)
        result.append(line)

    return result


def _extract_from_gridly_path(path: str, current_line: dict[str, object]) -> dict[str, object]:
    """
    Extract game_area / chapter / scene / game_feature from a Gridly path.

    Matches the specific Gridly setup used in our current database.
    If the path collapses to two segments and the chapter is "Global" (case-insensitive),
    scene is set equal to chapter.

    Args:
        path: The Path of the Gridly dialogue line
        current_line: The dialogue line
    Returns:
        A copy of `current_line` with the extracted fields populated.
    """
    result: dict[str, object] = {**current_line}

    paths = path.split("/")
    paths_len = len(paths)
    if paths[0] != "":
        result["game_area"] = paths[0]

    if paths_len > 1:
        result["chapter"] = paths[1]

    if paths_len > 2:
        result["scene"] = paths[2]
    elif paths_len > 1 and paths[1].casefold() == "global":
        result["scene"] = result["chapter"]

    if paths_len > 3:
        result["game_feature"] = paths[3]
    else:
        result["game_feature"] = ""

    return result


def _is_valid_from_tuple(tuple_line: object) -> TypeIs[_DialogueRowTuple]:
    """
    Return True if a tuple will be acceptable to convert via from_tuple().
    Args:
        tuple_line: The tuple to validate.
    """
    for key, key_type in _DIALOGUE_ROW_TUPLE_VAR_TYPES.items():
        if key not in _DIALOGUE_ROW_TUPLE_MANUAL_VERIFY_VARS and (
            not hasattr(tuple_line, key) or not isinstance(getattr(tuple_line, key), key_type)
        ):
            return False

    has_language = False
    if isinstance(tuple_line, _type_helpers.HasFields):
        for field_name in _type_helpers.get_fields(tuple_line):
            if field_name.startswith("text_"):
                has_language = True
                break
    return has_language


def _is_valid_from_dict(dict_line: object) -> TypeIs[_DialogueRowDict]:
    """
    Return True if a dictionary will be acceptable to convert via from_dict().
    Args:
        dict_line: The dictionary to validate.
    """
    if not _type_helpers.is_dict_str_obj(dict_line):
        return False

    for key, key_type in _DIALOGUE_ROW_DICT_VAR_TYPES.items():
        if key not in _DIALOGUE_ROW_DICT_MANUAL_VERIFY_VARS and not isinstance(dict_line.get(key), key_type):
            return False

    translations = dict_line.get("translations")
    if not _type_helpers.is_dict_str_str(translations):
        return False

    return len(translations) != 0


def _log_missing_unknown_lines(data: object, was_success: bool, data_id: str, fn: BrokenFieldsGetter) -> None:
    """
    Log any missing or unknown fields in the data structure against the current schema.
    Args:
        data: The structure to check
        was_success: If the structure had been validated successfully.  If so, it won't have missing fields but might have unknown.
        data_id: an id to help identify the data when reading the log.
        fn: The function that can identify the missing or unknown fields.
    """
    missing, unknown = fn(data)
    num_missing = len(missing)
    num_unknown = len(unknown)

    if num_missing > 0 or num_unknown > 0:
        success_str: str = "Successfully" if was_success else "Failed"
        logger.warning(
            "Warning - Processed dialogue line %s %s but missing or unknown fields present:\nMissing (%d):\n%s\nUnknown (%d):\n%s",
            success_str,
            data_id,
            num_missing,
            "\n".join(missing),
            num_unknown,
            "\n".join(unknown),
        )


class BrokenFieldsGetter(Protocol):
    def __call__(self, line: object) -> tuple[list[str], list[str]]: ...


def _get_broken_fields_from_tuple(line: object) -> tuple[list[str], list[str]]:
    """
    Return field names that do not match the expected schema.
    Args:
        line: Tuple to test.
    Returns:
        Tuple of lists of (missing, unknown) field names.
    """
    if not isinstance(line, _type_helpers.HasFields):
        return (["Does not have _fields.  All fields missing"], [])

    fields = _type_helpers.get_fields(line)
    unexpected = [k for k in fields if k not in _DIALOGUE_ROW_TUPLE_VAR_TYPES and not k.startswith("text_")]
    missing = [k for k in _DIALOGUE_ROW_TUPLE_VAR_TYPES if k not in fields]

    return (missing, unexpected)


def _get_broken_fields_from_dict(line: object) -> tuple[list[str], list[str]]:
    """
    Return field names that do not match the expected schema.
    Args:
        line: Dictionary to test.
    Returns:
        Tuple of lists of (missing, unknown) field names.
    """
    if not _type_helpers.is_dict_str_obj(line):
        return (["Is not a dict[str, Obj].  All fields missing"], [])

    unexpected = [k for k in line if k not in _DIALOGUE_ROW_DICT_VAR_TYPES]
    missing = [k for k in _DIALOGUE_ROW_DICT_VAR_TYPES if k not in line]

    return (missing, unexpected)

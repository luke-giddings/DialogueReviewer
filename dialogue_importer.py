"""
Importer to load in the dialogue lines.  You can load from a file (json, xlsx or csv) or from Gridly's database.

Usage: Create a DialogueImporter class and then call from_gridly() or from_file().

TODO: Describe the scheme.
"""

import json
from pathlib import Path
from typing import Any, Final

import pandas as pd

import _type_helpers
from _gridly_socket import GridlySocket
from dialogue import DialogueLine, is_valid_from_dict

GRIDLY_COLUMN_CHARACTER: Final[str] = "column_CharacterName"
GRIDLY_COLUMN_LANG_PREFIX: Final[tuple[str, ...]] = ("src_", "tg_")


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
            if not _type_helpers.is_dict_str_any(gridly_line):
                continue

            # convert gridly results into a dict
            new_dialogue_line: dict[str, Any] = {}
            new_dialogue_line["translations"] = {}
            all_characters: list[str] = []

            if "id" in gridly_line:
                new_dialogue_line["id"] = gridly_line["id"]
            if "path" in gridly_line and isinstance(gridly_line["path"], str):
                new_dialogue_line = _extract_from_path(gridly_line["path"], new_dialogue_line)
            if "cells" in gridly_line:
                cells = gridly_line["cells"]
                if _type_helpers.is_list_any(cells):
                    for cell in cells:
                        if not _type_helpers.is_dict_str_any(cell):
                            continue
                        if "columnId" in cell and "value" in cell and isinstance(cell["columnId"], str):
                            if cell["columnId"].startswith(GRIDLY_COLUMN_LANG_PREFIX[0]):
                                language = cell["columnId"][len(GRIDLY_COLUMN_LANG_PREFIX[0]) :]
                                new_dialogue_line["translations"][language] = cell["value"]
                            elif cell["columnId"].startswith(GRIDLY_COLUMN_LANG_PREFIX[1]):
                                language = cell["columnId"][len(GRIDLY_COLUMN_LANG_PREFIX[1]) :]
                                new_dialogue_line["translations"][language] = cell["value"]
                            elif cell["columnId"] == GRIDLY_COLUMN_CHARACTER:
                                cell_value = cell["value"]
                                if _type_helpers.is_list_str(cell_value):
                                    all_characters = cell_value

            for character in all_characters:
                char_converted_data: dict[str, Any] = {**new_dialogue_line, "character": character}
                if not is_valid_from_dict(char_converted_data):
                    continue
                line = DialogueLine.from_dict(char_converted_data)
                results.append(line)

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
                return self._from_csv(path)
            case ".xlsx":
                return self._from_xlsx(path)
            case ".json":
                return self._from_json(path)
            case _:
                raise ValueError(f"Unsupported file extension: {suffix}")

    def _from_csv(self, path: Path) -> list[DialogueLine]:
        """Load dialogue lines from a csv file."""
        file = pd.read_csv(path)
        return DialogueLine.load_from_dataframe(file)

    def _from_xlsx(self, path: Path) -> list[DialogueLine]:
        """Load dialogue lines from an excel file."""
        file: pd.DataFrame = pd.read_excel(path)  # pyright: ignore[reportUnknownMemberType] (pandas-stubs leaves an Unknown in the sig)
        return DialogueLine.load_from_dataframe(file)

    def _from_json(self, path: Path) -> list[DialogueLine]:
        """Load dialogue lines from a json file."""
        results: list[DialogueLine] = []
        with open(path) as file:
            data = json.load(file)
            for json_line in data:
                if not is_valid_from_dict(json_line):
                    continue
                line = DialogueLine.from_dict(json_line)
                results.append(line)
        return results


def _extract_from_path(path: str, current_line: dict[str, Any]) -> dict[str, Any]:
    """
    Extract game_area / chapter / scene / game_feature from a Gridly path.

    Matches the specific Gridly setup used in our current database.
    If the path collapses to two segments and the chapter is "Global" (case-insensitive),
    scene is set equal to chapter.

    Returns:
        A copy of `current_line` with the extracted fields populated.
    """
    result: dict[str, Any] = {**current_line}

    paths = path.split("/")
    paths_len = len(paths)
    if paths_len > 0:
        result["game_area"] = paths[0]

    if paths_len > 1:
        result["chapter"] = paths[1]

    if paths_len > 2:
        result["scene"] = paths[2]
    elif paths_len > 1 and result["chapter"].casefold() == "global":
        result["scene"] = result["chapter"]

    if paths_len > 3:
        result["game_feature"] = paths[3]
    else:
        result["game_feature"] = ""

    return result

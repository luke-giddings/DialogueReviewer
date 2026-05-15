"""
DialogueLine dataclass with the validators and converters to create them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NamedTuple, TypedDict, TypeIs

from pandas import DataFrame

import _type_helpers


@dataclass
class DialogueLine:
    """
    A single dialogue line containing all the information associated with it: character speaking, tranlations and pathing information.
    """

    character: str = ""
    translations: dict[str, str] = field(default_factory=dict[str, str])  # Lang -> Text

    # Pathing Info
    id: str = ""
    game_area: str = ""
    chapter: str = ""
    scene: str = ""
    game_feature: str = ""

    @classmethod
    def from_tuple(cls, tuple_line: _DialogueRowTuple) -> DialogueLine:
        """
        Create a dialogue line from a _DialogueRowTuple.
        Params:
            tuple_line : The tuple to convert.
        Returns:
            The new dialogue line.
        """
        translations: dict[str, str] = {}
        for namedfield in tuple_line._fields:
            if namedfield.startswith("text_"):
                lang_id = namedfield[len("text_") :]
                translations[lang_id] = getattr(tuple_line, namedfield)

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
    def from_dict(cls, dict_line: _DialogueRowDict):
        """
        Create a dialogue line from a dictionary.
        Params:
            dict_line : The dictionary to convert.
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

    @staticmethod
    def load_from_dataframe(dataframe: DataFrame) -> list[DialogueLine]:
        """
        Convert all the dialogue lines within a data frame.
        Params:
            dataframe : The DataFrame to convert.
        Returns:
            A list of the new dialogue lines.
        """
        result: list[DialogueLine] = []

        for dialogue_row in dataframe.itertuples(index=False):
            if not is_valid_from_tuple(dialogue_row):
                continue
            line = DialogueLine.from_tuple(dialogue_row)
            result.append(line)

        return result


def is_valid_from_tuple(tuple_line: Any) -> TypeIs[_DialogueRowTuple]:
    """
    Return True if a tuple will be acceptable to convert via from_tuple().
    Params:
        tuple_line : The tuple to validate.
    """

    if not hasattr(tuple_line, "character") or not isinstance(tuple_line.character, str):
        return False
    if not hasattr(tuple_line, "id") or not isinstance(tuple_line.id, str):
        return False
    if not hasattr(tuple_line, "game_area") or not isinstance(tuple_line.game_area, str):
        return False
    if not hasattr(tuple_line, "chapter") or not isinstance(tuple_line.chapter, str):
        return False
    if not hasattr(tuple_line, "scene") or not isinstance(tuple_line.scene, str):
        return False
    if not hasattr(tuple_line, "game_feature") or not isinstance(tuple_line.game_feature, str):
        return False

    # Check for some languages
    has_language = False
    for fieldname in tuple_line._fields:
        if fieldname.startswith("text_"):
            has_language = True
            break

    return has_language


def is_valid_from_dict(dict_line: Any) -> TypeIs[_DialogueRowDict]:
    """
    Return True if a dictionary will be acceptable to convert via from_dict().
    Params:
        dict_line : The dictionary to validate.
    """
    if not isinstance(dict_line, dict):
        return False
    if "character" not in dict_line or not isinstance(dict_line["character"], str):
        return False
    if "id" not in dict_line or not isinstance(dict_line["id"], str):
        return False
    if "game_area" not in dict_line or not isinstance(dict_line["game_area"], str):
        return False
    if "chapter" not in dict_line or not isinstance(dict_line["chapter"], str):
        return False
    if "scene" not in dict_line or not isinstance(dict_line["scene"], str):
        return False
    if "game_feature" not in dict_line or not isinstance(dict_line["game_feature"], str):
        return False
    if "translations" not in dict_line:
        return False
    if not _type_helpers.is_dict_str_str(dict_line["translations"]):
        return False
    return len(dict_line["translations"]) != 0


class _DialogueRowTuple(NamedTuple):
    """Expected shape of a row from DataFrame.itertuples() (CSV/XLSX path)."""

    id: str
    character: str
    game_area: str
    chapter: str
    scene: str
    game_feature: str


class _DialogueRowDict(TypedDict):
    """Expected shape of a row from JSON or Gridly input."""

    id: str
    character: str
    game_area: str
    chapter: str
    scene: str
    game_feature: str
    translations: dict[str, str]

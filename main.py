"""This file is a work in progress. At the moment, any code in here is expected to be thrown away and should be disregarded."""

import logging
import os
import pprint
from pathlib import Path

from dotenv import load_dotenv

from character_bible import BibleImporter
from dialogue import DialogueImporter

load_dotenv()

GRIDLY_VIEW_ID = os.environ["GRIDLY_VIEW_ID"]
GRIDLY_API_KEY = os.environ["GRIDLY_API_KEY"]
TEST_DATA_FOLDER: Path = Path(__file__).parent / "test_data"
LOG_DATA_FOLDER: Path = Path(__file__).parent / "logs"


def main():
    LOG_DATA_FOLDER.mkdir(exist_ok=True)

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=LOG_DATA_FOLDER / "dialogue_reviewer.log", level=logging.INFO)
    logger.info("Program Start")

    # Module 1: Test Dialogue Importer
    # test_module_one()

    # Module 2: Test Bible Importer
    test_module_two()


def test_module_one() -> None:
    """Module 1: Test Dialogue Importer"""
    importer = DialogueImporter()
    gridly_dialogue = importer.from_gridly(GRIDLY_VIEW_ID, GRIDLY_API_KEY)
    json_dialogue = importer.from_file(TEST_DATA_FOLDER / "sample_dialogue.json")
    csv_dialogue = importer.from_file(TEST_DATA_FOLDER / "sample_dialogue.csv")
    xls_dialogue = importer.from_file(TEST_DATA_FOLDER / "sample_dialogue.xlsx")

    pprint.pprint(gridly_dialogue)
    pprint.pprint(json_dialogue)
    pprint.pprint(csv_dialogue)
    pprint.pprint(xls_dialogue)


def test_module_two() -> None:
    """Module 2: Test Bible Importer"""
    bible_importer = BibleImporter()

    character_lib = bible_importer.load_library(TEST_DATA_FOLDER / "sample_character_bible.json")
    if character_lib is not None:
        bible_importer.save_library(TEST_DATA_FOLDER / "sample_library_cpy.json", character_lib)
    pprint.pprint(character_lib)


if __name__ == "__main__":
    main()

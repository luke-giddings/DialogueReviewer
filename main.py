"""This file is a work in progress. At the moment, any code in here is expected to be thrown away and should be disregarded."""

import logging
import os
import pprint
from pathlib import Path

from dotenv import load_dotenv

from dialogue_importer import DialogueImporter

load_dotenv()

GRIDLY_VIEW_ID = os.environ["GRIDLY_VIEW_ID"]
GRIDLY_API_KEY = os.environ["GRIDLY_API_KEY"]


def main():
    test_data_folder: Path = Path(__file__).parent / "test_data"
    log_data_folder: Path = Path(__file__).parent / "logs"

    log_data_folder.mkdir(exist_ok=True)

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_data_folder / "dialogue_reviewer.log", level=logging.INFO)
    logger.info("Program Start")

    importer: DialogueImporter = DialogueImporter()

    gridly_dialogue = importer.from_gridly(GRIDLY_VIEW_ID, GRIDLY_API_KEY)
    json_dialogue = importer.from_file(test_data_folder / "sample_dialogue.json")
    csv_dialogue = importer.from_file(test_data_folder / "sample_dialogue.csv")
    xls_dialogue = importer.from_file(test_data_folder / "sample_dialogue.xlsx")

    pprint.pprint(gridly_dialogue)
    pprint.pprint(json_dialogue)
    pprint.pprint(csv_dialogue)
    pprint.pprint(xls_dialogue)


if __name__ == "__main__":
    main()

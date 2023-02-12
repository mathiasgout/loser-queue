from src import logger
from src import config
from src.tools.error_tools import exception
from src.tools import api_tools, basic_tools

import os
import json
import pathlib


DATA_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data"
)


@exception(logger)
def create_json_file():

    settings = config.get_settings()

    for tier in settings.TIERS:
        if tier not in [
            "CHALLENGER",
            "GRANDMASTER",
            "MASTER",
            "DIAMOND",
            "PLATINUM",
            "GOLD",
            "SILVER",
            "BRONZE",
            "IRON",
        ]:
            raise ValueError(f"'tier': '{tier}' does not exist")

    # Create "data" folder
    pathlib.Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)

    for tier in settings.TIERS:
        matches_with_tier = api_tools.get_a_sample_of_matches(
            tier=tier, number_of_matches=settings.NUMBER_OF_MATCHES_BY_TIER
        )
        infos = api_tools.extract_infos_from_matches(
            matches_with_tier=matches_with_tier
        )

        file_path = os.path.join(
            DATA_FOLDER,
            f"data_{tier}_{len(infos)}_{basic_tools.get_timestamp_utc()}.json",
        )
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(infos, f, ensure_ascii=False)
            logger.info(
                f"Data of the 'tier': '{tier}' ({len(infos)} matches) are located in file with path: '{file_path}'"
            )

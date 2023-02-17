import os
import ast
from configparser import ConfigParser


CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config.ini")

def get_config(filename="config.ini", section="default"):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    return config


config = get_config(filename=CONFIG_FILE_PATH)

class Settings:
    """Base config"""

    TIERS: list = ast.literal_eval(config["tiers"])
    NUMBER_OF_MATCHES_BY_TIER: int = int(config["number_of_matches_by_tier"])


def get_settings():
    """Returns the bot settings
    Returns:
        Settings: the bot settings
    """
    return Settings()

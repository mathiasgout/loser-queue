class Settings:
    """Base config"""

    # Possible values for "tiers" to add in the list : "DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"
    TIERS: list = ["CHALLENGER", "GRANDMASTER", "MASTER"]
    NUMBER_OF_MATCHES_BY_TIER: int = 300


def get_settings():
    """Returns the bot settings
    Returns:
        Settings: the bot settings
    """
    return Settings()

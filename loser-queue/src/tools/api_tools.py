from src import logger
from src.tools.error_tools import (
    exception,
    retry,
    NotWaitableHttpError,
    WaitableHttpError,
)

import os
import random
from typing import List, Dict, Union

import dotenv
import requests


ENV_FILE_FOLDER = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
dotenv.load_dotenv(os.path.join(ENV_FILE_FOLDER, ".env"))


@exception(logger)
def get_api_key() -> str:
    """Returns the Riot API Key that is stored in the 'loser-queue/src/.env' file

    Returns:
        str: Riot API Key
    """
    return os.environ.get("API_KEY")


@exception(logger)
@retry(requests.exceptions.ConnectionError, tries=9000, delay=10, backoff=1, logger=logger)
@retry(WaitableHttpError, tries=3000, delay=30, backoff=1, logger=logger)
def get_summoner_from_summoner_name(summoner_name: str) -> dict:
    """Returns Summoner's dict from summoner's name

    Args:
        summoner_name (str): summoner's name

    Raises:
        WaitableHttpError: HTTP code >= 429
        NotWaitableHttpError: HTTP code >= 400 and HTTP code < 429

    Returns:
        dict: Summoner's infos in a dict
    """
    api_key = get_api_key()
    params = {"api_key": api_key}
    r_get = requests.get(
        f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name.lower()}",
        params=params,
    )
    if r_get.ok:
        logger.info(f"Summoner with name: '{summoner_name}' extracted")
        return r_get.json()

    if r_get.status_code >= 429:
        logger.warning(
            f"WaitableHttpError ({r_get.status_code}). Summoner with name: '{summoner_name}' can not be extracted"
        )
        raise WaitableHttpError(f"HTTP {r_get.status_code}")

    logger.warning(
        f"NotWaitableHttpError ({r_get.status_code}). Summoner with name: '{summoner_name}' can not be extracted."
    )
    raise NotWaitableHttpError(f"HTTP {r_get.status_code}")


@exception(logger)
@retry(requests.exceptions.ConnectionError, tries=9000, delay=10, backoff=1, logger=logger)
@retry(WaitableHttpError, tries=3000, delay=30, backoff=1, logger=logger)
def get_active_entry_from_rank(page: int, tier: str, division: str) -> List[dict]:
    """Returns a list of active entries from a rank

    Args:
        page (int): the page
        tier (str): the tier (DIAMOND, PLATINUM, MASTER, ...)
        division (str): the division (I, II, III, IV)

    Raises:
        WaitableHttpError: HTTP code >= 429
        NotWaitableHttpError: HTTP code >= 400 and HTTP code < 429

    Returns:
        List[dict]: a list of entries
    """
    api_key = get_api_key()

    queue = "RANKED_SOLO_5x5"
    params = {"api_key": api_key, "page": page}
    r_get = requests.get(
        f"https://euw1.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}",
        params=params,
    )
    if r_get.ok:
        entries = [entry for entry in r_get.json() if entry["inactive"] is False]
        logger.info(
            f"Entries ({len(entries)}) of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' extracted"
        )
        return entries

    if r_get.status_code >= 429:
        logger.warning(
            f"WaitableHttpError ({r_get.status_code}). Entries of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' can not be extracted"
        )
        raise WaitableHttpError(f"HTTP {r_get.status_code}")

    logger.warning(
        f"NotWaitableHttpError ({r_get.status_code}). Entries of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' can not be extracted"
    )
    raise NotWaitableHttpError(f"HTTP {r_get.status_code}")


@exception(logger)
@retry(requests.exceptions.ConnectionError, tries=9000, delay=10, backoff=1, logger=logger)
@retry(WaitableHttpError, tries=3000, delay=30, backoff=1, logger=logger)
def get_match_ids_from_summoner_puuid(
    summoner_puuid: str, limit: int = 20
) -> List[str]:
    """Returns a list of summoner's Match ID from the summoner's PUUID

    Args:
        summoner_puuid (str): summoner's PUUID
        limit (int, optional): number of Match ID to extract. Defaults to 20.

    Raises:
        WaitableHttpError: HTTP code >= 429
        NotWaitableHttpError: HTTP code >= 400 and HTTP code < 429

    Returns:
        List[str]: a list of summoner's Match ID
    """
    api_key = get_api_key()
    params = {
        "api_key": api_key,
        "count": limit,
        "queue": 420,
        "type": "ranked",
    }  # queue=420 -> ranked 5V5
    r_get = requests.get(
        f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids",
        params=params,
    )
    if r_get.ok:
        match_ids = r_get.json()
        logger.info(
            f"Match IDs ({len(match_ids)}) of Summoner with puuid: {summoner_puuid} extracted"
        )
        return match_ids

    if r_get.status_code >= 429:
        logger.warning(
            f"WaitableHttpError ({r_get.status_code}). Match IDs of Summoner with puuid: {summoner_puuid} can not be extracted"
        )
        raise WaitableHttpError(f"HTTP {r_get.status_code}")

    logger.warning(
        f"NotWaitableHttpError ({r_get.status_code}). Match IDs of Summoner with puuid: {summoner_puuid} can not be extracted"
    )
    raise NotWaitableHttpError(f"HTTP {r_get.status_code}")


@exception(logger)
@retry(requests.exceptions.ConnectionError, tries=9000, delay=10, backoff=1, logger=logger)
@retry(WaitableHttpError, tries=3000, delay=30, backoff=1, logger=logger)
def get_match_from_match_id(match_id: str) -> dict:
    """Returns the dict of a Match from a Match ID

    Args:
        match_id (str): Match ID

    Raises:
        RateLimitError: HTTP code >= 429
        NotWaitableHttpError: HTTP code >= 400 and HTTP code < 429

    Returns:
        dict: the dict of a Match
    """
    api_key = get_api_key()
    params = {"api_key": api_key}
    r_get = requests.get(
        f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}",
        params=params,
    )
    if r_get.ok:
        logger.info(f"Match with ID: {match_id} extracted")
        return r_get.json()

    if r_get.status_code >= 429:
        logger.warning(
            f"WaitableHttpError ({r_get.status_code}). Match with ID: {match_id} can not be extracted"
        )
        raise WaitableHttpError(f"HTTP {r_get.status_code}")

    logger.warning(
        f"NotWaitableHttpError ({r_get.status_code}). Match with ID: {match_id} can not be extracted"
    )
    raise NotWaitableHttpError(f"HTTP {r_get.status_code}")


@exception(logger)
def extract_puuid_from_summoner(summoner: dict) -> str:
    """Extracts summoner's PUUID from summoner's dict

    Args:
        summoner (dict): summoner's dict

    Returns:
        str: summoner's puuid
    """
    return summoner["puuid"]


@exception(logger)
def extract_summoner_name_from_entry(entry: dict) -> str:
    """Extracts summoner's name from entry dict

    Args:
        entry (dict): entry dict

    Returns:
        str: summoner's name
    """
    return entry["summonerName"]


@exception(logger)
def extract_match_id_from_match(match: dict) -> str:
    """Extracts Match ID from match dict

    Args:
        match (dict): match dict

    Returns:
        str: Match ID
    """
    metadata = match["metadata"]
    return metadata["matchId"]


@exception(logger)
def extract_match_result_from_match(
    match: dict, summoner_puuid: str
) -> Union[None, str]:
    """Extracts summoner's result from a match dict and summoner's PUUID

    Args:
        match (dict): match dict
        summoner_puuid (str): summoner's puuid

    Returns:
        Union[None, str]: None or 'victory' or 'defeat'
    """
    if summoner_puuid not in match["metadata"]["participants"]:
        logger.warning(f"Summoner with puuid: {summoner_puuid} was not in this match")
        return None

    infos = match["info"]
    for participant in infos["participants"]:
        if participant["puuid"] == summoner_puuid:
            if participant["win"] is True:
                return "victory"
            return "defeat"


@exception(logger)
def extract_team_id_from_match(match: dict, summoner_puuid: str) -> Union[None, str]:
    """Extracts summoner's team ID from a match dict and summoner's PUUID

    Args:
        match (dict): match dict
        summoner_puuid (str): summoner's PUUID

    Returns:
        Union[None, str]: None or 'team_100' or 'team_200'
    """
    if summoner_puuid not in match["metadata"]["participants"]:
        logger.warning(f"Summoner with puuid: {summoner_puuid} was not in this match")
        return None

    infos = match["info"]
    for participant in infos["participants"]:
        if participant["puuid"] == summoner_puuid:
            return f'team_{participant["teamId"]}'


@exception(logger)
def extract_participants_puuid_from_match(match: dict) -> List[str]:
    """Extracts a list of participant's PUUID from a match dict

    Args:
        match (dict): match dict

    Returns:
        List[str]: list of participant's PUUID
    """
    metadata = match["metadata"]
    return metadata["participants"]


@exception(logger)
def get_summoner_names_from_tier(tier: str, number: int) -> List[str]:
    """Returns a list of summoner names from a tier

    Args:
        tier (str): a tier (DIAMOND, PLATINUM, MASTER, ...)
        number (int): the size of the list

    Returns:
        List[str]: list of summoner names
    """
    divisions = ["I", "II", "III", "IV"]
    entries = []
    summoner_names = []
    if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
        for i in range(1, 100):
            entries_packaged = get_active_entry_from_rank(page=i, tier=tier, division="I")

            if entries_packaged:
                entries.extend(entries_packaged)
            else:
                break
    else:
        for division in divisions:
            for i in range(1, 100):
                entries_packaged = get_active_entry_from_rank(page=i, tier=tier, division=division)

                if entries_packaged:
                    entries.extend(entries_packaged)
                else:
                    break

    # Random sample of entries
    entries_selected = random.sample(entries, k=min(number, len(entries)))
    
    # Extract summoners names
    for entry in entries_selected:
        summoner_names.append(extract_summoner_name_from_entry(entry=entry))

    return summoner_names


@exception(logger)
def get_last_matches_of_summoner_by_puuid(
    summoner_puuid: str, number_of_matches: int, max_match_id: Union[None, str] = None
) -> List[dict]:
    """Returns a list of the latest matches of a summoner from the summoner's PUUID

    Args:
        summoner_puuid (str): summoner's PUUID
        number_of_matches (int): number of matches to extract
        max_match_id (Union[None, str], optional): extracted match ID older than this match ID. Defaults to None.

    Returns:
        List[dict]: list of the latest matches
    """
    if max_match_id:
        max_id = int(max_match_id.split("_")[1])
        all_match_ids = get_match_ids_from_summoner_puuid(
            summoner_puuid=summoner_puuid, limit=100
        )
        limit_reached = False
        for i, match_id in enumerate(all_match_ids):
            if int(match_id.split("_")[1]) < max_id:
                match_ids = all_match_ids[i : (i + number_of_matches)]
                limit_reached = True
                break

        if not limit_reached:
            match_ids = []
    else:
        match_ids = get_match_ids_from_summoner_puuid(
            summoner_puuid=summoner_puuid, limit=number_of_matches
        )

    matches = []
    for match_id in match_ids:
        match = get_match_from_match_id(match_id=match_id)
        matches.append(match)
    return matches


@exception(logger)
def get_last_matches_of_summoner_by_summoner_name(
    summoner_name: str, number_of_matches: int, max_match_id: Union[None, str] = None
) -> List[dict]:
    """Returns a list of the latest matches of a summoner from the summoner's name

    Args:
        summoner_puuid (str): summoner's name
        number_of_matches (int): number of matches to extract
        max_match_id (Union[None, str], optional): extracted match ID older than this match ID. Defaults to None.

    Returns:
        List[dict]: list of the latest matches
    """
    try:
        summoner = get_summoner_from_summoner_name(summoner_name=summoner_name)
        summoner_puuid = extract_puuid_from_summoner(summoner=summoner)
    except NotWaitableHttpError as e:
        return []

    return get_last_matches_of_summoner_by_puuid(
        summoner_puuid=summoner_puuid,
        number_of_matches=number_of_matches,
        max_match_id=max_match_id,
    )


@exception(logger)
def get_matches_of_a_tier(tier: str, number_of_matches: int) -> List[Dict[str, dict]]:
    """Returns a list of matches of a tier (with tier)

    Args:
        tier (str): a tier (DIAMOND, PLATINUM, MASTER, ...)
        number_of_matches (int): number of matches to get

    Returns:
        List[Dict[str, dict]]: list of matches of a tier (with tier)
    """
    summoner_names = get_summoner_names_from_tier(tier=tier, number=number_of_matches)

    # If len(summoner_names) < number_of_matches, extract more than 1 game by summoner
    matches = []
    size_summoner_names = len(summoner_names) 
    if size_summoner_names < number_of_matches:
        remainder = number_of_matches % size_summoner_names
        floor = number_of_matches // size_summoner_names
        for i in range(remainder):
            matches_packaged = get_last_matches_of_summoner_by_summoner_name(summoner_name=summoner_names[i], number_of_matches=floor+1)
            matches.extend(matches_packaged)
        for i in range(remainder, size_summoner_names):
            match = get_last_matches_of_summoner_by_summoner_name(summoner_name=summoner_names[i], number_of_matches=1)
            matches.extend(match)

    else:
        for summoner_name in summoner_names:
            match = get_last_matches_of_summoner_by_summoner_name(
                summoner_name=summoner_name, number_of_matches=1
            )
            matches.extend(match)

    matches_with_tier = []
    for match in matches:
        matches_with_tier.append({"tier": tier, "match": match})

    logger.info(f"Matches ({len(matches_with_tier)}) of 'tier': '{tier}' extracted")
    return matches_with_tier


@exception(logger)
def get_a_sample_of_matches(
    tier: str, number_of_matches: int = 300
) -> List[Dict[str, dict]]:
    """Returns a list of unique matches of a tier (with tier)

    Args:
        tier (str): a tier (DIAMOND, PLATINUM, MASTER, ...)
        number_of_matches (int, optional): number of matches to get. Defaults to 300.

    Returns:
        List[Dict[str, dict]]: list of unique matches of a tier (with tier)
    """

    matches_with_tier = get_matches_of_a_tier(
        tier=tier, number_of_matches=number_of_matches
    )

    match_ids = []
    matches_with_tier_unique = []
    for match_with_tier in matches_with_tier:
        match_id = extract_match_id_from_match(match_with_tier["match"])
        if match_id not in match_ids:
            matches_with_tier_unique.append(match_with_tier)
            match_ids.append(match_id)

    logger.info(
        f"Matches unique ({len(matches_with_tier_unique)}) of 'tier': '{tier}' extracted (missing {number_of_matches - len(matches_with_tier_unique)})"
    )
    return matches_with_tier_unique


@exception(logger)
def extract_infos_from_match(match_with_tier: dict) -> dict:
    """Returns informations from a match with tier

    Args:
        match_with_tier (dict): match with tier

    Returns:
        dict: informations from the match
    """
    match_id = extract_match_id_from_match(match=match_with_tier["match"])
    participants_puuid = extract_participants_puuid_from_match(
        match=match_with_tier["match"]
    )

    infos = {
        "match_id": match_id,
        "tier": match_with_tier["tier"],
        "team_100": [],
        "team_200": [],
    }
    for participant_puuid in participants_puuid:
        team_id = extract_team_id_from_match(
            match=match_with_tier["match"], summoner_puuid=participant_puuid
        )
        participant_infos = {
            "participant_puuid": participant_puuid,
            "previous_matches": [],
        }

        previous_matches = get_last_matches_of_summoner_by_puuid(
            summoner_puuid=participant_puuid,
            number_of_matches=20,
            max_match_id=match_id,
        )
        for previous_match in previous_matches:
            previous_match_info = {
                "match_id": extract_match_id_from_match(match=previous_match),
                "result": extract_match_result_from_match(
                    match=previous_match, summoner_puuid=participant_puuid
                ),
            }

            participant_infos["previous_matches"].append(previous_match_info)

        infos[team_id].append(participant_infos)

    return infos


@exception(logger)
def extract_infos_from_matches(matches_with_tier: List[dict]) -> List[dict]:
    """Returns informations from a list of matches with tier

    Args:
        matches_with_tier (List[dict]): list of matches with tier

    Returns:
        List[dict]: list of informations from the matches
    """
    infos_from_matches = []
    for match_with_tier in matches_with_tier:
        infos_from_matches.append(
            extract_infos_from_match(match_with_tier=match_with_tier)
        )

    return infos_from_matches

from src import logger
from src.tools.error_tools import exception, retry, CustomHttpError, RateLimitError

import os
import math
from typing import List, Dict

import dotenv
import requests


ENV_FILE_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
dotenv.load_dotenv(os.path.join(ENV_FILE_FOLDER, ".env"))


@exception(logger)
def get_api_key():
    return os.environ.get("API_KEY")


@exception(logger)
@retry(RateLimitError, tries=3000, delay=30, backoff=1, logger=logger)
def get_summoner_from_summoner_name(summoner_name: str) -> dict:
    api_key = get_api_key()
    params = {"api_key": api_key}
    r_get = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name.lower()}", params=params)
    if r_get.ok:
        logger.info(f"Summoner with name: '{summoner_name}' extracted")
        return r_get.json()
    
    if r_get.status_code == 429:
        logger.warning(f"RateLimitError. Summoner with name: '{summoner_name}' can not be extracted")
        raise RateLimitError

    logger.warning(f"Summoner with name: '{summoner_name}' can not be extracted, request status : {r_get.status_code}")
    raise CustomHttpError(status_code=r_get.status_code)


@exception(logger)
@retry(RateLimitError, tries=3000, delay=30, backoff=1, logger=logger)
def get_active_entry_by_ranking(page: int, tier: str, division: str):
    api_key = get_api_key()
    
    queue = "RANKED_SOLO_5x5"
    params = {"api_key": api_key, "page": page}
    r_get = requests.get(f"https://euw1.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}", params=params)
    if r_get.ok:
        entries = [entry for entry in r_get.json() if entry["inactive"] is False]
        logger.info(f"Entries ({len(entries)}) of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' extracted")
        return entries

    if r_get.status_code == 429:
        logger.warning(f"RateLimitError. Entries of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' can not be extracted")
        raise RateLimitError
        
    logger.warning(f"Entries of 'queue': '{queue}', 'tier': '{tier}', 'division': '{division}' can not be extracted, request status : {r_get.status_code}")
    raise CustomHttpError(status_code=r_get.status_code)


@exception(logger)
@retry(RateLimitError, tries=3000, delay=30, backoff=1, logger=logger)
def get_match_ids_by_puuid(summoner_puuid: str, limit: int = 20):
    api_key = get_api_key()
    params = {"api_key": api_key, "count": limit, "queue": 420, "type": "ranked"} # queue=420 -> ranked 5V5
    r_get = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids", params=params)
    if r_get.ok:
        match_ids = r_get.json()
        logger.info(f"Match IDs ({len(match_ids)}) of Summoner with puuid: {summoner_puuid} extracted")
        return match_ids
    
    if r_get.status_code == 429:
        logger.warning(f"RateLimitError. Match IDs of Summoner with puuid: {summoner_puuid} can not be extracted")
        raise RateLimitError

    logger.warning(f"Match IDs of Summoner with puuid: {summoner_puuid} can not be extracted, request status : {r_get.status_code}")
    raise CustomHttpError(status_code=r_get.status_code)


@exception(logger)
@retry(RateLimitError, tries=3000, delay=30, backoff=1, logger=logger)
def get_match_by_match_id(match_id: str):
    api_key = get_api_key()
    params = {"api_key": api_key}
    r_get = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}", params=params)
    if r_get.ok:
        logger.info(f"Match with ID: {match_id} extracted")
        return r_get.json()

    if r_get.status_code == 429:
        logger.warning(f"RateLimitError. Match with ID: {match_id} can not be extracted")
        raise RateLimitError

    logger.warning(f"Match with ID: {match_id} can not be extracted, request status : {r_get.status_code}")
    raise CustomHttpError(status_code=r_get.status_code)


@exception(logger)
def extract_puuid_from_summoner(summoner):
    return summoner["puuid"]


@exception(logger)
def extract_summoner_name_from_entry(entry):
    return entry["summonerName"]


@exception(logger)
def extract_match_id_from_match(match):
    metadata = match["metadata"]
    return metadata["matchId"]


@exception(logger)
def extract_match_result_from_match(match, summoner_puuid: str):
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
def extract_team_id_from_match(match, summoner_puuid: str):
    if summoner_puuid not in match["metadata"]["participants"]:
        logger.warning(f"Summoner with puuid: {summoner_puuid} was not in this match")
        return None

    infos = match["info"]
    for participant in infos["participants"]:
        if participant["puuid"] == summoner_puuid:
            return f'team_{participant["teamId"]}'


@exception(logger)
def extract_participants_puuid_from_match(match):
    metadata = match["metadata"]
    return metadata["participants"]


@exception(logger)
def get_summoner_names_from_tier(tier: str, number: int):
    number_by_division = math.ceil(number/4)

    divisions = ["I", "II", "III", "IV"]
    summoner_names = []
    if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
        page = 1
        while len(summoner_names) < number:
            entries = get_active_entry_by_ranking(page=page, tier=tier, division="I")
            
            # If no more entries
            if not entries:
                return summoner_names

            for entry in entries:
                if len(summoner_names) >= number:
                    break
                summoner_names.append(extract_summoner_name_from_entry(entry=entry))
            page += 1
    else:
        for division in divisions:
            summoner_names_division = []
            page = 1
            while len(summoner_names_division) < number_by_division:
                entries = get_active_entry_by_ranking(page=page, tier=tier, division=division)
                
                # If no more entries
                if not entries:
                    return summoner_names
                
                for entry in entries:
                    if len(summoner_names_division) >= number_by_division:
                        break
                    summoner_names_division.append(extract_summoner_name_from_entry(entry=entry))
                page += 1
            summoner_names.extend(summoner_names_division)
    return summoner_names


@exception(logger)
def get_last_matches_of_summoner_by_puuid(summoner_puuid: str, number_of_matches: int, max_match_id = None):
    if max_match_id:
        max_id = int(max_match_id.split("_")[1])
        all_match_ids = get_match_ids_by_puuid(summoner_puuid=summoner_puuid, limit=100)
        limit_reached = False
        for i, match_id in enumerate(all_match_ids):
            if int(match_id.split("_")[1]) < max_id:
                match_ids = all_match_ids[i:(i+number_of_matches)]
                limit_reached = True
                break

        if not limit_reached:
            match_ids = []
    else:
        match_ids = get_match_ids_by_puuid(summoner_puuid=summoner_puuid, limit=number_of_matches)

    matches = []
    for match_id in match_ids:
        match = get_match_by_match_id(match_id=match_id)
        matches.append(match)
    return matches


@exception(logger)
def get_last_matches_of_summoner_by_summoner_name(summoner_name: str, number_of_matches: int, max_match_id = None):
    summoner = get_summoner_from_summoner_name(summoner_name=summoner_name)
    summoner_puuid = extract_puuid_from_summoner(summoner=summoner)

    return get_last_matches_of_summoner_by_puuid(summoner_puuid=summoner_puuid, number_of_matches=number_of_matches, max_match_id=max_match_id)


@exception(logger)
def get_matches_of_a_tier(tier: str, number_of_matches: int) -> List[Dict[str, dict]]:
    summoner_names = get_summoner_names_from_tier(tier=tier, number=number_of_matches)

    matches = []
    for summoner_name in summoner_names:
        match = get_last_matches_of_summoner_by_summoner_name(summoner_name=summoner_name, number_of_matches=1)
        matches.extend(match)

    matches_with_tier = []
    for match in matches:
        matches_with_tier.append({"tier": tier, "match": match})

    logger.info(f"Matches ({len(matches_with_tier)}) of 'tier': '{tier}' extracted")
    return matches_with_tier


@exception(logger)
def get_a_sample_of_matches(tier: str, number_of_matches: int = 300):

    matches_with_tier = get_matches_of_a_tier(tier=tier, number_of_matches=number_of_matches)
    
    match_ids = []
    matches_with_tier_unique = []
    for match_with_tier in matches_with_tier:
        match_id = extract_match_id_from_match(match_with_tier["match"])
        if match_id not in match_ids:
            matches_with_tier_unique.append(match_with_tier)
        else:
            match_ids.append(match_id)

    logger.info(f"Matches unique ({len(matches_with_tier_unique)}) of 'tier': '{tier}' extracted (missing {number_of_matches - len(matches_with_tier_unique)})")
    return matches_with_tier_unique


@exception(logger)
def extract_infos_from_match(match_with_tier: dict):
    match_id = extract_match_id_from_match(match=match_with_tier["match"])
    participants_puuid = extract_participants_puuid_from_match(match=match_with_tier["match"])

    infos = {"match_id": match_id, "tier": match_with_tier["tier"], "team_100": [], "team_200": []}
    for participant_puuid in participants_puuid:
        team_id = extract_team_id_from_match(match=match_with_tier["match"], summoner_puuid=participant_puuid)
        participant_infos = {"participant_puuid": participant_puuid, "previous_matches": []}

        previous_matches = get_last_matches_of_summoner_by_puuid(summoner_puuid=participant_puuid, number_of_matches=20, max_match_id=match_id)
        for previous_match in previous_matches:
            previous_match_info = {"match_id": extract_match_id_from_match(match=previous_match), "result": extract_match_result_from_match(match=previous_match, summoner_puuid=participant_puuid)}
            
            participant_infos["previous_matches"].append(previous_match_info)
        
        infos[team_id].append(participant_infos)

    return infos


@exception(logger)
def extract_infos_from_matches(matches_with_tier: List[dict]):
    infos_from_matches = []
    for match_with_tier in matches_with_tier:
        infos_from_matches.append(extract_infos_from_match(match_with_tier=match_with_tier))
    
    return infos_from_matches
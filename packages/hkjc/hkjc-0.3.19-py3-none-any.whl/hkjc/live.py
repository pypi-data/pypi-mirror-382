"""Functions to fetch and process data from HKJC
"""
from __future__ import annotations
from typing import Tuple, List

import requests
from cachetools.func import ttl_cache
import numpy as np

HKJC_LIVEODDS_ENDPOINT = "https://info.cld.hkjc.com/graphql/base/"

RACEMTG_PAYLOAD = {
    "operationName": "raceMeetings",
    "variables": {"date": None, "venueCode": None},
    "query": """
    fragment raceFragment on Race {
    id
    no
    status
    raceName_en
    raceName_ch
    postTime
    country_en
    country_ch
    distance
    wageringFieldSize
    go_en
    go_ch
    ratingType
    raceTrack {
        description_en
        description_ch
    }
    raceCourse {
        description_en
        description_ch
        displayCode
    }
    claCode
    raceClass_en
    raceClass_ch
    judgeSigns {
        value_en
    }
    }

    fragment racingBlockFragment on RaceMeeting {
    jpEsts: pmPools(
        oddsTypes: [WIN, PLA, TCE, TRI, FF, QTT, DT, TT, SixUP]
        filters: ["jackpot", "estimatedDividend"]
    ) {
        leg {
        number
        races
        }
        oddsType
        jackpot
        estimatedDividend
        mergedPoolId
    }
    poolInvs: pmPools(
        oddsTypes: [WIN, PLA, QIN, QPL, CWA, CWB, CWC, IWN, FCT, TCE, TRI, FF, QTT, DBL, TBL, DT, TT, SixUP]
    ) {
        id
        leg {
        races
        }
    }
    penetrometerReadings(filters: ["first"]) {
        reading
        readingTime
    }
    hammerReadings(filters: ["first"]) {
        reading
        readingTime
    }
    changeHistories(filters: ["top3"]) {
        type
        time
        raceNo
        runnerNo
        horseName_ch
        horseName_en
        jockeyName_ch
        jockeyName_en
        scratchHorseName_ch
        scratchHorseName_en
        handicapWeight
        scrResvIndicator
    }
    }

    query raceMeetings($date: String, $venueCode: String) {
    timeOffset {
        rc
    }
    activeMeetings: raceMeetings {
        id
        venueCode
        date
        status
        races {
        no
        postTime
        status
        wageringFieldSize
        }
    }
    raceMeetings(date: $date, venueCode: $venueCode) {
        id
        status
        venueCode
        date
        totalNumberOfRace
        currentNumberOfRace
        dateOfWeek
        meetingType
        totalInvestment
        country {
        code
        namech
        nameen
        seq
        }
        races {
        ...raceFragment
        runners {
            id
            no
            standbyNo
            status
            name_ch
            name_en
            horse {
            id
            code
            }
            color
            barrierDrawNumber
            handicapWeight
            currentWeight
            currentRating
            internationalRating
            gearInfo
            racingColorFileName
            allowance
            trainerPreference
            last6run
            saddleClothNo
            trumpCard
            priority
            finalPosition
            deadHeat
            winOdds
            jockey {
            code
            name_en
            name_ch
            }
            trainer {
            code
            name_en
            name_ch
            }
        }
        }
        obSt: pmPools(oddsTypes: [WIN, PLA]) {
        leg {
            races
        }
        oddsType
        comingleStatus
        }
        poolInvs: pmPools(
        oddsTypes: [WIN, PLA, QIN, QPL, CWA, CWB, CWC, IWN, FCT, TCE, TRI, FF, QTT, DBL, TBL, DT, TT, SixUP]
        ) {
        id
        leg {
            number
            races
        }
        status
        sellStatus
        oddsType
        investment
        mergedPoolId
        lastUpdateTime
        }
        ...racingBlockFragment
        pmPools(oddsTypes: []) {
        id
        }
        jkcInstNo: foPools(oddsTypes: [JKC], filters: ["top"]) {
        instNo
        }
        tncInstNo: foPools(oddsTypes: [TNC], filters: ["top"]) {
        instNo
        }
    }
    }
"""}

LIVEODDS_PAYLOAD = {
    "operationName": "racing",
    "variables": {"date": None, "venueCode": None, "raceNo": None, "oddsTypes": None},
    "query": """
query racing($date: String, $venueCode: String, $oddsTypes: [OddsType], $raceNo: Int) {
    raceMeetings(date: $date, venueCode: $venueCode) {
        pmPools(oddsTypes: $oddsTypes, raceNo: $raceNo) {
            id
            status
            sellStatus
            oddsType
            lastUpdateTime
            guarantee
            minTicketCost
            name_en
            name_ch
            leg {
                number
                races
            }
            cWinSelections {
                composite
                name_ch
                name_en
                starters
            }
            oddsNodes {
                combString
                oddsValue
                hotFavourite
                oddsDropValue
                bankerOdds {
                    combString
                    oddsValue
                }
            }
        }
    }
}""",
}


@ttl_cache(maxsize=12, ttl=1000)
def _fetch_live_races(date: str=None, venue_code: str=None) -> dict:
    """Fetch live race data from HKJC GraphQL endpoint."""
    payload = RACEMTG_PAYLOAD.copy()
    payload["variables"] = payload["variables"].copy()
    payload["variables"]["date"] = date
    payload["variables"]["venueCode"] = venue_code

    headers = {
        "Origin": "https://bet.hkjc.com",
        "Referer": "https://bet.hkjc.com",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "python-hkjc-fetch/0.1",
    }

    r = requests.post(HKJC_LIVEODDS_ENDPOINT, json=payload,
                      headers=headers, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"Request failed: {r.status_code} - {r.text}")

    data = r.json()['data']['raceMeetings'][0]
    races = data['races']

    race_info = {'Date': data['date'], 'Venue': data['venueCode'], 'Races': {}}
    for race in races:
        race_num = race['no']
        race_name = race['raceName_en']
        race_dist = race['distance']
        race_going = race['go_en']
        race_track = race['raceTrack']['description_en']
        race_class = race['raceClass_en']
        race_course = race['raceCourse']['displayCode']

        runners = [{'No': runner['no'],
                    'Name': runner['name_en'],
                    'Dr': runner['barrierDrawNumber'],
                    'Rtg': int(runner['currentRating']),
                    'Wt': int(runner['currentWeight']),
                    'Handicap': int(runner['handicapWeight']),
                    'HorseNo': runner['horse']['code']
                    } for runner in race['runners'] if runner['status'] != "Standby"]
        race_info['Races'][race_num] = {
            'No': race_num,
            'Name': race_name,
            'Class': race_class,
            'Course': race_course,
            'Dist': race_dist,
            'Going': race_going,
            'Track': race_track,
            'Runners': runners
        }
    return race_info


@ttl_cache(maxsize=12, ttl=30)
def _fetch_live_odds(date: str, venue_code: str, race_number: int, odds_type: Tuple[str] = ('PLA', )) -> List[dict]:
    """Fetch live odds data from HKJC GraphQL endpoint."""
    payload = LIVEODDS_PAYLOAD.copy()
    payload["variables"] = payload["variables"].copy()
    payload["variables"]["date"] = date
    payload["variables"]["venueCode"] = venue_code
    payload["variables"]["raceNo"] = race_number
    payload["variables"]["oddsTypes"] = odds_type

    headers = {
        "Origin": "https://bet.hkjc.com",
        "Referer": "https://bet.hkjc.com",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "python-hkjc-fetch/0.1",
    }

    r = requests.post(HKJC_LIVEODDS_ENDPOINT, json=payload,
                      headers=headers, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"Request failed: {r.status_code} - {r.text}")

    meetings = r.json().get("data", {}).get("raceMeetings", [])

    return [
        {"HorseID": node["combString"], "Type": pool.get(
            "oddsType"), "Odds": float(node["oddsValue"])}
        for meeting in meetings
        for pool in meeting.get("pmPools", [])
        for node in pool.get("oddsNodes", [])
    ]


def live_odds(date: str, venue_code: str, race_number: int, odds_type: List[str] = ['WIN', 'PLA', 'QPL', 'QIN']) -> dict:
    """Fetch live odds as numpy arrays.

    Args:
        date (str): Date in 'YYYY-MM-DD' format.
        venue_code (str): Venue code, e.g., 'ST' for Shatin, 'HV' for Happy Valley.
        race_number (int): Race number.
        odds_type (List[str]): Types of odds to fetch. Default is ['WIN', 'PLA', 'QPL', 'QIN']. Currently the following types are supported:
            - 'WIN': Win odds
            - 'PLA': Place odds
            - 'QIN': Quinella odds
            - 'QPL': Quinella Place odds
        fit_harville (bool): Whether to fit the odds using Harville model. Default is False.

    Returns:
        dict: Dictionary with keys as odds types and values as numpy arrays containing the odds.
            If odds_type is 'WIN','PLA', returns a 1D array of place odds.
            If odds_type is 'QIN','QPL', returns a 2D array of quinella place odds. 
    """
    race_info = _fetch_live_races(date, venue_code)
    N = len(race_info['Races'][race_number]['Runners'])

    if (race_info['Date'] != date) or (race_info['Venue'] != venue_code):
        print(f"[WARNING] Requested {date} {venue_code} but server returned {race_info['Date']} {race_info['Venue']}.")
        date = race_info['Date']
        venue_code = race_info['Venue']

    data = _fetch_live_odds(date, venue_code, race_number,
                            odds_type=tuple(odds_type))

    odds = {'WIN': np.full(N, np.nan, dtype=float),
            'PLA': np.full(N, np.nan, dtype=float),
            'QIN': np.full((N, N), np.nan, dtype=float),
            'QPL': np.full((N, N), np.nan, dtype=float)}

    for entry in data:
        if entry["Type"] in ["QIN", "QPL"]:
            horse_ids = list(map(int, entry["HorseID"].split(",")))
            odds[entry["Type"]][horse_ids[0] - 1,
                                horse_ids[1] - 1] = entry["Odds"]
            odds[entry["Type"]][horse_ids[1] - 1,
                                horse_ids[0] - 1] = entry["Odds"]
        elif entry["Type"] in ["PLA", "WIN"]:
            odds[entry["Type"]][int(entry["HorseID"]) - 1] = entry["Odds"]

    return {t: odds[t] for t in odds_type}

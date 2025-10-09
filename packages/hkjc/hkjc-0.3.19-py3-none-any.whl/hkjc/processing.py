"""Functions to batch process trades into dataframes for analysis.
"""
from __future__ import annotations
from typing import Tuple, List, Union

from .live import live_odds
from .strategy import qpbanker, place_only
from .harville_model import fit_harville_to_odds
from .historical import _extract_horse_data, _extract_race_data, _clean_horse_data
from .utils import _validate_date

import polars as pl
import numpy as np
from itertools import combinations
from tqdm import tqdm
from datetime import datetime as dt


def _all_subsets(lst): return [list(x) for r in range(
    1, len(lst)+1) for x in combinations(lst, r)]  # list subsets of a list


# ======================================
# Historical data processing functions
# ======================================



def _historical_process_single_date_venue(date: str, venue_code: str) -> List[pl.DataFrame]:
    dfs = []
    iter_date = tqdm(
        range(1, 12), desc=f"Processing {date} {venue_code} ...", leave=False)
    for race_number in iter_date:
        try:
            dfs.append(_extract_race_data(date.strftime('%Y/%m/%d'),
                                     venue_code, race_number))
        except:
            if race_number == 1:
                iter_date.close()
                return []
    return dfs


def generate_historical_data(start_date: str, end_date: str) -> pl.DataFrame:
    """Generate historical race dataset from start_date to end_date"""
    _validate_date(start_date)
    _validate_date(end_date)
    start_dt = dt.strptime(start_date, '%Y-%m-%d')
    end_dt = dt.strptime(end_date, '%Y-%m-%d')

    dfs = []

    for date in tqdm(pl.date_range(start_dt, end_dt, interval='1d', eager=True), leave=False, desc='Scanning for horse IDs ...'):
        for venue_code in ['ST', 'HV']:
            dfs += _historical_process_single_date_venue(date, venue_code)

    if dfs == []:
        raise ValueError(
            "Failed to obtain any race data. This could be due to invalid date range, or server requests limit. Please try again later.")

    horse_ids = pl.concat(dfs)['HorseID'].unique()

    # Use horse track records
    dfs = [_extract_horse_data(horse_id) for horse_id in tqdm(horse_ids, desc='Processing horses ...', leave=False)]
    df = pl.concat(dfs)

    try:
        return _clean_horse_data(df).filter(pl.col('Date').is_between(start_dt, end_dt))
    except:
        print('Failed to clean data. Returning raw data for debug.')
    return df


# ==========================
# Trade processing functions
# ==========================

def _process_single_qp_trade(banker: int, covered: List[int], pla_odds: np.ndarray, qpl_odds: np.ndarray, rebate: float) -> Tuple[int, List, float, float, float]:
    """Process a single qp trade.
    """
    win_prob = qpbanker.win_probability(pla_odds, banker, covered)
    exp_value = qpbanker.expected_value(
        pla_odds, qpl_odds, banker, covered, rebate)
    ave_odds = qpbanker.average_odds(qpl_odds, banker, covered)
    return (banker, covered, win_prob, exp_value, ave_odds)


def generate_all_qp_trades(date: str, venue_code: str, race_number: int, rebate: float = 0.12, fit_harville: bool = False) -> pl.DataFrame:
    """Generate all possible qp tickets for the specified race.

    Args:
        date (str): Date in 'YYYY-MM-DD' format.
        venue_code (str): Venue code, e.g., 'ST' for Shatin, 'HV' for Happy Valley.
        race_number (int): Race number.
        rebate (float, optional): The rebate percentage. Defaults to 0.12.
        fit_harville (bool, optional): Whether to fit the odds using Harville model. Defaults to False.

    Returns:
        pl.DataFrame: DataFrame with all possible trades and their metrics.
    """

    odds = live_odds(date, venue_code, race_number,
                     odds_type=['PLA', 'QPL'] + (['WIN', 'QIN'] if fit_harville else []))
    N = len(odds['PLA'])
    candidates = np.arange(1, N+1)

    if fit_harville:
        fit_res = fit_harville_to_odds(
            W_obs=odds['WIN'],
            Qin_obs=odds['QIN'],
            Q_obs=odds['QPL'],
            b_obs=odds['PLA']
        )
        if fit_res['success']:
            odds['PLA'] = np.nan_to_num(1/fit_res['b_fitted'], posinf=0)
            odds['QPL'] = np.nan_to_num(1/fit_res['Q_fitted'], posinf=0)
            odds['WIN'] = np.nan_to_num(1/fit_res['W_fitted'], posinf=0)
            odds['QIN'] = np.nan_to_num(1/fit_res['Qin_fitted'], posinf=0)
        else:
            print(
                f"[WARNING] Harville model fitting failed: {fit_res.get('message','')}")

    results = [_process_single_qp_trade(banker, covered, odds['PLA'], odds['QPL'], rebate)
               for banker in tqdm(candidates, desc="Processing bankers")
               for covered in _all_subsets(candidates[candidates != banker])]

    df = (pl.DataFrame(results, schema=['Banker', 'Covered', 'WinProb', 'ExpValue', 'AvgOdds'])
          .with_columns(pl.col('Covered').list.len().alias('NumCovered')))

    return df


def _process_single_pla_trade(covered: List[int], pla_odds: np.ndarray, p_matrix: np.ndarray, rebate: float = 0.1) -> Tuple[List, float, float, float]:
    """Process a single place-only trade.
    """
    win_prob = place_only.win_probability(p_matrix, covered)
    exp_value = place_only.expected_value(pla_odds, p_matrix, covered, rebate)
    ave_odds = place_only.average_odds(pla_odds, covered)
    return (covered, win_prob, exp_value, ave_odds)


def generate_all_pla_trades(date: str, venue_code: str, race_number: int, rebate: float = 0.1) -> pl.DataFrame:
    """Generate all possible place-only tickets for the specified race.

    Args:
        date (str): Date in 'YYYY-MM-DD' format.
        venue_code (str): Venue code, e.g., 'ST' for Shatin, 'HV' for Happy Valley.
        race_number (int): Race number.
        rebate (float, optional): The rebate percentage. Defaults to 0.12.

    Returns:
        pl.DataFrame: DataFrame with all possible trades and their metrics.
    """

    odds = live_odds(date, venue_code, race_number,
                     odds_type=['PLA', 'QPL', 'WIN', 'QIN'])
    N = len(odds['PLA'])
    candidates = np.arange(1, N+1)

    fit_res = fit_harville_to_odds(odds)

    if fit_res['success']:
        odds['PLA'] = np.nan_to_num(1/fit_res['b_fitted'], posinf=0)
        odds['QPL'] = np.nan_to_num(1/fit_res['Q_fitted'], posinf=0)
        odds['WIN'] = np.nan_to_num(1/fit_res['W_fitted'], posinf=0)
        odds['QIN'] = np.nan_to_num(1/fit_res['Qin_fitted'], posinf=0)
    else:
        raise RuntimeError(
            f"[ERROR] Harville model fitting failed: {fit_res.get('message','')}")
    p_matrix = fit_res['P_fitted']

    results = [_process_single_pla_trade(covered, odds['PLA'], p_matrix, rebate)
               for covered in _all_subsets(candidates)]

    df = (pl.DataFrame(results, schema=['Covered', 'WinProb', 'ExpValue', 'AvgOdds'])
          .with_columns(pl.col('Covered').list.len().alias('NumCovered')))

    return df

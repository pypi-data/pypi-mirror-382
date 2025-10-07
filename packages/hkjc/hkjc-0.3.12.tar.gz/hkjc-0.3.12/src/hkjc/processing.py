"""Functions to batch process trades into dataframes for analysis.
"""
from __future__ import annotations
from typing import Tuple, List, Union

from .live_odds import live_odds
from .strategy import qpbanker, place_only
from .harville_model import fit_harville_to_odds
from .historical import _extract_race_data
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
incidents = ['DISQ', 'DNF', 'FE', 'ML', 'PU', 'TNP', 'TO',
             'UR', 'VOID', 'WR', 'WV', 'WV-A', 'WX', 'WX-A', 'WXNR']


def _historical_process_single_date_venue(date: str, venue_code: str) -> Union[pl.DataFrame, None]:
    for race_number in range(1, 12):
        try:
            _extract_race_data(date.strftime('%Y/%m/%d'),
                               venue_code, race_number)
        except:
            return None


def generate_historical_data(start_date: str, end_date: str) -> pl.DataFrame:
    """Generate historical race dataset from start_date to end_date"""
    _validate_date(start_date)
    _validate_date(end_date)
    start_dt = dt.strptime(start_date, '%Y-%m-%d')
    end_dt = dt.strptime(end_date, '%Y-%m-%d')

    dfs = []

    for date in pl.date_range(start_dt, end_dt, interval='1d'):
        for venue_code in ['ST', 'HV']:
            df = _historical_process_single_date_venue(date, venue_code)
            if df is None:
                continue
            dfs.append(df)

    df = (pl.concat(dfs)
          .filter(~pl.col('Pla').is_in(incidents))
          .with_columns(
        pl.col('Pla').str.split(' ').list.first().alias('Pla')
    )
    )

    df = df.with_columns([
        pl.col('Pla').cast(pl.Int64, strict=False),
        pl.col('HorseNo').cast(pl.Int64, strict=False),
        pl.col('ActWt').cast(pl.Int64, strict=False),
        pl.col('DeclarHorseWt').cast(pl.Int64, strict=False),
        pl.col('Dr').cast(pl.Int64, strict=False),
        pl.col('RaceDistance').cast(pl.Int64, strict=False),
        pl.col('WinOdds').cast(pl.Float64, strict=False)
    ])

    df = df.with_columns(pl.col('Finish Time')
        .str.strptime(pl.Duration, format='%M:%S.%f', strict=False)
        .dt.total_seconds()
        .alias('Finish Time')
    )

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

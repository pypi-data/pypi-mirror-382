"""Functions to perform probability and expectation calculations for the QP Banker strategy.
"""
from __future__ import annotations

from typing import List
import numpy as np


def _pla_odds_partition(pla_odds: np.ndarray, banker: int, covered: List[int]) -> tuple[float, float, float]:
    """Partition the place odds into banker, covered and eliminated sets.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).

    Returns:
        tuple[float, float, float]: A tuple containing the probabilities of the banker,
                                    covered set and eliminated set.
    """
    p_banker = 1 / pla_odds[banker - 1]
    Z_covered = sum([1/pla_odds[c-1] for c in covered])
    Z_total = (1/pla_odds).sum()
    Z_elim = Z_total - p_banker - Z_covered

    return p_banker, Z_covered, Z_elim

def _double_win_probability(pla_odds: np.ndarray, banker: int, covered: List[int]) -> float:
    """Calculate the probability of winning a two tickets in the QPBanker strategy.
    See overleaf document for derivation.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).

    Returns:
        float: probability
    """
    p_banker, Z_covered, Z_elim = _pla_odds_partition(pla_odds, banker, covered)
    Z_total = p_banker + Z_covered + Z_elim

    return 3*p_banker*Z_covered**2 / Z_total**3


def _single_win_probability(pla_odds: np.ndarray, banker: int, covered: List[int]) -> float:
    """Calculate the probability of winning a single ticket in the QPBanker strategy.
    See overleaf document for derivation.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).

    Returns:
        float: probability
    """
    p_banker, Z_covered, Z_elim = _pla_odds_partition(pla_odds, banker, covered)
    Z_total = p_banker + Z_covered + Z_elim

    return 6*p_banker*Z_covered*Z_elim / Z_total**3


def win_probability(pla_odds: np.ndarray, banker: int, covered: List[int]) -> float:
    """Calculate the probability of winning at least one ticket in the QPBanker strategy.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).

    Returns:
        float: probability
    """
    p_double = _double_win_probability(pla_odds, banker, covered)
    p_single = _single_win_probability(pla_odds, banker, covered)

    return p_double + p_single


def expected_value(pla_odds: np.ndarray, qpl_odds: np.ndarray, banker: int, covered: List[int], rebate: float = 0.12) -> float:
    """Calculate the expected value (per dollar) of the QPBanker strategy using constant stake.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        qpl_odds (np.ndarray): An array of quinella place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).
        rebate (float, optional): The rebate percentage. Defaults to 0.12.
    
    Returns:
            float: expected value per dollar staked
    """
    p_banker, Z_covered, Z_elim = _pla_odds_partition(pla_odds, banker, covered)
    Z_total = p_banker + Z_covered + Z_elim
    pla_prob = 1/pla_odds

    P_dbl = _double_win_probability(pla_odds, banker, covered)
    P_single = _single_win_probability(pla_odds, banker, covered)
    C = len(covered)

    BigSum = sum([qpl_odds[banker-1][c-1]*pla_prob[c-1]*(Z_covered-pla_prob[c-1]+Z_elim) for c in covered])
    EV = 6*p_banker*BigSum / Z_total**3 - (1-rebate)*C - rebate*(2*P_dbl + P_single)

    return EV / C

def average_odds(qpl_odds: np.ndarray, banker: int, covered: List[int]) -> float:
    """Calculate the (harmonic) average odds across the covered set.

    Args:
        qpl_odds (np.ndarray): An array of quinella place odds for the horses (0-indexed).
        banker (int): The horse number of the banker (1-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).
        
    Returns:
            float: average odds
    """
    C = len(covered)
    avg_odds = C / sum([1/qpl_odds[banker-1][c-1] for c in covered])
    return avg_odds
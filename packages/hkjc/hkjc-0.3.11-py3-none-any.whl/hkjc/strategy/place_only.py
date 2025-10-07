"""Functions to perform probability and expectation calculations for the place-only strategy.
"""
from __future__ import annotations

from typing import List
import numpy as np


def win_probability(p_matrix: np.ndarray, covered: List[int]) -> float:
    """Calculate the probability of winning at least one ticket in the place-only strategy.

    Args:
        p_matrix (np.ndarray): An array of place probabilities for the horses (0-indexed). p_ij is the probability of horse i placing in position j.
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).

    Returns:
        float: probability
    """
    
    win_prob = 1-np.prod(1-np.sum([p_matrix[c-1, :3] for c in covered], axis=1))
    return win_prob


def expected_value(pla_odds: np.ndarray, p_matrix: np.ndarray, covered: List[int], rebate: float = 0.10) -> float:
    """Calculate the expected value (per dollar) of the place-only strategy using constant stake.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        p_matrix (np.ndarray): An array of place probabilities for the horses (0-indexed). p_ij is the probability of horse i placing in position j.
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).
        rebate (float, optional): The rebate percentage. Defaults to 0.10.
    
    Returns:
            float: expected value per dollar staked
    """
    true_prob = np.sum(p_matrix[:, :3], axis=1)
    C = len(covered)
    ev = np.sum([(true_prob*(pla_odds-rebate))[c-1] for c in covered])/C - (1-rebate)
    return ev

def average_odds(pla_odds: np.ndarray, covered: List[int]) -> float:
    """Calculate the (harmonic) average odds across the covered set.

    Args:
        pla_odds (np.ndarray): An array of place odds for the horses (0-indexed).
        covered (List[int]): A list of horse numbers in the cover set (1-indexed).
        
    Returns:
            float: average odds
    """
    C = len(covered)
    avg_odds = C / sum([1/pla_odds[c-1] for c in covered])
    return avg_odds
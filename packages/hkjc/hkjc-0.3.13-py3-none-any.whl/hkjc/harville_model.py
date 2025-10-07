"""
Harville Race Model Optimizer

Estimates horse racing outcome probabilities using the Harville model via dynamic
programming. Fits latent strength parameters from observed betting market odds across
multiple pool types (Win, Qin, Quinella, Banker).

The optimizer uses O(N * 2^N) complexity DP with Numba JIT compilation for speed.
Suitable for races with up to ~20 horses.

Example:
    >>> optimizer = HarvilleOptimizer(n_horses=14)
    >>> results = optimizer.fit(W_obs=win_odds, Qin_obs=qin_odds, 
    ...                          Q_obs=quinella_odds, b_obs=banker_odds)
    >>> print(results['theta'])  # Fitted strength parameters
"""

import numpy as np
from scipy.optimize import minimize
from numba import njit
from typing import Tuple, Optional

LAMBDA_DEFAULTS = {
    'WIN': 1.0,
    'QIN': 2.0,
    'QPL': 1.5,
    'PLA': 0.7
}

@njit(cache=True)
def _popcount(mask: int) -> int:
    count = 0
    while mask:
        count += 1
        mask &= mask - 1
    return count


@njit(cache=True)
def _precompute_mask_info(n: int) -> Tuple[np.ndarray, np.ndarray]:
    max_mask = 1 << n
    mask_strength_coef = np.zeros((max_mask, n), dtype=np.float64)
    mask_popcount = np.zeros(max_mask, dtype=np.int32)
    
    for mask in range(max_mask):
        mask_popcount[mask] = _popcount(mask)
        for i in range(n):
            if mask & (1 << i):
                mask_strength_coef[mask, i] = 1.0
    
    return mask_strength_coef, mask_popcount


@njit(cache=True)
def _compute_dp_vectorized(theta: np.ndarray, k_max: int) -> np.ndarray:
    n = len(theta)
    max_mask = 1 << n
    
    mask_strength_coef, mask_popcount = _precompute_mask_info(n)
    mask_strength = mask_strength_coef @ theta
    
    dp = np.zeros((k_max + 1, max_mask))
    dp[0, 0] = 1.0
    
    for k in range(k_max):
        valid_masks = np.where(mask_popcount == k)[0]
        
        for mask in valid_masks:
            if dp[k, mask] == 0:
                continue
            
            s_mask = mask_strength[mask]
            remaining = 1.0 - s_mask
            
            if remaining < 1e-12:
                continue
            
            prob_current = dp[k, mask]
            
            for i in range(n):
                if not (mask & (1 << i)):
                    next_mask = mask | (1 << i)
                    dp[k + 1, next_mask] += prob_current * theta[i] / remaining
    
    return dp


@njit(cache=True)
def _extract_pair_in_top_k(dp: np.ndarray, n: int, k: int) -> np.ndarray:
    M = np.zeros((n, n))
    max_mask = 1 << n
    
    mask_popcount = np.zeros(max_mask, dtype=np.int32)
    for mask in range(max_mask):
        mask_popcount[mask] = _popcount(mask)
    
    masks_size_k = np.where(mask_popcount == k)[0]
    
    for mask in masks_size_k:
        prob = dp[k, mask]
        if prob == 0:
            continue
        
        horses = np.empty(k, dtype=np.int32)
        idx = 0
        for i in range(n):
            if mask & (1 << i):
                horses[idx] = i
                idx += 1
        
        for i in range(k):
            for j in range(k):
                if horses[i] != horses[j]:
                    M[horses[i], horses[j]] += prob
    
    return M


@njit(cache=True)
def _extract_top_k_probs(dp: np.ndarray, n: int, k_max: int) -> np.ndarray:
    T = np.zeros((n, k_max + 1))
    max_mask = 1 << n
    
    mask_popcount = np.zeros(max_mask, dtype=np.int32)
    for mask in range(max_mask):
        mask_popcount[mask] = _popcount(mask)
    
    for k in range(1, k_max + 1):
        masks_size_k = np.where(mask_popcount == k)[0]
        
        for mask in masks_size_k:
            prob = dp[k, mask]
            if prob == 0:
                continue
            
            for i in range(n):
                if mask & (1 << i):
                    T[i, k] += prob
    
    return T


@njit(cache=True)
def _compute_probabilities(theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = len(theta)
    
    dp = _compute_dp_vectorized(theta, n)
    
    T = _extract_top_k_probs(dp, n, n)
    
    P = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            P[i, j] = T[i, j + 1] - T[i, j]
    
    W = P[:, 0]
    Qin = _extract_pair_in_top_k(dp, n, 2)
    Q = _extract_pair_in_top_k(dp, n, 3)
    b = T[:, 3]
    
    return W, Qin, Q, b, P


@njit(cache=True)
def _kl_divergence(p_obs: np.ndarray, p_model: np.ndarray) -> float:
    eps = 1e-10
    
    p_obs_flat = np.maximum(p_obs.ravel(), eps)
    p_model_flat = np.maximum(p_model.ravel(), eps)
    
    sum_obs = p_obs_flat.sum()
    sum_model = p_model_flat.sum()
    
    if sum_obs > eps:
        p_obs_flat = p_obs_flat / sum_obs
    if sum_model > eps:
        p_model_flat = p_model_flat / sum_model
    
    return np.sum(p_obs_flat * np.log(p_obs_flat / p_model_flat))


class HarvilleModel:
    """
    Fits Harville race model to betting market odds using dynamic programming.
    
    The Harville model assigns each horse a latent strength parameter theta_i, where
    the probability of finishing next among remaining horses is proportional to 
    relative strength. This optimizer estimates theta from observed betting odds
    across multiple pool types.
    
    Default lambda weights reflect that early Win odds are biased by informed 
    traders waiting until closing, while exotic pools provide more stable 
    signals for ensemble estimation.
    
    Attributes:
        n (int): Number of horses
        lambda_win (float): Weight for Win pool loss
        lambda_qin (float): Weight for Qin pool loss
        lambda_quinella (float): Weight for Quinella pool loss
        lambda_banker (float): Weight for Banker pool loss
    """
    
    def __init__(self, n_horses: int, lambda_win: float = LAMBDA_DEFAULTS['WIN'], lambda_qin: float = LAMBDA_DEFAULTS['QIN'], 
                 lambda_quinella: float = LAMBDA_DEFAULTS['QPL'], lambda_banker: float = LAMBDA_DEFAULTS['PLA']) -> None:
        """
        Initialize model.
        
        Args:
            n_horses: Number of horses in race (recommend <= 20 for speed)
            lambda_win: Weight for Win odds (prob horse finishes 1st)
            lambda_qin: Weight for Qin odds (prob pair finishes 1st-2nd)
            lambda_quinella: Weight for Quinella odds (prob pair in top 3)
            lambda_banker: Weight for Banker odds (prob horse in top 3)
            
        Raises:
            ValueError: If n_horses > 20 (exponential complexity warning)
        """
        if n_horses > 20:
            raise ValueError("N > 20 may be too slow (2^N complexity)")
        
        self.n = n_horses
        self.lambda_win = lambda_win
        self.lambda_qin = lambda_qin
        self.lambda_quinella = lambda_quinella
        self.lambda_banker = lambda_banker
        self._eval_count = 0
        self.result = None
    
    def _loss(self, theta: np.ndarray, W_obs: Optional[np.ndarray], 
             Qin_obs: Optional[np.ndarray], Q_obs: Optional[np.ndarray], 
             b_obs: Optional[np.ndarray]) -> float:
        """
        Compute weighted KL divergence loss between observed and model odds.
        
        Args:
            theta: Strength parameters (will be normalized to simplex)
            W_obs: Observed Win probabilities (n,) or None
            Qin_obs: Observed Qin probabilities (n, n) or None
            Q_obs: Observed Quinella probabilities (n, n) or None
            b_obs: Observed Banker probabilities (n,) or None
            
        Returns:
            Scalar loss value (sum of weighted KL divergences)
        """
        self._eval_count += 1
        
        theta = np.abs(theta) + 1e-10
        theta = theta / theta.sum()
        
        W_model, Qin_model, Q_model, b_model, P_model = _compute_probabilities(theta)
        
        loss = 0.0
        
        if W_obs is not None:
            loss += self.lambda_win * _kl_divergence(W_obs, W_model)
        
        if Qin_obs is not None:
            loss += self.lambda_qin * _kl_divergence(Qin_obs, Qin_model)
        
        if Q_obs is not None:
            loss += self.lambda_quinella * _kl_divergence(Q_obs, Q_model)
        
        if b_obs is not None:
            loss += self.lambda_banker * _kl_divergence(b_obs, b_model)
        
        return loss
    
    def fit(self, W_obs: Optional[np.ndarray] = None, 
            Qin_obs: Optional[np.ndarray] = None,
            Q_obs: Optional[np.ndarray] = None, 
            b_obs: Optional[np.ndarray] = None,
            theta_init: Optional[np.ndarray] = None, 
            method: str = 'L-BFGS-B') -> dict:
        """
        Fit Harville model to observed betting odds.
        
        At least one odds type must be provided. All odds should be probabilities
        (not decimal/fractional odds). Matrices should be symmetric where applicable.
        
        Args:
            W_obs: Win probabilities, shape (n,). W_obs[i] = prob horse i wins
            Qin_obs: Qin probabilities, shape (n, n). Qin_obs[i,j] = prob horses
                     i,j finish 1st-2nd in any order
            Q_obs: Quinella probabilities, shape (n, n). Q_obs[i,j] = prob horses
                   i,j both finish in top 3
            b_obs: Banker probabilities, shape (n,). b_obs[i] = prob horse i 
                   finishes in top 3
            theta_init: Initial strength guess (default: W_obs if available, else uniform)
            method: Scipy optimizer ('L-BFGS-B' or 'SLSQP')
            
        Returns:
            Dictionary containing:
                - theta: Fitted strength parameters (n,)
                - W_fitted: Fitted Win probabilities (n,)
                - Qin_fitted: Fitted Qin probabilities (n, n)
                - Q_fitted: Fitted Quinella probabilities (n, n)
                - b_fitted: Fitted Banker probabilities (n,)
                - P_fitted: Full place probability matrix (n, n), P[i,j] = 
                            prob horse i finishes in position j
                - loss: Final loss value
                - success: Whether optimization converged
                - message: Optimizer status message
                - n_eval: Number of loss function evaluations
                
        Raises:
            ValueError: If no odds provided or shapes don't match n_horses
            
        Example:
            >>> opt = HarvilleOptimizer(n_horses=10)
            >>> results = opt.fit(W_obs=win_probs, Q_obs=quinella_probs)
            >>> print(f"Fitted strengths: {results['theta']}")
            >>> print(f"Converged: {results['success']}")
        """
        if W_obs is None and Qin_obs is None and Q_obs is None and b_obs is None:
            raise ValueError("At least one type of odds must be provided")
        
        if W_obs is not None and W_obs.shape != (self.n,):
            raise ValueError(f"W_obs must be ({self.n},)")
        if Qin_obs is not None and Qin_obs.shape != (self.n, self.n):
            raise ValueError(f"Qin_obs must be ({self.n}, {self.n})")
        if Q_obs is not None and Q_obs.shape != (self.n, self.n):
            raise ValueError(f"Q_obs must be ({self.n}, {self.n})")
        if b_obs is not None and b_obs.shape != (self.n,):
            raise ValueError(f"b_obs must be ({self.n},)")
        
        if theta_init is None:
            if W_obs is not None:
                theta_init = W_obs / W_obs.sum()
            else:
                theta_init = np.ones(self.n) / self.n
        else:
            theta_init = theta_init / theta_init.sum()
        
        self._eval_count = 0
        
        if method == 'L-BFGS-B':
            result = minimize(
                fun=lambda x: self._loss(x, W_obs, Qin_obs, Q_obs, b_obs),
                x0=theta_init,
                method='L-BFGS-B',
                bounds=[(1e-6, 1.0) for _ in range(self.n)],
                options={'maxiter': 500, 'ftol': 1e-9, 'maxls': 50}
            )
        else:
            result = minimize(
                fun=lambda x: self._loss(x, W_obs, Qin_obs, Q_obs, b_obs),
                x0=theta_init,
                method='SLSQP',
                bounds=[(1e-6, 1.0) for _ in range(self.n)],
                constraints={'type': 'eq', 'fun': lambda x: x.sum() - 1},
                options={'maxiter': 500, 'ftol': 1e-9}
            )
        
        theta_opt = np.abs(result.x) + 1e-10
        theta_opt = theta_opt / theta_opt.sum()
        
        W_fitted, Qin_fitted, Q_fitted, b_fitted, P_fitted = _compute_probabilities(theta_opt)
        
        self.result = {
            'theta': theta_opt,
            'W_fitted': W_fitted,
            'Qin_fitted': Qin_fitted,
            'Q_fitted': Q_fitted,
            'b_fitted': b_fitted,
            'P_fitted': P_fitted,
            'loss': result.fun,
            'success': result.success,
            'message': result.message,
            'n_eval': self._eval_count
        }

        return self.result
    
def fit_harville_to_odds(odds : dict[str, np.ndarray], lambdas : dict[str, float] = None) -> dict:
    """
    Fit Harville model to observed betting odds.
    
    At least one odds type must be provided. All odds should be probabilities
    (not decimal/fractional odds). Matrices should be symmetric where applicable.
    
    Args:
        odds: Dictionary of odds arrays with types as keys.:
                'WIN' (n,), 'QIN' (n,n), 'QPL' (n,n), 'PLA' (n,)
        lambdas: Optional dictionary of lambda weights for each odds type.
                    Keys can be 'WIN', 'QIN', 'QPL', 'PLA'. Defaults to
                    {'WIN': 1.0, 'QIN': 2.0, 'QPL': 1.5, 'PLA': 0.7}
        
    Returns:
        Dictionary containing:
            - theta: Fitted strength parameters (n,)
            - W_fitted: Fitted Win probabilities (n,)
            - Qin_fitted: Fitted Qin probabilities (n, n)
            - Q_fitted: Fitted Quinella probabilities (n, n)
            - b_fitted: Fitted Banker probabilities (n,)
            - P_fitted: Full place probability matrix (n, n), P[i,j] = 
                        prob horse i finishes in position j
            - loss: Final loss value
            - success: Whether optimization converged
            - message: Optimizer status message
            - n_eval: Number of loss function evaluations
    """
    n_horses = None
    W_obs = None
    Qin_obs = None
    Q_obs = None
    b_obs = None
    
    if 'WIN' in odds:
        W_odds = odds['WIN']
        if n_horses is None:
            n_horses = len(W_odds)
        elif n_horses != len(W_odds):
            raise ValueError("Inconsistent number of horses in WIN odds")
        W_obs = np.nan_to_num(1.0 / W_odds, 0)
    
    if 'QIN' in odds:
        Qin_odds = odds['QIN']
        if n_horses is None:
            n_horses = Qin_odds.shape[0]
        elif n_horses != Qin_odds.shape[0]:
            raise ValueError("Inconsistent number of horses in QIN odds")
        Qin_obs = np.nan_to_num(1.0 / Qin_odds, 0)
    
    if 'QPL' in odds:
        Q_odds = odds['QPL']
        if n_horses is None:
            n_horses = Q_odds.shape[0]
        elif n_horses != Q_odds.shape[0]:
            raise ValueError("Inconsistent number of horses in QPL odds")
        Q_obs = np.nan_to_num(1.0 / Q_odds, 0)
    
    if 'PLA' in odds:
        b_odds = odds['PLA']
        if n_horses is None:
            n_horses = len(b_odds)
        elif n_horses != len(b_odds):
            raise ValueError("Inconsistent number of horses in PLA odds")
        b_obs = np.nan_to_num(1.0 / b_odds, 0)
    
    merged_lambdas = {**LAMBDA_DEFAULTS, **(lambdas or {})}
    ho = HarvilleModel(
        n_horses,
        lambda_win=merged_lambdas['WIN'],
        lambda_qin=merged_lambdas['QIN'],
        lambda_quinella=merged_lambdas['QPL'],
        lambda_banker=merged_lambdas['PLA']
    )
    result = ho.fit(W_obs=W_obs, Qin_obs=Qin_obs, Q_obs=Q_obs, b_obs=b_obs)
    return result
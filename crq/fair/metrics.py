# computes financial risk metrics from distribution

import numpy as np

def compute_ale(losses: np.ndarray):
    return np.mean(losses)

def compute_var(losses: np.ndarray, percentile: float):
    return np.percentile(losses, percentile)

def compute_cvar(losses: np.ndarray, percentile: float):
    var_threshold = np.percentile(losses, percentile)
    tail_losses = losses[losses >= var_threshold]
    return np.mean(tail_losses)
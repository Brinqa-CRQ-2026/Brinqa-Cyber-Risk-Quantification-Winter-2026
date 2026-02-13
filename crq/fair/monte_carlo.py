#simulate annual losses

import numpy as np

def simulate_annual_losses(
    lef: float,
    loss_samples: np.ndarray,
    iterations: int=10000
):
    """
    Run Monte Carlo sim
    """
    events = np.random.poisson(lam=lef, size=iterations)

    sampled_losses = np.random.choice(loss_samples, size=iterations)

    annual_losses = events * sampled_losses

    return annual_losses
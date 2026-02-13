import numpy as np
from fair.frequency import compute_lef
from fair.magnitude  import sample_loss_lognormal
from fair.monte_carlo import simulate_annual_losses
from fair.metrics import compute_ale, compute_var, compute_cvar

class FairRiskEngine:

    def evaluate_asset(
        self,
        exploit_probability: float,
        threat_frequency: float,
        loss_mu: float,
        loss_sigma: float,
        iterations: int=10000
    ):
        lef = compute_lef(threat_frequency, exploit_probability)

        loss_samples = sample_loss_lognormal(
            mu=loss_mu,
            sigma=loss_sigma,
            size=iterations
        )

        annual_losses = simulate_annual_losses(
            lef=lef,
            loss_samples=loss_samples,
            iterations=iterations
        )

        results = {
            "LEF": lef,
            "ALE": compute_ale(annual_losses),
            "VaR_90": compute_var(annual_losses, 90),
            "VaR_95": compute_var(annual_losses, 95),
            "VaR_99": compute_var(annual_losses, 99),
            "CVaR_95": compute_cvar(annual_losses, 95),
            "distribution": annual_losses
        }

        return results
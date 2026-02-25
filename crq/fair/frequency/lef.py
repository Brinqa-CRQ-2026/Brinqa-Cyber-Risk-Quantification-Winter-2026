import numpy as np
from tef import TEF

class LEF:
    def __init__(self):
        pass

    def simulate(
        self,
        lambda_samples: np.ndarray,
        vulnerability: float,
    ) -> dict:
        if not 0 <= vulnerability <= 1:
            raise ValueError("Vuln must be between 0 and 1")
        
        lambda_success = lambda_samples * vulnerability

        successful_events = np.random.poisson(
            lam=lambda_success
        )

        return {
            "lef_mean": np.mean(successful_events),
            "lef_distribution": successful_events,
            "lambda_success_mean": np.mean(lambda_success)
        }
    
#need to build test module
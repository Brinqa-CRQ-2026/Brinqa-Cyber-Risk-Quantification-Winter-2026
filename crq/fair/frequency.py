import numpy as np
from scipy.stats import lognorm

class ThreatCapabilityModel:
    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma

    def sample(self, iterations: int = 10000):
        return np.random.lognormal(self.mu, self.sigma, iterations)
    
class ResistanceStrengthModel:
    def __init__(self, base_force: float = 1.2, sigma: float = 0.4):
        self.base_force = base_force
        self.sigma = sigma

    def mu_from_score(self, control_score: float):
        control_score = min(max(control_score, 0.0), 1.0)

        force = self.base_force * (1+2*control_score)
        return np.log(force)
    
    def sample(self, control_score: float, iterations: int = 10000):
        mu_r = self.mu_from_score(control_score)
        return np.random.lognormal(mu_r, self.sigma, iterations)
    
class VulnerabilityEngine:
    def __init__(self, tcap_model: ThreatCapabilityModel, rs_model: ResistanceStrengthModel):
        self.tcap_model = tcap_model
        self.rs_model = rs_model

    def compute(self, control_score: float, iterations: int = 10000) -> float:
        tcap_samples = self.tcap_model.sample(iterations)
        rs_samples = self.rs_model.sample(control_score, iterations)

        vulnerability = np.mean(tcap_samples > rs_samples)
        return vulnerability

def annualize_epss(epss_30d: float) -> float:
    """
    Convert 30-day EPSS probability to annual probability.

    Assumes independence between months

    P_annual = 1 - (1 - EPSS)^12
    """
    return 1 - (1 - epss_30d) ** 12

def sample_contact_frequency():
    pass

def sample_probability_of_action():
    pass

def sample_tef():
    pass

def compute_lambda():
    pass
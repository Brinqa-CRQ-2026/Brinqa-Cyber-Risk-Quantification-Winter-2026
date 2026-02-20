import numpy as np

def annualize_epss(epss_30d: float) -> float:
    """
    Convert 30-day EPSS probability to annual probability.

    Assumes independence between months

    P_annual = 1 - (1 - EPSS)^12
    """
    return 1 - (1 - epss_30d) ** 12

def calculate_exposure_factor(
    internet_exposed_norm: float = 0.5,
    network_accesibility: str = "UNKNOWN",
    asset_crit_norm: float = 0.5,
    service: str = ""
) -> float:
    """
    Compute ExposureFactor (0-1).
    Exposure factor captures how likely an asset is to be 
    contacted by a threat actor.
    """
    internet_exposed_norm = min(max(internet_exposed_norm, 0.0), 1.0)
    asset_crit_norm = min(max(asset_crit_norm, 0.0), 1.0)

    # network scoring
    if network_accesibility == "NETWORK":
        network_score = 1.0
    elif network_accesibility == "LOCAL":
        network_score = 0.3
    else:
        network_score = 0.7

    #service scoring
    service_scores = {
        "http": 1.0,
        "https": 1.0,
        "ssh": 0.9,
        "rdp": 0.9,
        "mysql": 0.8,
        "postgres": 0.8,
        "mongodb": 0.8
    }

    service_score = service_scores.get(str(service).lower(), 0.6)

    #assign weights
    #weights are in experimental phase, will have to
    #verify if these are optimal
    w1, w2, w3, w4 = 0.45, 0.25, 0.20, 0.10

    exposure = w1*internet_exposed_norm + w2*network_score + w3*service_score + w4*asset_crit_norm

    return min(max(exposure, 0.0), 1.0)

def calculate_control_factor(
    patch_age_days: int,
    privileges_required: str
) -> float:
    """
    Compute ControlFactor (0-1).
    Represents how effective defensive controls are.
    """
    pass

def calculate_fair_vulnerability(
    epss_30d: float,
    internet_exposed_norm: float,
    network_accessibility: str,
    asset_crit_norm: float,
    service: str,
    patch_age_days: int,
    privileges_required: str
) -> float:
    """
    Compute FAIR Vulnerability (probability an attack attempt succeeds).
    """
    

def calculate_lambda(
    internet_exposed: bool,
    asset_type: str,
    base_rate: float = 5.0,
    exposure_multiplier: float = 100.0
) -> float:
    """
    Estimate TEF rate in attempts per year.
    base_rate is the expected annual hostile attempts for a non-internet-facing internal asset
        - most optimal if exact observation was inputted
        - can be taken from logs, derived from epss, or approximated using ML
    """
    exposure_multiplier = 200.0 if internet_exposed else 1.0

    #possibly have user manually tweak these weights?
    asset_multipliers = {
        "Web Server": 3.0,
        "Application Server": 2.5,
        "Database Server": 2.0,
        "Domain Controller": 2.5,
        "File Server": 1.5,
        "Misc Server": 1.0
    }

    asset_multiplier = asset_multipliers.get(asset_type, 1.0)
    return base_rate * exposure_multiplier * asset_multiplier

def sample_tef(lambda_rate: float, iterations: int = 10000):
    """
    Sample annual threat event counts.
    TEF ~ Poisson((λ)
    """
    return np.random.poisson(lam=lambda_rate, size=iterations)

def compute_lef(
    lambda_tef: float,
    vulnerability: float
) -> float:
    """
    Expected Loss Event Frequency.
    """
    return lambda_tef * vulnerability

def sample_successful_events(
    lambda_tef: float,
    vulnerability: float,
    iteration: int=10000
) -> np.ndarray:
    """
    Sample successful events using Poisson thinning.
    """
    pass
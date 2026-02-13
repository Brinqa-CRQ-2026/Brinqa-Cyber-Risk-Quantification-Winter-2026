import numpy as np

def annualize_epss(epss_30d: float) -> float:
    """
    Convert 30-day EPSS probability to annual probability.

    Assumes independence between months

    P_annual = 1 - (1 - EPSS)^12
    """
    return 1 - (1 - epss_30d) ** 12

def calculate_exposure_factor(
    internet_exposed: bool,
    asset_type: str,
    service: str
) -> float:
    """
    Compute ExposureFactor (0-1).
    Represents how reachable the asset is.
    """
    pass

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
    internet_exposed: bool,
    asset_type: str,
    service: str,
    patch_age_days: int,
    privileges_required: str
) -> float:
    """
    Compute FAIR Vulnerability (probability an attack attempt succeeds).
    """
    pass

def calculate_tef_rate(
    internet_exposed: bool,
    asset_type: str
) -> float:
    """
    Estimate TEF rate in attempts per year.
    """
    pass

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
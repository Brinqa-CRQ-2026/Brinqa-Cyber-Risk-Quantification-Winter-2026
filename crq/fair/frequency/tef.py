import numpy as np
from scipy.stats import lognorm, beta

def compute_cf_mean(
    internet_exposed: bool,
    asset_type: str,
    service: str,
    base_rate: float = 5.0
):
    exposure_multiplier = 200.0 if internet_exposed else 1.0

    service_multipliers = {
        "http": 3.0,
        "https": 3.0,
        "rdp": 4.0,
        "ssh": 3.0,
        "database": 2.0
    }

    asset_multipliers = {
        "Web Server": 2.5,
        "Application Server": 2.0,
        "Database Server": 2.0,
        "Domain Controller": 3.0,
        "File Server": 1.5,
        "Misc Server": 1.0
    }

    S = service_multipliers.get(service.lower(), 1.5)
    A = asset_multipliers.get(asset_type, 1.0)

    return base_rate * exposure_multiplier * S * A

def sample_contact_frequency(
    cf_mean: float,
    sigma: float = 1.0,
    iterations: int = 10000
):
    mu = np.log(cf_mean) - (sigma**2) / 2
    return np.random.lognormal(mean=mu, sigma=sigma, size=iterations)

def compute_poa_mean(
    epss_annual: float,
    base_rate: float = 0.05,
    sensitivity: float = 0.5
):
    m = base_rate + sensitivity + epss_annual
    return min(max(m, 0.001), 0.999)

def sample_poa(
    poa_mean: float,
    concentration: float = 20,
    iterations: int = 10000
):
    alpha = poa_mean * concentration
    beta_param = (1 - poa_mean) * concentration
    return np.random.beta(alpha, beta_param, size=iterations)

def simulate_tef(
    internet_exposed: bool,
    asset_type: str,
    service: str,
    epss_annual: float,
    iterations: int = 10000
):
    cf_mean = compute_cf_mean(
        internet_exposed=internet_exposed,
        asset_type=asset_type,
        service=service
    )

    cf_samples = sample_contact_frequency(cf_mean, iterations=iterations)

    poa_mean = compute_poa_mean(epss_annual=epss_annual)
    poa_samples = sample_poa(poa_mean=poa_mean, iterations=iterations)

    lambda_samples = cf_samples * poa_samples

    tef_samples = np.random.poisson(lam=lambda_samples)

    return {
        "lambda_mean": np.mean(lambda_samples),
        "tef_mean": np.mean(tef_samples),
        "tef_distribution": tef_samples
    }
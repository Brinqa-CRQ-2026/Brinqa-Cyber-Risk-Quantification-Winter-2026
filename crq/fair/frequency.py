import numpy as np

def annualize_epss(epss_30d: float) -> float:
    """
    Convert 30-day EPSS probability to annual probability.

    Assumes independence between months

    P_annual = 1 - (1 - EPSS)^12
    """
    return 1 - (1 - epss_30d) ** 12

def estimate_tcap_score(
    epss_annual: float,
    attack_vector: str,
    privileges_required: str,
    user_interaction: str
) -> float:
    """
    Estimate normalized Threat Capability score (0-1)
    Lower score = easier exploit
    Higher score = stronger attacker required
    """
    score = 0.0

    # EPSS influence
    score += 0.5 * (1 - epss_annual)

    #ATTACK VECTOR
    if attack_vector == "NETWORK":
        score += 0.2
    else:
        score += 0.05

    if privileges_required == "NONE":
        score += 0.2
    else:
        score += 0.05

    if user_interaction == "NONE":
        score += 0.1
    else:
        score += 0.02

    return min(max(score, 0.01), 1.0)

def estimate_rs_score(
    auth_required: bool,
    internet_exposed: bool,
    vuln_age_days: int
) -> float:
    """
    Estimate normalized Resistance Strength score (0-1)
    Higher score = stronger defenses
    """
    score = 0.0

    score += 0.3 if auth_required else 0.05

    score += 0.05 if internet_exposed else 0.2

    if vuln_age_days < 30:
        score += 0.3
    elif vuln_age_days < 100:
        score += 0.15
    else:
        score += 0.05
    
    return min(max(score, 0.01), 1.0)

def score_to_scale(x: float) -> float:
    return 0.1 + 4.9 * x

def score_to_lognormal_params(
    score: float,
    sigma: float = 0.5
):
    scaled = score_to_scale(score)
    mu = np.log(scaled)
    return mu, sigma

def sample_lognormal(mu: float, sigma: float, iterations: int = 10000):
    return np.random.lognormal(mean=mu, sigma=sigma, size=iterations)

def compute_vulnerability(tcap_samples, rs_samples):
    """
    Vulnerability = P(TCap > RS)
    """
    return np.mean(tcap_samples > rs_samples)

def calculate_fair_vulnerability(
    epss_annual: float,
    attack_vector: str,
    privileges_required: str,
    user_interaction: str,
    auth_required: bool,
    internet_exposed: bool,
    vuln_age_days: int,
    iterations: int = 10000    
) -> float:
    tcap_score = estimate_tcap_score(
        epss_annual=epss_annual, 
        attack_vector=attack_vector, 
        privileges_required=privileges_required,
        user_interaction=user_interaction
        )
    
    rs_score = estimate_rs_score(
        auth_required=auth_required,
        internet_exposed=internet_exposed,
        vuln_age_days=vuln_age_days
    )

    mu_t, sigma_t = score_to_lognormal_params(tcap_score)
    mu_r, sigma_r = score_to_lognormal_params(rs_score)

    tcap_samples = sample_lognormal(mu=mu_t, sigma=sigma_t, iterations=iterations)
    rs_samples = sample_lognormal(mu=mu_r, sigma=sigma_r, iterations=iterations)

    vulnerability = compute_vulnerability(tcap_samples, rs_samples)

    return vulnerability

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

if __name__ == "__main__":
    epss_30d = 0.004
    epss_annual = 1 - (1 - epss_30d) ** 12
    vuln = calculate_fair_vulnerability(
    epss_annual=epss_annual,
    attack_vector="NETWORK",
    privileges_required="NONE",
    user_interaction="NONE",
    auth_required=False,
    internet_exposed=True,
    vuln_age_days=300,
    iterations=20000
    )

    print("FAIR Vulnerability:", vuln)
    vuln_strong = calculate_fair_vulnerability(
    epss_annual=epss_annual,
    attack_vector="NETWORK",
    privileges_required="NONE",
    user_interaction="NONE",
    auth_required=True,
    internet_exposed=False,
    vuln_age_days=10,
    iterations=20000
    )

    print("FAIR Vulnerability (strong controls):", vuln_strong)

    
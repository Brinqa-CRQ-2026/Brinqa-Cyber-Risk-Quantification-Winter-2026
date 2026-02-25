import numpy as np
from scipy.stats import lognorm, beta

class TEF:
    def __init__(
        self,
        base_contact_rate: float = 5.0,
        cf_sigma: float = 1.0,
        poa_base: float = 0.02,
        poa_sensitivity: float = 0.25,
        poa_concentration: float = 20,
        seed: int | None = None,
    ):
        self.base_contact_rate = base_contact_rate
        self.cf_sigma = cf_sigma
        self.poa_base = poa_base
        self.poa_sensitivity = poa_sensitivity
        self.poa_concentration = poa_concentration

        if seed is not None:
            np.random.seed(seed)

        self.service_multipliers = {
            "http": 3.0,
            "https": 3.0,
            "rdp": 4.0,
            "ssh": 3.0,
            "database": 2.0
        }

        self.asset_multipliers = {
            "Web Server": 2.5,
            "Application Server": 2.0,
            "Database Server": 2.0,
            "Domain Controller": 3.0,
            "File Server": 1.5,
            "Misc Server": 1.0,
        }

    def compute_cf_mean(
        self,
        internet_exposed: bool,
        asset_type: str,
        service: str,
    ) -> float:
        exposure_multiplier = 200.0 if internet_exposed else 1.0

        S = self.service_multipliers.get(service.lower(), 1.5)
        A = self.asset_multipliers.get(asset_type, 1.0)

        return self.base_contact_rate * exposure_multiplier * S * A

    def sample_contact_frequency(
        self,
        cf_mean: float,
        iterations: int = 10000
    ) -> np.ndarray:
        mu = np.log(cf_mean) - (self.cf_sigma**2) / 2
        return np.random.lognormal(mean=mu, sigma=self.cf_sigma, size=iterations)

    def compute_poa_mean(
        self,
        epss_annual: float
    ) -> float:
        m = self.poa_base + self.poa_sensitivity + epss_annual
        return min(max(m, 0.001), 0.999)

    def sample_poa(
        self,
        poa_mean: float,
        iterations: int = 10000
    ):
        alpha = poa_mean * self.poa_concentration
        beta_param = (1 - poa_mean) * self.poa_concentration
        return np.random.beta(alpha, beta_param, size=iterations)

    def simulate(
        self,
        internet_exposed: bool,
        asset_type: str,
        service: str,
        epss_annual: float,
        iterations: int = 10000
    ) -> dict:
        cf_mean = self.compute_cf_mean(
            internet_exposed=internet_exposed,
            asset_type=asset_type,
            service=service
        )

        cf_samples = self.sample_contact_frequency(cf_mean, iterations=iterations)

        poa_mean = self.compute_poa_mean(epss_annual=epss_annual)
        poa_samples = self.sample_poa(poa_mean=poa_mean, iterations=iterations)

        lambda_samples = cf_samples * poa_samples

        tef_samples = np.random.poisson(lam=lambda_samples)

        return {
            "cf_mean": cf_mean,
            "poa_mean": poa_mean,
            "lambda_mean": np.mean(lambda_samples),
            "tef_mean": np.mean(tef_samples),
            "lambda_distribution": lambda_samples,
            "tef_distribution": tef_samples
        }

if __name__ == "__main__":

    model = TEF(seed=42)

    scenarios = [
        # Internal baseline
        {
            "name": "Internal App Server (Low EPSS)",
            "internet_exposed": False,
            "asset_type": "Application Server",
            "service": "http",
            "epss_annual": 0.01
        },
        # Internet low epss
        {
            "name": "Internet Web Server (Low EPSS)",
            "internet_exposed": True,
            "asset_type": "Web Server",
            "service": "http",
            "epss_annual": 0.01
        },
        # Internet moderate epss
        {
            "name": "Internet Web Server (Moderate EPSS)",
            "internet_exposed": True,
            "asset_type": "Web Server",
            "service": "http",
            "epss_annual": 0.10
        },
        # RDP scenario
        {
            "name": "Internet Domain Controller (RDP)",
            "internet_exposed": True,
            "asset_type": "Domain Controller",
            "service": "rdp",
            "epss_annual": 0.05
        },
    ]

    for s in scenarios:
        result = model.simulate(
            internet_exposed=s["internet_exposed"],
            asset_type=s["asset_type"],
            service=s["service"],
            epss_annual=s["epss_annual"],
            iterations=20000
        )

        print("\n=== ", s["name"], " ===")
        print("CF Mean:", round(result["cf_mean"], 2))
        print("PoA Mean:", round(result["poa_mean"], 4))
        print("Lambda Mean:", round(result["lambda_mean"], 2))
        print("TEF Mean:", round(result["tef_mean"], 2))
        print("TEF Std Dev:", round(result["tef_distribution"].std(), 2))
        print("TEF 95th percentile:", round(
            np.percentile(result["tef_distribution"], 95), 2))
    
    print("\n=== Convergence Test ===")

    for iters in [5000, 20000, 100000]:
        result = model.simulate(
            internet_exposed=True,
            asset_type="Web Server",
            service="http",
            epss_annual=0.05,
            iterations=iters
        )
        print(f"Iterations={iters}, TEF Mean={round(result['tef_mean'], 2)}")
    
    print("\n=== Tail Behavior Check ===")

    result = model.simulate(
        internet_exposed=True,
        asset_type="Web Server",
        service="http",
        epss_annual=0.05,
        iterations=20000
    )

    mean = result["tef_mean"]
    p99 = np.percentile(result["tef_distribution"], 99)

    print("Mean:", round(mean, 2))
    print("99th percentile:", round(p99, 2))
    print("P99 / Mean ratio:", round(p99 / mean, 2))
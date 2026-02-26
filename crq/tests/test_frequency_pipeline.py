import numpy as np

from fair.frequency.tef import TEF
from fair.frequency.vulnerability import (
    ThreatCapabilityModel,
    ResistanceStrengthModel,
    VulnerabilityEngine
)
from fair.frequency.lef import LEF


def run_frequency_simulation(iterations: int = 10000):

    print("\n=== FAIR Frequency Simulation Test ===\n")

    # -----------------------------
    # 1️⃣ Initialize TEF
    # -----------------------------
    tef_engine = TEF(seed=42)

    tef_results = tef_engine.simulate(
        internet_exposed=True,
        asset_type="Web Server",
        service="https",
        epss_annual=0.3,
        iterations=iterations
    )

    lambda_samples = tef_results["lambda_distribution"]
    tef_distribution = tef_results["tef_distribution"]

    print(f"TEF Mean: {np.mean(tef_distribution):.4f}")
    print(f"Lambda Mean: {np.mean(lambda_samples):.4f}")

    # -----------------------------
    # 2️⃣ Initialize Vulnerability
    # -----------------------------
    tcap_model = ThreatCapabilityModel(
        mu=1.0,
        sigma=0.8
    )

    rs_model = ResistanceStrengthModel(
        base_force=1.5,
        sigma=0.5
    )

    vuln_engine = VulnerabilityEngine(
        tcap_model=tcap_model,
        rs_model=rs_model
    )

    vulnerability = vuln_engine.compute(
        control_score=0.6,
        iterations=iterations
    )

    print(f"Vulnerability (P[TCap > RS]): {vulnerability:.4f}")

    # -----------------------------
    # 3️⃣ Compute LEF
    # -----------------------------
    lef_engine = LEF()

    lef_results = lef_engine.simulate(
        lambda_samples=lambda_samples,
        vulnerability=vulnerability
    )

    lef_distribution = lef_results["lef_distribution"]

    print(f"LEF Mean: {lef_results['lef_mean']:.4f}")
    print(f"Lambda Success Mean: {lef_results['lambda_success_mean']:.4f}")

    # -----------------------------
    # 4️⃣ Statistical Summary
    # -----------------------------
    print("\n--- LEF Distribution Summary ---")
    print(f"Std Dev: {np.std(lef_distribution):.4f}")
    print(f"P50: {np.percentile(lef_distribution, 50):.4f}")
    print(f"P90: {np.percentile(lef_distribution, 90):.4f}")
    print(f"P95: {np.percentile(lef_distribution, 95):.4f}")
    print(f"Max: {np.max(lef_distribution):.4f}")

    # -----------------------------
    # 5️⃣ Sanity Checks
    # -----------------------------
    print("\n--- Sanity Checks ---")

    if vulnerability == 0:
        assert np.mean(lef_distribution) == 0

    if vulnerability == 1:
        assert abs(np.mean(lef_distribution) - np.mean(tef_distribution)) < 0.1

    print("Sanity checks passed.")

    print("\n=== Simulation Complete ===\n")


if __name__ == "__main__":
    run_frequency_simulation(iterations=20000)
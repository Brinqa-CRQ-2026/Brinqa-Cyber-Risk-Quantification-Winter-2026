# Canonical FAIR Vulnerability Model
This model implements canonical OpenFAIR vulnerability:

$V = P(TCap > RS)$

Where:
* TCap = Threat Capability distribution
* RS = Resistance Strength distribution
* Both modeled as lognormal
* Vulnerability computed via Monte Carlo simulation

The parameterization choices reflect structural FAIR guidance and empirical risk modeling conventions.

# Why Lognormal Distributions
Both TCap and RS are modeled as:

X ~ $LogNormal(\mu, \sigma)$

* Real-world capability distributions are right-skewed
* A small moniroty of actors posses very high capability
* control effectiveness exhibits variability and tail behavior

Lognormal modeling is standard in quantitative risk analysis and consistent with FAIR

# Threat Capability Parameters
$\mu _T = ln(2.0), \sigma _T = 0.5$

This produces:
* Median attacker capability = 2.0 units of force
* Moderate dispersion reflecting heterogeneous attacker population

## Median Anchoring
* The media is set to 2.0 to create realistic overlap with typical enterprise control strength
    - Ensures neither automatic dominance of attacker nor defender
    - Produces non-saturted vulnerability outputs

## Dispersion
* Reflects moderate heterogeneity:
    - Commodity attackers in lower quantiles
    - Organized actors and elite attackers in upper tail
    - Avoids unrealistic heavy-tail nation-state dominance

## Scenario Sensitivity
* Increasing $\mu _T$ corrently increases vulnerability.

# Resistance Strength Parameterization
RS is defined as:

RS ~ $LogNormal(\mu _R, \sigma _R)$

Where:

$\mu_R = \ln(1.2 * (1 + 2 * \text{control score}))$

and:

$\sigma_R = 0.4$

## Baseline Force
The constant 1.2 represents:
* Minimal baseline exploit difficulty
* Even without strong controls, exploitation requires non-zero force

## Control Scaling Multiplier (1 + 2 * score)
* Monotonicity : Increasing control_score must strictly increase required force
* Multiplicative Control Impact: Controls increase required force proportionally; reflcts layered defense increasing attack complexity
* Reasonable force spread
    - control_score = 0.1 -> multiplier = 1.2
    - control_score = 0.5 -> multiplier = 2.0
    - control_score = 0.9 -> multiplier = 2.8
* Empirical Stability: Scaling validated through sensitivity testing

## RS Dispersion
* Reflects variability inc ontrol effectiveness, operational inconsistencies, environmental variability
* Slightly lower than TCaap dispersion to reflect more structured enterprise controls relative to attacker heterogeneity
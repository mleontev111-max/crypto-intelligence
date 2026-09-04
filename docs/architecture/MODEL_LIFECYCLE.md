# MODEL LIFECYCLE

## Roles

- Baseline: intentionally simple comparison strategy/model.
- Champion: current production research model whose forecasts are shown as canonical.
- Challenger: candidate evaluated in parallel without silently replacing the champion.

## Promotion path

`TRAIN -> OUT-OF-SAMPLE TEST -> WALK-FORWARD -> SHADOW FORECASTS -> COMPARE -> PROMOTE OR REJECT`

Promotion criteria must be defined before looking at final test results and should include calibration, predictive quality, robustness across regimes, and later risk-adjusted paper-portfolio performance.

## Drift

Track both input/data drift and performance/calibration drift. A drifting champion is not automatically retrained into production; retraining creates a new challenger version.

## LLM boundary

LLMs may extract events, summarize evidence, identify contradictions and generate human-readable scenario narratives. They must not mutate historical forecasts, promote models, or silently replace numerical probabilities produced by the quant layer.

## Reproducibility

Every model version must eventually link to training window, feature-set version, code commit, hyperparameters/configuration, evaluation artifacts and promotion decision.

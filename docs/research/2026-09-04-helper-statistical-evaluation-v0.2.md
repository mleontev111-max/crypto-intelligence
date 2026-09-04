# Helper Research Intake — Statistical Evaluation & Event Definition v0.2

**Date:** 2026-09-04  
**Status:** RESEARCH INPUT — NOT CANONICAL POLICY

This intake records reviewed research supplied by the project research assistant. It does not change production contracts or authorize ingestion/model promotion.

## Accepted research directions

- Overlapping multi-step forecast evaluation must account for serial dependence; DM with HAC and/or block-bootstrap inference is a serious candidate.
- Full overlapping evaluation should be supplemented by a thinned non-overlapping robustness check.
- Horizon-aware purging and embargo address different leakage/dependence mechanisms; no universal embargo length is assumed.
- Strict chronological TRAIN -> CALIBRATION -> future TEST walk-forward remains the primary evaluation direction; CPCV is a later robustness tool.
- DOWN/RANGE/UP has no canonical definition yet. A point-in-time volatility-normalized definition is a leading research candidate, but exact thresholds remain OPEN and must be frozen before evaluation.
- Baselines must be fully reproducible rather than informal.
- One-vs-rest isotonic + renormalization remains an experimental multiclass comparator, not canonical default.
- Champion/challenger promotion must rely on proper-score improvement, dependence-robust evidence, multiple future folds, robustness across regimes, and no major calibration/resolution degradation.

## Still OPEN

- HAC bandwidth / block-bootstrap block length for 4h, 24h and 7d BTC forecasts.
- Best causal volatility estimator for target labels.
- Minimum evidence/fold count for model promotion without arbitrary thresholds.
- Regime-global versus regime-conditional calibration.
- Finite-sample behaviour of candidate inference methods on crypto-like heavy-tailed data.

## Architecture impact

None yet. `target_definition_id` remains versioned and unresolved. Research conclusions require project review before they become canonical evaluation or target-definition contracts.

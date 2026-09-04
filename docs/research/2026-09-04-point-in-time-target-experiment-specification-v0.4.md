# Research Memo v0.4 — Point-in-Time Target Experiment Specification

**Project:** Crypto Intelligence  
**Status:** RESEARCH / NOT YET CANONICAL  
**Date archived:** 2026-09-04

This document is research/design input only. No production code, architecture change, final threshold selection, or live-ingestion permission is implied. Recommendations require explicit canonicalization after PIT data is available.

## FINDINGS

### A. FORECAST ORIGIN GRID

**RECOMMENDATION**

Origin time is a discrete timestamp `t` at which a forecast may be issued. All inputs must be fully observed at or before `t`. Align origins to closed bar boundaries of the chosen base granularity (candidate: closed 1h bars).

Research-default issuance candidate: every 4 hours on the closed-bar grid. This intentionally creates overlap for 24h and 7d horizons; dependence must be handled in evaluation rather than hidden by thinning at design time.

For horizon `h ∈ {4h,24h,7d}`, outcome interval is `(t,t+h]`; outcome cutoff is `t+h`, and the label resolves only after the relevant closing bar is fully closed.

No open/incomplete candle may enter features, volatility estimates, or returns. Missing-bar policy must be frozen; skipping affected origins is the safer PIT default than silent forward-fill/interpolation.

### B. CAUSAL VOLATILITY FORMULAS

All estimators use only data available at origin. Lookback `L`, EWMA decay `lambda`, initialization and horizon scaling are parameters, not frozen constants.

Base-bar log return: `r_i = ln(C_i / C_{i-1})`.

**Trailing realized volatility**

`sigma_RV(t,L) = sqrt((1/L) * sum r_i^2)` over the last L closed returns (unbiased variant is an alternative that must be frozen explicitly).

**EWMA**

`sigma_EWMA(t)^2 = (1-lambda) * r_t^2 + lambda * sigma_EWMA(t-delta)^2`, initialized from a causal trailing window.

**Parkinson**

`sigma_P(t,L) = sqrt((1/(4 L ln 2)) * sum [ln(H_i/L_i)]^2)` over closed bars only.

**ATR**

`TR_i = max(H_i-L_i, abs(H_i-C_{i-1}), abs(L_i-C_{i-1}))`; ATR is a trailing mean or explicitly versioned Wilder recursion.

Estimator is undefined until minimum history exists. Missing bars follow the same frozen policy as the origin grid. If per-base-bar volatility is horizon-scaled, `sqrt(h/delta)` is a candidate explicit parameter, not a canonical choice. Annualization is unnecessary for a dimensionless normalized target unless deliberately standardized.

### C. TARGET DEFINITION FAMILY

Future return candidate: `R(t,h)=ln(C_(t+h)/C_t)` (simple return remains an alternative to freeze explicitly).

**Fixed-return:** DOWN below frozen lower threshold, UP above frozen upper threshold, RANGE between them.

**Volatility-normalized:** `Z(t,h)=R(t,h)/(sigma_t * s(h))`, where `sigma_t` is causal volatility known at origin and `s(h)` is an explicit scaling function. Thresholds are frozen from target-design data only.

Future realized volatility in the denominator is leakage and forbidden.

**Past-only quantile:** estimate return or normalized-return quantiles strictly on data before the design cutoff, freeze them, and apply them prospectively. Re-estimating frozen quantiles with later information is forbidden.

No final threshold, quantile, lookback, lambda, or scaling choice is made by this memo.

### D. LABEL STABILITY METRICS

Candidate diagnostics:

- class frequency — detect degenerate classes;
- rolling base rate — detect temporal drift/collapse;
- entropy — distribution informativeness;
- transition rate — detect stuck or chaotic labels;
- regime-conditioned class balance — identify regime-specific collapse;
- threshold drift under diagnostic re-estimation — assess frozen-threshold stability;
- tail-event frequency — verify extreme-move coverage;
- spike sensitivity — inspect behavior around elevated volatility;
- missing-label rate — quantify data-quality/sample loss.

No numeric pass/fail thresholds are asserted without empirical evidence.

### E. TARGET-DESIGN DATA PARTITION

**RECOMMENDATION**

`TARGET-DESIGN -> TRAIN -> CALIBRATION -> TEST`

TARGET-DESIGN is an earliest contiguous segment used only for label-stability inspection and parameter freezing. After freezing, target definition becomes immutable. TRAIN/CALIBRATION/TEST lie strictly after the design cutoff. No model performance from those later partitions may feed back into target-parameter choice.

A more complex rolling/nested design is possible but not required for v0.1.

### F. CAUSAL BASELINES

Formal persistence rule:

`last_resolved_label(t,h) = Y(t*,h)` where `t* = max{t' : t'+h <= t}`.

If no resolved prior label exists, persistence is undefined for that origin. With 4h issuance, a 24h persistence baseline may only use origins at least 24h old; a 7d persistence baseline may only use origins at least 7d old.

### G. LEAKAGE TEST SPECIFICATION

Mandatory candidates before historical model experiments:

1. Future-candle mutation after origin must not change origin-time inputs.
2. Future-volatility path must be rejected/not equal to production causal path.
3. Full-history quantiles must not replace design-sample-only frozen quantiles.
4. Persistence must reject a prior label whose outcome cutoff is later than current origin.
5. Changing label parameters must create a new target-definition ID; historical labels under the old ID may not be rewritten in place.

Additional candidates: missing-bar policy consistency, open-candle rejection, timezone/alignment invariance.

### H. TARGET DEFINITION REGISTRY

Use a short immutable `target_definition_id` backed by immutable metadata/config hash. The immutable definition must cover at minimum:

- horizon;
- return convention;
- volatility estimator + version;
- lookback/lambda/scaling parameters;
- threshold family + frozen threshold/quantile parameters;
- bar granularity;
- timezone/session convention;
- target-design cutoff;
- code/config version;
- PIT source dataset identifier/version.

Human description, design metrics snapshot, author/date/notes may remain metadata. Any label-affecting parameter change requires a new ID.

## RECOMMENDED EXPERIMENT PROTOCOL v0.1

1. Fix origin grid and missing-bar policy.
2. Implement causal volatility estimators with versioned parameters.
3. On TARGET-DESIGN only, compare label-stability diagnostics for fixed, volatility-normalized, and past-only quantile families.
4. Freeze one or a small set of candidate definitions under new registry IDs.
5. Run all mandatory leakage tests.
6. Only after they pass, allow TRAIN -> CALIBRATION -> TEST model experiments.
7. Never revise a frozen ID after later-period model evaluation begins.

## RISKS

- Target thresholds chosen using future evaluation periods.
- Horizon scaling silently mixing units.
- 24/7 crypto OHLC semantics differing from equity assumptions.
- Missing bars reducing effective sample.
- Overlap-induced dependence ignored when interpreting stability.

## OPEN QUESTIONS

- Preferred base granularity (1h versus 4h) across horizons.
- Whether `s(h)=sqrt(h/delta)` or `s(h)=1` is preferable for label purposes.
- Required TARGET-DESIGN history length before diagnostics stabilize.
- Parkinson/ATR behavior under extreme crypto jumps versus EWMA.

## SOURCES CITED BY THE RESEARCH MEMO

- López de Prado (2018), point-in-time/purge principles.
- Parkinson (1980); Garman–Klass (1980); Rogers–Satchell (1991); Wilder ATR.
- EWMA / RiskMetrics-style recursion.
- White (2000), data snooping / selection concerns.
- Prior project research memos v0.2–v0.3.

## ANSWERS TO FOUR FINAL QUESTIONS

1. **PIT-safe DOWN/RANGE/UP:** use future return `R(t,h)` or normalized `Z(t,h)=R(t,h)/(sigma_t*s(h))`, with `sigma_t` computed solely from closed bars available at origin. Apply thresholds frozen on TARGET-DESIGN data only.
2. **Choose target without contaminating TEST:** all target inspection/parameter freezing occurs in a TARGET-DESIGN partition ending before TRAIN/CALIBRATION/TEST; publish immutable target-definition ID and do not revisit thresholds based on later model performance.
3. **Causal persistence:** `last_resolved_label(t,h)` may select only `t'` satisfying `t'+h <= t`.
4. **Five mandatory leakage tests:** future candle, future volatility, full-history quantile, unresolved previous label, and historical parameter rewrite without a new target-definition ID.

## CANONICALIZATION NOTE

This memo is archived as research input. In particular, the proposed 4-hour issuance grid, 1-hour base-bar candidate, missing-bar skip default, volatility formula variants, target partition structure, and experiment protocol are not yet project law. They must be validated against reproducible point-in-time data and explicitly promoted before becoming canonical.
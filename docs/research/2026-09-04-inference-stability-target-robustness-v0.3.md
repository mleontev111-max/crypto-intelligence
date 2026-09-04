# Research Memo v0.3 — Inference Stability & Target Robustness

**Project:** Crypto Intelligence  
**Status:** RESEARCH / NOT YET CANONICAL  
**Date archived:** 2026-09-04

This memo is research input only. It does not change production architecture, target definitions, model-promotion policy, or live-ingestion permissions. Any recommendation below must pass an explicit canonicalization decision before implementation.

## FINDINGS

### HAC / DM

**ESTABLISHED**

Diebold–Mariano (1995) compares mean loss differentials. For multi-step / overlapping forecasts the loss differential is serially correlated; inference requires a HAC long-run variance (Newey–West 1987; Andrews 1991).

Harvey, Leybourne & Newbold (1997) provide a finite-sample bias correction to the DM statistic and recommend Student-t critical values instead of standard normal; the correction is widely used and improves size in moderate samples.

**Bandwidth practice**

- Rule-of-thumb (Newey–West style): `L ≈ 0.75 n^(1/3)` (or similar).
- Data-driven: Andrews (1991) plug-in (AR(1) approximation + asymptotic MSE minimisation); Newey–West (1994) non-parametric variant.
- Mechanically setting bandwidth equal to the number of overlapping intervals (for example `7d/4h = 42`) has no general theoretical justification and can produce large/noisy variance estimates when evaluation samples are not huge.

**For 7d forecasts every 4h**

Dependence is strong and long-lived. HAC variance estimates become more variable; negative long-run variance estimates can occur with some kernels when samples are short relative to the horizon. Results can be sensitive to bandwidth choice in finite samples.

**When DM-HAC becomes unreliable**

When the evaluation sample is small relative to dependence length, or when the long-run variance estimate is unstable/negative. In such regimes fixed-smoothing asymptotics or bootstrap methods may be preferable.

**RECOMMENDATION**

Primary inference candidate: DM with HAC, preferably with Harvey–Leybourne–Newbold finite-sample correction. Report results under at least two bandwidth choices (rule-of-thumb and data-driven). Do not adopt `bandwidth = number of overlapping intervals` as a default.

**OPEN**

Optimal practical bandwidth (or fixed-smoothing parameter) specifically for crypto loss differentials at 4h/24h/7d issuance frequencies.

## BLOCK BOOTSTRAP

**ESTABLISHED**

- Moving Block Bootstrap (Künsch 1989)
- Stationary Bootstrap (Politis & Romano 1994) — random geometric block length, stationary by construction
- Circular Block Bootstrap — related overlapping-block variant

Automatic block-length selection: Politis & White (2004), corrected by Patton, Politis & White (2009), using spectral flat-top lag-window methods.

**RECOMMENDATION**

Use block bootstrap (preferably Stationary Bootstrap with Politis–White/Patton automatic length, or a sensitivity grid around it) as a primary robustness check alongside DM-HAC. It supplies a confidence interval for the mean loss differential without relying on asymptotic normality of the HAC estimator. Do not tune block length to obtain desired significance.

**OPEN**

Finite-sample behaviour of automatic selectors on heavy-tailed crypto loss series; whether a horizon-informed lower bound on block length is beneficial.

## VOLATILITY ESTIMATORS

Only point-in-time (causal) estimators are admissible for label definition.

| Estimator | Data needed | Jumps | 24/7 crypto | Stability / speed | Leakage if causal | Notes |
|---|---|---|---|---|---|---|
| Trailing realized vol (close-to-close) | closes | Sensitive | Natural fit | Stable, slower | None if window ends at origin | Simple baseline |
| EWMA | closes | Sensitive | Natural fit | Faster reaction | None if recursive and causal | Good practical candidate |
| Parkinson | high/low | Under-reacts to jumps/gaps | Gaps less relevant in 24/7 | Efficient under pure diffusion | None | No open needed |
| Garman–Klass | OHLC | Sensitive to open jumps | Open can be noisy in continuous markets | High efficiency in theory | None | Crypto open definition ambiguous |
| Rogers–Satchell | OHLC | Drift-robust | Same open issues | Competitive | None | Handles drift |
| ATR | high/low/close | Practical, less theoretical | Widely used | Interpretable | None if causal | Useful comparator |

**ESTABLISHED**

Range-based estimators (Parkinson, GK, RS) are more efficient than close-to-close under ideal diffusion assumptions. In crypto, continuous trading and microstructure/jump behaviour can change relative ranking.

**RECOMMENDATION**

First empirical comparison set for volatility-normalized targets:

1. Trailing realized volatility (close-to-close)
2. EWMA
3. Parkinson
4. ATR (practical benchmark)

Garman–Klass / Rogers–Satchell are secondary candidates once open-price conventions for continuous crypto markets are fixed. All estimators must be computed strictly from information available at forecast origin.

**OPEN**

Which estimator yields the most temporally stable class balance and cleanest economic interpretation for 4h versus 7d horizons on BTC.

## LABEL STABILITY

**RECOMMENDATION — Experiment design (not a production threshold)**

On a long historical archive, for each candidate definition (fixed %, volatility-normalized with each shortlisted estimator, historical quantile):

- Compute rolling class frequencies and base-rate trajectories.
- Measure transition matrix / regime-switching frequency of labels.
- Stratify by known market regimes and record balance/event rates.
- Examine behaviour around volatility spikes.
- Check temporal stability of implied thresholds.
- Verify point-in-time feasibility; no future information in volatility or quantile estimates.

A definition is usable for multi-year walk-forward if class frequencies do not collapse for long periods, base-rate drift is gradual rather than caused by look-ahead/arbitrary re-estimation, economic meaning remains intelligible, and genuine regime shifts are not washed out. No numerical cutoff is asserted here.

## REGIME CALIBRATION

**ESTABLISHED**

Calibration can degrade under distribution/concept drift. Sample splitting by regime reduces data available per calibrator and adds classification error.

Risks include fragmentation/higher variance, propagation of regime-label error, mismatch between origin regime and horizon regime, and overfitting to short regime windows.

**RECOMMENDATION**

Default research candidate is a global calibrator. Consider regime-conditional or hierarchical/mixture calibrators only after clear persistent regime-specific miscalibration on held-out future data, sufficient samples per regime, and demonstrated proper-score improvement after accounting for regime-classification noise.

**OPEN**

Whether a simple mixture or hierarchical calibrator can capture regime effects with less fragmentation than hard regime splits.

## MULTIPLE MODEL TESTING

**ESTABLISHED**

When many challengers are tested, the best observed performer is upward-biased (data snooping).

- White (2000) Reality Check tests whether the best of a universe beats a benchmark after accounting for search.
- Hansen (2005) Superior Predictive Ability (SPA) improves power by studentizing and down-weighting clearly inferior models.
- Both typically rely on a stationary bootstrap for the null distribution of the maximum performance statistic.

**RECOMMENDATION**

If multiple challengers are evaluated against the same champion/baseline, apply Hansen SPA (or White RC) on the matrix of loss differentials using a dependence-robust bootstrap. A challenger that wins a naïve pairwise DM test after a large search is not sufficient evidence. Report the full distribution of challenger performances and freeze the evaluation protocol before inspecting results.

**OPEN**

Exact power of SPA under strong overlapping dependence of 7d/4h BTC forecasts; how to incorporate the CALIBRATION step inside the multiple-testing framework.

## RECOMMENDED EXPERIMENT DESIGN

1. **Inference stack:** DM + HAC (with HLN correction) as primary candidate; Stationary Bootstrap CI as mandatory robustness candidate; thinned non-overlapping evaluation as an additional check.
2. **Volatility estimators for labels:** compare trailing RV, EWMA, Parkinson, ATR, causal only.
3. **Label stability:** run rolling diagnostics and freeze a definition only after diagnostics on a historical archive separated from final model ranking.
4. **Calibration:** global calibrator first; regime-conditional only with explicit held-out justification.
5. **Multiple testing:** multi-challenger comparison should be accompanied by Hansen SPA (or White RC) or equivalent search-adjusted procedure.

## RISKS

- Bandwidth / block-length sensitivity can change significance calls.
- Small effective sample under long horizons makes asymptotic tests fragile.
- Volatility estimator choice alters class balance and baseline difficulty.
- Regime splits can create illusory calibration gains.
- Uncorrected multiple testing can turn the best of many noise models into a false champion.

## OPEN QUESTIONS

- Practical HAC bandwidth or fixed-smoothing parameter for crypto loss differentials.
- Best automatic versus horizon-informed block length on BTC.
- Ranking of causal volatility estimators specifically for 4h versus 7d label stability.
- Power of SPA under heavy overlapping dependence.
- Whether a hierarchical calibrator can safely capture regime effects.

## SOURCES CITED BY THE RESEARCH MEMO

- Diebold & Mariano (1995), JBES.
- Harvey, Leybourne & Newbold (1997), IJF.
- Newey & West (1987, 1994); Andrews (1991) — HAC bandwidth.
- Künsch (1989); Politis & Romano (1994); Politis & White (2004); Patton, Politis & White (2009) — block bootstrap & length selection.
- White (2000) Reality Check, Econometrica.
- Hansen (2005) SPA, JBES.
- Parkinson (1980); Garman & Klass (1980); Rogers & Satchell (1991) — range volatility.
- Literature on DM size distortions and fixed-smoothing asymptotics (Kiefer–Vogelsang, Sun, Coroneo–Iacone, etc.).

## ANSWERS TO FOUR FINAL QUESTIONS

1. **Inference for overlapping 4h / 24h / 7d BTC forecasts:** DM with HAC long-run variance + HLN finite-sample correction as primary candidate; Stationary Bootstrap confidence interval as mandatory robustness candidate; plus thinned non-overlapping evaluation. Report bandwidth/block-length sensitivity and avoid significance claims from a single un-robustified p-value.
2. **Causal volatility estimators to compare first:** trailing realized volatility, EWMA, Parkinson, ATR; all strictly up to forecast origin. GK and RS secondary once continuous-market open handling is fixed.
3. **Regime-dependent calibration:** only after a global calibrator leaves persistent regime-specific miscalibration on future data and conditional calibration has adequate samples plus quantified regime-classification error.
4. **Protection against data snooping:** Hansen SPA (or White Reality Check) over the challenger set using dependence-robust bootstrap; do not promote solely because a model is best among many under naïve pairwise tests.

## CANONICALIZATION NOTE

This document intentionally preserves the memo as research input. Terms such as “primary”, “mandatory”, or “default” above are recommendations from the research memo, not current project law. Before any of them becomes canonical, Crypto Intelligence must separately define and validate target semantics, evaluation windows, dependence handling, calibration protocol, and promotion gates using point-in-time data.
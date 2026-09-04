# FORECAST LEDGER

## Purpose

The Forecast Ledger is the immutable audit trail connecting market knowledge at forecast time to a later measurable outcome.

## Minimum forecast identity

Each published forecast must include:

- forecast ID;
- created_at UTC;
- asset/instrument;
- horizon;
- reference market price;
- model ID/version;
- data snapshot ID;
- regime label/version when used;
- probability distribution or explicitly defined target probabilities;
- confidence/calibration metadata where applicable;
- status (`OPEN`, `CLOSED`, `VOID` only for predefined data-integrity reasons).

## Immutability

Published forecast values are never edited after the fact. A discovered defect is recorded as an audit event and, when appropriate, a corrected new forecast/version. The original remains queryable.

## Outcome closure

Outcomes should record realized return, target hit/miss, maximum favorable/adverse excursion where useful, close timestamp, source data lineage and evaluation metrics.

## Evaluation

Primary quality measures include Brier/log loss where appropriate, calibration curves, MAE for numeric targets, directional/baseline comparisons, and regime stability. Later portfolio evaluation adds drawdown, Sharpe/Sortino, turnover, fees and slippage.

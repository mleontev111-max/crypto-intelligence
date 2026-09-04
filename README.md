# Crypto Intelligence

Crypto Intelligence is a research and decision-support system for observing crypto markets, producing probabilistic forecasts, measuring forecast quality, and improving models without rewriting history.

The project does **not** claim to predict markets with certainty and does not permit live-money automation during the early phases.

## Start here

Every human or AI contributor must begin in this order:

1. `START_HERE.md`
2. `PROJECT_STATE.json`
3. the checkpoint referenced by `current_checkpoint`
4. `AGENTS.md`
5. `PROJECT_CONSTITUTION.md`
6. `ARCHITECTURE.md`
7. `ROADMAP.md`

Do not infer current state from an old chat, local checkout, stale issue, or old checkpoint.

## Current phase

Phase 0 — Foundation.

The current goal is to define the canonical project state model, checkpoint discipline, architecture boundaries, BTC-first MVP scope, forecast ledger, and model lifecycle before ingestion or trading logic is implemented.

## Core principle

The system must preserve what it actually knew at forecast time:

`RAW -> NORMALIZED -> DERIVED -> FORECAST -> OUTCOME -> EVALUATION`

Forecasts are immutable after publication. New models are challengers until they beat the champion under predefined out-of-sample evaluation.

## Safety boundary

No real-money execution is allowed in Phase 0-5. Paper portfolios and research outputs are permitted later according to the roadmap.

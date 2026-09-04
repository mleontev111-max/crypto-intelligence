# ARCHITECTURE

## System goal

Build a reproducible crypto research and probabilistic decision-support system, starting with BTC, that can explain what data it used, what it predicted, and how the prediction performed.

## Canonical flow

`SOURCES -> RAW -> NORMALIZED -> FEATURES -> MARKET REGIME -> FORECAST -> LEDGER -> OUTCOME -> EVALUATION -> MODEL LAB`

LLM analysis is adjacent to, not a replacement for, numerical forecast models.

## Initial components

- Ingestion adapters for approved sources.
- Immutable RAW storage.
- PostgreSQL/TimescaleDB for normalized time-series and metadata.
- Feature engine with versioned feature definitions.
- Market regime engine.
- Quant forecast service.
- LLM analyst for event/context extraction and explanation.
- Immutable Forecast Ledger.
- Outcome/evaluation engine.
- Model registry and champion/challenger lifecycle.
- Dashboard/API layer.

## Point-in-time rule

Every forecast must be reconstructable from data that was available at its creation time. Revised vendor history must not silently replace the original knowledge snapshot used by a forecast.

## MVP infrastructure direction

Backend: Python + FastAPI.
Database: PostgreSQL + TimescaleDB.
Analysis: Polars/Pandas, scikit-learn, XGBoost/LightGBM later.
Frontend: Next.js + TradingView Lightweight Charts.
Object storage: S3-compatible storage for large RAW payloads when needed.
Deployment: Docker; avoid Kafka/Kubernetes/Spark until scale proves they are needed.

# PostgreSQL Decisions v0.1

Status: Phase 0 implementation decision record. No live ingestion approval.

## Decisions

### UUID strategy
Use application-generated UUIDs and store them in PostgreSQL `uuid` columns without a database extension dependency. The application layer should prefer time-ordered UUIDv7 when the runtime supports it; the database contract does not depend on a specific UUID generator function.

### TimescaleDB
Deferred. The first migration targets plain PostgreSQL 16-compatible SQL. TimescaleDB may be introduced later only after measured volume/query requirements justify it.

### Append-only enforcement
The first migration uses database triggers that reject UPDATE and DELETE on scientific-evidence tables: RAW events, snapshots, model versions, target definitions, forecasts, forecast probabilities, and outcomes. Later role/permission hardening may supplement this, but application discipline alone is not considered sufficient.

### Numeric precision
Initial conservative fixed-precision mapping:
- generic normalized numeric observation: `numeric(38,18)`;
- reference prices: `numeric(38,18)`;
- returns / expected return / excursions: `numeric(24,18)`;
- probabilities: `numeric(20,18)`.

These are storage engineering choices, not claims about forecast accuracy. They may be revised only through a new migration after empirical range/precision requirements are measured.

### Probability vector invariant
Each class probability is constrained to [0,1] in PostgreSQL. The cross-row sum-to-one invariant remains outside migration 0001 because it requires a deferred aggregate constraint/trigger design. Forecast publication must therefore remain blocked until an atomic publication transaction validates the complete vector.

### Snapshot cutoff invariant
`data_snapshot_components.max_available_at <= data_snapshots.cutoff_available_at` cannot be expressed with a simple CHECK across tables. It remains an explicit later trigger/application invariant; no ingestion is allowed before it is enforced in the write path.

## Safety boundary
Migration 0001 creates schema only. It does not create credentials, ingestion jobs, exchange connections, model execution, paper trading, or live trading.
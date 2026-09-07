# Single-Node Runtime v0.1

Status: Phase 0 runtime package. Manual collection only. No scheduler.

## Purpose

Run Crypto Intelligence on one host with:

- PostgreSQL 16 persisted in a Docker volume;
- exact RAW response bytes persisted in a second Docker volume;
- migrations executed manually;
- the approved-source collector executed manually with explicit bounded windows.

This package does not authorize regular live ingestion. `PROJECT_STATE.live_ingestion_allowed` remains `false` until a later checkpoint accepts a controlled persistent-host collection.

## Runtime variables

Copy `.env.example` to `.env` on the target host and set:

- `POSTGRES_DB` — database name;
- `POSTGRES_USER` — database user;
- `POSTGRES_PASSWORD` — local database password;
- `FRED_API_KEY` — FRED runtime key.

Do not commit `.env`.

The collector container receives `RAW_STORAGE_DIR=/data/raw` internally. Docker volume `raw_data` persists that directory. PostgreSQL data are persisted in volume `postgres_data`.

## Start PostgreSQL only

```bash
docker compose up -d db
```

The collector and migration services are under the `manual` profile and do not run with the normal database startup.

## Apply Phase 0 migrations manually

```bash
docker compose --profile manual run --rm migrate
```

Run this after the first database startup and after future migration additions. Current v0.1 applies migrations `0001` and `0002` only.

## Verify collector remains disabled by default

```bash
docker compose --profile manual run --rm collector
```

Expected result: JSON with `status=disabled`, `network_fetch_performed=false`, and `database_write_performed=false`.

## Controlled manual collection

Example bounded research window:

```bash
docker compose --profile manual run --rm collector \
  --write \
  --coinbase-start 2026-09-01T00:00:00Z \
  --coinbase-end 2026-09-01T03:00:00Z \
  --fred-realtime-date 2026-09-01 \
  --fred-observation-start 2026-08-25 \
  --fred-observation-end 2026-09-01
```

The collector performs the following sequence per source response:

1. HTTPS GET through the existing constrained read-only transport.
2. Verify SHA-256 evidence.
3. Store exact response bytes in the content-addressed RAW volume.
4. Parse/normalize approved observations.
5. Write `raw_events`, `observations`, and `observation_raw_events` through ordinary PostgreSQL transactions.
6. Print only sanitized evidence/summary; FRED API key must remain redacted.

Running the exact same bounded collection again is expected to be idempotent by deterministic IDs/content hashes.

### Selecting a single source

`--sources {all,coinbase,fred}` (default `all`) limits a bounded run to one
approved source. Only the flags for the selected source(s) are required —
e.g. `--sources fred` needs the three `--fred-*` flags but not
`--coinbase-start`/`--coinbase-end`, and vice versa for `--sources
coinbase`. This exists to support the FRED-only Stage 1 cadence in
`docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`; it changes nothing
about what a plain `--write` (no `--sources`) run does.

## Inspect counts

```bash
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'select count(*) from raw_events;'
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'select count(*) from observations;'
```

## Stop services

```bash
docker compose down
```

Do not use `docker compose down -v` unless intentionally deleting the persistent database and RAW volumes.

## Explicitly not included in v0.1

- cron / scheduler;
- Celery / Temporal;
- automatic historical backfill;
- additional market/on-chain/news sources;
- trading/execution;
- automatic activation of `live_ingestion_allowed`.

## Next gate

After this compose package is validated in CI, one manual collection may be performed on the selected persistent host only after a checkpoint explicitly records the target runtime and keeps the collection scope narrow. Regular scheduling is a later decision.
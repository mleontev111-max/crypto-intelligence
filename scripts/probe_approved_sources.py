#!/usr/bin/env python3
"""Zero-write live probe for Phase 0 approved sources.

The script prints sanitized evidence only. It never writes raw payloads or database rows.
FRED requires FRED_API_KEY from the runtime environment; the value is never printed.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapters.coinbase_exchange_candles import build_url as coinbase_url, parse_candles  # noqa: E402
from adapters.fred_h15_treasury import build_url as fred_url, parse_observations  # noqa: E402
from transport.read_only_http import read_only_get  # noqa: E402


def probe_coinbase() -> dict:
    url = coinbase_url(
        start="2026-09-01T00:00:00Z",
        end="2026-09-01T03:00:00Z",
        granularity=3600,
    )
    result = read_only_get(url)
    payload = json.loads(result.body.decode("utf-8"))
    candles = parse_candles(payload)
    return {
        "source": "market.coinbase.exchange.btcusd.candles",
        "parsed_records": len(candles),
        "evidence": result.evidence.__dict__,
    }


def probe_fred(series_id: str) -> dict:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY runtime secret is required for FRED live probe")
    url = fred_url(
        series_id=series_id,
        api_key=api_key,
        realtime_start="2026-09-01",
        realtime_end="2026-09-01",
    )
    result = read_only_get(url)
    payload = json.loads(result.body.decode("utf-8"))
    observations = parse_observations(payload)
    return {
        "source": "macro.fred.h15.dgs2_dgs10",
        "series_id": series_id,
        "parsed_records": len(observations),
        "evidence": result.evidence.__dict__,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=["coinbase", "fred-dgs2", "fred-dgs10"])
    args = parser.parse_args()

    if args.source == "coinbase":
        evidence = probe_coinbase()
    elif args.source == "fred-dgs2":
        evidence = probe_fred("DGS2")
    else:
        evidence = probe_fred("DGS10")

    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

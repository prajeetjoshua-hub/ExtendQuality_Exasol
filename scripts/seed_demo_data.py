"""Deterministic synthetic records, never represented as measured factory data."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.db.exasol_client import AnalyticsRecord, AnalyticsUnavailable, save_records


def generate(seed=20260907):
    rng = random.Random(seed)
    for batch in range(3):
        for day in range(7):
            for index in range(40):
                unresolved = rng.random() < .05
                rejected = rng.random() < (.04 + day * .06 if batch == 0 else .08 if batch == 1 else .30 - day * .03)
                disposition = "REVIEW" if unresolved else "REJECT" if rejected else "ACCEPT"
                label = rng.choice(["rust", "displaced"]) if rejected else "normal"
                yield AnalyticsRecord(
                    inspection_id=f"synthetic-v1-{seed}-{batch}-{day}-{index}",
                    component_id=f"SIM-{batch}-{day}-{index}", component_type="6204",
                    batch_id=f"DEMO-B{batch+1}", machine_id=f"DEMO-M{batch+1}",
                    observed_at=datetime(2026, 9, 1, tzinfo=timezone.utc)+timedelta(days=day, minutes=index),
                    data_source="synthetic_demo", disposition=disposition, model_label=label,
                    model_confidence=None, image_quality_score=.85,
                    model_version="synthetic-generator-v1", vlm_mode="synthetic_not_invoked",
                    vlm_summary="Synthetic demonstration data; no image or model inference was run.", processing_time_ms=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-exasol", action="store_true", help="Explicitly insert synthetic data into configured Exasol")
    args = parser.parse_args()
    records = list(generate())
    if not args.write_exasol:
        print(json.dumps({"label": "Synthetic demonstration data", "rows": len(records), "example": records[0].model_dump(mode="json")}, indent=2))
        return 0
    from exasol_admin import load_environment
    load_environment()
    try:
        save_records(records)
    except AnalyticsUnavailable as exc:
        print(str(exc))
        return 1
    print(f"Committed {len(records)} synthetic demonstration records (idempotent IDs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

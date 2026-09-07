import os
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

import pytest
from pydantic import ValidationError

from backend.app.analytics.risk import assess_batch
from backend.app.db import exasol_client as exa
from scripts.seed_demo_data import generate


def test_seed_is_repeatable_and_honestly_labelled():
    first, second = list(generate()), list(generate())
    assert first == second and len(first) == 840
    assert len({r.inspection_id for r in first}) == 840
    assert {r.data_source for r in first} == {"synthetic_demo"}
    assert all(r.model_confidence is None for r in first)


def test_unknown_and_small_samples_are_not_low_risk():
    assert assess_batch(0, 0, 0)["score"] is None
    assert assess_batch(100, 0, 0)["level"] == "INSUFFICIENT_EVIDENCE"
    assert assess_batch(100, 19, 0)["score"] is None
    result = assess_batch(100, 80, 20)
    assert result["reject_rate"] == .25
    assert result["unresolved_rate"] == .2
    assert result["score"] == 24
    assert result["wilson_95"][0] < .25 < result["wilson_95"][1]


@pytest.mark.parametrize("counts", [(1,2,0), (1,1,2), (-1,0,0), (2,1,-1)])
def test_invalid_counts_fail(counts):
    with pytest.raises(ValueError):
        assess_batch(*counts)


def test_trend_requires_two_sufficient_observed_periods():
    daily = [{"day":"2026-09-02", "eligible":40, "rejected":10}, {"day":"2026-09-01", "eligible":40, "rejected":2}]
    assert assess_batch(80,80,12,daily)["trend"] == "rising"
    daily[0]["eligible"] = 19
    assert assess_batch(80,80,12,daily)["trend"] == "insufficient_evidence"


def test_record_rejects_nan_and_naive_timestamps():
    record = next(generate()).model_dump()
    with pytest.raises(ValidationError):
        exa.AnalyticsRecord(**{**record, "image_quality_score":float("nan")})
    with pytest.raises(ValidationError):
        exa.AnalyticsRecord(**{**record, "observed_at":datetime(2026,9,7)})


def test_disabled_database_fails_explicitly(monkeypatch):
    monkeypatch.setenv("EXASOL_ENABLED", "false")
    with pytest.raises(exa.AnalyticsUnavailable, match="disabled"):
        exa.health()


def test_schema_and_insert_use_driver_formatting(monkeypatch):
    calls = []
    class Fake:
        def execute(self, query, params=None): calls.append((query,params)); return self
        def commit(self): calls.append(("COMMIT",None))
    @contextmanager
    def fake_connection(): yield Fake(), "EQ_TEST"
    monkeypatch.setattr(exa, "connection", fake_connection)
    exa.initialize_schema()
    record = next(generate()).model_copy(update={"batch_id":"a'; DROP SCHEMA x; --"})
    exa.save_records([record])
    query, params = calls[-2]
    assert "DROP SCHEMA" not in query
    assert params["batch_id"] == record.batch_id
    assert "WHEN NOT MATCHED" in query and "WHEN MATCHED" not in query


def test_driver_errors_do_not_leak_secrets(monkeypatch):
    import pyexasol
    for key,value in {"EXASOL_ENABLED":"true", "EXASOL_DSN":"localhost:8563", "EXASOL_USER":"test", "EXASOL_PASSWORD":"private-value"}.items():
        monkeypatch.setenv(key,value)
    def fail(**kwargs): raise RuntimeError("private-value full SQL payload")
    monkeypatch.setattr(pyexasol,"connect",fail)
    with pytest.raises(exa.AnalyticsUnavailable) as caught:
        exa.health()
    assert "private-value" not in str(caught.value)


@pytest.mark.skipif(os.getenv("EXASOL_INTEGRATION") != "true", reason="Requires a real configured Exasol instance")
def test_real_exasol_roundtrip(monkeypatch):
    # Dedicated schema, no destructive cleanup of shared data.
    monkeypatch.setenv("EXASOL_SCHEMA", "EQ_INTEGRATION_TEST")
    exa.initialize_schema()
    records = list(generate())[:40]
    exa.save_records(records)
    exa.save_records(records)
    result = exa.analytics("synthetic_demo")
    assert int(result["overview"][0]["total"]) == 40
    assert not exa.analytics("prototype_inspection")["batches"]
    exa.save_reviews([{"inspection_id":records[0].inspection_id, "decision":"REJECT", "reviewed_at":"2026-09-07T12:00:00+00:00"}])
    assert exa.health()["status"] == "connected"

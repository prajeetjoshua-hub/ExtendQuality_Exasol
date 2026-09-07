import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import analytics_outbox as outbox
from backend.app.db.database import connect
from backend.app.db.exasol_client import AnalyticsUnavailable
from backend.tests.test_inspections import sample_image


def test_phone_accept_reject_updates_status_counts_and_keeps_model_evidence():
    with TestClient(app) as client:
        created = client.post("/api/inspections", files={"image":("phone.jpg",sample_image(),"image/jpeg")}, data={"capture_source":"camera","batch_id":"PHONE-B1"}).json()
        original = created["status"]
        before = client.get("/api/inspections/summary").json()["status_counts"]
        for decision in ("ACCEPT","REJECT"):
            review = client.post(f"/api/inspections/{created['id']}/review", json={"decision":decision})
            assert review.status_code == 200
            assert review.json()["status"] == decision
            detail = client.get(f"/api/inspections/{created['id']}").json()
            assert detail["status"] == decision
            assert detail["original_status"] == original
            assert detail["decision"]["disposition"] == original
        after = client.get("/api/inspections/summary").json()["status_counts"]
        assert after["REJECT"] == before["REJECT"] + 1
        assert after[original] == before[original] - 1


def test_outage_keeps_queue_and_retry_acknowledges_only_success(monkeypatch):
    with TestClient(app) as client:
        created = client.post("/api/inspections", files={"image":("bearing.jpg",sample_image(),"image/jpeg")}).json()
        assert created["exasol_status"] == "pending_configuration"
        def fail(records): raise AnalyticsUnavailable("offline")
        monkeypatch.setattr(outbox,"save_records",fail)
        pending = outbox.status()["pending"]
        with pytest.raises(AnalyticsUnavailable): outbox.flush()
        assert outbox.status()["pending"] == pending
        monkeypatch.setattr(outbox,"save_records",lambda records: None)
        monkeypatch.setattr(outbox,"save_reviews",lambda records: None)
        outbox.flush(1000)
        assert outbox.status()["pending"] == 0


def test_metadata_not_served_and_unavailable_not_fake_analytics():
    with TestClient(app) as client:
        assert client.get("/artifacts/metadata/extendquality.db").status_code == 404
        assert client.get("/api/analytics").status_code == 503
        assert client.get("/api/analytics?source=all").status_code == 422
        assert client.post("/api/inspections", files={"image":("bad.jpg",b"invalid","image/jpeg")}).status_code == 422

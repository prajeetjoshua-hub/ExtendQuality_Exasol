from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.inspection import VisionResult


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "vlm_provider" in payload
    assert isinstance(payload["vlm_configured"], bool)
    assert payload["service"] == "EXtendQuality API"


def test_warmup_exercises_model_without_creating_an_inspection(monkeypatch) -> None:
    from backend.app.api.routes import health as health_module

    class Detector:
        def inspect(self, image, edges) -> VisionResult:
            assert image.shape == (640, 640, 3)
            assert edges.shape == (640, 640)
            return VisionResult(mode="yolo_classifier", model_ready=True,
                                model_version="test.pt", detections=[],
                                note="warm")

    monkeypatch.setattr(health_module, "get_detector", lambda: Detector())
    with TestClient(app) as client:
        before = client.get("/api/inspections/summary").json()["total"]
        response = client.post("/api/warmup")
        after = client.get("/api/inspections/summary").json()["total"]

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["model_ready"] is True
    assert before == after

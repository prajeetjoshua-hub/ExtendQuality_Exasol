import cv2
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app


def sample_image() -> bytes:
    image = np.full((640, 640, 3), 160, dtype=np.uint8)
    cv2.circle(image, (320, 320), 220, (45, 45, 45), 45)
    cv2.circle(image, (320, 320), 110, (160, 160, 160), -1)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def test_create_list_and_review_inspection() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/inspections",
            files={"image": ("bearing.jpg", sample_image(), "image/jpeg")},
            data={"bearing_type": "6204"},
        )
        assert created.status_code == 201
        payload = created.json()
        assert payload["bearing_type"] == "6204"
        assert payload["capture_source"] == "upload"
        assert payload["vision_result"]["mode"] in {
            "yolo_classifier",
            "opencv_contour_fallback",
        }
        assert payload["decision"]["disposition"] in {
            "ACCEPT",
            "REJECT",
            "RECAPTURE",
            "REVIEW",
        }

        history = client.get("/api/inspections")
        assert history.status_code == 200
        assert any(item["id"] == payload["id"] for item in history.json())

        summary = client.get("/api/inspections/summary")
        assert summary.status_code == 200
        analytics = summary.json()
        assert analytics["total"] >= 1
        assert sum(analytics["status_counts"].values()) == analytics["total"]
        assert analytics["average_processing_time_ms"] >= 0

        review = client.post(
            f"/api/inspections/{payload['id']}/review",
            json={"decision": "ACCEPT", "reason": "Mentor demo verification"},
        )
        assert review.status_code == 200
        assert review.json()["review_status"] == "reviewed"

        reviewed_summary = client.get("/api/inspections/summary").json()
        assert reviewed_summary["reviewed"] >= 1


def test_camera_capture_is_never_automatically_accepted_or_rejected() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/inspections",
            files={"image": ("camera.jpg", sample_image(), "image/jpeg")},
            data={"bearing_type": "6204", "capture_source": "camera"},
        )
    assert created.status_code == 201
    payload = created.json()
    assert payload["capture_source"] == "camera"
    assert payload["status"] in {"REVIEW", "RECAPTURE"}
    if payload["status"] == "REVIEW":
        assert payload["decision"]["needs_vlm"] is True
        assert "not validated" in payload["decision"]["reasons"][0]


def test_rejects_non_image_upload() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/inspections",
            files={"image": ("notes.txt", b"not an image", "text/plain")},
        )
    assert response.status_code == 415

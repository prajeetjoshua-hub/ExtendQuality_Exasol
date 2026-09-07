"""Exercise actual Exasol + current API in isolated local storage/test schema."""
import json
from io import BytesIO
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exasol_admin import load_environment


def main():
    load_environment()
    os.environ["EXASOL_SCHEMA"] = "EQ_PIPELINE_TEST"
    os.environ["EXTENDQUALITY_VLM_PROVIDER"] = "demo"
    with tempfile.TemporaryDirectory(prefix="eq-pipeline-") as temporary:
        os.environ["EXTENDQUALITY_STORAGE_PATH"] = temporary
        os.environ["EXTENDQUALITY_DATABASE_PATH"] = str(Path(temporary) / "metadata.db")
        os.environ["YOLO_CONFIG_DIR"] = str(Path(temporary) / "ultralytics")
        os.environ["EXTENDQUALITY_YOLO_WEIGHTS"] = str(Path(temporary) / "no-model.pt")
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.db.exasol_client import initialize_schema
        initialize_schema()
        with TestClient(app) as client:
            baseline = client.get("/api/analytics").json()["overview"][0]["total"]
            from PIL import Image, ImageDraw
            fixture = Image.new("RGB", (640, 480), (180, 180, 180))
            draw = ImageDraw.Draw(fixture)
            draw.ellipse((170, 90, 470, 390), fill=(45, 45, 45))
            draw.ellipse((235, 155, 405, 325), fill=(200, 200, 200))
            buffer = BytesIO()
            fixture.save(buffer, format="JPEG")
            photo = buffer.getvalue()
            uploaded = client.post("/api/inspections", files={"image":("prepared.jpg", photo, "image/jpeg")},
                                   data={"capture_source":"camera","batch_id":"PIPELINE-TEST","machine_id":"GENERATED-FIXTURE"})
            assert uploaded.status_code == 201
            record = uploaded.json()
            assert record["exasol_status"] == "saved", record["exasol_status"]
            assert record["status"] == "REVIEW"
            current = client.get("/api/analytics").json()
            assert current["overview"][0]["total"] == baseline + 1
            actions = []
            for decision in ("ACCEPT", "REJECT"):
                review = client.post(f"/api/inspections/{record['id']}/review",json={"decision":decision,"reason":"Automated end-to-end test on artificial fixture; not a product-quality assessment"})
                assert review.status_code == 200
                assert review.json()["status"] == decision
                history = client.get("/api/analytics").json()["history"]
                assert next(r for r in history if r["inspection_id"] == record["id"])["disposition"] == decision
                detail = client.get(f"/api/inspections/{record['id']}").json()
                assert detail["original_status"] == "REVIEW" and detail["status"] == decision
                actions.append({"decision":decision,"exasol_status":review.json()["exasol_status"]})
            health = client.get("/api/analytics/health").json()
            assert health["pending"] == 0
            print(json.dumps({"passed":True,"schema":"EQ_PIPELINE_TEST","capture":"generated artificial fixture via camera route; no real product, trained model or live camera validation",
                              "initial_status":record["status"],"classification":record["vision_result"]["classification"],"reviews":actions,"pending":health["pending"]},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

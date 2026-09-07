"""Run the four fixed SSN demo cases through an isolated EXtendQuality session."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))
CASES = (
    ("normal", "d1c83ab19c7b467082bf513c8516d378.jpg", "normal", "ACCEPT", False),
    ("displaced", "974fdfd1b1564360a8a5c16bd648fd3c.jpg", "displaced", "REJECT", False),
    ("rust", "7f8e3e9a4924486a8ef38419bd878cd3.jpg", "rust", "REJECT", False),
    ("uncertain", "6df2224d3a4c45409d6b2526b47e28c4.jpg", "displaced", "REVIEW", True),
)


def main() -> int:
    missing = [name for _, name, *_ in CASES if not (REPOSITORY_ROOT / "storage" / "raw" / name).is_file()]
    if missing:
        print("Rehearsal cannot start. Missing prepared image(s):", ", ".join(missing))
        return 2

    with tempfile.TemporaryDirectory(prefix="extendquality_rehearsal_", ignore_cleanup_errors=True) as workspace:
        os.environ["EXTENDQUALITY_STORAGE_PATH"] = workspace
        os.environ["EXTENDQUALITY_DATABASE_PATH"] = str(Path(workspace) / "metadata.db")
        os.environ["EXTENDQUALITY_VLM_PROVIDER"] = "demo"
        config_dir = REPOSITORY_ROOT / ".demo-runtime" / "rehearsal-ultralytics"
        config_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))

        from fastapi.testclient import TestClient
        from backend.app.main import app

        results: list[dict] = []
        with TestClient(app) as client:
            for scenario, filename, expected_label, expected_status, expected_vlm in CASES:
                path = REPOSITORY_ROOT / "storage" / "raw" / filename
                with path.open("rb") as image:
                    response = client.post(
                        "/api/inspections",
                        files={"image": (filename, image, "image/jpeg")},
                        data={"bearing_type": "6204" if scenario != "uncertain" else "8-ball test"},
                    )
                payload = response.json()
                classification = payload.get("vision_result", {}).get("classification") or {}
                actual = (
                    classification.get("label"),
                    payload.get("status"),
                    payload.get("decision", {}).get("needs_vlm"),
                )
                expected = (expected_label, expected_status, expected_vlm)
                passed = response.status_code == 201 and actual == expected
                results.append(
                    {
                        "scenario": scenario,
                        "passed": passed,
                        "label": classification.get("label"),
                        "confidence": classification.get("confidence"),
                        "status": payload.get("status"),
                        "needs_vlm": payload.get("decision", {}).get("needs_vlm"),
                        "vlm_mode": payload.get("vlm_result", {}).get("mode"),
                        "processing_time_ms": payload.get("processing_time_ms"),
                    }
                )
            summary = client.get("/api/inspections/summary").json()

    report = {"passed": all(item["passed"] for item in results) and summary.get("total") == 4,
              "cases": results, "summary": summary,
              "note": (
                  "The first case includes one-time model loading; warm the model before presenting. "
                  "This isolated startup rehearsal intentionally forces offline VLM mode; verify Gemini "
                  "through the running API or dashboard."
              )}
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

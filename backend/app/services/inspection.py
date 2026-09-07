from datetime import datetime, timezone
import json
from time import perf_counter
from uuid import uuid4

import cv2

from backend.app.db.database import create_inspection
from backend.app.schemas.inspection import ArtifactUrls, DecisionResult, InspectionResponse
from backend.app.services.decision.engine import decide
from backend.app.services.storage import artifact_path, artifact_url, safe_suffix
from backend.app.services.vision.detector import draw_overlay, get_detector
from backend.app.services.vision.preprocessor import decode_and_preprocess
from backend.app.services.vlm.adapter import analyze


def run_inspection(
    content: bytes,
    filename: str | None,
    bearing_type: str,
    capture_source: str = "upload",
    batch_id: str = "UNASSIGNED",
    machine_id: str = "UNASSIGNED",
    component_id: str = "",
) -> InspectionResponse:
    started = perf_counter()
    inspection_id = uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    suffix = safe_suffix(filename)

    preprocessed = decode_and_preprocess(content)
    vision = get_detector().inspect(preprocessed.original, preprocessed.edges)
    decision = decide(preprocessed.quality, vision)
    if capture_source == "camera" and decision.disposition != "RECAPTURE":
        decision = DecisionResult(
            disposition="REVIEW",
            score=decision.score,
            needs_vlm=True,
            reasons=[
                "Live-camera transfer is not validated; the class prediction is evidence only and requires inspector review.",
                *decision.reasons,
            ],
        )
    vlm = analyze(preprocessed.quality, vision, decision, content)
    overlay = draw_overlay(preprocessed.original, vision)

    raw_path = artifact_path("raw", inspection_id, suffix)
    processed_path = artifact_path("processed", inspection_id)
    overlay_path = artifact_path("overlays", inspection_id)
    raw_path.write_bytes(content)
    if not cv2.imwrite(str(processed_path), preprocessed.enhanced):
        raise RuntimeError("Could not save the processed inspection image.")
    if not cv2.imwrite(str(overlay_path), overlay):
        raise RuntimeError("Could not save the inspection overlay.")

    elapsed_ms = round((perf_counter() - started) * 1000, 2)
    response = InspectionResponse(
        id=inspection_id,
        created_at=created_at,
        bearing_type=bearing_type,
        capture_source=capture_source,
        status=decision.disposition,
        image_quality=preprocessed.quality,
        vision_result=vision,
        decision=decision,
        vlm_result=vlm,
        artifacts=ArtifactUrls(
            processed=artifact_url("processed", inspection_id),
            overlay=artifact_url("overlays", inspection_id),
        ),
        review_status="pending",
        processing_time_ms=elapsed_ms,
    )
    create_inspection(
        {
            "id": inspection_id,
            "created_at": created_at,
            "bearing_type": bearing_type,
            "status": decision.disposition,
            "raw_image_path": str(raw_path),
            "processed_image_path": str(processed_path),
            "overlay_image_path": str(overlay_path),
            "image_quality_json": preprocessed.quality.model_dump_json(),
            "yolo_result_json": vision.model_dump_json(),
            "geometry_result_json": json.dumps(
                {"status": "planned", "capture_source": capture_source}
            ),
            "decision_json": decision.model_dump_json(),
            "vlm_result_json": vlm.model_dump_json(),
            "review_status": "pending",
            "model_version": vision.model_version,
            "processing_time_ms": elapsed_ms,
        }
    )
    from backend.app.db.analytics_outbox import record_result
    response.batch_id = batch_id
    response.machine_id = machine_id
    response.component_id = component_id.strip() or response.id
    try:
        response.exasol_status = record_result(response, batch_id, machine_id, response.component_id)
    except Exception:
        # The original inspection is already durably stored. Do not fabricate SQL success.
        response.exasol_status = "queue_failed"
    return response

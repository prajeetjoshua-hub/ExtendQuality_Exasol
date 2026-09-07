from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from backend.app.core.config import get_settings
from backend.app.db.database import (
    get_inspection,
    inspection_summary,
    list_inspections,
    save_human_review,
)
from backend.app.schemas.inspection import (
    HumanReviewRequest,
    HumanReviewResponse,
    InspectionResponse,
)
from backend.app.services.inspection import run_inspection


router = APIRouter(prefix="/inspections", tags=["inspections"])
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection_endpoint(
    image: Annotated[UploadFile, File(description="Captured bearing image")],
    bearing_type: Annotated[str, Form(min_length=1, max_length=50)] = "6204",
    capture_source: Annotated[str, Form(pattern="^(upload|camera)$")] = "upload",
    batch_id: Annotated[str, Form(min_length=1, max_length=80, pattern=r".*\S.*")] = "UNASSIGNED",
    machine_id: Annotated[str, Form(min_length=1, max_length=80, pattern=r".*\S.*")] = "UNASSIGNED",
    component_id: Annotated[str, Form(max_length=80)] = "",
) -> InspectionResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image.")
    content = await image.read(get_settings().max_upload_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(content) > get_settings().max_upload_bytes:
        raise HTTPException(status_code=413, detail="The image exceeds the 10 MB prototype limit.")
    try:
        return await run_in_threadpool(
            run_inspection, content, image.filename, bearing_type, capture_source, batch_id, machine_id, component_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("")
def inspection_history(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    return list_inspections(limit)


@router.get("/summary")
def inspection_analytics() -> dict:
    return inspection_summary()


@router.get("/{inspection_id}")
def inspection_detail(inspection_id: str) -> dict:
    record = get_inspection(inspection_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Inspection not found.")
    return record


@router.post("/{inspection_id}/review", response_model=HumanReviewResponse)
def review_inspection(
    inspection_id: str, payload: HumanReviewRequest
) -> HumanReviewResponse:
    if not save_human_review(inspection_id, payload.decision, payload.reason):
        raise HTTPException(status_code=404, detail="Inspection not found.")
    from backend.app.db.analytics_outbox import flush, inspection_status
    from backend.app.db.exasol_client import AnalyticsUnavailable
    sync_status = "pending_retry"
    try:
        flush()
    except AnalyticsUnavailable:
        pass
    sync_status = inspection_status(inspection_id)
    return HumanReviewResponse(
        status=payload.decision,
        exasol_status=sync_status,
        inspection_id=inspection_id,
        review_status="reviewed",
        human_decision=payload.decision,
    )

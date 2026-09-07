from typing import Literal

from pydantic import BaseModel, Field


Disposition = Literal["ACCEPT", "REJECT", "RECAPTURE", "REVIEW", "SYSTEM_HOLD"]


class ImageQuality(BaseModel):
    score: float = Field(ge=0, le=1)
    blur_score: float = Field(ge=0, le=1)
    exposure_score: float = Field(ge=0, le=1)
    contrast_score: float = Field(ge=0, le=1)
    edge_density: float = Field(ge=0, le=1)
    width: int
    height: int
    issues: list[str]


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    box: tuple[int, int, int, int]


class Classification(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[str, float]


class VisionResult(BaseModel):
    mode: Literal["yolo", "yolo_classifier", "opencv_contour_fallback"]
    model_ready: bool
    model_version: str
    detections: list[Detection]
    classification: Classification | None = None
    note: str


class DecisionResult(BaseModel):
    disposition: Disposition
    score: float = Field(ge=0, le=1)
    needs_vlm: bool
    reasons: list[str]


class VlmResult(BaseModel):
    invoked: bool
    mode: Literal["not_required", "gemini", "offline_fallback", "not_configured"]
    analysis: str
    recommendation: str
    disclaimer: str


class ArtifactUrls(BaseModel):
    processed: str
    overlay: str


class InspectionResponse(BaseModel):
    exasol_status: str = "pending_configuration"
    batch_id: str = "UNASSIGNED"
    machine_id: str = "UNASSIGNED"
    component_id: str = ""
    id: str
    created_at: str
    bearing_type: str
    capture_source: Literal["upload", "camera"]
    status: Disposition
    image_quality: ImageQuality
    vision_result: VisionResult
    decision: DecisionResult
    vlm_result: VlmResult
    artifacts: ArtifactUrls
    review_status: str
    processing_time_ms: float


class HumanReviewRequest(BaseModel):
    decision: Literal["ACCEPT", "REJECT"]
    reason: str | None = Field(default=None, max_length=500)


class HumanReviewResponse(BaseModel):
    status: Literal["ACCEPT", "REJECT"]
    exasol_status: str = "pending_retry"
    inspection_id: str
    review_status: Literal["reviewed"]
    human_decision: Literal["ACCEPT", "REJECT"]

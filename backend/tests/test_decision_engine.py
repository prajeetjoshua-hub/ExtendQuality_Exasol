from backend.app.schemas.inspection import Classification, Detection, ImageQuality, VisionResult
from backend.app.services.decision.engine import decide


def quality(score: float) -> ImageQuality:
    return ImageQuality(
        score=score,
        blur_score=score,
        exposure_score=score,
        contrast_score=score,
        edge_density=0.1,
        width=1280,
        height=720,
        issues=["Poor capture"] if score < 0.45 else [],
    )


def test_low_quality_frame_requests_recapture() -> None:
    result = decide(
        quality(0.2),
        VisionResult(
            mode="opencv_contour_fallback",
            model_ready=False,
            model_version="not_loaded",
            detections=[],
            note="fallback",
        ),
    )
    assert result.disposition == "RECAPTURE"
    assert result.needs_vlm is False


def test_high_confidence_yolo_defect_is_rejected() -> None:
    result = decide(
        quality(0.9),
        VisionResult(
            mode="yolo",
            model_ready=True,
            model_version="test.pt",
            detections=[Detection(label="scratch", confidence=0.92, box=(1, 2, 3, 4))],
            note="model",
        ),
    )
    assert result.disposition == "REJECT"
    assert result.needs_vlm is False


def classification(label: str, confidence: float) -> Classification:
    return Classification(
        label=label,
        confidence=confidence,
        probabilities={label: confidence},
    )


def test_high_confidence_normal_classification_is_accepted() -> None:
    result = decide(
        quality(0.9),
        VisionResult(
            mode="yolo_classifier",
            model_ready=True,
            model_version="test.pt",
            detections=[],
            classification=classification("normal", 0.91),
            note="classifier",
        ),
    )
    assert result.disposition == "ACCEPT"
    assert result.needs_vlm is False


def test_uncertain_displaced_classification_routes_to_vlm() -> None:
    result = decide(
        quality(0.9),
        VisionResult(
            mode="yolo_classifier",
            model_ready=True,
            model_version="test.pt",
            detections=[],
            classification=classification("displaced", 0.62),
            note="classifier",
        ),
    )
    assert result.disposition == "REVIEW"
    assert result.needs_vlm is True

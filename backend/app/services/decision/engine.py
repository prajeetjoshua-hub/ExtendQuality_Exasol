from backend.app.core.config import get_settings
from backend.app.schemas.inspection import DecisionResult, ImageQuality, VisionResult
from backend.app.services.vision.detector import DEFECT_TERMS


def decide(quality: ImageQuality, vision: VisionResult) -> DecisionResult:
    settings = get_settings()
    if quality.score < settings.recapture_quality_threshold:
        return DecisionResult(
            disposition="RECAPTURE",
            score=round(1 - quality.score, 3),
            needs_vlm=False,
            reasons=quality.issues or ["The frame failed the image-quality gate."],
        )

    if not vision.model_ready:
        return DecisionResult(
            disposition="REVIEW",
            score=0.5,
            needs_vlm=True,
            reasons=[
                "No validated YOLO weights are loaded.",
                "OpenCV proposals are evidence for review, not defect classifications.",
            ],
        )

    if vision.classification is not None:
        label = vision.classification.label.lower()
        confidence = vision.classification.confidence
        if label == "normal":
            if confidence >= settings.normal_accept_threshold:
                return DecisionResult(
                    disposition="ACCEPT",
                    score=confidence,
                    needs_vlm=False,
                    reasons=["The frame was classified as normal above the acceptance threshold."],
                )
            return DecisionResult(
                disposition="REVIEW",
                score=confidence,
                needs_vlm=True,
                reasons=["Normal was predicted, but confidence is below the automatic acceptance threshold."],
            )
        if label in {"displaced", "rust"}:
            if confidence >= settings.decision_confidence_threshold:
                action = (
                    "abnormal ball arrangement"
                    if label == "displaced"
                    else "rust-or-grease surface condition"
                )
                return DecisionResult(
                    disposition="REJECT",
                    score=confidence,
                    needs_vlm=False,
                    reasons=[f"The classifier found {action} above the rejection threshold."],
                )
            return DecisionResult(
                disposition="REVIEW",
                score=confidence,
                needs_vlm=True,
                reasons=[f"Possible {label} was predicted below the automatic rejection threshold."],
            )
        return DecisionResult(
            disposition="REVIEW",
            score=confidence,
            needs_vlm=True,
            reasons=[f"The classifier returned the unsupported label '{label}'."],
        )

    defects = [
        item
        for item in vision.detections
        if any(term in item.label.lower() for term in DEFECT_TERMS)
    ]
    if defects:
        confidence = max(item.confidence for item in defects)
        if confidence >= settings.decision_confidence_threshold:
            return DecisionResult(
                disposition="REJECT",
                score=confidence,
                needs_vlm=False,
                reasons=["YOLO localized a known defect above the decision threshold."],
            )
        return DecisionResult(
            disposition="REVIEW",
            score=confidence,
            needs_vlm=True,
            reasons=["A possible known defect was found below the automatic threshold."],
        )

    return DecisionResult(
        disposition="REVIEW",
        score=0.55,
        needs_vlm=True,
        reasons=["No high-confidence known defect was found; human confirmation is required."],
    )

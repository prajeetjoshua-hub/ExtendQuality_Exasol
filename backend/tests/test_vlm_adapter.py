import json

import httpx

from backend.app.core.config import Settings
from backend.app.schemas.inspection import Classification, DecisionResult, ImageQuality, VisionResult
from backend.app.services.vlm.adapter import _analyze_gemini, analyze


def quality() -> ImageQuality:
    return ImageQuality(score=0.88, blur_score=0.9, exposure_score=0.84, contrast_score=0.86,
                        edge_density=0.12, width=1280, height=720, issues=[])


def vision() -> VisionResult:
    return VisionResult(mode="yolo_classifier", model_ready=True, model_version="test.pt",
                        detections=[], classification=Classification(label="rust", confidence=0.61,
                        probabilities={"rust": 0.61, "normal": 0.39}), note="classifier")


def review_decision() -> DecisionResult:
    return DecisionResult(disposition="REVIEW", score=0.61, needs_vlm=True,
                          reasons=["Below automatic threshold."])


def settings() -> Settings:
    from backend.app.core.config import get_settings
    current = get_settings()
    return Settings(**{**current.__dict__, "vlm_provider": "gemini", "vlm_api_key": "test-key"})


def test_terminal_decision_never_invokes_vlm() -> None:
    decision = DecisionResult(disposition="REJECT", score=0.92, needs_vlm=False, reasons=["Certain"])
    result = analyze(quality(), vision(), decision, b"image")
    assert result.mode == "not_required"
    assert result.invoked is False


def test_gemini_response_is_grounded_and_parsed(monkeypatch) -> None:
    class Response:
        def raise_for_status(self) -> None: pass
        def json(self) -> dict:
            output = {"observation": "Rust-like discoloration is visible.",
                      "recommended_action": "Clean and recapture for inspector confirmation."}
            return {"candidates": [{"content": {"parts": [{"text": json.dumps(output)}]}}]}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())
    result = _analyze_gemini(settings(), quality(), vision(), b"jpeg-bytes")
    assert result.mode == "gemini"
    assert result.invoked is True
    assert "Rust-like" in result.analysis


def test_missing_key_uses_safe_fallback(monkeypatch) -> None:
    from backend.app.services.vlm import adapter
    no_key = Settings(**{**settings().__dict__, "vlm_api_key": ""})
    monkeypatch.setattr(adapter, "get_settings", lambda: no_key)
    result = analyze(quality(), vision(), review_decision(), b"image")
    assert result.mode == "offline_fallback"
    assert result.invoked is False
    assert "final" not in result.recommendation.lower()

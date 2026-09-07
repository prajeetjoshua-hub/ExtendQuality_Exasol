import base64
import json

import httpx

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.inspection import DecisionResult, ImageQuality, VisionResult, VlmResult


RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "observation": {"type": "STRING"},
        "recommended_action": {"type": "STRING"},
    },
    "required": ["observation", "recommended_action"],
}


def _image_mime_type(image_bytes: bytes) -> str:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _offline_fallback(quality: ImageQuality, vision: VisionResult, reason: str) -> VlmResult:
    if vision.classification is not None:
        label = vision.classification.label.lower()
        evidence = (
            f"Local vision predicted {vision.classification.label} at "
            f"{vision.classification.confidence:.1%} confidence."
        )
        if label == "displaced":
            action = "Hold for inspector review and verify all eight balls are evenly spaced before deciding."
        elif label == "rust":
            action = "Hold for inspector review; clean and recapture because the current class cannot separate rust from grease or staining."
        else:
            action = "Hold for inspector review and recapture under controlled lighting if uncertainty remains."
    else:
        evidence = f"Local vision marked {len(vision.detections)} region(s) for review."
        action = "Hold for inspector review; clean and recapture if the bearing surface is obscured."
    return VlmResult(
        invoked=False,
        mode="offline_fallback",
        analysis=f"{evidence} Image-quality score: {quality.score:.0%}.",
        recommendation=action,
        disclaimer=f"VLM unavailable ({reason}). This fallback uses measured local evidence only.",
    )


def _analyze_gemini(
    settings: Settings,
    quality: ImageQuality,
    vision: VisionResult,
    image_bytes: bytes,
) -> VlmResult:
    evidence = vision.model_dump(mode="json")
    prompt = (
        "You are assisting a human bearing inspector. Inspect only the supplied image and local "
        "vision evidence. Describe visible surface or ball-arrangement evidence without claiming "
        "millimetre precision, hidden damage, or safety certification. Never make the final accept/"
        "reject decision. Return a concise observation and a reversible next action. "
        f"Image quality: {quality.model_dump_json()}. Local vision evidence: {json.dumps(evidence)}"
    )
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {
                "mime_type": _image_mime_type(image_bytes),
                "data": base64.b64encode(image_bytes).decode("ascii"),
            }},
        ]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 512,
            "thinkingConfig": {"thinkingLevel": "minimal"},
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.vlm_model}:generateContent"
    response = httpx.post(
        url,
        headers={"x-goog-api-key": settings.vlm_api_key},
        json=payload,
        timeout=settings.vlm_timeout_seconds,
    )
    response.raise_for_status()
    body = response.json()
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(text)
    for field in ("observation", "recommended_action"):
        if not isinstance(parsed[field], str) or not parsed[field].strip() or len(parsed[field]) > 4000:
            raise ValueError("Malformed VLM response.")
    return VlmResult(
        invoked=True,
        mode="gemini",
        analysis=str(parsed["observation"]).strip(),
        recommendation=str(parsed["recommended_action"]).strip(),
        disclaimer=(
            f"Gemini {settings.vlm_model} assisted only because local evidence was uncertain. "
            "The inspector remains the final authority."
        ),
    )


def analyze(
    quality: ImageQuality,
    vision: VisionResult,
    decision: DecisionResult,
    image_bytes: bytes = b"",
) -> VlmResult:
    if not decision.needs_vlm:
        return VlmResult(
            invoked=False,
            mode="not_required",
            analysis="The deterministic quality and detection gates produced a terminal result.",
            recommendation=decision.disposition,
            disclaimer="No VLM was used for this inspection.",
        )

    settings = get_settings()
    if settings.vlm_provider == "gemini":
        if not settings.vlm_api_key:
            return _offline_fallback(quality, vision, "API key is not configured")
        if not image_bytes:
            return _offline_fallback(quality, vision, "inspection image is unavailable")
        try:
            return _analyze_gemini(settings, quality, vision, image_bytes)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
            return _offline_fallback(quality, vision, "provider request failed")

    if settings.vlm_provider != "demo":
        return VlmResult(
            invoked=False,
            mode="not_configured",
            analysis="The case requires semantic review, but no VLM provider is configured.",
            recommendation="Ask the inspector to review the original image and overlay.",
            disclaimer="This is a system status message, not an AI visual assessment.",
        )

    return _offline_fallback(quality, vision, "offline demo mode")

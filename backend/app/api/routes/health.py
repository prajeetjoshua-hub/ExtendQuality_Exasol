from datetime import datetime, timezone
from time import perf_counter

import cv2
import numpy as np
from fastapi import APIRouter

from backend.app.core.config import get_settings
from backend.app.services.vision.detector import get_detector


router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, object]:
    """Return a lightweight readiness response for frontend connection tests."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "vlm_provider": settings.vlm_provider,
        "vlm_configured": settings.vlm_provider == "gemini" and bool(settings.vlm_api_key),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/warmup")
def warmup() -> dict:
    """Load and exercise the local model before a latency-sensitive demo."""
    started = perf_counter()
    image = np.full((640, 640, 3), 160, dtype=np.uint8)
    cv2.circle(image, (320, 320), 220, (45, 45, 45), 45)
    cv2.circle(image, (320, 320), 110, (160, 160, 160), -1)
    edges = cv2.Canny(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 80, 160)
    result = get_detector().inspect(image, edges)
    return {
        "status": "ready" if result.model_ready else "degraded",
        "model_ready": result.model_ready,
        "model_version": result.model_version,
        "mode": result.mode,
        "warmup_time_ms": round((perf_counter() - started) * 1000, 2),
        "note": "Synthetic warm-up only; this is not an inspection or accuracy result.",
    }

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _repository_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPOSITORY_ROOT / path


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    database_path: Path
    storage_path: Path
    allowed_origins: list[str]
    max_upload_bytes: int
    yolo_weights_path: Path
    yolo_confidence_threshold: float
    decision_confidence_threshold: float
    normal_accept_threshold: float
    recapture_quality_threshold: float
    vlm_provider: str
    vlm_api_key: str
    vlm_model: str
    vlm_timeout_seconds: float


@lru_cache
def get_settings() -> Settings:
    origins = os.getenv(
        "EXTENDQUALITY_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    )
    return Settings(
        app_name="EXtendQuality API",
        environment=os.getenv("EXTENDQUALITY_ENVIRONMENT", "development"),
        database_path=_repository_path(
            os.getenv(
                "EXTENDQUALITY_DATABASE_PATH",
                "storage/metadata/extendquality.db",
            )
        ),
        storage_path=_repository_path(
            os.getenv("EXTENDQUALITY_STORAGE_PATH", "storage")
        ),
        allowed_origins=[item.strip() for item in origins.split(",") if item.strip()],
        max_upload_bytes=int(
            os.getenv("EXTENDQUALITY_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))
        ),
        yolo_weights_path=_repository_path(
            os.getenv(
                "EXTENDQUALITY_YOLO_WEIGHTS",
                "models/weights/bearing_real_3class.pt",
            )
        ),
        yolo_confidence_threshold=float(
            os.getenv("EXTENDQUALITY_YOLO_CONFIDENCE", "0.35")
        ),
        decision_confidence_threshold=float(
            os.getenv("EXTENDQUALITY_DECISION_CONFIDENCE", "0.70")
        ),
        normal_accept_threshold=float(
            os.getenv("EXTENDQUALITY_NORMAL_ACCEPT_CONFIDENCE", "0.80")
        ),
        recapture_quality_threshold=float(
            os.getenv("EXTENDQUALITY_RECAPTURE_QUALITY", "0.45")
        ),
        vlm_provider=os.getenv("EXTENDQUALITY_VLM_PROVIDER", "demo").lower(),
        vlm_api_key=os.getenv("EXTENDQUALITY_VLM_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip(),
        vlm_model=os.getenv("EXTENDQUALITY_VLM_MODEL", "gemini-3.6-flash").strip(),
        vlm_timeout_seconds=float(os.getenv("EXTENDQUALITY_VLM_TIMEOUT_SECONDS", "45")),
    )

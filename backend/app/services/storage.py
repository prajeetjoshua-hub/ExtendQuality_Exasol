from pathlib import Path
import re

from backend.app.core.config import get_settings


SAFE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def prepare_storage() -> None:
    root = get_settings().storage_path
    for folder in ("raw", "processed", "overlays", "reviewed", "training_candidates", "metadata"):
        (root / folder).mkdir(parents=True, exist_ok=True)


def safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "capture.jpg").suffix.lower()
    return suffix if suffix in SAFE_SUFFIXES else ".jpg"


def artifact_path(folder: str, inspection_id: str, suffix: str = ".jpg") -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", inspection_id)
    return get_settings().storage_path / folder / f"{safe_id}{suffix}"


def artifact_url(folder: str, inspection_id: str, suffix: str = ".jpg") -> str:
    return f"/artifacts/{folder}/{inspection_id}{suffix}"

import sqlite3
import json
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Any

from backend.app.core.config import get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    bearing_type TEXT NOT NULL,
    status TEXT NOT NULL,
    raw_image_path TEXT,
    processed_image_path TEXT,
    overlay_image_path TEXT,
    image_quality_json TEXT,
    yolo_result_json TEXT,
    geometry_result_json TEXT,
    decision_json TEXT,
    vlm_result_json TEXT,
    human_decision TEXT,
    human_reason TEXT,
    review_status TEXT NOT NULL DEFAULT 'pending',
    model_version TEXT,
    processing_time_ms REAL
);
CREATE INDEX IF NOT EXISTS idx_inspections_created_at
ON inspections(created_at DESC);
CREATE TABLE IF NOT EXISTS human_review_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT,
    reviewed_at TEXT NOT NULL,
    synced INTEGER NOT NULL DEFAULT 0
);
"""


@contextmanager
def connect():
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the prototype metadata database without storing image blobs."""
    with connect() as connection:
        connection.executescript(SCHEMA)


def create_inspection(record: dict[str, Any]) -> None:
    columns = ", ".join(record)
    placeholders = ", ".join("?" for _ in record)
    with connect() as connection:
        connection.execute(
            f"INSERT INTO inspections ({columns}) VALUES ({placeholders})",
            tuple(record.values()),
        )


def get_inspection(inspection_id: str) -> dict[str, Any] | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM inspections WHERE id = ?", (inspection_id,)
        ).fetchone()
    return _deserialize_row(row) if row else None


def list_inspections(limit: int = 20) -> list[dict[str, Any]]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM inspections ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_deserialize_row(row) for row in rows]


def inspection_summary() -> dict[str, Any]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT COALESCE(human_decision,status) AS status, review_status, processing_time_ms, yolo_result_json
            FROM inspections
            """
        ).fetchall()

    status_counts = {key: 0 for key in ("ACCEPT", "REJECT", "RECAPTURE", "REVIEW", "SYSTEM_HOLD")}
    class_counts: dict[str, int] = {}
    reviewed = 0
    processing_times: list[float] = []
    for row in rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["review_status"] == "reviewed":
            reviewed += 1
        if row["processing_time_ms"] is not None:
            processing_times.append(float(row["processing_time_ms"]))
        payload = json.loads(row["yolo_result_json"]) if row["yolo_result_json"] else {}
        classification = payload.get("classification") or {}
        label = classification.get("label")
        if label:
            class_counts[label] = class_counts.get(label, 0) + 1

    total = len(rows)
    return {
        "total": total,
        "status_counts": status_counts,
        "class_counts": class_counts,
        "reviewed": reviewed,
        "pending_review": total - reviewed,
        "average_processing_time_ms": round(sum(processing_times) / len(processing_times), 2)
        if processing_times
        else 0.0,
    }


def save_human_review(
    inspection_id: str, decision: str, reason: str | None
) -> bool:
    if decision not in {"ACCEPT", "REJECT"}:
        raise ValueError("Review must be ACCEPT or REJECT.")
    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE inspections
            SET human_decision = ?, human_reason = ?, review_status = 'reviewed'
            WHERE id = ?
            """,
            (decision, reason, inspection_id),
        )
        if cursor.rowcount == 1:
            connection.execute("INSERT INTO human_review_events (inspection_id,decision,reason,reviewed_at) VALUES (?,?,?,?)",
                               (inspection_id, decision, reason, datetime.now(timezone.utc).isoformat()))
    return cursor.rowcount == 1


def _deserialize_row(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["original_status"] = result["status"]
    result["status"] = result["human_decision"] or result["status"]
    for key in (
        "image_quality_json",
        "yolo_result_json",
        "geometry_result_json",
        "decision_json",
        "vlm_result_json",
    ):
        value = result.pop(key, None)
        result[key.removesuffix("_json")] = json.loads(value) if value else None
    return result

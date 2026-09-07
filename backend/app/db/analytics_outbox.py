"""Durable capture journal queue. Only acknowledge after Exasol commits."""
import json

from backend.app.db.database import connect
from backend.app.db.exasol_client import AnalyticsRecord, AnalyticsUnavailable, enabled, save_records, save_reviews


def initialize_outbox():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS analytics_outbox (
            inspection_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
            synced INTEGER NOT NULL DEFAULT 0)""")


def enqueue(record: AnalyticsRecord):
    with connect() as conn:
        conn.execute("INSERT OR IGNORE INTO analytics_outbox (inspection_id,payload) VALUES (?,?)",
                     (record.inspection_id, record.model_dump_json()))


def status():
    with connect() as conn:
        pending = conn.execute("SELECT COUNT(*) FROM analytics_outbox WHERE synced=0").fetchone()[0]
        pending += conn.execute("SELECT COUNT(*) FROM human_review_events WHERE synced=0").fetchone()[0]
    return {"enabled": enabled(), "pending": pending}


def inspection_status(inspection_id):
    with connect() as conn:
        record = conn.execute("SELECT synced FROM analytics_outbox WHERE inspection_id=?", (inspection_id,)).fetchone()
        reviews = conn.execute("SELECT COUNT(*) FROM human_review_events WHERE inspection_id=? AND synced=0", (inspection_id,)).fetchone()[0]
    if record is None:
        return "not_queued"
    if record["synced"] and reviews == 0:
        return "saved"
    return "pending_retry" if enabled() else "pending_configuration"


def flush(limit: int = 100):
    with connect() as conn:
        rows = conn.execute("SELECT inspection_id,payload FROM analytics_outbox WHERE synced=0 ORDER BY rowid LIMIT ?", (limit,)).fetchall()
    if rows:
        save_records([AnalyticsRecord.model_validate(json.loads(row["payload"])) for row in rows])
        with connect() as conn:
            conn.executemany("UPDATE analytics_outbox SET synced=1 WHERE inspection_id=?", [(r["inspection_id"],) for r in rows])
    with connect() as conn:
        reviews = conn.execute("SELECT * FROM human_review_events WHERE synced=0 ORDER BY event_id LIMIT ?", (limit,)).fetchall()
    if reviews:
        save_reviews([dict(row) for row in reviews])
        with connect() as conn:
            conn.executemany("UPDATE human_review_events SET synced=1 WHERE event_id=?", [(r["event_id"],) for r in reviews])
    return {**status(), "sent": len(rows) + len(reviews)}


def record_result(response, batch_id: str, machine_id: str, component_id: str):
    vision = response.vision_result
    classification = vision.classification
    record = AnalyticsRecord(
        inspection_id=response.id, component_id=component_id or response.id,
        component_type=response.bearing_type, batch_id=batch_id, machine_id=machine_id,
        observed_at=response.created_at, data_source="prototype_inspection",
        disposition=response.status, model_label=classification.label if classification else "unverified",
        model_confidence=classification.confidence if classification else None,
        image_quality_score=response.image_quality.score, model_version=vision.model_version,
        vlm_mode=response.vlm_result.mode, vlm_summary=response.vlm_result.analysis[:4000],
        processing_time_ms=response.processing_time_ms,
    )
    enqueue(record)
    if not enabled():
        return "pending_configuration"
    try:
        # Send this inspection specifically; older queue backlog is retried explicitly.
        save_records([record])
        with connect() as conn:
            conn.execute("UPDATE analytics_outbox SET synced=1 WHERE inspection_id=?", (record.inspection_id,))
        return "saved"
    except AnalyticsUnavailable:
        return "pending_retry"

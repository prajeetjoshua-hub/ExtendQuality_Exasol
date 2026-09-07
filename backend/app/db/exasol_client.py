"""Exasol analytics boundary. No credentials or raw driver errors reach callers."""
from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import ssl

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


SQL_DIR = Path(__file__).resolve().parents[2] / "database"


class AnalyticsUnavailable(RuntimeError):
    pass


class AnalyticsRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    inspection_id: str = Field(min_length=1, max_length=64)
    component_id: str = Field(min_length=1, max_length=80)
    component_type: str = Field(min_length=1, max_length=50)
    batch_id: str = Field(min_length=1, max_length=80)
    machine_id: str = Field(min_length=1, max_length=80)
    observed_at: datetime
    data_source: Literal["prototype_inspection", "synthetic_demo"]
    disposition: Literal["ACCEPT", "REJECT", "REVIEW", "RECAPTURE", "SYSTEM_HOLD"]
    model_label: str = Field(max_length=100)
    model_confidence: float | None = Field(default=None, ge=0, le=1)
    image_quality_score: float = Field(ge=0, le=1)
    model_version: str = Field(max_length=200)
    vlm_mode: str = Field(max_length=40)
    vlm_summary: str = Field(max_length=4000)
    processing_time_ms: float = Field(ge=0)

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone.")
        return value.astimezone(timezone.utc)

    @field_validator("inspection_id", "component_id", "batch_id", "machine_id", "component_type")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Identifier cannot be blank.")
        return value.strip()


def enabled() -> bool:
    return os.getenv("EXASOL_ENABLED", "false").lower() == "true"


@contextmanager
def connection():
    if not enabled():
        raise AnalyticsUnavailable("Exasol is disabled. Configure it to enable SQL analytics.")
    required = [os.getenv(key, "").strip() for key in ("EXASOL_DSN", "EXASOL_USER", "EXASOL_PASSWORD")]
    if not all(required):
        raise AnalyticsUnavailable("Exasol configuration is incomplete.")
    schema = os.getenv("EXASOL_SCHEMA", "EQ_HACKATHON")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", schema):
        raise AnalyticsUnavailable("Use an uppercase Exasol schema identifier.")
    conn = None
    try:
        import pyexasol
        ssl_options = {"cert_reqs": ssl.CERT_REQUIRED}
        ca = os.getenv("EXASOL_CA_FILE")
        if ca:
            ssl_options["ca_certs"] = ca
        # Local-only development escape hatch, never silently disable TLS checks.
        if os.getenv("EXASOL_LOCAL_INSECURE", "false").lower() == "true":
            if not re.fullmatch(r"(127\.0\.0\.1|localhost):[0-9]+", required[0]):
                raise AnalyticsUnavailable("Unverified TLS is restricted to loopback development.")
            ssl_options = {"cert_reqs": ssl.CERT_NONE}
        conn = pyexasol.connect(dsn=required[0], user=required[1], password=required[2],
                               encryption=True, websocket_sslopt=ssl_options,
                               connection_timeout=5, socket_timeout=15, query_timeout=15,
                               autocommit=False, fetch_dict=True, lower_ident=True)
        yield conn, schema
    except AnalyticsUnavailable:
        raise
    except Exception:
        raise AnalyticsUnavailable("Exasol operation failed. Check database health, credentials, TLS and schema locally.") from None
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def initialize_schema():
    with connection() as (conn, schema):
        for statement in (SQL_DIR / "schema.sql").read_text(encoding="utf-8").split(";"):
            if statement.strip():
                conn.execute(statement, {"schema": schema})
        conn.commit()


def health():
    with connection() as (conn, _):
        conn.execute("SELECT 1").fetchone()
    return {"status": "connected", "platform": "Exasol Personal"}


def save_records(records: list[AnalyticsRecord]):
    """Idempotent immutable inserts; repeated IDs never overwrite model evidence."""
    with connection() as (conn, schema):
        columns = list(AnalyticsRecord.model_fields)
        # Identifiers below come exclusively from the fixed model, not user input.
        projection = ", ".join("{" + key + "} AS " + key for key in columns)
        sql = "MERGE INTO {schema!q}.INSPECTIONS target USING (SELECT " + projection + ") incoming ON target.inspection_id=incoming.inspection_id WHEN NOT MATCHED THEN INSERT (" + ", ".join(columns) + ") VALUES (" + ", ".join("incoming." + key for key in columns) + ")"
        for record in records:
            params = record.model_dump()
            params["observed_at"] = record.observed_at.strftime("%Y-%m-%d %H:%M:%S.%f")
            conn.execute(sql, {**params, "schema": schema})
        conn.commit()


def analytics(source: str, batch: str | None = None):
    if source not in {"prototype_inspection", "synthetic_demo"}:
        raise ValueError("Choose one explicit data source.")
    from backend.app.analytics.risk import assess_batch
    result = {"platform": "Exasol Personal", "data_source": source, "batch_filter": batch}
    with connection() as (conn, schema):
        for block in (SQL_DIR / "queries.sql").read_text(encoding="utf-8").split("-- name: ")[1:]:
            name, sql = block.split("\n", 1)
            result[name.strip()] = conn.execute(sql.strip().rstrip(";"), {"schema": schema, "source": source, "batch": batch}).fetchall()
    for item in result["batches"]:
        periods = [d for d in result["daily"] if d["batch_id"] == item["batch_id"] and d["machine_id"] == item["machine_id"]]
        item["risk"] = assess_batch(int(item["total"]), int(item["eligible"]), int(item["rejected"]), periods)
    return result


def save_reviews(reviews: list[dict]):
    with connection() as (conn, schema):
        for review in reviews:
            if review["decision"] not in {"ACCEPT", "REJECT"}:
                raise ValueError("Invalid review.")
            params = {"schema": schema, "id": review["inspection_id"], "decision": review["decision"],
                      "reviewed_at": datetime.fromisoformat(review["reviewed_at"]).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")}
            conn.execute("""MERGE INTO {schema!q}.HUMAN_REVIEWS target
            USING (SELECT {id} AS inspection_id, {decision} AS decision, CAST({reviewed_at} AS TIMESTAMP) AS reviewed_at) incoming
            ON target.inspection_id=incoming.inspection_id
            WHEN MATCHED THEN UPDATE SET decision=incoming.decision, reviewed_at=incoming.reviewed_at
                WHERE incoming.reviewed_at >= target.reviewed_at
            WHEN NOT MATCHED THEN INSERT (inspection_id,decision,reviewed_at)
                VALUES (incoming.inspection_id,incoming.decision,incoming.reviewed_at)""", params)
        conn.commit()

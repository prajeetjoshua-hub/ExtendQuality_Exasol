from typing import Literal
from fastapi import APIRouter, HTTPException, Query

from backend.app.db import analytics_outbox, exasol_client

router = APIRouter(prefix="/analytics", tags=["Exasol analytics"])


@router.get("/health")
def analytics_health():
    try:
        return {**exasol_client.health(), **analytics_outbox.status()}
    except exasol_client.AnalyticsUnavailable as exc:
        return {"status": "unavailable", "message": str(exc), **analytics_outbox.status()}


@router.get("")
def query_analytics(source: Literal["prototype_inspection", "synthetic_demo"] = "prototype_inspection",
                    batch: str | None = Query(default=None, min_length=1, max_length=80)):
    try:
        return exasol_client.analytics(source, batch)
    except exasol_client.AnalyticsUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None


@router.post("/retry")
def retry_pending():
    try:
        return analytics_outbox.flush()
    except exasol_client.AnalyticsUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

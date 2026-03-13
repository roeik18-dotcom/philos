"""Analytics API routes."""
import logging
from fastapi import APIRouter, Request
from services.analytics import get_daily_summary, get_event_log, log_event, get_funnel
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analytics/summary")
async def analytics_summary(days: int = 7):
    """Per-day summary of key usage events."""
    clamped = max(1, min(days, 30))
    summary = await get_daily_summary(clamped)
    return {"success": True, "days": clamped, "summary": summary}


@router.get("/analytics/events")
async def analytics_events(limit: int = 50):
    """Recent raw analytics events."""
    clamped = max(1, min(limit, 200))
    events = await get_event_log(clamped)
    return {"success": True, "count": len(events), "events": events}


@router.post("/analytics/track")
async def track_event(data: dict):
    """Lightweight frontend event tracker. No auth required — uses user_id from body."""
    event_type = data.get("event")
    user_id = data.get("user_id", "anonymous")
    metadata = data.get("metadata", {})
    if not event_type:
        return {"success": False}
    await log_event(user_id, event_type, metadata)
    return {"success": True}


@router.get("/analytics/funnel")
async def analytics_funnel(days: int = 7):
    """Tester funnel: landing_view → start_clicked → base_selected → question_answered → trust_shown → invite_copied."""
    clamped = max(1, min(days, 30))
    funnel = await get_funnel(clamped)
    return {"success": True, "days": clamped, "funnel": funnel}

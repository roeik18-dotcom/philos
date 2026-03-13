"""Analytics API routes."""
import logging
from fastapi import APIRouter
from services.analytics import get_daily_summary, get_event_log

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

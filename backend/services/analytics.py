"""Lightweight analytics event logging service."""
import logging
from datetime import datetime, timezone, timedelta
from database import db

logger = logging.getLogger("analytics")


async def log_event(user_id: str, event_type: str, metadata: dict = None):
    """Log a single analytics event."""
    doc = {
        "user_id": user_id,
        "event_type": event_type,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.analytics_events.insert_one(doc)
    return doc


async def log_session(user_id: str):
    """Log a return session (called on auth/login)."""
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    existing = await db.analytics_events.find_one({
        "user_id": user_id,
        "event_type": "session_start",
        "metadata.date": today,
    })
    if not existing:
        await log_event(user_id, "session_start", {"date": today})
        logger.info(f"Session logged: user={user_id}")


async def get_daily_summary(days: int = 7) -> list:
    """Get per-day summary of key events for the last N days."""
    now = datetime.now(timezone.utc)
    results = []

    for i in range(days):
        day = now - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end = (day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat()

        query = {"timestamp": {"$gte": day_start, "$lt": day_end}}

        daily_actions = await db.analytics_events.count_documents({**query, "event_type": "daily_action"})
        missions_joined = await db.analytics_events.count_documents({**query, "event_type": "mission_joined"})
        globe_points = await db.analytics_events.count_documents({**query, "event_type": "globe_point"})
        trust_changes = await db.analytics_events.count_documents({**query, "event_type": "trust_change"})
        sessions = await db.analytics_events.count_documents({**query, "event_type": "session_start"})

        results.append({
            "date": day_str,
            "daily_actions": daily_actions,
            "missions_joined": missions_joined,
            "globe_points": globe_points,
            "trust_changes": trust_changes,
            "return_sessions": sessions,
        })

    return results


async def get_event_log(limit: int = 50) -> list:
    """Get recent raw events for debugging."""
    events = await db.analytics_events.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return events


FUNNEL_STEPS = [
    "landing_view",
    "start_clicked",
    "base_selected",
    "question_answered",
    "trust_shown",
    "invite_copied",
]


async def get_funnel(days: int = 7) -> dict:
    """Count unique users at each funnel step over the last N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    base_query = {"timestamp": {"$gte": cutoff}}

    steps = []
    for step in FUNNEL_STEPS:
        count = len(await db.analytics_events.distinct(
            "user_id", {**base_query, "event_type": step}
        ))
        steps.append({"step": step, "unique_users": count})

    # Add drop-off percentages
    for i, s in enumerate(steps):
        if i == 0 or steps[0]["unique_users"] == 0:
            s["pct_of_top"] = 100.0 if s["unique_users"] > 0 else 0.0
        else:
            s["pct_of_top"] = round(s["unique_users"] / steps[0]["unique_users"] * 100, 1)
        if i > 0 and steps[i - 1]["unique_users"] > 0:
            s["pct_of_prev"] = round(s["unique_users"] / steps[i - 1]["unique_users"] * 100, 1)
        else:
            s["pct_of_prev"] = None

    return {"steps": steps, "period_days": days}

"""Maps real product flows to trust system action events.

Mapping rules:
  Daily action (contribution) → action_type='contribute', impact=streak-based, authenticity=1.0
  Daily action (recovery)     → action_type='help',       impact=streak-based, authenticity=1.0
  Daily action (order)        → action_type='create',     impact=streak-based, authenticity=1.0
  Daily action (exploration)  → action_type='explore',    impact=streak-based, authenticity=1.0
  Globe point sent            → action_type='contribute', impact=3,            authenticity=0.8
  Mission joined              → action_type='contribute', impact=5,            authenticity=0.9
  Onboarding first action     → action_type='explore',    impact=2,            authenticity=0.7
  Invite code used            → action_type='contribute', impact=8,            authenticity=0.9
"""
import logging
from services.trust import calculate_action_value, recalculate_user_state
from database import db
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

DIRECTION_TO_ACTION_TYPE = {
    'contribution': 'contribute',
    'recovery': 'help',
    'order': 'create',
    'exploration': 'explore',
}


async def record_trust_action(user_id: str, action_type: str, impact: float, authenticity: float, source: str):
    """Insert an action and recalculate user state. Returns the action doc or None on error."""
    try:
        value = calculate_action_value(impact, authenticity)
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action_type": action_type,
            "impact": round(impact, 2),
            "authenticity": round(authenticity, 2),
            "value": value,
            "source": source,
            "timestamp": now,
        }
        await db.actions.insert_one(doc)
        await recalculate_user_state(user_id)
        logger.info(f"Trust action: user={user_id} type={action_type} value={value} src={source}")
        return doc
    except Exception as e:
        logger.error(f"record_trust_action error: {e}")
        return None


async def on_daily_action(user_id: str, direction: str, streak: int):
    """Called when a user completes a daily orientation action."""
    action_type = DIRECTION_TO_ACTION_TYPE.get(direction, 'explore')
    impact = min(3 + streak * 0.5, 15)
    return await record_trust_action(user_id, action_type, impact, 1.0, "daily_action")


async def on_globe_point(user_id: str):
    """Called when a user sends a point to the globe."""
    return await record_trust_action(user_id, "contribute", 3, 0.8, "globe_point")


async def on_mission_joined(user_id: str):
    """Called when a user joins a community mission."""
    return await record_trust_action(user_id, "contribute", 5, 0.9, "mission_join")


async def on_onboarding_action(user_id: str, direction: str):
    """Called when a user completes their onboarding first action."""
    action_type = DIRECTION_TO_ACTION_TYPE.get(direction, 'explore')
    return await record_trust_action(user_id, action_type, 2, 0.7, "onboarding")


async def on_invite_used(inviter_id: str):
    """Called when someone joins via an invite code (credits the inviter)."""
    return await record_trust_action(inviter_id, "contribute", 8, 0.9, "invite_used")

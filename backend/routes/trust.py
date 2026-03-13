"""Trust system API routes: actions, risk signals, and trust profile."""
from fastapi import APIRouter, HTTPException, Depends
from database import db
from auth_utils import get_current_user
from models.trust import (
    ActionCreate, ActionResponse,
    RiskSignalCreate, RiskSignalResponse,
    TrustProfileResponse,
)
from services.trust import (
    calculate_action_value, calculate_risk_score,
    recalculate_user_state,
    VALID_ACTION_TYPES, VALID_SIGNAL_TYPES,
)
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/actions", response_model=ActionResponse)
async def record_action(data: ActionCreate, user=Depends(get_current_user)):
    """Record a user action and update their value score."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if data.action_type not in VALID_ACTION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action_type. Must be one of: {', '.join(sorted(VALID_ACTION_TYPES))}",
        )

    user_id = user["id"]
    value = calculate_action_value(data.impact, data.authenticity)
    now = datetime.now(timezone.utc).isoformat()
    action_id = str(uuid.uuid4())

    doc = {
        "id": action_id,
        "user_id": user_id,
        "action_type": data.action_type,
        "impact": data.impact,
        "authenticity": data.authenticity,
        "value": value,
        "timestamp": now,
    }
    await db.actions.insert_one(doc)
    await recalculate_user_state(user_id)

    return ActionResponse(**doc)


@router.post("/risk-signal", response_model=RiskSignalResponse)
async def record_risk_signal(data: RiskSignalCreate):
    """Record a risk signal against a user and update their risk score."""
    if data.signal_type not in VALID_SIGNAL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid signal_type. Must be one of: {', '.join(sorted(VALID_SIGNAL_TYPES))}",
        )

    # Verify user exists
    user = await db.users.find_one({"id": data.user_id}, {"_id": 0, "id": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    risk = calculate_risk_score(data.confidence, data.severity)
    now = datetime.now(timezone.utc).isoformat()
    signal_id = str(uuid.uuid4())

    doc = {
        "id": signal_id,
        "user_id": data.user_id,
        "signal_type": data.signal_type,
        "confidence": data.confidence,
        "severity": data.severity,
        "risk": risk,
        "timestamp": now,
    }
    await db.risk_signals.insert_one(doc)
    await recalculate_user_state(data.user_id)

    return RiskSignalResponse(**doc)


@router.get("/user/{user_id}/trust", response_model=TrustProfileResponse)
async def get_trust_profile(user_id: str):
    """Get a user's full trust profile: value, risk, and trust scores."""
    # Verify user exists
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "id": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    state = await db.user_state.find_one({"user_id": user_id}, {"_id": 0})
    if not state:
        state = await recalculate_user_state(user_id)

    recent_actions = await db.actions.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)

    recent_signals = await db.risk_signals.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)

    return TrustProfileResponse(
        user_id=user_id,
        value_score=state.get("value_score", 0),
        risk_score=state.get("risk_score", 0),
        trust_score=state.get("trust_score", 0),
        total_actions=state.get("total_actions", 0),
        total_risk_signals=state.get("total_risk_signals", 0),
        last_updated=state.get("last_updated", ""),
        recent_actions=[ActionResponse(**a) for a in recent_actions],
        recent_risk_signals=[RiskSignalResponse(**s) for s in recent_signals],
    )

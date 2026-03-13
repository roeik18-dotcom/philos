"""Value + Risk + Trust calculation service."""
import math
import logging
import uuid
from datetime import datetime, timezone
from database import db

logger = logging.getLogger(__name__)

VALID_ACTION_TYPES = {'help', 'create', 'explore', 'contribute'}
VALID_SIGNAL_TYPES = {'manipulation', 'aggression', 'spam', 'deception', 'disruption'}

VALUE_DECAY = 0.98
RISK_DECAY = 0.95


def calculate_action_value(impact: float, authenticity: float) -> float:
    """value = log(1 + impact) * authenticity"""
    return round(math.log(1 + impact) * authenticity, 4)


def calculate_risk_score(confidence: float, severity: float) -> float:
    """risk = confidence * severity"""
    return round(confidence * severity, 4)


async def write_ledger(user_id: str, source_flow: str, action_type: str,
                       impact: float, authenticity: float,
                       value_delta: float, risk_delta: float,
                       trust_score_after: float, metadata: dict = None):
    """Write an immutable ledger entry for every trust-affecting event."""
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "source_flow": source_flow,
        "action_type": action_type,
        "impact": round(impact, 4),
        "authenticity": round(authenticity, 4),
        "computed_value_delta": round(value_delta, 4),
        "computed_risk_delta": round(risk_delta, 4),
        "trust_score_after": round(trust_score_after, 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
    await db.trust_ledger.insert_one(entry)
    return entry


async def recalculate_user_state(user_id: str) -> dict:
    """Recalculate value_score and risk_score from all actions and signals, then compute trust_score."""
    actions = await db.actions.find({"user_id": user_id}, {"_id": 0}).to_list(10000)
    signals = await db.risk_signals.find({"user_id": user_id}, {"_id": 0}).to_list(10000)

    value_score = sum(a.get("value", 0) for a in actions)
    risk_score = sum(s.get("risk", 0) for s in signals)
    trust_score = round(value_score - risk_score, 4)

    now = datetime.now(timezone.utc).isoformat()
    state = {
        "user_id": user_id,
        "value_score": round(value_score, 4),
        "risk_score": round(risk_score, 4),
        "trust_score": trust_score,
        "total_actions": len(actions),
        "total_risk_signals": len(signals),
        "last_updated": now,
    }

    await db.user_state.update_one(
        {"user_id": user_id},
        {"$set": state},
        upsert=True,
    )
    return state


async def run_daily_decay():
    """Apply daily decay to all user scores and write ledger entries."""
    cursor = db.user_state.find({}, {"_id": 0, "user_id": 1, "value_score": 1, "risk_score": 1, "trust_score": 1})
    count = 0
    async for state in cursor:
        old_value = state.get("value_score", 0)
        old_risk = state.get("risk_score", 0)
        new_value = round(old_value * VALUE_DECAY, 4)
        new_risk = round(old_risk * RISK_DECAY, 4)
        new_trust = round(new_value - new_risk, 4)
        value_delta = round(new_value - old_value, 4)
        risk_delta = round(new_risk - old_risk, 4)

        await db.user_state.update_one(
            {"user_id": state["user_id"]},
            {"$set": {
                "value_score": new_value,
                "risk_score": new_risk,
                "trust_score": new_trust,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }}
        )

        if value_delta != 0 or risk_delta != 0:
            await write_ledger(
                user_id=state["user_id"],
                source_flow="decay",
                action_type="decay",
                impact=0, authenticity=0,
                value_delta=value_delta,
                risk_delta=risk_delta,
                trust_score_after=new_trust,
                metadata={"value_before": old_value, "risk_before": old_risk,
                           "value_decay": VALUE_DECAY, "risk_decay": RISK_DECAY},
            )
        count += 1
    logger.info(f"Daily decay applied to {count} user states")
    return count

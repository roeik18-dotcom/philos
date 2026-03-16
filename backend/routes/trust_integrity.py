"""Trust Integrity Layer — verification, anti-spam, decay, suspicious flags."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import os
import logging
from auth_utils import get_current_user

router = APIRouter()
logger = logging.getLogger("trust_integrity")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

VERIFICATION_LEVELS = {"self_reported": 1, "community_verified": 2, "org_verified": 3}
VERIFICATION_ORDER = ["self_reported", "community_verified", "org_verified"]

# ── Anti-Spam Constants ──
MAX_ACTIONS_PER_HOUR = 5
DUPLICATE_WINDOW_HOURS = 24
REACTION_BURST_THRESHOLD = 10  # reactions to same poster in 1 hour
ACTION_REACTION_VELOCITY = 20  # reactions on 1 action in 5 minutes


class VerifyActionRequest(BaseModel):
    verification_level: str
    verifier_community: str = ""


# ── Verification ──

@router.post("/trust/verify/{action_id}")
async def verify_action(action_id: str, req: VerifyActionRequest, user=Depends(get_current_user)):
    """Upgrade an action's verification level. Only allows upgrades, not downgrades."""
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    if req.verification_level not in VERIFICATION_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid level. Use: {', '.join(VERIFICATION_ORDER)}")

    try:
        oid = ObjectId(action_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid action ID")

    action = db.impact_actions.find_one({"_id": oid})
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    current_level = action.get("verification_level", "self_reported")
    new_level = req.verification_level
    if VERIFICATION_LEVELS[new_level] <= VERIFICATION_LEVELS.get(current_level, 1):
        raise HTTPException(status_code=400, detail=f"Cannot downgrade from {current_level} to {new_level}")

    # Apply verification
    multiplier = VERIFICATION_LEVELS[new_level]
    base_trust = _calc_base_trust(action.get("reactions", {}))
    new_trust = base_trust * multiplier

    db.impact_actions.update_one({"_id": oid}, {"$set": {
        "verification_level": new_level,
        "verified_by": user["id"],
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verifier_community": req.verifier_community,
        "trust_signal": new_trust,
    }})

    # Log verification
    db.trust_audit_log.insert_one({
        "type": "verification",
        "action_id": action_id,
        "old_level": current_level,
        "new_level": new_level,
        "verifier_id": user["id"],
        "verifier_community": req.verifier_community,
        "old_trust": action.get("trust_signal", 0),
        "new_trust": new_trust,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "success": True,
        "verification_level": new_level,
        "trust_signal": new_trust,
        "multiplier": multiplier,
    }


# ── Anti-Spam Checks ──

def check_rate_limit(user_id: str) -> dict:
    """Check if user exceeded action posting rate limit."""
    one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    recent_count = db.impact_actions.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": one_hour_ago},
    })
    if recent_count >= MAX_ACTIONS_PER_HOUR:
        return {"blocked": True, "reason": f"Rate limit: max {MAX_ACTIONS_PER_HOUR} actions per hour"}
    return {"blocked": False}


def check_duplicate(user_id: str, title: str, description: str) -> dict:
    """Check for duplicate action within time window."""
    window = (datetime.now(timezone.utc) - timedelta(hours=DUPLICATE_WINDOW_HOURS)).isoformat()
    dup = db.impact_actions.find_one({
        "user_id": user_id,
        "title": title,
        "description": description,
        "created_at": {"$gte": window},
    })
    if dup:
        return {"blocked": True, "reason": "Duplicate action detected within 24 hours"}
    return {"blocked": False}


def check_self_reaction(user_id: str, action) -> dict:
    """Prevent users from reacting to their own actions."""
    if action.get("user_id") == user_id:
        return {"blocked": True, "reason": "Cannot react to your own action"}
    return {"blocked": False}


# ── Suspicious Activity Detection ──

def check_suspicious_reaction(reactor_id: str, action) -> list:
    """Check for suspicious reaction patterns. Returns list of flags."""
    flags = []
    poster_id = action.get("user_id", "")
    action_id = str(action["_id"])
    now = datetime.now(timezone.utc)

    # Check 1: Same user reacting to many actions from same poster in 1 hour
    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    poster_actions = list(db.impact_actions.find({"user_id": poster_id}, {"_id": 1, "reactions": 1}))
    recent_reactions_to_poster = 0
    for pa in poster_actions:
        for rtype in ["support", "useful", "verified"]:
            reactors = pa.get("reactions", {}).get(rtype, [])
            if reactor_id in reactors:
                recent_reactions_to_poster += 1

    if recent_reactions_to_poster >= REACTION_BURST_THRESHOLD:
        flags.append({
            "type": "reaction_farming",
            "detail": f"User reacted to {recent_reactions_to_poster} actions from same poster",
            "reactor_id": reactor_id,
            "poster_id": poster_id,
            "action_id": action_id,
            "severity": "medium",
            "created_at": now.isoformat(),
        })

    # Check 2: Action received too many reactions too quickly
    all_reaction_count = sum(
        len(action.get("reactions", {}).get(rt, []))
        for rt in ["support", "useful", "verified"]
    )
    if all_reaction_count >= ACTION_REACTION_VELOCITY:
        flags.append({
            "type": "velocity_spike",
            "detail": f"Action received {all_reaction_count} total reactions",
            "action_id": action_id,
            "poster_id": poster_id,
            "severity": "high",
            "created_at": now.isoformat(),
        })

    # Store flags
    for flag in flags:
        db.trust_flags.update_one(
            {"type": flag["type"], "action_id": flag["action_id"], "reactor_id": flag.get("reactor_id", "")},
            {"$set": flag},
            upsert=True,
        )

    return flags


# ── Reputation Decay ──

def run_trust_decay():
    """Decay trust scores for inactive users (30+ days, 5% reduction).
    Users with burst_and_vanish signals get accelerated decay (10%).
    Called by scheduler. Returns count of affected users."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Find users who haven't posted or reacted in 30 days
    active_pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$user_id"}},
    ]
    active_users = set(r["_id"] for r in db.impact_actions.aggregate(active_pipeline))

    # Also check recent reactors
    all_recent_actions = db.impact_actions.find({"created_at": {"$gte": cutoff}}, {"reactions": 1})
    for a in all_recent_actions:
        for rtype in ["support", "useful", "verified"]:
            for uid in a.get("reactions", {}).get(rtype, []):
                active_users.add(uid)

    # Find all unique users with actions
    all_users_pipeline = [{"$group": {"_id": "$user_id"}}]
    all_users = set(r["_id"] for r in db.impact_actions.aggregate(all_users_pipeline))

    inactive_users = all_users - active_users

    # Pre-load burst_and_vanish signals for accelerated decay
    burst_users = set()
    try:
        burst_signals = db.risk_signals.find(
            {"signal_type": "burst_and_vanish", "status": "active"},
            {"_id": 0, "subject_user_id": 1},
        )
        burst_users = set(s["subject_user_id"] for s in burst_signals)
    except Exception as e:
        logger.warning(f"Failed to load burst_and_vanish signals: {e}")

    decayed_count = 0

    for user_id in inactive_users:
        # Check last_decayed to avoid double-decay
        decay_record = db.trust_decay_log.find_one({"user_id": user_id}, sort=[("decayed_at", -1)])
        if decay_record and decay_record.get("decayed_at", "") > cutoff:
            continue

        # Accelerated decay for burst_and_vanish users (10% vs 5%)
        decay_rate = 0.10 if user_id in burst_users else 0.05
        retain_rate = 1.0 - decay_rate

        # Apply decay to all their actions
        user_actions = db.impact_actions.find({"user_id": user_id, "trust_signal": {"$gt": 0}})
        for action in user_actions:
            old_trust = action.get("trust_signal", 0)
            new_trust = round(old_trust * retain_rate, 2)
            if new_trust != old_trust:
                db.impact_actions.update_one(
                    {"_id": action["_id"]},
                    {"$set": {"trust_signal": new_trust, "last_decayed": now_iso}}
                )

        db.trust_decay_log.insert_one({
            "user_id": user_id,
            "decay_rate": decay_rate,
            "accelerated": user_id in burst_users,
            "decayed_at": now_iso,
        })
        decayed_count += 1

    logger.info(f"Trust decay: {decayed_count} inactive users decayed ({len(burst_users & inactive_users)} accelerated), {len(active_users)} active users skipped")
    return decayed_count


# ── Trust Score Helpers ──

REACTION_WEIGHTS = {"support": 1, "useful": 2, "verified": 5}


def _calc_base_trust(reactions: dict) -> float:
    """Calculate base trust signal from reactions (before verification multiplier)."""
    return (
        len(reactions.get("support", [])) * 1
        + len(reactions.get("useful", [])) * 2
        + len(reactions.get("verified", [])) * 5
    )


def _load_enforcement_context(action_id: str, poster_id: str, community: str, reactor_ids: set) -> dict:
    """Load active risk signals relevant to this action. Returns enforcement adjustments.
    Returns None on error (caller falls back to normal calculation)."""
    ctx = {
        "frozen": False,
        "suppressed_reactors": set(),
        "discounted_reactors": set(),
        "ghost_reactors": set(),
        "community_monopoly": False,
    }

    # 1. Check trust_flags for inline signals (reaction_farming, velocity_spike)
    flags = list(db.trust_flags.find(
        {"action_id": action_id},
        {"_id": 0, "type": 1, "reactor_id": 1},
    ))
    for f in flags:
        if f["type"] == "velocity_spike":
            ctx["frozen"] = True
        elif f["type"] == "reaction_farming":
            rid = f.get("reactor_id", "")
            if rid:
                ctx["suppressed_reactors"].add(rid)

    # 2. Check risk_signals for scanner-detected signals
    # Query signals about the poster OR about any reactor on this action
    lookup_ids = list(reactor_ids | {poster_id})
    signals = list(db.risk_signals.find(
        {"status": "active", "subject_user_id": {"$in": lookup_ids}},
        {"_id": 0, "signal_type": 1, "subject_user_id": 1,
         "related_user_ids": 1, "_community_key": 1},
    ))

    for s in signals:
        stype = s["signal_type"]
        if stype == "reciprocal_boosting":
            ctx["discounted_reactors"].add(s["subject_user_id"])
            for uid in s.get("related_user_ids", []):
                ctx["discounted_reactors"].add(uid)
        elif stype == "ghost_reactor":
            ctx["ghost_reactors"].add(s["subject_user_id"])
        elif stype == "community_monopoly":
            if s.get("_community_key", "") == community:
                ctx["community_monopoly"] = True

    return ctx


def _calc_enforced_trust(reactions: dict, ctx: dict) -> float:
    """Calculate base trust with enforcement: suppress, discount, or reduce reaction weights."""
    total = 0.0
    for rtype, weight in REACTION_WEIGHTS.items():
        for reactor_id in reactions.get(rtype, []):
            if reactor_id in ctx["suppressed_reactors"]:
                continue  # reaction_farming: fully suppress
            eff = weight
            if reactor_id in ctx["discounted_reactors"]:
                eff *= 0.5  # reciprocal_boosting: half weight
            if reactor_id in ctx["ghost_reactors"]:
                eff *= 0.5  # ghost_reactor: half weight
            total += eff
    return total


def recalc_trust_signal(action: dict) -> float:
    """Recalculate trust signal with enforcement layer.
    Falls back to normal calculation if enforcement lookup fails."""
    reactions = action.get("reactions", {})
    level = action.get("verification_level", "self_reported")
    verification_mult = VERIFICATION_LEVELS.get(level, 1)

    try:
        action_id = str(action.get("_id", ""))
        poster_id = action.get("user_id", "")
        community = action.get("community", "")

        # Collect all reactor IDs
        reactor_ids = set()
        for rtype in ["support", "useful", "verified"]:
            reactor_ids.update(reactions.get(rtype, []))

        ctx = _load_enforcement_context(action_id, poster_id, community, reactor_ids)

        # velocity_spike: freeze trust score
        if ctx["frozen"]:
            return action.get("trust_signal", 0)

        # Calculate with enforcement adjustments
        base = _calc_enforced_trust(reactions, ctx)
        trust = base * verification_mult

        # community_monopoly: cap at 0.5x
        if ctx["community_monopoly"]:
            trust *= 0.5

        return trust
    except Exception as e:
        logger.warning(f"Enforcement fallback for action: {e}")
        base = _calc_base_trust(reactions)
        return base * verification_mult


# ── Admin Endpoints ──

@router.get("/trust/flags")
async def get_trust_flags(limit: int = 50):
    """Get recent suspicious activity flags."""
    flags = list(db.trust_flags.find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
    return {"success": True, "flags": flags, "total": db.trust_flags.count_documents({})}


@router.get("/trust/integrity-stats")
async def get_integrity_stats():
    """Get trust integrity system stats."""
    total_actions = db.impact_actions.count_documents({})
    verified_actions = db.impact_actions.count_documents({"verification_level": {"$in": ["community_verified", "org_verified"]}})
    total_flags = db.trust_flags.count_documents({})
    high_flags = db.trust_flags.count_documents({"severity": "high"})
    decay_count = db.trust_decay_log.count_documents({})

    # Verification breakdown
    self_reported = db.impact_actions.count_documents({"$or": [
        {"verification_level": "self_reported"},
        {"verification_level": {"$exists": False}},
    ]})

    return {
        "success": True,
        "stats": {
            "total_actions": total_actions,
            "self_reported": self_reported,
            "community_verified": db.impact_actions.count_documents({"verification_level": "community_verified"}),
            "org_verified": db.impact_actions.count_documents({"verification_level": "org_verified"}),
            "total_flags": total_flags,
            "high_severity_flags": high_flags,
            "users_decayed": decay_count,
        },
    }

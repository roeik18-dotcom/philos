"""Trust Integrity Layer — verification, anti-spam, decay, suspicious flags."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import os
import logging
from auth_utils import get_current_user
from utils.status_calculator import calculate_status, get_consequence_multiplier, get_consequence_panel, get_recovery_progress

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



# ── Trust Score API ──

@router.get("/trust/{user_id}")
async def get_user_trust(user_id: str):
    """Get a user's trust score with enforcement context, decay info, and active risk signals."""
    # Aggregate trust from all user's actions (enforcement-adjusted)
    actions = list(db.impact_actions.find({"user_id": user_id}))
    if not actions:
        return {
            "success": True,
            "trust_score": 0,
            "action_count": 0,
            "referral_bonus": 0,
            "decay_rate": 0.05,
            "decay_status": "active",
            "active_risk_signals": [],
            "risk_signal_count": 0,
            "enforcement_active": False,
            "last_updated": None,
        }

    # Recalculate each action's trust with enforcement
    total_trust = 0.0
    for a in actions:
        total_trust += recalc_trust_signal(a)

    # Referral bonus: +2 per active referral (referred user posted at least 1 action)
    referral_bonus = 0.0
    try:
        referrals = list(db.referrals.find({"inviter_id": user_id}, {"invited_user_id": 1, "_id": 0}))
        for ref in referrals:
            invited_id = ref.get("invited_user_id", "")
            if invited_id and db.impact_actions.count_documents({"user_id": invited_id}) > 0:
                referral_bonus += 2.0
    except Exception as e:
        logger.warning(f"Referral bonus calc failed: {e}")

    total_trust += referral_bonus

    # Get decay info
    has_burst = db.risk_signals.find_one({
        "signal_type": "burst_and_vanish",
        "subject_user_id": user_id,
        "status": "active",
    })
    decay_rate = 0.10 if has_burst else 0.05

    # Check inactivity
    last_activity = db.user_activity.find_one({"user_id": user_id}, {"_id": 0})
    last_active = last_activity.get("last_active") if last_activity else None
    decay_status = "active"
    if last_active:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        if last_active < cutoff:
            decay_status = "decaying"

    # Get active risk signals
    signals = list(db.risk_signals.find(
        {"subject_user_id": user_id, "status": "active"},
        {"_id": 0, "signal_type": 1, "category": 1, "severity": 1, "evidence": 1, "created_at": 1},
    ))

    # Also check trust_flags for this user's actions
    user_action_ids = [str(a["_id"]) for a in actions]
    flags = list(db.trust_flags.find(
        {"action_id": {"$in": user_action_ids}},
        {"_id": 0, "type": 1, "severity": 1, "action_id": 1},
    ))

    enforcement_active = len(signals) > 0 or len(flags) > 0

    return {
        "success": True,
        "trust_score": round(total_trust, 1),
        "action_count": len(actions),
        "referral_bonus": referral_bonus,
        "decay_rate": decay_rate,
        "decay_status": decay_status,
        "active_risk_signals": signals,
        "risk_signal_count": len(signals),
        "trust_flags": flags,
        "trust_flag_count": len(flags),
        "enforcement_active": enforcement_active,
        "last_updated": last_active,
    }



# ── Position Score API ──

@router.get("/position/{user_id}")
async def get_user_position(user_id: str):
    """Calculate user's position on the Self ↔ Network spectrum.
    0.0 = Self (no public engagement), 1.0 = Full Network.
    Private actions do not affect position."""

    # Only count public actions
    public_actions = list(db.impact_actions.find(
        {"user_id": user_id, "visibility": {"$ne": "private"}},
        {"_id": 0, "reactions": 1, "trust_signal": 1, "created_at": 1},
    ))
    public_count = len(public_actions)
    private_count = db.impact_actions.count_documents(
        {"user_id": user_id, "visibility": "private"}
    )

    if public_count == 0:
        # Still compute status for zero-position users
        now_zero = datetime.now(timezone.utc)
        last_a = db.impact_actions.find_one(
            {"user_id": user_id}, sort=[("created_at", -1)],
            projection={"_id": 0, "created_at": 1},
        )
        days_zero = 999
        if last_a:
            try:
                days_zero = max(0, (now_zero - datetime.fromisoformat(last_a["created_at"])).days)
            except Exception:
                pass
        recent_zero = db.impact_actions.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": (now_zero - timedelta(days=3)).isoformat()},
        })
        has_risk_zero = db.risk_signals.count_documents(
            {"subject_user_id": user_id, "status": "active"}
        ) > 0
        prev_zero = db.position_snapshots.find_one(
            {"user_id": user_id}, sort=[("created_at", -1)],
            projection={"_id": 0, "position": 1, "trust": 1},
        )
        status_zero = calculate_status(
            current_position=0.0, current_trust=0.0,
            prev_position=prev_zero["position"] if prev_zero else None,
            prev_trust=prev_zero["trust"] if prev_zero else None,
            recent_action_count=recent_zero,
            days_since_last_action=days_zero,
            has_active_risk_signals=has_risk_zero,
        )
        panel_zero = get_consequence_panel(
            status_zero["status"],
            get_consequence_multiplier(status_zero["status"], has_risk_zero),
            has_risk_zero, days_zero, recent_zero,
        )
        recovery_zero = get_recovery_progress(
            status=status_zero["status"],
            reason=status_zero["reason"],
            has_active_risk_signals=has_risk_zero,
            days_since_last_action=days_zero,
            recent_action_count=recent_zero,
            recent_public_count=0,
            unique_reactor_count=0,
        )
        return {
            "success": True,
            "position": 0.0,
            "label": "Self",
            "public_actions": 0,
            "private_actions": private_count,
            "unique_reactors": 0,
            "total_trust": 0.0,
            "active_referrals": 0,
            "factors": {"actions": 0, "reactors": 0, "trust": 0, "referrals": 0},
            "status": status_zero,
            "consequence_multiplier": get_consequence_multiplier(status_zero["status"], has_risk_zero),
            "consequence_panel": panel_zero,
            "recovery_progress": recovery_zero,
        }

    # Factor 1: Public actions (max 0.35)
    actions_factor = min(public_count / 15, 1.0) * 0.35

    # Factor 2: Unique reactors across public actions (max 0.25)
    all_reactors = set()
    for a in public_actions:
        for rtype in ["support", "useful", "verified"]:
            all_reactors.update(a.get("reactions", {}).get(rtype, []))
    all_reactors.discard(user_id)  # exclude self
    reactor_count = len(all_reactors)
    reactors_factor = min(reactor_count / 10, 1.0) * 0.25

    # Factor 3: Trust score from public actions (max 0.25)
    total_trust = sum(a.get("trust_signal", 0) for a in public_actions)
    trust_factor = min(total_trust / 50, 1.0) * 0.25

    # Factor 4: Active referrals (max 0.15)
    referral_count = 0
    try:
        referrals = list(db.referrals.find({"inviter_id": user_id}, {"invited_user_id": 1, "_id": 0}))
        for ref in referrals:
            if db.impact_actions.count_documents({"user_id": ref["invited_user_id"]}) > 0:
                referral_count += 1
    except Exception:
        pass
    referrals_factor = min(referral_count / 5, 1.0) * 0.15

    position = round(actions_factor + reactors_factor + trust_factor + referrals_factor, 3)
    position = min(position, 1.0)

    # Label based on position
    if position < 0.15:
        label = "Self"
    elif position < 0.35:
        label = "Emerging"
    elif position < 0.55:
        label = "Contributing"
    elif position < 0.75:
        label = "Connected"
    else:
        label = "Network"

    # ── Status calculation (movement-based) ──
    now = datetime.now(timezone.utc)
    three_days_ago = (now - timedelta(days=3)).isoformat()

    # Recent activity count (last 3 days)
    recent_action_count = 0
    for a in public_actions:
        if a.get("created_at", "") >= three_days_ago:
            recent_action_count += 1
    # Also count private actions in recent window
    recent_action_count += db.impact_actions.count_documents({
        "user_id": user_id, "visibility": "private",
        "created_at": {"$gte": three_days_ago},
    })

    # Days since last action
    last_action = db.impact_actions.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)],
        projection={"_id": 0, "created_at": 1},
    )
    days_since_last = 999
    if last_action:
        try:
            last_dt = datetime.fromisoformat(last_action["created_at"])
            days_since_last = max(0, (now - last_dt).days)
        except Exception:
            pass

    # Active risk signals
    has_risk = db.risk_signals.count_documents(
        {"subject_user_id": user_id, "status": "active"}
    ) > 0

    # Previous snapshot
    prev_snap = db.position_snapshots.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)],
        projection={"_id": 0, "position": 1, "trust": 1},
    )

    status_result = calculate_status(
        current_position=position,
        current_trust=round(total_trust, 1),
        prev_position=prev_snap["position"] if prev_snap else None,
        prev_trust=prev_snap["trust"] if prev_snap else None,
        recent_action_count=recent_action_count,
        days_since_last_action=days_since_last,
        has_active_risk_signals=has_risk,
    )

    # Save snapshot (one per user per day)
    today_str = now.strftime("%Y-%m-%d")
    db.position_snapshots.update_one(
        {"user_id": user_id, "date": today_str},
        {"$set": {
            "user_id": user_id,
            "date": today_str,
            "position": position,
            "trust": round(total_trust, 1),
            "created_at": now.isoformat(),
        }},
        upsert=True,
    )

    multiplier = get_consequence_multiplier(status_result["status"], has_risk)
    panel = get_consequence_panel(
        status_result["status"], multiplier,
        has_risk, days_since_last, recent_action_count,
    )

    # Recent public action count (for recovery progress)
    recent_public_count = 0
    for a in public_actions:
        if a.get("created_at", "") >= three_days_ago:
            recent_public_count += 1

    recovery = get_recovery_progress(
        status=status_result["status"],
        reason=status_result["reason"],
        has_active_risk_signals=has_risk,
        days_since_last_action=days_since_last,
        recent_action_count=recent_action_count,
        recent_public_count=recent_public_count,
        unique_reactor_count=reactor_count,
    )

    return {
        "success": True,
        "position": position,
        "label": label,
        "public_actions": public_count,
        "private_actions": private_count,
        "unique_reactors": reactor_count,
        "total_trust": round(total_trust, 1),
        "active_referrals": referral_count,
        "factors": {
            "actions": round(actions_factor, 3),
            "reactors": round(reactors_factor, 3),
            "trust": round(trust_factor, 3),
            "referrals": round(referrals_factor, 3),
        },
        "status": status_result,
        "consequence_multiplier": multiplier,
        "consequence_panel": panel,
        "recovery_progress": recovery,
    }



# ── Daily Orientation API ──

@router.get("/orientation/{user_id}")
async def get_daily_orientation(user_id: str):
    """Generate one rule-based recommendation based on position, trust, and activity.
    Decision rules (first match wins):
    1. No actions → post first action
    2. Only private, no public → make one visible
    3. Inactive 7+ days → re-engage
    4. Self (< 0.15) → publish public action
    5. Emerging (< 0.35), low reactors → react to others
    6. Contributing (< 0.55), no referrals → share to invite
    7. Connected (< 0.75) → keep contributing
    8. Network (>= 0.75) → verify others
    """
    # Gather data
    total_actions = db.impact_actions.count_documents({"user_id": user_id})
    public_count = db.impact_actions.count_documents(
        {"user_id": user_id, "visibility": {"$ne": "private"}}
    )
    private_count = total_actions - public_count

    # Last activity
    last_action = db.impact_actions.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)],
        projection={"_id": 0, "created_at": 1}
    )
    days_inactive = 0
    if last_action:
        try:
            last_dt = datetime.fromisoformat(last_action["created_at"])
            days_inactive = (datetime.now(timezone.utc) - last_dt).days
        except Exception:
            pass

    # Position
    position = 0.0
    label = "Self"
    unique_reactors = 0
    active_referrals = 0
    try:
        # Inline position calc (avoid circular call)
        pub_actions = list(db.impact_actions.find(
            {"user_id": user_id, "visibility": {"$ne": "private"}},
            {"_id": 0, "reactions": 1, "trust_signal": 1}
        ))
        pc = len(pub_actions)
        reactors = set()
        total_trust = 0.0
        for a in pub_actions:
            total_trust += a.get("trust_signal", 0)
            for rt in ["support", "useful", "verified"]:
                reactors.update(a.get("reactions", {}).get(rt, []))
        reactors.discard(user_id)
        unique_reactors = len(reactors)

        refs = list(db.referrals.find({"inviter_id": user_id}, {"invited_user_id": 1, "_id": 0}))
        for ref in refs:
            if db.impact_actions.count_documents({"user_id": ref["invited_user_id"]}) > 0:
                active_referrals += 1

        af = min(pc / 15, 1.0) * 0.35
        rf = min(unique_reactors / 10, 1.0) * 0.25
        tf = min(total_trust / 50, 1.0) * 0.25
        rrf = min(active_referrals / 5, 1.0) * 0.15
        position = round(af + rf + tf + rrf, 3)
        position = min(position, 1.0)

        if position < 0.15: label = "Self"
        elif position < 0.35: label = "Emerging"
        elif position < 0.55: label = "Contributing"
        elif position < 0.75: label = "Connected"
        else: label = "Network"
    except Exception:
        pass

    # ── Compute status for orientation context ──
    now_ori = datetime.now(timezone.utc)
    three_days_ago_ori = (now_ori - timedelta(days=3)).isoformat()
    recent_ori_count = db.impact_actions.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": three_days_ago_ori},
    })
    has_risk_ori = db.risk_signals.count_documents(
        {"subject_user_id": user_id, "status": "active"}
    ) > 0
    prev_snap_ori = db.position_snapshots.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)],
        projection={"_id": 0, "position": 1, "trust": 1},
    )
    ori_trust = 0.0
    try:
        ori_trust = total_trust
    except Exception:
        pass
    status_ori = calculate_status(
        current_position=position,
        current_trust=round(ori_trust, 1),
        prev_position=prev_snap_ori["position"] if prev_snap_ori else None,
        prev_trust=prev_snap_ori["trust"] if prev_snap_ori else None,
        recent_action_count=recent_ori_count,
        days_since_last_action=days_inactive,
        has_active_risk_signals=has_risk_ori,
    )

    # ── Decision rules (first match wins) ──
    msg = ""
    action_type = ""
    cta = ""
    status_key = status_ori["status"]

    # Status-aware overrides for At Risk and Decaying
    if status_key == "atRisk" and total_actions > 0:
        if has_risk_ori:
            msg = "Your account has active risk signals — your actions have reduced visibility. Focus on authentic contributions to recover."
        else:
            msg = f"You've been inactive for {days_inactive} days — your actions have reduced visibility. Post one action to start recovering."
        action_type = "post"
        cta = "Post Action"
    elif total_actions == 0:
        msg = "Post your first action to begin building trust."
        action_type = "post"
        cta = "Create Action"
    elif public_count == 0 and private_count > 0:
        msg = "Your private layer is active — make one action visible to start building trust."
        action_type = "visibility"
        cta = "Post Public Action"
    elif status_key == "decaying":
        msg = "Your position is decaying and your actions are losing visibility — post an action to reverse the trend."
        action_type = "post"
        cta = "Post Action"
    elif label == "Self":
        msg = "Publish one public action to move toward Emerging."
        action_type = "post"
        cta = "Create Action"
    elif label == "Emerging" and unique_reactors < 3:
        msg = "Engage with others' actions to strengthen your network position."
        action_type = "react"
        cta = "View Feed"
    elif label == "Emerging":
        prefix = "You're rising and your actions are getting boosted — k" if status_key == "rising" else "K"
        msg = f"{prefix}eep posting public actions to move toward Contributing."
        action_type = "post"
        cta = "Create Action"
    elif label == "Contributing" and active_referrals == 0:
        msg = "Share an action to invite others and move toward Connected."
        action_type = "share"
        cta = "Go to Feed"
    elif label == "Contributing":
        prefix = "Your rising status gives your actions a visibility boost — " if status_key == "rising" else ""
        msg = f"{prefix}You're contributing well — engage with more people to move toward Connected."
        action_type = "react"
        cta = "View Feed"
    elif label == "Connected":
        prefix = "Your rising status gives your actions a visibility boost. " if status_key == "rising" else ""
        msg = f"{prefix}Keep contributing — you're building real influence in the network."
        action_type = "post"
        cta = "Create Action"
    elif label == "Network":
        msg = "You're deeply connected. Help verify others' actions to strengthen the network."
        action_type = "verify"
        cta = "View Feed"
    else:
        msg = "Post a public action to build trust."
        action_type = "post"
        cta = "Create Action"

    return {
        "success": True,
        "message": msg,
        "action_type": action_type,
        "cta": cta,
        "context": {
            "position": position,
            "label": label,
            "public_actions": public_count,
            "private_actions": private_count,
            "days_inactive": days_inactive,
            "unique_reactors": unique_reactors,
            "active_referrals": active_referrals,
        },
        "status": status_ori,
        "consequence_multiplier": get_consequence_multiplier(status_ori["status"], has_risk_ori),
    }

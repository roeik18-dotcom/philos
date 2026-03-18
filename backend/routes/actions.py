"""Actions API — post actions, feed, reactions, map data."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import os
from auth_utils import get_current_user
from utils.status_calculator import (
    calculate_status, get_consequence_multiplier,
    CONSEQUENCE_MULTIPLIERS, ENFORCEMENT_CAP,
)

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

CATEGORIES = ["education", "environment", "health", "community", "technology", "mentorship", "volunteering", "other"]
REACTION_TYPES = ["support", "useful", "verified"]
VERIFICATION_MULTIPLIERS = {"self_reported": 1, "community_verified": 2, "org_verified": 3}


class PostActionRequest(BaseModel):
    title: str
    description: str
    category: str = "other"
    community: str = ""
    location_name: str = ""
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    visibility: str = "public"


class ReactionRequest(BaseModel):
    reaction_type: str


def serialize_action(a, viewer_id="", author_multiplier=1.0):
    raw_reactions = a.get("reactions", {})
    verification = a.get("verification_level", "self_reported")
    trust_signal = a.get("trust_signal", 0)
    reaction_count = sum(len(raw_reactions.get(rt, [])) for rt in ["support", "useful", "verified"])

    # ── Rank score: recency + trust + reactions, weighted by author status ──
    created = a.get("created_at", "")
    recency_score = 0.0
    if created:
        try:
            age_hours = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(created)).total_seconds() / 3600)
            recency_score = max(0, 1.0 - (age_hours / 168))  # decays over 7 days
        except Exception:
            pass
    base_score = (recency_score * 50) + (trust_signal * 2) + (reaction_count * 3)
    rank_score = round(base_score * author_multiplier, 2)
    visibility_weight = round(author_multiplier, 2)

    return {
        "id": str(a["_id"]),
        "user_id": a.get("user_id", ""),
        "user_name": a.get("user_name", "Anonymous"),
        "title": a.get("title", ""),
        "description": a.get("description", ""),
        "category": a.get("category", "other"),
        "community": a.get("community", ""),
        "location": a.get("location", {}),
        "reactions": {
            "support": len(raw_reactions.get("support", [])),
            "useful": len(raw_reactions.get("useful", [])),
            "verified": len(raw_reactions.get("verified", [])),
        },
        "user_reacted": {
            "support": viewer_id in raw_reactions.get("support", []),
            "useful": viewer_id in raw_reactions.get("useful", []),
            "verified": viewer_id in raw_reactions.get("verified", []),
        } if viewer_id else {"support": False, "useful": False, "verified": False},
        "trust_signal": trust_signal,
        "visibility": a.get("visibility", "public"),
        "verification_level": verification,
        "verification_multiplier": VERIFICATION_MULTIPLIERS.get(verification, 1),
        "rank_score": rank_score,
        "visibility_weight": visibility_weight,
        "created_at": created,
    }


@router.post("/actions/post")
async def post_action(req: PostActionRequest, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Login required to post actions")

    from routes.trust_integrity import check_rate_limit, check_duplicate

    # Anti-spam: rate limit
    rate_check = check_rate_limit(user["id"])
    if rate_check["blocked"]:
        raise HTTPException(status_code=429, detail=rate_check["reason"])

    # Anti-spam: duplicate detection
    dup_check = check_duplicate(user["id"], req.title.strip(), req.description.strip())
    if dup_check["blocked"]:
        raise HTTPException(status_code=409, detail=dup_check["reason"])

    location = {}
    if req.location_lat is not None and req.location_lng is not None:
        location = {"lat": req.location_lat, "lng": req.location_lng, "name": req.location_name}

    action = {
        "user_id": user["id"],
        "user_name": user.get("name", user.get("email", "").split("@")[0]),
        "title": req.title.strip(),
        "description": req.description.strip(),
        "category": req.category if req.category in CATEGORIES else "other",
        "community": req.community,
        "location": location,
        "visibility": req.visibility if req.visibility in ("public", "private") else "public",
        "reactions": {"support": [], "useful": [], "verified": []},
        "trust_signal": 0.0,
        "verification_level": "self_reported",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = db.impact_actions.insert_one(action)
    action_id = str(result.inserted_id)

    # Update user's last_active
    db.user_activity.update_one(
        {"user_id": user["id"]},
        {"$set": {"last_active": datetime.now(timezone.utc).isoformat(), "last_action": "post"}},
        upsert=True,
    )

    _update_impact_profile(user["id"])

    return {"success": True, "action_id": action_id}


@router.get("/actions/feed")
async def get_feed(skip: int = 0, limit: int = 20, category: str = "", viewer_id: str = "", visibility: str = ""):
    """Public feed of actions, ranked by status-weighted score.
    Ranking formula: rank_score = (recency*50 + trust*2 + reactions*3) * author_status_multiplier
    Status multipliers: Rising=1.15, Stable=1.0, Decaying=0.85, AtRisk=0.7
    Enforcement override: active risk signals cap multiplier at 0.7."""
    query = {}
    if category and category in CATEGORIES:
        query["category"] = category

    if visibility == "private" and viewer_id:
        query["visibility"] = "private"
        query["user_id"] = viewer_id
    elif visibility == "public":
        query["visibility"] = {"$ne": "private"}
    else:
        # Default: show all public + viewer's own private
        if viewer_id:
            query["$or"] = [
                {"visibility": {"$ne": "private"}},
                {"visibility": "private", "user_id": viewer_id},
            ]
        else:
            query["visibility"] = {"$ne": "private"}

    # Fetch more than needed for re-ranking (2x buffer for skip+limit)
    fetch_limit = min((skip + limit) * 2, 200)
    actions = list(
        db.impact_actions.find(query)
        .sort("created_at", -1)
        .limit(fetch_limit)
    )

    if not actions:
        return {"success": True, "actions": []}

    # ── Batch-compute author status multipliers ──
    author_ids = list(set(a.get("user_id", "") for a in actions if a.get("user_id")))
    author_multipliers = _get_author_multipliers(author_ids)

    # Serialize with per-author multiplier
    serialized = []
    for a in actions:
        uid = a.get("user_id", "")
        mult = author_multipliers.get(uid, 1.0)
        serialized.append(serialize_action(a, viewer_id, author_multiplier=mult))

    # Sort by rank_score descending (status-weighted ranking)
    serialized.sort(key=lambda x: x["rank_score"], reverse=True)

    # Apply skip/limit after ranking
    page = serialized[skip : skip + limit]

    return {"success": True, "actions": page}


def _get_author_multipliers(user_ids: list[str]) -> dict[str, float]:
    """Compute status consequence multiplier for each user in batch.
    Uses latest position snapshot + risk signal check."""
    if not user_ids:
        return {}

    now = datetime.now(timezone.utc)
    three_days_ago = (now - timedelta(days=3)).isoformat()
    result = {}

    for uid in user_ids:
        try:
            # Get latest snapshot
            snap = db.position_snapshots.find_one(
                {"user_id": uid}, sort=[("created_at", -1)],
                projection={"_id": 0, "position": 1, "trust": 1},
            )
            # Get previous snapshot (2nd most recent)
            prev_snaps = list(db.position_snapshots.find(
                {"user_id": uid},
                projection={"_id": 0, "position": 1, "trust": 1},
            ).sort("created_at", -1).limit(2))
            prev_snap = prev_snaps[1] if len(prev_snaps) > 1 else None

            # Recent activity
            recent_count = db.impact_actions.count_documents({
                "user_id": uid,
                "created_at": {"$gte": three_days_ago},
            })

            # Days since last action
            last_action = db.impact_actions.find_one(
                {"user_id": uid}, sort=[("created_at", -1)],
                projection={"_id": 0, "created_at": 1},
            )
            days_since = 999
            if last_action:
                try:
                    days_since = max(0, (now - datetime.fromisoformat(last_action["created_at"])).days)
                except Exception:
                    pass

            has_risk = db.risk_signals.count_documents(
                {"subject_user_id": uid, "status": "active"}
            ) > 0

            current_pos = snap["position"] if snap else 0.0
            current_trust = snap["trust"] if snap else 0.0

            status = calculate_status(
                current_position=current_pos,
                current_trust=current_trust,
                prev_position=prev_snap["position"] if prev_snap else None,
                prev_trust=prev_snap["trust"] if prev_snap else None,
                recent_action_count=recent_count,
                days_since_last_action=days_since,
                has_active_risk_signals=has_risk,
            )

            result[uid] = get_consequence_multiplier(status["status"], has_risk)
        except Exception:
            result[uid] = 1.0

    return result


@router.get("/actions/{action_id}")
async def get_action(action_id: str):
    """Get a single action by ID."""
    try:
        oid = ObjectId(action_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid action ID")
    action = db.impact_actions.find_one({"_id": oid})
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"success": True, "action": serialize_action(action)}


@router.post("/actions/{action_id}/react")
async def react_to_action(action_id: str, req: ReactionRequest, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Login required to react")
    if req.reaction_type not in REACTION_TYPES:
        raise HTTPException(status_code=400, detail="Invalid reaction type")

    user_id = user["id"]

    try:
        oid = ObjectId(action_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid action ID")

    action = db.impact_actions.find_one({"_id": oid})
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    # Anti-spam: prevent self-reaction
    from routes.trust_integrity import check_self_reaction, check_suspicious_reaction, recalc_trust_signal
    self_check = check_self_reaction(user_id, action)
    if self_check["blocked"]:
        raise HTTPException(status_code=403, detail=self_check["reason"])

    field = f"reactions.{req.reaction_type}"

    # Toggle: add if not present, remove if present
    existing = action.get("reactions", {}).get(req.reaction_type, [])
    if user_id in existing:
        db.impact_actions.update_one({"_id": oid}, {"$pull": {field: user_id}})
        added = False
    else:
        db.impact_actions.update_one({"_id": oid}, {"$addToSet": {field: user_id}})
        added = True

    # Recalculate trust signal with verification multiplier
    updated = db.impact_actions.find_one({"_id": oid})
    trust_signal = recalc_trust_signal(updated)
    db.impact_actions.update_one({"_id": oid}, {"$set": {"trust_signal": trust_signal}})

    # Check for suspicious activity (non-blocking)
    try:
        check_suspicious_reaction(user_id, updated)
    except Exception:
        pass  # Don't block the reaction for flag errors

    # Update reactor's last_active
    db.user_activity.update_one(
        {"user_id": user_id},
        {"$set": {"last_active": datetime.now(timezone.utc).isoformat(), "last_action": "react"}},
        upsert=True,
    )

    # Update poster's impact profile
    _update_impact_profile(action.get("user_id", ""))

    return {"success": True, "added": added, "trust_signal": trust_signal}


@router.get("/actions/map")
async def get_map_data():
    """Get actions with location for the impact map."""
    actions = list(
        db.impact_actions.find({"location.lat": {"$exists": True}})
        .sort("created_at", -1)
        .limit(200)
    )
    points = []
    for a in actions:
        loc = a.get("location", {})
        if loc.get("lat") and loc.get("lng"):
            points.append({
                "id": str(a["_id"]),
                "lat": loc["lat"],
                "lng": loc["lng"],
                "title": a.get("title", ""),
                "category": a.get("category", ""),
                "community": a.get("community", ""),
                "location_name": loc.get("name", ""),
                "trust_signal": a.get("trust_signal", 0),
                "user_name": a.get("user_name", "Anonymous"),
                "created_at": a.get("created_at", ""),
            })
    return {"success": True, "points": points}


@router.get("/impact/profile/{user_id}")
async def get_impact_profile(user_id: str):
    """Get a user's impact profile."""
    profile = db.impact_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        profile = _build_impact_profile(user_id)
    return {"success": True, "profile": profile}


@router.get("/impact/dashboard/{user_id}")
async def get_daily_dashboard(user_id: str):
    """Daily opening dashboard — personal impact + network + suggestions."""
    profile = db.impact_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        profile = _build_impact_profile(user_id)

    # Recent network activity
    recent_actions = list(
        db.impact_actions.find()
        .sort("created_at", -1)
        .limit(5)
    )
    network_activity = [
        {"user": a.get("user_name", "Someone"), "action": a.get("title", ""), "category": a.get("category", "")}
        for a in recent_actions
    ]

    # Suggested actions based on low-activity categories
    user_categories = profile.get("fields", [])
    suggestions = []
    for cat in CATEGORIES[:4]:
        if cat not in user_categories:
            suggestions.append({"category": cat, "prompt": f"Try an action in {cat}"})
    if not suggestions:
        suggestions = [{"category": "community", "prompt": "Keep contributing to your community"}]

    # Opportunities unlocked
    min_score = profile.get("impact_score", 0)
    opportunities = list(
        db.impact_opportunities.find(
            {"min_trust_score": {"$lte": min_score}, "status": "active"},
            {"_id": 0}
        ).limit(5)
    )

    return {
        "success": True,
        "profile_summary": {
            "impact_score": profile.get("impact_score", 0),
            "total_actions": profile.get("total_actions", 0),
            "verified_count": profile.get("verified_count", 0),
        },
        "network_activity": network_activity,
        "suggested_actions": suggestions[:3],
        "opportunities": opportunities,
    }


@router.get("/impact/opportunities")
async def get_opportunities(min_score: float = 0):
    """Get available opportunities."""
    query = {"status": "active"}
    if min_score > 0:
        query["min_trust_score"] = {"$lte": min_score}

    opps = list(db.impact_opportunities.find(query, {"_id": 0}).sort("created_at", -1).limit(20))
    return {"success": True, "opportunities": opps}


def _update_impact_profile(user_id: str):
    """Recalculate and store impact profile."""
    if not user_id:
        return
    profile = _build_impact_profile(user_id)
    db.impact_profiles.update_one(
        {"user_id": user_id},
        {"$set": profile},
        upsert=True,
    )


def _build_impact_profile(user_id: str):
    """Build impact profile from actions data."""
    actions = list(db.impact_actions.find({"user_id": user_id}))

    categories = set()
    communities = set()
    total_trust = 0.0
    verified_count = 0

    for a in actions:
        categories.add(a.get("category", "other"))
        if a.get("community"):
            communities.add(a["community"])
        total_trust += a.get("trust_signal", 0)
        verified_count += len(a.get("reactions", {}).get("verified", []))

    return {
        "user_id": user_id,
        "trust_score": round(total_trust, 1),
        "impact_score": round(total_trust + len(actions) * 2, 1),
        "total_actions": len(actions),
        "fields": list(categories),
        "communities": list(communities),
        "verified_count": verified_count,
        "opportunities_generated": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

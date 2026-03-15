"""Actions API — post actions, feed, reactions, map data."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
import os
from auth_utils import get_current_user

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

CATEGORIES = ["education", "environment", "health", "community", "technology", "mentorship", "volunteering", "other"]
REACTION_TYPES = ["support", "useful", "verified"]


class PostActionRequest(BaseModel):
    title: str
    description: str
    category: str = "other"
    community: str = ""
    location_name: str = ""
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class ReactionRequest(BaseModel):
    reaction_type: str


def serialize_action(a, viewer_id=""):
    raw_reactions = a.get("reactions", {})
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
        "trust_signal": a.get("trust_signal", 0),
        "created_at": a.get("created_at", ""),
    }


@router.post("/actions/post")
async def post_action(req: PostActionRequest, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Login required to post actions")

    location = {}
    if req.location_lat is not None and req.location_lng is not None:
        location = {"lat": req.location_lat, "lng": req.location_lng, "name": req.location_name}

    action = {
        "user_id": user["id"],
        "user_name": user.get("name", user.get("email", "").split("@")[0]),
        "title": req.title,
        "description": req.description,
        "category": req.category if req.category in CATEGORIES else "other",
        "community": req.community,
        "location": location,
        "reactions": {"support": [], "useful": [], "verified": []},
        "trust_signal": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = db.impact_actions.insert_one(action)
    action_id = str(result.inserted_id)
    _update_impact_profile(user["id"])

    return {"success": True, "action_id": action_id}


@router.get("/actions/feed")
async def get_feed(skip: int = 0, limit: int = 20, category: str = "", viewer_id: str = ""):
    """Public feed of actions. Pass viewer_id to get user_reacted flags."""
    query = {}
    if category and category in CATEGORIES:
        query["category"] = category

    actions = list(
        db.impact_actions.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(min(limit, 50))
    )

    return {"success": True, "actions": [serialize_action(a, viewer_id) for a in actions]}


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

    field = f"reactions.{req.reaction_type}"

    # Toggle: add if not present, remove if present
    existing = action.get("reactions", {}).get(req.reaction_type, [])
    if user_id in existing:
        db.impact_actions.update_one({"_id": oid}, {"$pull": {field: user_id}})
        added = False
    else:
        db.impact_actions.update_one({"_id": oid}, {"$addToSet": {field: user_id}})
        added = True

    # Recalculate trust signal (Support=1, Useful=2, Verified=5)
    updated = db.impact_actions.find_one({"_id": oid})
    reactions = updated.get("reactions", {})
    trust_signal = (
        len(reactions.get("support", [])) * 1
        + len(reactions.get("useful", [])) * 2
        + len(reactions.get("verified", [])) * 5
    )
    db.impact_actions.update_one({"_id": oid}, {"$set": {"trust_signal": trust_signal}})

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

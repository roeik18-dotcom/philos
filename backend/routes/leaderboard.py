"""Leaderboard + Weekly Impact Report APIs."""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import os

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 20):
    """Top users ranked by trust score (aggregated from actions)."""
    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "user_name": {"$first": "$user_name"},
            "total_actions": {"$sum": 1},
            "trust_score": {"$sum": "$trust_signal"},
            "categories": {"$addToSet": "$category"},
        }},
        {"$sort": {"trust_score": -1}},
        {"$limit": min(limit, 50)},
    ]
    results = list(db.impact_actions.aggregate(pipeline))
    leaders = []
    for i, r in enumerate(results):
        leaders.append({
            "rank": i + 1,
            "user_id": r["_id"],
            "user_name": r.get("user_name", "Anonymous"),
            "trust_score": round(r.get("trust_score", 0), 1),
            "total_actions": r.get("total_actions", 0),
            "categories": r.get("categories", []),
        })
    return {"success": True, "leaders": leaders}


@router.get("/weekly-report/{user_id}")
async def weekly_impact_report(user_id: str):
    """Generate a weekly impact summary for a user."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    week_ago_str = week_ago.isoformat()

    # All user actions
    all_actions = list(db.impact_actions.find({"user_id": user_id}))

    # This week's actions
    week_actions = [a for a in all_actions if a.get("created_at", "") >= week_ago_str]

    # Totals
    total_trust = sum(a.get("trust_signal", 0) for a in all_actions)
    week_trust = sum(a.get("trust_signal", 0) for a in week_actions)

    # Categories this week
    week_cats = list(set(a.get("category", "other") for a in week_actions))

    # Communities this week
    week_communities = list(set(a.get("community", "") for a in week_actions if a.get("community")))

    # Network stats (all users, this week)
    network_pipeline = [
        {"$match": {"created_at": {"$gte": week_ago_str}}},
        {"$group": {
            "_id": None,
            "total_actions": {"$sum": 1},
            "total_trust": {"$sum": "$trust_signal"},
            "unique_users": {"$addToSet": "$user_id"},
        }},
    ]
    network_result = list(db.impact_actions.aggregate(network_pipeline))
    network = network_result[0] if network_result else {}

    # Rank calculation
    rank_pipeline = [
        {"$group": {"_id": "$user_id", "trust": {"$sum": "$trust_signal"}}},
        {"$sort": {"trust": -1}},
    ]
    all_ranks = list(db.impact_actions.aggregate(rank_pipeline))
    user_rank = 0
    for i, r in enumerate(all_ranks):
        if r["_id"] == user_id:
            user_rank = i + 1
            break
    total_users = len(all_ranks)

    return {
        "success": True,
        "report": {
            "period": f"{week_ago.strftime('%b %d')} — {datetime.now(timezone.utc).strftime('%b %d, %Y')}",
            "user_id": user_id,
            "week_actions": len(week_actions),
            "week_trust_earned": round(week_trust, 1),
            "total_trust_score": round(total_trust, 1),
            "total_actions": len(all_actions),
            "week_categories": week_cats,
            "week_communities": week_communities,
            "rank": user_rank,
            "total_users": total_users,
            "network_actions_this_week": network.get("total_actions", 0),
            "network_trust_this_week": round(network.get("total_trust", 0), 1),
            "network_active_users": len(network.get("unique_users", [])),
        },
    }

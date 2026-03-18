"""Opportunities API — MVP version with seed data and eligibility."""
from fastapi import APIRouter
from datetime import datetime, timezone
import os

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

SEED_OPPORTUNITIES = [
    {
        "title": "Community Mentor Program",
        "type": "collaboration",
        "description": "Join a mentoring program to guide newcomers in your community. Share your experience and help others grow.",
        "min_trust_score": 5,
        "community": "General",
    },
    {
        "title": "Local Impact Grant — $500",
        "type": "grant",
        "description": "Apply for a micro-grant to fund a local community initiative. Must demonstrate verified actions in the community.",
        "min_trust_score": 20,
        "community": "General",
    },
    {
        "title": "Verified Contributor Badge",
        "type": "support",
        "description": "Earn a verified contributor badge on your profile, visible to all network participants.",
        "min_trust_score": 10,
        "community": "General",
    },
    {
        "title": "Community Leadership Role",
        "type": "job",
        "description": "Become a community lead. Coordinate impact actions and help distribute resources in your area.",
        "min_trust_score": 50,
        "community": "General",
    },
    {
        "title": "Impact Partnership Access",
        "type": "collaboration",
        "description": "Get access to partnerships with NGOs and social enterprises working in your contribution areas.",
        "min_trust_score": 30,
        "community": "General",
    },
    {
        "title": "Education Scholarship Fund",
        "type": "grant",
        "description": "Access scholarships for skill development courses. Priority given to education-focused contributors.",
        "min_trust_score": 15,
        "community": "Education",
    },
    {
        "title": "Environmental Project Funding",
        "type": "grant",
        "description": "Apply for dedicated funding for environmental initiatives in your community.",
        "min_trust_score": 25,
        "community": "Environment",
    },
    {
        "title": "Health Outreach Coordinator",
        "type": "job",
        "description": "Paid position to coordinate health-related community actions across the network.",
        "min_trust_score": 40,
        "community": "Health",
    },
]

TYPE_COLORS = {"job": "#f59e0b", "grant": "#10b981", "collaboration": "#00d4ff", "support": "#7c3aed"}


def _seed_opportunities():
    if db.opportunities.count_documents({}) == 0:
        for opp in SEED_OPPORTUNITIES:
            opp["created_at"] = datetime.now(timezone.utc).isoformat()
        db.opportunities.insert_many(SEED_OPPORTUNITIES)


_seed_opportunities()


def _serialize_opp(o, user_trust=0):
    return {
        "id": str(o["_id"]),
        "title": o.get("title", ""),
        "type": o.get("type", "support"),
        "description": o.get("description", ""),
        "min_trust_score": o.get("min_trust_score", 0),
        "community": o.get("community", "General"),
        "eligible": user_trust >= o.get("min_trust_score", 0),
        "created_at": o.get("created_at", ""),
    }


def _get_user_trust(user_id: str) -> float:
    actions = list(db.impact_actions.find({"user_id": user_id}))
    total = 0
    for a in actions:
        total += a.get("trust_signal", 0)
    return total


@router.get("/opportunities")
async def list_opportunities(user_id: str = ""):
    """List all opportunities with optional eligibility check."""
    opps = list(db.opportunities.find().sort("min_trust_score", 1))
    trust = _get_user_trust(user_id) if user_id else 0
    return {
        "success": True,
        "user_trust_score": round(trust, 1),
        "opportunities": [_serialize_opp(o, trust) for o in opps],
    }

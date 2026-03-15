"""Community Funds API — leaderboard, fund summaries, seed data."""
from fastapi import APIRouter
from datetime import datetime, timezone
import os

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

SEED_COMMUNITIES = [
    {"name": "Tel Aviv Volunteers", "location": "Tel Aviv", "description": "Active volunteer network in central Tel Aviv."},
    {"name": "Haifa Tech for Good", "location": "Haifa", "description": "Technology volunteers building tools for social impact."},
    {"name": "Jerusalem Education Hub", "location": "Jerusalem", "description": "Education-focused community initiatives."},
    {"name": "Negev Green Initiative", "location": "Negev", "description": "Environmental restoration and sustainability projects."},
    {"name": "Galilee Health Network", "location": "Galilee", "description": "Healthcare access and outreach in northern communities."},
]

SEED_FUNDS = [
    {"community": "Tel Aviv Volunteers", "total_raised": 12500, "total_distributed": 8200, "transactions": [
        {"amount": 5000, "type": "donation", "description": "Annual fundraiser"},
        {"amount": 7500, "type": "donation", "description": "Corporate sponsorship"},
        {"amount": -3200, "type": "distribution", "description": "Community event funding"},
        {"amount": -5000, "type": "distribution", "description": "Volunteer stipends Q1"},
    ]},
    {"community": "Haifa Tech for Good", "total_raised": 8700, "total_distributed": 4100, "transactions": [
        {"amount": 3700, "type": "donation", "description": "Crowdfunding campaign"},
        {"amount": 5000, "type": "grant", "description": "Government tech grant"},
        {"amount": -4100, "type": "distribution", "description": "Hardware and hosting costs"},
    ]},
    {"community": "Jerusalem Education Hub", "total_raised": 15000, "total_distributed": 11500, "transactions": [
        {"amount": 10000, "type": "grant", "description": "Education ministry grant"},
        {"amount": 5000, "type": "donation", "description": "Alumni donations"},
        {"amount": -6500, "type": "distribution", "description": "Scholarship fund"},
        {"amount": -5000, "type": "distribution", "description": "Learning materials"},
    ]},
    {"community": "Negev Green Initiative", "total_raised": 6200, "total_distributed": 3800, "transactions": [
        {"amount": 4200, "type": "donation", "description": "Environmental foundation"},
        {"amount": 2000, "type": "grant", "description": "Sustainability grant"},
        {"amount": -3800, "type": "distribution", "description": "Tree planting project"},
    ]},
    {"community": "Galilee Health Network", "total_raised": 9800, "total_distributed": 7200, "transactions": [
        {"amount": 5800, "type": "donation", "description": "Health NGO partnership"},
        {"amount": 4000, "type": "grant", "description": "Medical equipment fund"},
        {"amount": -4200, "type": "distribution", "description": "Mobile clinic operations"},
        {"amount": -3000, "type": "distribution", "description": "Medicine supplies"},
    ]},
]


def _seed_communities():
    if db.communities.count_documents({}) == 0:
        for c in SEED_COMMUNITIES:
            c["created_at"] = datetime.now(timezone.utc).isoformat()
        db.communities.insert_many(SEED_COMMUNITIES)

    if db.community_funds.count_documents({}) == 0:
        for f in SEED_FUNDS:
            txns = f.pop("transactions")
            f["current_balance"] = f["total_raised"] - f["total_distributed"]
            f["created_at"] = datetime.now(timezone.utc).isoformat()
            result = db.community_funds.insert_one(f)
            fund_id = str(result.inserted_id)
            for t in txns:
                t["fund_id"] = fund_id
                t["community"] = f["community"]
                t["created_at"] = datetime.now(timezone.utc).isoformat()
            if txns:
                db.fund_transactions.insert_many(txns)


_seed_communities()


@router.get("/community-funds")
async def community_fund_leaderboard():
    """Leaderboard of community funds sorted by current balance."""
    funds = list(db.community_funds.find({}, {"_id": 0}).sort("current_balance", -1))
    return {"success": True, "funds": funds}


@router.get("/community-funds/{community_name}")
async def community_fund_detail(community_name: str):
    """Get fund details for a specific community."""
    fund = db.community_funds.find_one({"community": community_name}, {"_id": 0})
    if not fund:
        return {"success": False, "detail": "Community fund not found"}
    txns = list(db.fund_transactions.find({"community": community_name}, {"_id": 0}).sort("created_at", -1))
    return {"success": True, "fund": fund, "transactions": txns}


@router.get("/communities")
async def list_communities():
    """List all communities."""
    communities = list(db.communities.find({}, {"_id": 0}))
    return {"success": True, "communities": communities}

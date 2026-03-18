"""Risk Signals — detection, storage, and management of user-behavior risk signals."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from collections import defaultdict
import os
import logging

from models.risk_signal_models import UpdateSignalStatus

router = APIRouter()
logger = logging.getLogger("risk_signals")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]


# ═══════════════════════════════════════════════════
# SIGNAL DEFINITIONS — the canonical risk-signal table
# ═══════════════════════════════════════════════════

SIGNAL_DEFINITIONS = {
    "reaction_farming": {
        "category": "trust_manipulation",
        "severity": "medium",
        "description": "User reacts to many actions from the same poster in a short window, inflating that poster's trust.",
        "indicator": "10+ reactions to the same poster's actions within 1 hour.",
        "system_response": "Flag for review. Suppress flagged reactions from trust calculation.",
        "source": "existing",
    },
    "velocity_spike": {
        "category": "trust_manipulation",
        "severity": "high",
        "description": "A single action accumulates reactions abnormally fast, suggesting coordinated boosting.",
        "indicator": "20+ reactions on one action within 5 minutes.",
        "system_response": "Flag action. Temporarily freeze its trust score until reviewed.",
        "source": "existing",
    },
    "reciprocal_boosting": {
        "category": "trust_manipulation",
        "severity": "medium",
        "description": "Two users exclusively or heavily react to each other's content, forming a mutual trust-inflation loop.",
        "indicator": "Two users where >60% of their reactions target each other.",
        "system_response": "Flag both users. Discount mutual reactions by 50% in trust calculation.",
        "source": "existing",
    },
    "low_effort_content": {
        "category": "content_integrity",
        "severity": "low",
        "description": "Actions with minimal titles or descriptions that add no real value to the network.",
        "indicator": "Title < 5 characters or description < 15 characters.",
        "system_response": "Flag action. Exclude from featured/verified flows. Prompt user to add detail.",
        "source": "existing",
    },
    "category_flooding": {
        "category": "content_integrity",
        "severity": "low",
        "description": "User posts many actions in the same category within a short window, suggesting low-quality bulk posting.",
        "indicator": "4+ actions in the same category within 6 hours.",
        "system_response": "Flag user. Apply soft rate limit: max 3 actions per category per 6 hours.",
        "source": "existing",
    },
    "ghost_reactor": {
        "category": "account_behavior",
        "severity": "low",
        "description": "Account that only reacts but never posts actions. May indicate a sock-puppet used to boost others.",
        "indicator": "10+ total reactions given across all actions, but 0 posts.",
        "system_response": "Flag for review. Reduce reaction weight to 0.5x until first post.",
        "source": "existing",
    },
    "burst_and_vanish": {
        "category": "account_behavior",
        "severity": "medium",
        "description": "Intense activity burst followed by sudden silence, suggesting a one-time trust-farming attempt.",
        "indicator": "5+ actions within 24 hours, then 7+ days of zero activity.",
        "system_response": "Flag user. Apply accelerated trust decay (10% instead of 5%) for burst-created actions.",
        "source": "existing",
    },
    "community_monopoly": {
        "category": "network_anomaly",
        "severity": "medium",
        "description": "One user generates the vast majority of actions in a community, reducing community diversity.",
        "indicator": "One user produces >80% of a community's total actions (min 5 actions in community).",
        "system_response": "Flag user+community. Cap trust weight from monopolized community at 0.5x.",
        "source": "existing",
    },
}


# ═══════════════════════════════════════════════════
# DETECTION FUNCTIONS
# ═══════════════════════════════════════════════════

def _upsert_signal(signal_type: str, subject_user_id: str, key_fields: dict,
                   related_user_ids=None, related_action_ids=None, evidence=None):
    """Insert or update a risk signal. Uses signal_type + subject_user_id + key for dedup."""
    defn = SIGNAL_DEFINITIONS[signal_type]
    now = datetime.now(timezone.utc).isoformat()

    query = {"signal_type": signal_type, "subject_user_id": subject_user_id, **key_fields}
    existing = db.risk_signals.find_one(query)
    if existing and existing.get("status") in ("resolved", "dismissed"):
        return None  # Don't re-flag resolved signals

    doc = {
        "signal_type": signal_type,
        "category": defn["category"],
        "severity": defn["severity"],
        "subject_user_id": subject_user_id,
        "related_user_ids": related_user_ids or [],
        "related_action_ids": related_action_ids or [],
        "evidence": evidence or {},
        "status": "active",
        "system_response": defn["system_response"],
        "created_at": now,
        "resolved_at": None,
        "expires_at": None,
        **key_fields,
    }

    result = db.risk_signals.update_one(query, {"$set": doc}, upsert=True)
    return "created" if result.upserted_id else "updated"


def detect_reciprocal_boosting():
    """Detect pairs of users who heavily react to each other's content."""
    count = 0
    actions = list(db.impact_actions.find({}, {"_id": 1, "user_id": 1, "reactions": 1}))

    # Build: who reacted to whose actions
    # reaction_map[reactor_id][poster_id] = count
    reaction_map = defaultdict(lambda: defaultdict(int))
    for a in actions:
        poster = a.get("user_id", "")
        for rtype in ["support", "useful", "verified"]:
            for reactor_id in a.get("reactions", {}).get(rtype, []):
                if reactor_id != poster:
                    reaction_map[reactor_id][poster] += 1

    # Check for mutual heavy reaction pairs
    checked = set()
    for user_a, targets in reaction_map.items():
        total_a = sum(targets.values())
        if total_a < 3:
            continue
        for user_b, a_to_b_count in targets.items():
            pair = tuple(sorted([user_a, user_b]))
            if pair in checked:
                continue
            checked.add(pair)

            b_to_a_count = reaction_map.get(user_b, {}).get(user_a, 0)
            total_b = sum(reaction_map.get(user_b, {}).values())
            if total_b < 3:
                continue

            a_pct = a_to_b_count / total_a if total_a else 0
            b_pct = b_to_a_count / total_b if total_b else 0

            if a_pct > 0.6 and b_pct > 0.6:
                result = _upsert_signal(
                    "reciprocal_boosting", user_a,
                    key_fields={"_pair_key": "|".join(pair)},
                    related_user_ids=[user_b],
                    evidence={
                        "user_a": user_a, "user_b": user_b,
                        "a_to_b": a_to_b_count, "b_to_a": b_to_a_count,
                        "a_pct": round(a_pct, 2), "b_pct": round(b_pct, 2),
                    },
                )
                if result:
                    count += 1
    return count


def detect_low_effort_content():
    """Detect actions with very short titles or descriptions."""
    count = 0
    actions = list(db.impact_actions.find({}, {"_id": 1, "user_id": 1, "title": 1, "description": 1}))
    for a in actions:
        title = (a.get("title") or "").strip()
        desc = (a.get("description") or "").strip()
        if len(title) < 5 or len(desc) < 15:
            result = _upsert_signal(
                "low_effort_content", a.get("user_id", ""),
                key_fields={"_action_key": str(a["_id"])},
                related_action_ids=[str(a["_id"])],
                evidence={"title_len": len(title), "desc_len": len(desc), "title": title, "desc": desc},
            )
            if result:
                count += 1
    return count


def detect_category_flooding():
    """Detect users who post 4+ actions in the same category within 6 hours."""
    count = 0
    six_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
    recent = list(db.impact_actions.find(
        {"created_at": {"$gte": six_hours_ago}},
        {"_id": 1, "user_id": 1, "category": 1, "created_at": 1},
    ))

    user_cat = defaultdict(lambda: defaultdict(list))
    for a in recent:
        user_cat[a["user_id"]][a.get("category", "other")].append(str(a["_id"]))

    for user_id, cats in user_cat.items():
        for cat, action_ids in cats.items():
            if len(action_ids) >= 4:
                result = _upsert_signal(
                    "category_flooding", user_id,
                    key_fields={"_flood_cat": cat},
                    related_action_ids=action_ids,
                    evidence={"category": cat, "count": len(action_ids), "window": "6h"},
                )
                if result:
                    count += 1
    return count


def detect_ghost_reactors():
    """Detect users who react a lot but never post."""
    count = 0
    actions = list(db.impact_actions.find({}, {"_id": 1, "user_id": 1, "reactions": 1}))
    posters = set(a["user_id"] for a in actions if a.get("user_id"))

    # Count reactions per reactor
    reactor_counts = defaultdict(int)
    for a in actions:
        for rtype in ["support", "useful", "verified"]:
            for reactor_id in a.get("reactions", {}).get(rtype, []):
                reactor_counts[reactor_id] += 1

    for reactor_id, rcount in reactor_counts.items():
        if reactor_id not in posters and rcount >= 10:
            result = _upsert_signal(
                "ghost_reactor", reactor_id,
                key_fields={},
                evidence={"total_reactions_given": rcount, "total_posts": 0},
            )
            if result:
                count += 1
    return count


def detect_burst_and_vanish():
    """Detect users who posted 5+ actions in 24h then went silent for 7+ days."""
    count = 0
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    # Get all actions grouped by user and sorted by date
    pipeline = [
        {"$group": {"_id": "$user_id", "dates": {"$push": "$created_at"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 5}}},
    ]
    for doc in db.impact_actions.aggregate(pipeline):
        user_id = doc["_id"]
        if not user_id:
            continue
        dates = sorted(doc["dates"])
        last_action = dates[-1]

        # Check if last action was 7+ days ago
        if last_action > seven_days_ago:
            continue

        # Check if there was a 24h burst
        for i in range(len(dates)):
            window_end = dates[i][:10]  # date part
            burst_count = sum(
                1 for d in dates
                if d >= dates[i] and d <= (datetime.fromisoformat(dates[i]) + timedelta(hours=24)).isoformat()
            )
            if burst_count >= 5:
                result = _upsert_signal(
                    "burst_and_vanish", user_id,
                    key_fields={},
                    evidence={
                        "burst_count": burst_count,
                        "burst_start": dates[i],
                        "last_action": last_action,
                        "days_silent": (datetime.now(timezone.utc) - datetime.fromisoformat(last_action)).days,
                    },
                )
                if result:
                    count += 1
                break
    return count


def detect_community_monopoly():
    """Detect when one user produces >80% of a community's actions."""
    count = 0
    pipeline = [
        {"$match": {"community": {"$ne": ""}}},
        {"$group": {
            "_id": {"community": "$community", "user_id": "$user_id"},
            "count": {"$sum": 1},
        }},
    ]
    results = list(db.impact_actions.aggregate(pipeline))

    community_totals = defaultdict(int)
    community_users = defaultdict(lambda: defaultdict(int))
    for r in results:
        comm = r["_id"]["community"]
        uid = r["_id"]["user_id"]
        community_totals[comm] += r["count"]
        community_users[comm][uid] = r["count"]

    for comm, total in community_totals.items():
        if total < 5:
            continue
        for uid, user_count in community_users[comm].items():
            pct = user_count / total
            if pct > 0.8:
                result = _upsert_signal(
                    "community_monopoly", uid,
                    key_fields={"_community_key": comm},
                    evidence={
                        "community": comm,
                        "user_actions": user_count,
                        "community_total": total,
                        "monopoly_pct": round(pct * 100, 1),
                    },
                )
                if result:
                    count += 1
    return count


# ═══════════════════════════════════════════════════
# SCANNER — runs all detections
# ═══════════════════════════════════════════════════

def run_full_scan():
    """Run all risk signal detections. Returns per-signal counts."""
    results = {}
    detectors = [
        ("reciprocal_boosting", detect_reciprocal_boosting),
        ("low_effort_content", detect_low_effort_content),
        ("category_flooding", detect_category_flooding),
        ("ghost_reactor", detect_ghost_reactors),
        ("burst_and_vanish", detect_burst_and_vanish),
        ("community_monopoly", detect_community_monopoly),
    ]
    for name, fn in detectors:
        try:
            results[name] = fn()
        except Exception as e:
            logger.error(f"Risk signal detection error [{name}]: {e}")
            results[name] = f"error: {str(e)}"
    return results


# ═══════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/risk-signals/definitions")
async def get_signal_definitions():
    """Return the canonical risk-signal table with all 8 signal types."""
    table = []
    for sig_type, defn in SIGNAL_DEFINITIONS.items():
        table.append({
            "signal_type": sig_type,
            "category": defn["category"],
            "severity": defn["severity"],
            "description": defn["description"],
            "indicator": defn["indicator"],
            "system_response": defn["system_response"],
            "source": defn["source"],
        })
    return {"success": True, "signals": table, "total": len(table)}


@router.post("/risk-signals/scan")
async def trigger_scan():
    """Run the full risk-signal scanner across all current data."""
    results = run_full_scan()
    total_active = db.risk_signals.count_documents({"status": "active"})
    return {
        "success": True,
        "scan_results": results,
        "total_active_signals": total_active,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/risk-signals")
async def list_risk_signals(
    category: str = "",
    severity: str = "",
    status: str = "active",
    limit: int = 50,
):
    """List risk signals with optional filters."""
    query = {}
    if category:
        query["category"] = category
    if severity:
        query["severity"] = severity
    if status:
        query["status"] = status

    signals = list(
        db.risk_signals.find(query)
        .sort("created_at", -1)
        .limit(min(limit, 200))
    )
    for s in signals:
        s["signal_id"] = str(s.pop("_id"))

    return {"success": True, "signals": signals, "total": db.risk_signals.count_documents(query)}


@router.get("/risk-signals/summary")
async def get_risk_summary():
    """Aggregate overview of all risk signals by category and severity."""
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": {"category": "$category", "severity": "$severity"},
            "count": {"$sum": 1},
        }},
    ]
    agg = list(db.risk_signals.aggregate(pipeline))

    by_category = defaultdict(int)
    by_severity = defaultdict(int)
    for r in agg:
        by_category[r["_id"]["category"]] += r["count"]
        by_severity[r["_id"]["severity"]] += r["count"]

    total = db.risk_signals.count_documents({"status": "active"})

    return {
        "success": True,
        "total_active": total,
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
        "breakdown": [
            {"category": r["_id"]["category"], "severity": r["_id"]["severity"], "count": r["count"]}
            for r in agg
        ],
    }


@router.patch("/risk-signals/{signal_id}")
async def update_signal_status(signal_id: str, req: UpdateSignalStatus):
    """Update a signal's status (resolve or dismiss)."""
    if req.status not in ("active", "resolved", "dismissed"):
        raise HTTPException(status_code=400, detail="Status must be: active, resolved, dismissed")

    try:
        oid = ObjectId(signal_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signal ID")

    update = {"status": req.status}
    if req.status in ("resolved", "dismissed"):
        update["resolved_at"] = datetime.now(timezone.utc).isoformat()
        update["resolution_note"] = req.resolution_note

    result = db.risk_signals.update_one({"_id": oid}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Signal not found")

    return {"success": True, "signal_id": signal_id, "new_status": req.status}


@router.get("/risk-signals/user/{user_id}")
async def get_user_risk_signals(user_id: str):
    """Get all risk signals for a specific user."""
    signals = list(
        db.risk_signals.find({"subject_user_id": user_id})
        .sort("created_at", -1)
    )
    for s in signals:
        s["signal_id"] = str(s.pop("_id"))

    active = sum(1 for s in signals if s.get("status") == "active")
    return {
        "success": True,
        "user_id": user_id,
        "signals": signals,
        "total": len(signals),
        "active": active,
    }

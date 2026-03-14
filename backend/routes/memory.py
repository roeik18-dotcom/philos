"""Memory system, replay insights, and full user data routes."""
from fastapi import APIRouter, HTTPException
from database import db
from models.schemas import (
    PathSelectionRecord, PathLearningRecord, AdaptiveScores,
    DecisionRecordRequest, MemoryDataResponse, ReplayMetadataRequest,
    ReplayInsightsResponse, FullUserDataResponse
)
from services.helpers import generate_replay_insights_hebrew
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging
import math

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/memory/decision")
async def save_decision(data: DecisionRecordRequest):
    """
    Save a decision record to persistent storage and update frequency tracking.
    """
    try:
        now = datetime.now(timezone.utc)
        today = now.strftime('%Y-%m-%d')
        week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
        
        doc = {
            'id': str(uuid.uuid4()),
            'user_id': data.user_id,
            'action': data.action,
            'decision': data.decision,
            'chaos_order': data.chaos_order,
            'ego_collective': data.ego_collective,
            'balance_score': data.balance_score,
            'value_tag': data.value_tag,
            'session_id': data.session_id,
            'parent_decision_id': data.parent_decision_id,
            'template_type': data.template_type,
            'time': now.strftime('%H:%M'),
            'date': today,
            'week': week_start,
            'timestamp': now.isoformat()
        }
        
        await db.philos_decisions.insert_one(doc)
        
        # Update decision frequency tracking
        await db.philos_user_stats.update_one(
            {"user_id": data.user_id},
            {
                "$inc": {
                    "total_decisions": 1,
                    f"daily.{today}": 1,
                    f"weekly.{week_start}": 1
                },
                "$set": {
                    "last_decision_at": now.isoformat()
                },
                "$setOnInsert": {
                    "created_at": now.isoformat()
                }
            },
            upsert=True
        )
        
        return {"success": True, "id": doc['id'], "timestamp": now.isoformat()}
        
    except Exception as e:
        logger.error(f"Save decision error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/path-selection")
async def save_path_selection(data: PathSelectionRecord):
    """
    Save a path selection record.
    """
    try:
        doc = data.model_dump()
        await db.philos_path_selections.insert_one(doc)
        
        return {"success": True, "id": doc['id']}
        
    except Exception as e:
        logger.error(f"Save path selection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/path-learning")
async def save_path_learning(data: PathLearningRecord):
    """
    Save a path learning result and update adaptive scores.
    """
    try:
        # Save the learning record
        doc = data.model_dump()
        await db.philos_path_learning.insert_one(doc)
        
        # Update adaptive scores based on learning
        await update_adaptive_scores(data.user_id, data)
        
        return {"success": True, "id": doc['id']}
        
    except Exception as e:
        logger.error(f"Save path learning error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_adaptive_scores(user_id: str, learning: PathLearningRecord):
    """
    Update adaptive scores based on a new learning result.
    """
    try:
        # Get existing scores or create default
        existing = await db.philos_adaptive_scores.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        scores = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        if existing:
            scores = {
                'contribution': existing.get('contribution', 0),
                'recovery': existing.get('recovery', 0),
                'order': existing.get('order', 0),
                'harm': existing.get('harm', 0),
                'avoidance': existing.get('avoidance', 0)
            }
        
        path_type = learning.predicted_value_tag
        if path_type not in scores:
            return
        
        # Boost if actual recovery stability was better than predicted
        if learning.actual_recovery_stability > learning.predicted_recovery_stability:
            scores[path_type] += 2
        
        # Boost if harm pressure was lower than predicted
        if learning.actual_harm_pressure < learning.predicted_harm_pressure:
            scores[path_type] += 2
        
        # Boost if order drift improved
        if learning.actual_order_drift > learning.predicted_order_drift and learning.actual_order_drift > 0:
            scores[path_type] += 1
        
        # Penalty if harm pressure increased
        if learning.actual_harm_pressure > learning.predicted_harm_pressure:
            scores[path_type] -= 3
        
        # Penalty if match quality was low
        if learning.match_quality == 'low':
            scores[path_type] -= 2
        
        # Penalty if actual outcome moved toward avoidance or harm
        if learning.actual_value_tag in ['avoidance', 'harm']:
            scores[path_type] -= 4
        
        # Bonus for high match quality
        if learning.match_quality == 'high':
            scores[path_type] += 3
        
        # Clamp scores to reasonable range
        for key in scores:
            scores[key] = max(-20, min(20, scores[key]))
        
        # Save updated scores
        await db.philos_adaptive_scores.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                **scores,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
    except Exception as e:
        logger.error(f"Update adaptive scores error: {str(e)}")


@router.get("/memory/{user_id}", response_model=MemoryDataResponse)
async def get_memory_data(user_id: str):
    """
    Get all persistent memory data for a user (learning history + adaptive scores).
    """
    try:
        # Get learning history (last 50)
        learning_history = await db.philos_path_learning.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        # Reverse to get oldest first
        learning_history = list(reversed(learning_history))
        
        # Get adaptive scores
        adaptive_scores = await db.philos_adaptive_scores.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not adaptive_scores:
            adaptive_scores = {
                'contribution': 0,
                'recovery': 0,
                'order': 0,
                'harm': 0,
                'avoidance': 0
            }
        
        return MemoryDataResponse(
            success=True,
            user_id=user_id,
            learning_history=learning_history,
            adaptive_scores=adaptive_scores,
            last_synced=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Get memory data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/stats/{user_id}")
async def get_user_decision_stats(user_id: str):
    """
    Get decision frequency stats for a user (total, daily, weekly).
    """
    try:
        now = datetime.now(timezone.utc)
        today = now.strftime('%Y-%m-%d')
        week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
        
        stats = await db.philos_user_stats.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not stats:
            return {
                "success": True,
                "user_id": user_id,
                "total_decisions": 0,
                "today_decisions": 0,
                "week_decisions": 0,
                "last_decision_at": None
            }
        
        daily = stats.get("daily", {})
        weekly = stats.get("weekly", {})
        
        return {
            "success": True,
            "user_id": user_id,
            "total_decisions": stats.get("total_decisions", 0),
            "today_decisions": daily.get(today, 0),
            "week_decisions": weekly.get(week_start, 0),
            "last_decision_at": stats.get("last_decision_at")
        }
        
    except Exception as e:
        logger.error(f"Get user stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/replay")
async def save_replay_metadata(data: ReplayMetadataRequest):
    """
    Save decision replay metadata for counterfactual analysis.
    Tracks which alternative paths users explored and predicted outcomes.
    """
    try:
        now = datetime.now(timezone.utc)
        
        doc = {
            'id': str(uuid.uuid4()),
            'user_id': data.user_id,
            'replay_of_decision_id': data.replay_of_decision_id,
            'original_value_tag': data.original_value_tag,
            'alternative_path_id': data.alternative_path_id,
            'alternative_path_type': data.alternative_path_type,
            'predicted_metrics': data.predicted_metrics,
            'timestamp': data.timestamp or now.isoformat(),
            'created_at': now.isoformat()
        }
        
        await db.philos_replays.insert_one(doc)
        
        return {"success": True, "id": doc['id'], "timestamp": doc['timestamp']}
        
    except Exception as e:
        logger.error(f"Save replay metadata error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/replays/{user_id}")
async def get_replay_history(user_id: str, limit: int = 50):
    """
    Get replay history for a user to analyze counterfactual exploration patterns.
    """
    try:
        replays = await db.philos_replays.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Aggregate replay patterns
        pattern_counts = {}
        for replay in replays:
            orig = replay.get('original_value_tag', '')
            alt = replay.get('alternative_path_type', '')
            pattern = f"{orig}_to_{alt}"
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return {
            "success": True,
            "user_id": user_id,
            "replays": replays,
            "total_replays": len(replays),
            "pattern_counts": pattern_counts
        }
        
    except Exception as e:
        logger.error(f"Get replay history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/replay-insights/{user_id}", response_model=ReplayInsightsResponse)
async def get_replay_insights(user_id: str):
    """
    Get aggregated replay insights for behavioral analysis.
    Analyzes patterns, blind spots, and generates Hebrew insights.
    """
    try:
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        # Get all replays for user
        replays = await db.philos_replays.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(500)
        
        if not replays:
            return ReplayInsightsResponse(
                success=True,
                user_id=user_id,
                total_replays=0,
                insights=["אין עדיין נתוני הפעלה חוזרת. התחל לבדוק מסלולים חלופיים כדי לקבל תובנות."],
                generated_at=now.isoformat()
            )
        
        # 1. Count alternative path explorations
        alternative_path_counts = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        # 2. Count transition patterns
        transition_map = {}
        
        # 3. Count original tags that were replayed
        original_tag_counts = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        # 4. Recent replays count
        recent_count = 0
        
        for replay in replays:
            alt_type = replay.get('alternative_path_type', '')
            orig_type = replay.get('original_value_tag', '')
            timestamp = replay.get('timestamp', '')
            
            # Count alternative paths
            if alt_type in alternative_path_counts:
                alternative_path_counts[alt_type] += 1
            
            # Count original tags
            if orig_type in original_tag_counts:
                original_tag_counts[orig_type] += 1
            
            # Count transitions
            if orig_type and alt_type:
                pattern_key = f"{orig_type}_to_{alt_type}"
                transition_map[pattern_key] = transition_map.get(pattern_key, 0) + 1
            
            # Count recent replays
            if timestamp >= seven_days_ago:
                recent_count += 1
        
        # 5. Build sorted transition patterns list
        transition_patterns = [
            {"from": k.split('_to_')[0], "to": k.split('_to_')[1], "count": v}
            for k, v in sorted(transition_map.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # 6. Identify blind spots (possible transitions never explored)
        all_tags = ['contribution', 'recovery', 'order', 'harm', 'avoidance']
        explored_transitions = set(transition_map.keys())
        
        blind_spots = []
        # Focus on positive blind spots (not exploring positive alternatives)
        positive_tags = ['contribution', 'recovery', 'order']
        for orig in all_tags:
            if original_tag_counts.get(orig, 0) > 0:  # User has replayed this type
                for alt in positive_tags:
                    if orig != alt:
                        pattern = f"{orig}_to_{alt}"
                        if pattern not in explored_transitions:
                            blind_spots.append({"from": orig, "to": alt})
        
        # Limit blind spots to most relevant (max 3)
        blind_spots = blind_spots[:3]
        
        # 7. Generate Hebrew insights
        insights = generate_replay_insights_hebrew(
            alternative_path_counts,
            transition_patterns,
            blind_spots,
            original_tag_counts,
            len(replays)
        )
        
        return ReplayInsightsResponse(
            success=True,
            user_id=user_id,
            total_replays=len(replays),
            alternative_path_counts=alternative_path_counts,
            transition_patterns=transition_patterns[:10],  # Top 10
            blind_spots=blind_spots,
            most_replayed_original_tags=original_tag_counts,
            insights=insights,
            recent_replay_count=recent_count,
            generated_at=now.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Get replay insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_adaptive_scores(user_id: str, learning: PathLearningRecord):
    """
    Update adaptive scores based on a new learning result.
    """
    try:
        # Get existing scores or create default
        existing = await db.philos_adaptive_scores.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        scores = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        if existing:
            scores = {
                'contribution': existing.get('contribution', 0),
                'recovery': existing.get('recovery', 0),
                'order': existing.get('order', 0),
                'harm': existing.get('harm', 0),
                'avoidance': existing.get('avoidance', 0)
            }
        
        path_type = learning.predicted_value_tag
        if path_type not in scores:
            return
        
        # Boost if actual recovery stability was better than predicted
        if learning.actual_recovery_stability > learning.predicted_recovery_stability:
            scores[path_type] += 2
        
        # Boost if harm pressure was lower than predicted
        if learning.actual_harm_pressure < learning.predicted_harm_pressure:
            scores[path_type] += 2
        
        # Boost if order drift improved
        if learning.actual_order_drift > learning.predicted_order_drift and learning.actual_order_drift > 0:
            scores[path_type] += 1
        
        # Penalty if harm pressure increased
        if learning.actual_harm_pressure > learning.predicted_harm_pressure:
            scores[path_type] -= 3
        
        # Penalty if match quality was low
        if learning.match_quality == 'low':
            scores[path_type] -= 2
        
        # Penalty if actual outcome moved toward avoidance or harm
        if learning.actual_value_tag in ['avoidance', 'harm']:
            scores[path_type] -= 4
        
        # Bonus for high match quality
        if learning.match_quality == 'high':
            scores[path_type] += 3
        
        # Clamp scores to reasonable range
        for key in scores:
            scores[key] = max(-20, min(20, scores[key]))
        
        # Save updated scores
        await db.philos_adaptive_scores.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                **scores,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
    except Exception as e:
        logger.error(f"Update adaptive scores error: {str(e)}")


@router.post("/memory/sync")
async def sync_memory_data(user_id: str, learning_history: List[Dict[str, Any]] = []):
    """
    Sync local learning history with cloud storage.
    Merges local and cloud data.
    """
    try:
        # Get existing cloud learning history
        cloud_history = await db.philos_path_learning.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        # Create timestamp map for deduplication
        history_map = {}
        for h in cloud_history:
            key = h.get('timestamp', '')
            if key:
                history_map[key] = h
        
        # Add local entries if not already present
        new_entries = []
        for h in learning_history:
            key = h.get('timestamp', '')
            if key and key not in history_map:
                # Add user_id if not present
                h['user_id'] = user_id
                if 'id' not in h:
                    h['id'] = str(uuid.uuid4())
                new_entries.append(h)
                history_map[key] = h
        
        # Save new entries to database
        if new_entries:
            await db.philos_path_learning.insert_many(new_entries)
            
            # Recalculate adaptive scores from all learning history
            all_history = list(history_map.values())
            await recalculate_adaptive_scores(user_id, all_history)
        
        # Get updated data
        return await get_memory_data(user_id)
        
    except Exception as e:
        logger.error(f"Sync memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def recalculate_adaptive_scores(user_id: str, learning_history: List[Dict[str, Any]]):
    """
    Recalculate adaptive scores from full learning history.
    """
    try:
        scores = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        for entry in learning_history:
            path_type = entry.get('predicted_value_tag', '')
            if path_type not in scores:
                continue
            
            # Boost if actual recovery stability was better than predicted
            if entry.get('actual_recovery_stability', 0) > entry.get('predicted_recovery_stability', 0):
                scores[path_type] += 2
            
            # Boost if harm pressure was lower than predicted
            if entry.get('actual_harm_pressure', 0) < entry.get('predicted_harm_pressure', 0):
                scores[path_type] += 2
            
            # Boost if order drift improved
            if entry.get('actual_order_drift', 0) > entry.get('predicted_order_drift', 0) and entry.get('actual_order_drift', 0) > 0:
                scores[path_type] += 1
            
            # Penalty if harm pressure increased
            if entry.get('actual_harm_pressure', 0) > entry.get('predicted_harm_pressure', 0):
                scores[path_type] -= 3
            
            # Penalty if match quality was low
            if entry.get('match_quality', '') == 'low':
                scores[path_type] -= 2
            
            # Penalty if actual outcome moved toward avoidance or harm
            if entry.get('actual_value_tag', '') in ['avoidance', 'harm']:
                scores[path_type] -= 4
            
            # Bonus for high match quality
            if entry.get('match_quality', '') == 'high':
                scores[path_type] += 3
        
        # Clamp scores
        for key in scores:
            scores[key] = max(-20, min(20, scores[key]))
        
        # Save scores
        await db.philos_adaptive_scores.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                **scores,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
    except Exception as e:
        logger.error(f"Recalculate adaptive scores error: {str(e)}")


@router.get("/user/full-data/{user_id}", response_model=FullUserDataResponse)
async def get_full_user_data(user_id: str):
    """
    Get ALL user data for multi-device continuity.
    Returns: history, global_stats, trend_history, learning_history, 
    adaptive_scores, saved_sessions - everything needed to hydrate dashboard.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Get session data (history, global_stats, trend_history)
        session_data = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        history = []
        global_stats = {
            'contribution': 0, 'recovery': 0, 'harm': 0, 
            'order': 0, 'avoidance': 0, 'totalDecisions': 0, 'sessions': 0
        }
        trend_history = []
        
        if session_data:
            history = session_data.get('history', [])[:20]
            global_stats = session_data.get('global_stats', global_stats)
            trend_history = session_data.get('trend_history', [])[-30:]
        
        # 2. Get learning history (last 50)
        learning_history = await db.philos_path_learning.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        learning_history = list(reversed(learning_history))
        
        # 3. Get adaptive scores
        adaptive_scores_doc = await db.philos_adaptive_scores.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        adaptive_scores = {
            'contribution': 0, 'recovery': 0, 'order': 0, 'harm': 0, 'avoidance': 0
        }
        if adaptive_scores_doc:
            adaptive_scores = {
                'contribution': adaptive_scores_doc.get('contribution', 0),
                'recovery': adaptive_scores_doc.get('recovery', 0),
                'order': adaptive_scores_doc.get('order', 0),
                'harm': adaptive_scores_doc.get('harm', 0),
                'avoidance': adaptive_scores_doc.get('avoidance', 0)
            }
        
        # 4. Get saved sessions (session library)
        saved_sessions = await db.philos_saved_sessions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        return FullUserDataResponse(
            success=True,
            user_id=user_id,
            history=history,
            global_stats=global_stats,
            trend_history=trend_history,
            learning_history=learning_history,
            adaptive_scores=adaptive_scores,
            saved_sessions=saved_sessions,
            last_synced=now,
            device_sync_status="synced"
        )
        
    except Exception as e:
        logger.error(f"Get full user data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/full-sync/{user_id}")
async def full_sync_user_data(
    user_id: str,
    history: List[Dict[str, Any]] = [],
    global_stats: Dict[str, Any] = {},
    trend_history: List[Dict[str, Any]] = [],
    learning_history: List[Dict[str, Any]] = []
):
    """
    Full sync of all user data from device to cloud.
    Merges local data with cloud data.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Sync session data
        existing_session = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        # Merge history
        merged_history = []
        history_map = {}
        
        if existing_session:
            for h in existing_session.get('history', []):
                ts = h.get('timestamp', '')
                if ts:
                    history_map[ts] = h
        
        for h in history:
            ts = h.get('timestamp', '')
            if ts and ts not in history_map:
                history_map[ts] = h
        
        merged_history = sorted(
            history_map.values(),
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:20]
        
        # Merge global stats (take max values)
        cloud_stats = existing_session.get('global_stats', {}) if existing_session else {}
        merged_stats = {
            'contribution': max(cloud_stats.get('contribution', 0), global_stats.get('contribution', 0)),
            'recovery': max(cloud_stats.get('recovery', 0), global_stats.get('recovery', 0)),
            'harm': max(cloud_stats.get('harm', 0), global_stats.get('harm', 0)),
            'order': max(cloud_stats.get('order', 0), global_stats.get('order', 0)),
            'avoidance': max(cloud_stats.get('avoidance', 0), global_stats.get('avoidance', 0)),
            'totalDecisions': max(cloud_stats.get('totalDecisions', 0), global_stats.get('totalDecisions', 0)),
            'sessions': max(cloud_stats.get('sessions', 0), global_stats.get('sessions', 0))
        }
        
        # Merge trend history
        cloud_trends = existing_session.get('trend_history', []) if existing_session else []
        trend_map = {}
        for t in cloud_trends:
            date = t.get('date', '')
            if date:
                trend_map[date] = t
        for t in trend_history:
            date = t.get('date', '')
            if date:
                if date not in trend_map or t.get('totalDecisions', 0) >= trend_map[date].get('totalDecisions', 0):
                    trend_map[date] = t
        
        merged_trends = sorted(trend_map.values(), key=lambda x: x.get('date', ''))[-30:]
        
        # Save session data
        await db.philos_sessions.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "history": merged_history,
                "global_stats": merged_stats,
                "trend_history": merged_trends,
                "last_updated": now
            }},
            upsert=True
        )
        
        # 2. Sync learning history
        existing_learning = await db.philos_path_learning.find(
            {"user_id": user_id},
            {"_id": 0}
        ).to_list(100)
        
        learning_map = {entry.get('timestamp', ''): entry for entry in existing_learning if entry.get('timestamp')}
        
        new_learning = []
        for entry in learning_history:
            ts = entry.get('timestamp', '')
            if ts and ts not in learning_map:
                entry['user_id'] = user_id
                if 'id' not in entry:
                    entry['id'] = str(uuid.uuid4())
                new_learning.append(entry)
        
        if new_learning:
            await db.philos_path_learning.insert_many(new_learning)
            await recalculate_adaptive_scores(user_id, list(learning_map.values()) + new_learning)
        
        # Return updated data
        return await get_full_user_data(user_id)
        
    except Exception as e:
        logger.error(f"Full sync user data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


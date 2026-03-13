"""Philos data sync and session management routes."""
from fastapi import APIRouter, HTTPException
from database import db
from models.schemas import (
    PhilosSyncRequest, PhilosSyncResponse, SessionListResponse,
    SavedSession, SavedSessionSummary
)
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/philos/sync", response_model=PhilosSyncResponse)
async def sync_philos_data(data: PhilosSyncRequest):
    """
    Sync local Philos data with cloud storage.
    Merges local and cloud data, prioritizing newer entries.
    """
    try:
        user_id = data.user_id
        
        # Get existing cloud data for this user
        existing = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if existing:
            # Merge history (combine and dedupe by timestamp)
            cloud_history = existing.get('history', [])
            local_history = data.history
            
            # Create a dict keyed by timestamp to merge
            history_map = {}
            for h in cloud_history:
                key = h.get('timestamp', h.get('time', ''))
                if key:
                    history_map[key] = h
            for h in local_history:
                key = h.get('timestamp', h.get('time', ''))
                if key:
                    history_map[key] = h
            
            # Sort by timestamp (newest first)
            merged_history = sorted(
                history_map.values(),
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )[:20]  # Keep last 20
            
            # Merge global stats (take max values)
            cloud_stats = existing.get('global_stats', {})
            local_stats = data.global_stats
            merged_stats = {
                'contribution': max(cloud_stats.get('contribution', 0), local_stats.get('contribution', 0)),
                'recovery': max(cloud_stats.get('recovery', 0), local_stats.get('recovery', 0)),
                'harm': max(cloud_stats.get('harm', 0), local_stats.get('harm', 0)),
                'order': max(cloud_stats.get('order', 0), local_stats.get('order', 0)),
                'avoidance': max(cloud_stats.get('avoidance', 0), local_stats.get('avoidance', 0)),
                'totalDecisions': max(cloud_stats.get('totalDecisions', 0), local_stats.get('totalDecisions', 0)),
                'sessions': max(cloud_stats.get('sessions', 0), local_stats.get('sessions', 0))
            }
            
            # Merge trend history (combine and dedupe by date)
            cloud_trends = existing.get('trend_history', [])
            local_trends = data.trend_history
            
            trend_map = {}
            for t in cloud_trends:
                date = t.get('date', '')
                if date:
                    trend_map[date] = t
            for t in local_trends:
                date = t.get('date', '')
                if date:
                    # Prefer local if it has more decisions for the same date
                    if date in trend_map:
                        if t.get('totalDecisions', 0) >= trend_map[date].get('totalDecisions', 0):
                            trend_map[date] = t
                    else:
                        trend_map[date] = t
            
            merged_trends = sorted(
                trend_map.values(),
                key=lambda x: x.get('date', '')
            )[-30:]  # Keep last 30 days
            
        else:
            # No cloud data, use local data
            merged_history = data.history[:20]
            merged_stats = data.global_stats
            merged_trends = data.trend_history[-30:]
        
        # Save merged data to cloud
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            'user_id': user_id,
            'history': merged_history,
            'global_stats': merged_stats,
            'trend_history': merged_trends,
            'last_updated': now
        }
        
        await db.philos_sessions.update_one(
            {"user_id": user_id},
            {"$set": doc},
            upsert=True
        )
        
        return PhilosSyncResponse(
            success=True,
            user_id=user_id,
            history=merged_history,
            global_stats=merged_stats,
            trend_history=merged_trends,
            last_synced=now
        )
        
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/philos/sync/{user_id}", response_model=PhilosSyncResponse)
async def get_philos_data(user_id: str):
    """
    Get cloud data for a user.
    """
    try:
        existing = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if existing:
            return PhilosSyncResponse(
                success=True,
                user_id=user_id,
                history=existing.get('history', []),
                global_stats=existing.get('global_stats', {}),
                trend_history=existing.get('trend_history', []),
                last_synced=existing.get('last_updated', '')
            )
        else:
            return PhilosSyncResponse(
                success=True,
                user_id=user_id,
                history=[],
                global_stats={},
                trend_history=[],
                last_synced=''
            )
            
    except Exception as e:
        logger.error(f"Get data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/philos/sessions/save")
async def save_session(user_id: str, history: List[Dict[str, Any]]):
    """
    Save a completed session to the library.
    """
    try:
        if not history or len(history) == 0:
            raise HTTPException(status_code=400, detail="Cannot save empty session")
        
        # Calculate session metrics
        tag_counts = {'contribution': 0, 'recovery': 0, 'harm': 0, 'order': 0, 'avoidance': 0}
        total_order = 0
        total_collective = 0
        
        for h in history:
            tag = h.get('value_tag', '')
            if tag in tag_counts:
                tag_counts[tag] += 1
            total_order += h.get('chaos_order', 0)
            total_collective += h.get('ego_collective', 0)
        
        # Find dominant value
        dominant_value = max(tag_counts.items(), key=lambda x: x[1])[0] if any(tag_counts.values()) else 'neutral'
        
        # Calculate drifts
        order_drift = (tag_counts['order'] + tag_counts['recovery']) - (tag_counts['harm'] + tag_counts['avoidance'])
        collective_drift = tag_counts['contribution'] - tag_counts['harm']
        
        now = datetime.now(timezone.utc)
        session_id = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'date': now.strftime('%Y-%m-%d'),
            'total_decisions': len(history),
            'dominant_value': dominant_value,
            'order_drift': order_drift,
            'collective_drift': collective_drift,
            'history': history,
            'created_at': now.isoformat()
        }
        
        await db.philos_saved_sessions.insert_one(session)
        
        return {"success": True, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Save session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/philos/sessions/{user_id}", response_model=SessionListResponse)
async def list_sessions(user_id: str):
    """
    List all saved sessions for a user.
    """
    try:
        sessions = await db.philos_saved_sessions.find(
            {"user_id": user_id},
            {"_id": 0, "history": 0}  # Exclude history for list view
        ).sort("created_at", -1).to_list(100)
        
        return SessionListResponse(
            success=True,
            sessions=[SavedSessionSummary(**s) for s in sessions]
        )
        
    except Exception as e:
        logger.error(f"List sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/philos/sessions/{user_id}/{session_id}")
async def get_session(user_id: str, session_id: str):
    """
    Get a specific saved session with full history.
    """
    try:
        session = await db.philos_saved_sessions.find_one(
            {"user_id": user_id, "session_id": session_id},
            {"_id": 0}
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "session": session}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/philos/sessions/{user_id}/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """
    Delete a saved session.
    """
    try:
        result = await db.philos_saved_sessions.delete_one(
            {"user_id": user_id, "session_id": session_id}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "deleted": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

"""System health, status, and admin operations."""
import logging
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from database import db, client
from auth_utils import get_current_user
from services.scheduler import get_scheduler_status, run_decay_manual

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/system/status")
async def system_status():
    """Health info for database, trust engine, trust ledger, AI layer, and decay scheduler."""
    status = {"overall": "healthy", "components": {}}

    # 1. Database
    try:
        await client.admin.command("ping")
        status["components"]["database"] = {"status": "healthy", "message": "MongoDB connected"}
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["database"] = {"status": "unhealthy", "message": str(e)}

    # 2. Trust Engine
    try:
        user_count = await db.user_state.count_documents({})
        status["components"]["trust_engine"] = {"status": "healthy", "tracked_users": user_count}
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["trust_engine"] = {"status": "unhealthy", "message": str(e)}

    # 3. Trust Ledger
    try:
        ledger_count = await db.trust_ledger.count_documents({})
        status["components"]["trust_ledger"] = {"status": "healthy", "total_entries": ledger_count}
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["trust_ledger"] = {"status": "unhealthy", "message": str(e)}

    # 4. AI Layer
    try:
        has_key = bool(os.environ.get("EMERGENT_LLM_KEY"))
        status["components"]["ai_layer"] = {
            "status": "healthy" if has_key else "degraded",
            "message": "API key configured" if has_key else "API key missing",
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["ai_layer"] = {"status": "unhealthy", "message": str(e)}

    # 5. Decay Scheduler — flat fields as requested
    try:
        sched = await get_scheduler_status()
        sched_healthy = sched.get("scheduler_running", False)
        status["components"]["decay_scheduler"] = {
            "status": "healthy" if sched_healthy else "degraded",
            "scheduler_running": sched["scheduler_running"],
            "last_decay_run": sched["last_decay_run"],
            "last_decay_success": sched["last_decay_success"],
            "decay_runs_last_7_days": sched["decay_runs_last_7_days"],
            "next_decay_run": sched["next_decay_run"],
            "lock_state": sched["lock_state"],
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["decay_scheduler"] = {"status": "unhealthy", "message": str(e)}

    return status


@router.post("/system/decay/trigger")
async def trigger_decay(user=Depends(get_current_user)):
    """Admin-only: manually trigger a decay run. Respects concurrency lock."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    triggered_by = user.get("email", user.get("id", "unknown"))
    logger.info(f"Manual decay triggered by {triggered_by}")

    result = await run_decay_manual()
    return {
        "triggered_by": triggered_by,
        "triggered_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }

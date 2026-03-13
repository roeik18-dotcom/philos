"""System health and status endpoint."""
import logging
from fastapi import APIRouter
from database import db, client
from services.scheduler import get_scheduler_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/system/status")
async def system_status():
    """Return health info for database, trust engine, trust ledger, AI layer, and decay scheduler."""
    status = {"overall": "healthy", "components": {}}

    # 1. Database
    try:
        await client.admin.command("ping")
        status["components"]["database"] = {"status": "healthy", "message": "MongoDB connected"}
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["database"] = {"status": "unhealthy", "message": str(e)}

    # 2. Trust Engine (user_state collection)
    try:
        user_count = await db.user_state.count_documents({})
        status["components"]["trust_engine"] = {
            "status": "healthy",
            "tracked_users": user_count,
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["trust_engine"] = {"status": "unhealthy", "message": str(e)}

    # 3. Trust Ledger
    try:
        ledger_count = await db.trust_ledger.count_documents({})
        status["components"]["trust_ledger"] = {
            "status": "healthy",
            "total_entries": ledger_count,
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["trust_ledger"] = {"status": "unhealthy", "message": str(e)}

    # 4. AI Layer — check that the env var is present
    try:
        import os
        has_key = bool(os.environ.get("EMERGENT_LLM_KEY"))
        status["components"]["ai_layer"] = {
            "status": "healthy" if has_key else "degraded",
            "message": "API key configured" if has_key else "API key missing",
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["ai_layer"] = {"status": "unhealthy", "message": str(e)}

    # 5. Decay Scheduler
    try:
        sched = await get_scheduler_status()
        sched_healthy = sched.get("scheduler_running", False)
        status["components"]["decay_scheduler"] = {
            "status": "healthy" if sched_healthy else "degraded",
            **sched,
        }
    except Exception as e:
        status["overall"] = "degraded"
        status["components"]["decay_scheduler"] = {"status": "unhealthy", "message": str(e)}

    return status

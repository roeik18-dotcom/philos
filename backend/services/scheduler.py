"""Decay scheduler with MongoDB-based duplicate-run protection and execution logging."""
import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import db
from services.trust import run_daily_decay

logger = logging.getLogger("scheduler")

LOCK_ID = "daily_decay"
MIN_RUN_INTERVAL_HOURS = 23

scheduler: AsyncIOScheduler | None = None


async def _acquire_lock() -> bool:
    """Atomically acquire lock. Rejects if another run completed within MIN_RUN_INTERVAL_HOURS."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=MIN_RUN_INTERVAL_HOURS)).isoformat()
    result = await db.scheduler_locks.find_one_and_update(
        {
            "lock_id": LOCK_ID,
            "$or": [
                {"last_completed_at": {"$exists": False}},
                {"last_completed_at": {"$lt": cutoff}},
            ],
            "running": {"$ne": True},
        },
        {"$set": {"running": True, "started_at": datetime.now(timezone.utc).isoformat()}},
        upsert=False,
    )
    if result:
        return True
    existing = await db.scheduler_locks.find_one({"lock_id": LOCK_ID})
    if not existing:
        await db.scheduler_locks.insert_one({
            "lock_id": LOCK_ID,
            "running": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        return True
    return False


async def _acquire_lock_manual() -> bool:
    """Acquire lock for manual trigger. Only checks concurrent-run guard, ignores time interval."""
    result = await db.scheduler_locks.find_one_and_update(
        {"lock_id": LOCK_ID, "running": {"$ne": True}},
        {"$set": {"running": True, "started_at": datetime.now(timezone.utc).isoformat()}},
        upsert=False,
    )
    if result:
        return True
    existing = await db.scheduler_locks.find_one({"lock_id": LOCK_ID})
    if not existing:
        await db.scheduler_locks.insert_one({
            "lock_id": LOCK_ID,
            "running": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        return True
    return False


async def _release_lock(success: bool, users_processed: int, started_at: str, error: str = None):
    """Release the lock and record execution in decay_log."""
    completed_at = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"running": False}}
    if success:
        update["$set"]["last_completed_at"] = completed_at
    await db.scheduler_locks.update_one({"lock_id": LOCK_ID}, update)

    log_entry = {
        "job": LOCK_ID,
        "started_at": started_at,
        "completed_at": completed_at,
        "success": success,
        "users_processed": users_processed,
        "error": error,
    }
    await db.decay_log.insert_one(log_entry)
    return log_entry


async def _snapshot_totals():
    """Sum current value_score and risk_score across all user_state docs."""
    pipeline = [{"$group": {"_id": None, "tv": {"$sum": "$value_score"}, "tr": {"$sum": "$risk_score"}}}]
    result = await db.user_state.aggregate(pipeline).to_list(1)
    if result:
        return round(result[0]["tv"], 4), round(result[0]["tr"], 4)
    return 0.0, 0.0


async def run_decay_with_lock():
    """Scheduled decay: respects both concurrency lock and 23-hour interval."""
    started_at = datetime.now(timezone.utc).isoformat()
    acquired = await _acquire_lock()
    if not acquired:
        logger.info("Decay skipped: another run completed recently or is in progress")
        return

    logger.info("Decay job started (scheduled)")
    try:
        count = await run_daily_decay()
        await _release_lock(success=True, users_processed=count, started_at=started_at)
        logger.info(f"Decay job completed: {count} users processed")
    except Exception as e:
        await _release_lock(success=False, users_processed=0, started_at=started_at, error=str(e))
        logger.error(f"Decay job failed: {e}")


async def run_decay_manual() -> dict:
    """Manual trigger: respects concurrency lock only, returns detailed stats."""
    started_at = datetime.now(timezone.utc).isoformat()
    acquired = await _acquire_lock_manual()
    if not acquired:
        return {"success": False, "reason": "decay_in_progress", "users_processed": 0,
                "total_value_decay": 0, "total_risk_decay": 0}

    logger.info("Decay job started (manual trigger)")
    try:
        val_before, risk_before = await _snapshot_totals()
        count = await run_daily_decay()
        val_after, risk_after = await _snapshot_totals()
        await _release_lock(success=True, users_processed=count, started_at=started_at)
        logger.info(f"Manual decay completed: {count} users processed")
        return {
            "success": True,
            "users_processed": count,
            "total_value_decay": round(val_after - val_before, 4),
            "total_risk_decay": round(risk_after - risk_before, 4),
        }
    except Exception as e:
        await _release_lock(success=False, users_processed=0, started_at=started_at, error=str(e))
        logger.error(f"Manual decay failed: {e}")
        return {"success": False, "reason": str(e), "users_processed": 0,
                "total_value_decay": 0, "total_risk_decay": 0}


async def get_scheduler_status() -> dict:
    """Return structured scheduler health info."""
    lock = await db.scheduler_locks.find_one({"lock_id": LOCK_ID}, {"_id": 0})

    # Last run info
    last_log = await db.decay_log.find_one(
        {"job": LOCK_ID}, {"_id": 0}
    , sort=[("completed_at", -1)])

    # Runs in last 7 days
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    runs_7d = await db.decay_log.count_documents({"job": LOCK_ID, "completed_at": {"$gte": seven_days_ago}})

    running = scheduler is not None and scheduler.running
    next_fire = None
    if running:
        jobs = scheduler.get_jobs()
        if jobs and jobs[0].next_run_time:
            next_fire = jobs[0].next_run_time.isoformat()

    return {
        "scheduler_running": running,
        "next_decay_run": next_fire,
        "last_decay_run": last_log.get("completed_at") if last_log else None,
        "last_decay_success": last_log.get("success") if last_log else None,
        "decay_runs_last_7_days": runs_7d,
        "lock_state": lock,
    }


def start_scheduler():
    """Initialize and start APScheduler. Safe to call multiple times — ignores if already running."""
    global scheduler
    if scheduler and scheduler.running:
        logger.warning("Scheduler already running — skipping duplicate start")
        return
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_decay_with_lock,
        trigger=CronTrigger(hour=3, minute=0),
        id=LOCK_ID,
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("Decay scheduler started — next run at 03:00 UTC daily")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Decay scheduler stopped")

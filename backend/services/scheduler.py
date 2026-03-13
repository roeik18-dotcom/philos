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
_last_run_result: dict | None = None


async def _acquire_lock() -> bool:
    """Atomically acquire a lock. Returns True if acquired, False if another run happened recently."""
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
    # If no document exists at all, create it and acquire
    existing = await db.scheduler_locks.find_one({"lock_id": LOCK_ID})
    if not existing:
        await db.scheduler_locks.insert_one({
            "lock_id": LOCK_ID,
            "running": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        return True
    return False


async def _release_lock(success: bool, users_processed: int, error: str = None):
    """Release the lock and record completion."""
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"running": False}}
    if success:
        update["$set"]["last_completed_at"] = now
    await db.scheduler_locks.update_one({"lock_id": LOCK_ID}, update)

    # Log execution
    log_entry = {
        "job": LOCK_ID,
        "started_at": now,
        "completed_at": now,
        "success": success,
        "users_processed": users_processed,
        "error": error,
    }
    await db.decay_log.insert_one(log_entry)
    return log_entry


async def run_decay_with_lock():
    """Run daily decay with lock protection and logging."""
    global _last_run_result
    acquired = await _acquire_lock()
    if not acquired:
        logger.info("Decay skipped: another run completed recently or is in progress")
        return

    logger.info("Decay job started")
    try:
        count = await run_daily_decay()
        result = await _release_lock(success=True, users_processed=count)
        _last_run_result = result
        logger.info(f"Decay job completed: {count} users processed")
    except Exception as e:
        result = await _release_lock(success=False, users_processed=0, error=str(e))
        _last_run_result = result
        logger.error(f"Decay job failed: {e}")


def get_last_run_result() -> dict | None:
    return _last_run_result


async def get_scheduler_status() -> dict:
    """Return scheduler health info."""
    lock = await db.scheduler_locks.find_one({"lock_id": LOCK_ID}, {"_id": 0})
    recent_logs = await db.decay_log.find(
        {"job": LOCK_ID}, {"_id": 0}
    ).sort("completed_at", -1).limit(5).to_list(5)

    running = scheduler is not None and scheduler.running
    next_fire = None
    if running:
        jobs = scheduler.get_jobs()
        if jobs:
            next_fire = jobs[0].next_run_time.isoformat() if jobs[0].next_run_time else None

    return {
        "scheduler_running": running,
        "next_scheduled_run": next_fire,
        "lock_state": lock,
        "recent_executions": recent_logs,
    }


def start_scheduler():
    """Initialize and start APScheduler. Runs decay at 03:00 UTC daily."""
    global scheduler
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

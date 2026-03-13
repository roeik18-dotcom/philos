"""Philos Orientation - Main application entry point."""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all route modules
from routes.auth import router as auth_router
from routes.philos import router as philos_router
from routes.memory import router as memory_router
from routes.collective import router as collective_router
from routes.orientation import router as orientation_router
from routes.social import router as social_router
from routes.profile import router as profile_router
from routes.admin import router as admin_router
from routes.trust import router as trust_router

app.include_router(auth_router, prefix="/api")
app.include_router(philos_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(collective_router, prefix="/api")
app.include_router(orientation_router, prefix="/api")
app.include_router(social_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(trust_router, prefix="/api")

# Database shutdown
from database import client

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Demo agents background loop
from services.demo import _demo_event_loop

# Daily decay background loop
from services.trust import run_daily_decay

async def _daily_decay_loop():
    """Run decay once per day (every 24 hours)."""
    await asyncio.sleep(10)
    while True:
        try:
            count = await run_daily_decay()
            logger.info(f"Daily decay completed for {count} users")
        except Exception as e:
            logger.error(f"Daily decay error: {str(e)}")
        await asyncio.sleep(86400)  # 24 hours

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(_demo_event_loop())
    asyncio.create_task(_daily_decay_loop())

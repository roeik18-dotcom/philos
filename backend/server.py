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

# ✅ ROOT ROUTE (FIX FOR EMPTY SCREEN)
@app.get("/")
async def root():
    return {"status": "backend alive"}

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
from routes.system import router as system_router
from routes.analytics import router as analytics_router
from routes.invites import router as invites_router

app.include_router(auth_router, prefix="/api")
app.include_router(philos_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(collective_router, prefix="/api")
app.include_router(orientation_router, prefix="/api")
app.include_router(social_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(trust_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(invites_router, prefix="/api")

# Database shutdown
from database import client
from services.scheduler import start_scheduler, stop_scheduler

@app.on_event("shutdown")
async def shutdown_db_client():
    stop_scheduler()
    if client:  # ✅ FIX (avoid crash)
        client.close()

# Demo agents background loop
from services.demo import _demo_event_loop

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(_demo_event_loop())
    start_scheduler()
    logger.info("All background tasks started")

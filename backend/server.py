from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'philos-orientation-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security bearer
security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        # Get user from database
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return user
    except JWTError:
        return None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# Authentication Models
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str
    last_login_at: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    message: Optional[str] = None


# Philos Session Models
class DecisionRecord(BaseModel):
    action: str
    decision: str
    chaos_order: int
    ego_collective: int
    balance_score: int
    value_tag: str
    time: str
    timestamp: str

class SessionSnapshot(BaseModel):
    date: str
    timestamp: str
    totalDecisions: int
    contribution: int = 0
    recovery: int = 0
    harm: int = 0
    order: int = 0
    avoidance: int = 0

class GlobalStats(BaseModel):
    contribution: int = 0
    recovery: int = 0
    harm: int = 0
    order: int = 0
    avoidance: int = 0
    totalDecisions: int = 0
    sessions: int = 0

class PhilosSessionData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: List[DecisionRecord] = []
    global_stats: GlobalStats = GlobalStats()
    trend_history: List[SessionSnapshot] = []
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PhilosSyncRequest(BaseModel):
    user_id: str
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []

class PhilosSyncResponse(BaseModel):
    success: bool
    user_id: str
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []
    last_synced: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# ============================================================
# Authentication Endpoints
# ============================================================

@api_router.post("/auth/register", response_model=AuthResponse)
async def register_user(data: UserRegister):
    """
    Register a new user.
    """
    try:
        # Check if email already exists
        existing = await db.users.find_one({"email": data.email.lower()})
        if existing:
            return AuthResponse(
                success=False,
                message="כתובת האימייל כבר קיימת במערכת"  # Email already exists
            )
        
        # Create new user
        now = datetime.now(timezone.utc).isoformat()
        user_id = str(uuid.uuid4())
        
        user_doc = {
            "id": user_id,
            "email": data.email.lower(),
            "password_hash": get_password_hash(data.password),
            "created_at": now,
            "last_login_at": now
        }
        
        await db.users.insert_one(user_doc)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        return AuthResponse(
            success=True,
            user=UserResponse(
                id=user_id,
                email=data.email.lower(),
                created_at=now,
                last_login_at=now
            ),
            token=access_token,
            message="ההרשמה הצליחה!"  # Registration successful
        )
        
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(data: UserLogin):
    """
    Login a user.
    """
    try:
        # Find user by email
        user = await db.users.find_one({"email": data.email.lower()})
        
        if not user:
            return AuthResponse(
                success=False,
                message="אימייל או סיסמה שגויים"  # Invalid email or password
            )
        
        # Verify password
        if not verify_password(data.password, user["password_hash"]):
            return AuthResponse(
                success=False,
                message="אימייל או סיסמה שגויים"  # Invalid email or password
            )
        
        # Update last login
        now = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"last_login_at": now}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return AuthResponse(
            success=True,
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                created_at=user["created_at"],
                last_login_at=now
            ),
            token=access_token,
            message="התחברת בהצלחה!"  # Login successful
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/auth/logout")
async def logout_user():
    """
    Logout a user (client-side token removal).
    """
    return {"success": True, "message": "התנתקת בהצלחה"}  # Logged out successfully


@api_router.get("/auth/me", response_model=AuthResponse)
async def get_current_user_info(user = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    if not user:
        return AuthResponse(
            success=False,
            message="לא מחובר"  # Not logged in
        )
    
    return AuthResponse(
        success=True,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            created_at=user["created_at"],
            last_login_at=user.get("last_login_at")
        )
    )


@api_router.post("/auth/migrate-data")
async def migrate_anonymous_data(anonymous_user_id: str, user = Depends(get_current_user)):
    """
    Migrate anonymous user data to authenticated user account.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        authenticated_user_id = user["id"]
        
        # Migrate philos_sessions
        await db.philos_sessions.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        # Migrate philos_saved_sessions
        await db.philos_saved_sessions.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        # Migrate philos_decisions
        await db.philos_decisions.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        # Migrate philos_path_selections
        await db.philos_path_selections.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        # Migrate philos_path_learning
        await db.philos_path_learning.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        # Migrate philos_adaptive_scores
        await db.philos_adaptive_scores.update_many(
            {"user_id": anonymous_user_id},
            {"$set": {"user_id": authenticated_user_id}}
        )
        
        return {
            "success": True,
            "message": "הנתונים הועברו בהצלחה לחשבון שלך",  # Data migrated successfully
            "new_user_id": authenticated_user_id
        }
        
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Philos Sync Endpoints
@api_router.post("/philos/sync", response_model=PhilosSyncResponse)
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


@api_router.get("/philos/sync/{user_id}", response_model=PhilosSyncResponse)
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


# Session Library Models
class SavedSession(BaseModel):
    session_id: str
    user_id: str
    date: str
    total_decisions: int
    dominant_value: str
    order_drift: int
    collective_drift: int
    history: List[Dict[str, Any]]
    created_at: str

class SavedSessionSummary(BaseModel):
    session_id: str
    date: str
    total_decisions: int
    dominant_value: str
    order_drift: int
    collective_drift: int
    created_at: str

class SessionListResponse(BaseModel):
    success: bool
    sessions: List[SavedSessionSummary]


# Session Library Endpoints
@api_router.post("/philos/sessions/save")
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


@api_router.get("/philos/sessions/{user_id}", response_model=SessionListResponse)
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


@api_router.get("/philos/sessions/{user_id}/{session_id}")
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


@api_router.delete("/philos/sessions/{user_id}/{session_id}")
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


# ============================================================
# Persistent Memory Layer - Path Learning & Adaptive Engine
# ============================================================

# Models for Path Selection
class PathSelectionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    selected_path_id: int
    suggested_action: str
    predicted_value_tag: str
    predicted_order_drift: int
    predicted_collective_drift: int
    predicted_harm_pressure: int
    predicted_recovery_stability: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PathLearningRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    predicted_value_tag: str
    actual_value_tag: str
    predicted_order_drift: int
    actual_order_drift: int
    predicted_collective_drift: int
    actual_collective_drift: int
    predicted_harm_pressure: int
    actual_harm_pressure: int
    predicted_recovery_stability: int
    actual_recovery_stability: int
    match_quality: str  # 'high', 'medium', 'low'
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AdaptiveScores(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    contribution: int = 0
    recovery: int = 0
    order: int = 0
    harm: int = 0
    avoidance: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DecisionRecordRequest(BaseModel):
    user_id: str
    action: str
    decision: str
    chaos_order: int
    ego_collective: int
    balance_score: int
    value_tag: str
    session_id: Optional[str] = None
    parent_decision_id: Optional[str] = None
    template_type: Optional[str] = None

class MemoryDataResponse(BaseModel):
    success: bool
    user_id: str
    learning_history: List[Dict[str, Any]] = []
    adaptive_scores: Dict[str, Any] = {}
    last_synced: str = ""


# Persistent Memory Endpoints

@api_router.post("/memory/decision")
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


@api_router.post("/memory/path-selection")
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


@api_router.post("/memory/path-learning")
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


@api_router.get("/memory/{user_id}", response_model=MemoryDataResponse)
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


@api_router.get("/memory/stats/{user_id}")
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


# ============================================================
# Decision Replay - Counterfactual Path Analysis
# ============================================================

class ReplayMetadataRequest(BaseModel):
    user_id: str
    replay_of_decision_id: str
    original_value_tag: str
    alternative_path_id: int
    alternative_path_type: str
    predicted_metrics: Dict[str, Any]
    timestamp: Optional[str] = None


@api_router.post("/memory/replay")
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


@api_router.get("/memory/replays/{user_id}")
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


# ============================================================
# Replay Insights Summary - Aggregated Pattern Analysis
# ============================================================

class ReplayInsightsResponse(BaseModel):
    success: bool
    user_id: str
    total_replays: int = 0
    # Alternative path exploration counts
    alternative_path_counts: Dict[str, int] = {}
    # Transition patterns (from -> to)
    transition_patterns: List[Dict[str, Any]] = []
    # Blind spots (patterns never explored)
    blind_spots: List[Dict[str, str]] = []
    # Most replayed decision types
    most_replayed_original_tags: Dict[str, int] = {}
    # Generated Hebrew insights
    insights: List[str] = []
    # Time-based metrics
    recent_replay_count: int = 0  # Last 7 days
    generated_at: str = ""


@api_router.get("/memory/replay-insights/{user_id}", response_model=ReplayInsightsResponse)
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


def generate_replay_insights_hebrew(
    alt_counts: Dict[str, int],
    transitions: List[Dict],
    blind_spots: List[Dict],
    orig_counts: Dict[str, int],
    total: int
) -> List[str]:
    """
    Generate Hebrew insight text based on replay patterns.
    """
    insights = []
    
    # Hebrew labels
    tag_labels = {
        'contribution': 'תרומה',
        'recovery': 'התאוששות',
        'order': 'סדר',
        'harm': 'נזק',
        'avoidance': 'הימנעות'
    }
    
    # 1. Most explored alternative path insight
    if alt_counts:
        top_alt = max(alt_counts.items(), key=lambda x: x[1])
        if top_alt[1] > 0:
            percentage = round((top_alt[1] / total) * 100)
            insights.append(
                f"המסלול החלופי הנבדק ביותר הוא {tag_labels.get(top_alt[0], top_alt[0])} ({percentage}% מההפעלות החוזרות)."
            )
    
    # 2. Top transition pattern insight
    if transitions and len(transitions) > 0:
        top_trans = transitions[0]
        from_label = tag_labels.get(top_trans['from'], top_trans['from'])
        to_label = tag_labels.get(top_trans['to'], top_trans['to'])
        count = top_trans['count']
        
        if top_trans['from'] in ['harm', 'avoidance'] and top_trans['to'] in ['contribution', 'recovery', 'order']:
            insights.append(
                f"אתה נוטה לבדוק מסלולי {to_label} כשאתה בוחר ב{from_label}. "
                f"זה מצביע על מודעות לחלופות חיוביות ({count} פעמים)."
            )
        elif top_trans['from'] == top_trans['to']:
            pass  # Skip same-to-same
        else:
            insights.append(
                f"הדפוס הנפוץ ביותר: מ{from_label} ל{to_label} ({count} פעמים)."
            )
    
    # 3. Most replayed original decision type
    if orig_counts:
        top_orig = max(orig_counts.items(), key=lambda x: x[1])
        if top_orig[1] > 2:  # Only if significant
            insights.append(
                f"אתה מרבה לבדוק חלופות להחלטות מסוג {tag_labels.get(top_orig[0], top_orig[0])}."
            )
    
    # 4. Blind spot insight
    if blind_spots and len(blind_spots) > 0:
        spot = blind_spots[0]
        from_label = tag_labels.get(spot['from'], spot['from'])
        to_label = tag_labels.get(spot['to'], spot['to'])
        insights.append(
            f"נקודה עיוורת: מעולם לא בדקת מסלול {to_label} אחרי החלטת {from_label}."
        )
    
    # 5. Recovery-specific insight
    if alt_counts.get('recovery', 0) > alt_counts.get('order', 0) * 1.5:
        insights.append(
            "יש לך נטייה לבדוק מסלולי התאוששות - ייתכן שאתה מרגיש צורך במנוחה שלא מתממש."
        )
    
    # 6. Harm avoidance insight
    if alt_counts.get('harm', 0) == 0 and total > 5:
        insights.append(
            "אתה נמנע מלבדוק מסלולי נזק בהפעלות חוזרות - סימן חיובי למודעות ערכית."
        )
    
    # Limit to 4 most relevant insights
    return insights[:4]


@api_router.post("/memory/sync")
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


# ============================================================
# Multi-Device Continuity - Full User Data Sync
# ============================================================

class FullUserDataResponse(BaseModel):
    success: bool
    user_id: str
    # Session data
    history: List[Dict[str, Any]] = []
    global_stats: Dict[str, Any] = {}
    trend_history: List[Dict[str, Any]] = []
    # Memory data  
    learning_history: List[Dict[str, Any]] = []
    adaptive_scores: Dict[str, Any] = {}
    # Session library
    saved_sessions: List[Dict[str, Any]] = []
    # Sync metadata
    last_synced: str = ""
    device_sync_status: str = "synced"


@api_router.get("/user/full-data/{user_id}", response_model=FullUserDataResponse)
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


@api_router.post("/user/full-sync/{user_id}")
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
        
        learning_map = {l.get('timestamp', ''): l for l in existing_learning if l.get('timestamp')}
        
        new_learning = []
        for l in learning_history:
            ts = l.get('timestamp', '')
            if ts and ts not in learning_map:
                l['user_id'] = user_id
                if 'id' not in l:
                    l['id'] = str(uuid.uuid4())
                new_learning.append(l)
        
        if new_learning:
            await db.philos_path_learning.insert_many(new_learning)
            await recalculate_adaptive_scores(user_id, list(learning_map.values()) + new_learning)
        
        # Return updated data
        return await get_full_user_data(user_id)
        
    except Exception as e:
        logger.error(f"Full sync user data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Collective Layer - Cross-User Aggregated Analytics
# ============================================================

class CollectiveLayerResponse(BaseModel):
    success: bool
    total_users: int = 0
    total_decisions: int = 0
    # Value tag counts
    value_counts: Dict[str, int] = {}
    # Averages
    avg_order_drift: float = 0.0
    avg_collective_drift: float = 0.0
    avg_harm_pressure: float = 0.0
    avg_recovery_stability: float = 0.0
    # Dominant values
    dominant_value: str = ""
    dominant_direction: str = ""
    # Time-based trends (last 7 days)
    recent_trend: Dict[str, Any] = {}
    # Summary insights
    insights: List[str] = []


@api_router.get("/collective/layer", response_model=CollectiveLayerResponse)
async def get_collective_layer():
    """
    Get aggregated anonymized data across all authenticated users.
    No usernames or identifying information is returned.
    """
    try:
        # 1. Aggregate from philos_sessions (global_stats)
        all_sessions = await db.philos_sessions.find(
            {},
            {"_id": 0, "user_id": 0}  # Exclude identifying info
        ).to_list(1000)
        
        total_users = len(all_sessions)
        total_decisions = 0
        value_counts = {
            'contribution': 0,
            'recovery': 0,
            'order': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        for session in all_sessions:
            gs = session.get('global_stats', {})
            total_decisions += gs.get('totalDecisions', 0)
            value_counts['contribution'] += gs.get('contribution', 0)
            value_counts['recovery'] += gs.get('recovery', 0)
            value_counts['order'] += gs.get('order', 0)
            value_counts['harm'] += gs.get('harm', 0)
            value_counts['avoidance'] += gs.get('avoidance', 0)
        
        # 2. Aggregate from philos_path_learning for drift/pressure metrics
        all_learning = await db.philos_path_learning.find(
            {},
            {"_id": 0, "user_id": 0}  # Exclude identifying info
        ).to_list(5000)
        
        order_drifts = []
        collective_drifts = []
        harm_pressures = []
        recovery_stabilities = []
        
        for entry in all_learning:
            if entry.get('actual_order_drift') is not None:
                order_drifts.append(entry['actual_order_drift'])
            if entry.get('actual_collective_drift') is not None:
                collective_drifts.append(entry['actual_collective_drift'])
            if entry.get('actual_harm_pressure') is not None:
                harm_pressures.append(entry['actual_harm_pressure'])
            if entry.get('actual_recovery_stability') is not None:
                recovery_stabilities.append(entry['actual_recovery_stability'])
        
        # Calculate averages
        avg_order_drift = sum(order_drifts) / len(order_drifts) if order_drifts else 0.0
        avg_collective_drift = sum(collective_drifts) / len(collective_drifts) if collective_drifts else 0.0
        avg_harm_pressure = sum(harm_pressures) / len(harm_pressures) if harm_pressures else 0.0
        avg_recovery_stability = sum(recovery_stabilities) / len(recovery_stabilities) if recovery_stabilities else 0.0
        
        # 3. Determine dominant value
        positive_values = {k: v for k, v in value_counts.items() if k not in ['harm', 'avoidance']}
        dominant_value = max(positive_values, key=positive_values.get) if positive_values and max(positive_values.values()) > 0 else 'recovery'
        
        # 4. Determine dominant direction
        if avg_order_drift > 5:
            dominant_direction = 'order'
        elif avg_order_drift < -5:
            dominant_direction = 'chaos'
        elif avg_collective_drift > 5:
            dominant_direction = 'collective'
        elif avg_collective_drift < -5:
            dominant_direction = 'ego'
        else:
            dominant_direction = 'balanced'
        
        # 5. Calculate recent trend (last 7 days from trend_history)
        recent_trend = {
            'total_recent_decisions': 0,
            'trend_direction': 'stable'
        }
        
        from datetime import timedelta
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()[:10]
        
        recent_values = {'contribution': 0, 'recovery': 0, 'order': 0, 'harm': 0, 'avoidance': 0}
        
        for session in all_sessions:
            trends = session.get('trend_history', [])
            for t in trends:
                if t.get('date', '') >= seven_days_ago:
                    recent_trend['total_recent_decisions'] += t.get('totalDecisions', 0)
                    recent_values['contribution'] += t.get('contribution', 0)
                    recent_values['recovery'] += t.get('recovery', 0)
                    recent_values['order'] += t.get('order', 0)
                    recent_values['harm'] += t.get('harm', 0)
                    recent_values['avoidance'] += t.get('avoidance', 0)
        
        if recent_values['order'] > recent_values['recovery']:
            recent_trend['trend_direction'] = 'order_rising'
        elif recent_values['recovery'] > recent_values['order']:
            recent_trend['trend_direction'] = 'recovery_rising'
        
        # 6. Generate Hebrew insights
        insights = []
        
        # Value insight
        value_labels = {
            'contribution': 'תרומה',
            'recovery': 'התאוששות',
            'order': 'סדר',
            'harm': 'נזק',
            'avoidance': 'הימנעות'
        }
        
        if dominant_value:
            top_values = sorted(positive_values.items(), key=lambda x: x[1], reverse=True)[:2]
            if len(top_values) >= 2 and top_values[1][1] > 0:
                insights.append(f"השדה הקולקטיבי נוטה כעת ל{value_labels.get(top_values[0][0], '')} ו{value_labels.get(top_values[1][0], '')}.")
            elif top_values:
                insights.append(f"השדה הקולקטיבי נוטה כעת ל{value_labels.get(top_values[0][0], '')}.")
        
        # Harm pressure insight
        if avg_harm_pressure < 0:
            insights.append("לחץ הנזק הממוצע נמוך.")
        elif avg_harm_pressure > 10:
            insights.append("לחץ הנזק הממוצע גבוה יחסית.")
        else:
            insights.append("לחץ הנזק הממוצע בינוני.")
        
        # Direction insight
        if dominant_direction == 'order':
            insights.append("יש עלייה קלה בכיוון סדר.")
        elif dominant_direction == 'collective':
            insights.append("יש עלייה קלה בכיוון קולקטיבי.")
        elif dominant_direction == 'balanced':
            insights.append("הכיוון הממוצע מאוזן.")
        
        # Recovery insight
        if avg_recovery_stability > 10:
            insights.append("יציבות ההתאוששות הקולקטיבית גבוהה.")
        
        return CollectiveLayerResponse(
            success=True,
            total_users=total_users,
            total_decisions=total_decisions,
            value_counts=value_counts,
            avg_order_drift=round(avg_order_drift, 1),
            avg_collective_drift=round(avg_collective_drift, 1),
            avg_harm_pressure=round(avg_harm_pressure, 1),
            avg_recovery_stability=round(avg_recovery_stability, 1),
            dominant_value=dominant_value,
            dominant_direction=dominant_direction,
            recent_trend=recent_trend,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Get collective layer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Collective Layer Phase 2 - Time-Based Trends & Comparisons
# ============================================================

class DayTrend(BaseModel):
    date: str
    total_decisions: int = 0
    avg_order_drift: float = 0.0
    avg_collective_drift: float = 0.0
    avg_harm_pressure: float = 0.0
    avg_recovery_stability: float = 0.0
    value_counts: Dict[str, int] = {}

class PeriodComparison(BaseModel):
    current_period: Dict[str, Any] = {}
    previous_period: Dict[str, Any] = {}
    changes: Dict[str, Any] = {}

class CollectiveTrendsResponse(BaseModel):
    success: bool
    # Daily trends (last 14 days)
    daily_trends: List[DayTrend] = []
    # Period comparison (last 7 days vs previous 7 days)
    comparison: PeriodComparison = PeriodComparison()
    # Trend insights
    insights: List[str] = []


@api_router.get("/collective/trends", response_model=CollectiveTrendsResponse)
async def get_collective_trends():
    """
    Get time-based collective trends and comparison views.
    Aggregates data by day and compares current period vs previous period.
    """
    try:
        from datetime import timedelta
        
        now = datetime.now(timezone.utc)
        dates_14_days = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
        dates_7_days = dates_14_days[:7]
        dates_prev_7_days = dates_14_days[7:14]
        
        # Initialize daily aggregates
        daily_data = {date: {
            'total_decisions': 0,
            'order_drifts': [],
            'collective_drifts': [],
            'harm_pressures': [],
            'recovery_stabilities': [],
            'value_counts': {'contribution': 0, 'recovery': 0, 'order': 0, 'harm': 0, 'avoidance': 0}
        } for date in dates_14_days}
        
        # 1. Aggregate from philos_sessions (trend_history)
        all_sessions = await db.philos_sessions.find(
            {},
            {"_id": 0, "user_id": 0}
        ).to_list(1000)
        
        for session in all_sessions:
            trends = session.get('trend_history', [])
            for t in trends:
                date = t.get('date', '')
                if date in daily_data:
                    daily_data[date]['total_decisions'] += t.get('totalDecisions', 0)
                    daily_data[date]['value_counts']['contribution'] += t.get('contribution', 0)
                    daily_data[date]['value_counts']['recovery'] += t.get('recovery', 0)
                    daily_data[date]['value_counts']['order'] += t.get('order', 0)
                    daily_data[date]['value_counts']['harm'] += t.get('harm', 0)
                    daily_data[date]['value_counts']['avoidance'] += t.get('avoidance', 0)
        
        # 2. Aggregate from philos_path_learning for drift/pressure metrics
        all_learning = await db.philos_path_learning.find(
            {},
            {"_id": 0, "user_id": 0}
        ).to_list(5000)
        
        for entry in all_learning:
            timestamp = entry.get('timestamp', '')
            if timestamp:
                date = timestamp[:10]  # Extract date part
                if date in daily_data:
                    if entry.get('actual_order_drift') is not None:
                        daily_data[date]['order_drifts'].append(entry['actual_order_drift'])
                    if entry.get('actual_collective_drift') is not None:
                        daily_data[date]['collective_drifts'].append(entry['actual_collective_drift'])
                    if entry.get('actual_harm_pressure') is not None:
                        daily_data[date]['harm_pressures'].append(entry['actual_harm_pressure'])
                    if entry.get('actual_recovery_stability') is not None:
                        daily_data[date]['recovery_stabilities'].append(entry['actual_recovery_stability'])
        
        # 3. Build daily trends list
        daily_trends = []
        for date in sorted(dates_14_days, reverse=True):
            data = daily_data[date]
            trend = DayTrend(
                date=date,
                total_decisions=data['total_decisions'],
                avg_order_drift=round(sum(data['order_drifts']) / len(data['order_drifts']), 1) if data['order_drifts'] else 0.0,
                avg_collective_drift=round(sum(data['collective_drifts']) / len(data['collective_drifts']), 1) if data['collective_drifts'] else 0.0,
                avg_harm_pressure=round(sum(data['harm_pressures']) / len(data['harm_pressures']), 1) if data['harm_pressures'] else 0.0,
                avg_recovery_stability=round(sum(data['recovery_stabilities']) / len(data['recovery_stabilities']), 1) if data['recovery_stabilities'] else 0.0,
                value_counts=data['value_counts']
            )
            daily_trends.append(trend)
        
        # 4. Build period comparison (last 7 days vs previous 7 days)
        def aggregate_period(dates_list):
            total_decisions = 0
            order_drifts = []
            collective_drifts = []
            harm_pressures = []
            recovery_stabilities = []
            value_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'harm': 0, 'avoidance': 0}
            
            for date in dates_list:
                if date in daily_data:
                    data = daily_data[date]
                    total_decisions += data['total_decisions']
                    order_drifts.extend(data['order_drifts'])
                    collective_drifts.extend(data['collective_drifts'])
                    harm_pressures.extend(data['harm_pressures'])
                    recovery_stabilities.extend(data['recovery_stabilities'])
                    for k in value_counts:
                        value_counts[k] += data['value_counts'].get(k, 0)
            
            return {
                'total_decisions': total_decisions,
                'avg_order_drift': round(sum(order_drifts) / len(order_drifts), 1) if order_drifts else 0.0,
                'avg_collective_drift': round(sum(collective_drifts) / len(collective_drifts), 1) if collective_drifts else 0.0,
                'avg_harm_pressure': round(sum(harm_pressures) / len(harm_pressures), 1) if harm_pressures else 0.0,
                'avg_recovery_stability': round(sum(recovery_stabilities) / len(recovery_stabilities), 1) if recovery_stabilities else 0.0,
                'value_counts': value_counts
            }
        
        current_period = aggregate_period(dates_7_days)
        previous_period = aggregate_period(dates_prev_7_days)
        
        # Calculate changes
        def safe_change(current, previous):
            if previous == 0:
                return current
            return round(current - previous, 1)
        
        def safe_percent_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / abs(previous)) * 100, 1)
        
        changes = {
            'decisions_change': safe_change(current_period['total_decisions'], previous_period['total_decisions']),
            'decisions_percent': safe_percent_change(current_period['total_decisions'], previous_period['total_decisions']),
            'order_drift_change': safe_change(current_period['avg_order_drift'], previous_period['avg_order_drift']),
            'collective_drift_change': safe_change(current_period['avg_collective_drift'], previous_period['avg_collective_drift']),
            'harm_pressure_change': safe_change(current_period['avg_harm_pressure'], previous_period['avg_harm_pressure']),
            'recovery_stability_change': safe_change(current_period['avg_recovery_stability'], previous_period['avg_recovery_stability'])
        }
        
        comparison = PeriodComparison(
            current_period=current_period,
            previous_period=previous_period,
            changes=changes
        )
        
        # 5. Generate Hebrew insights based on comparison
        insights = []
        
        # Order drift insight
        if changes['order_drift_change'] > 3:
            insights.append("השדה הקולקטיבי נע השבוע יותר לכיוון סדר.")
        elif changes['order_drift_change'] < -3:
            insights.append("השדה הקולקטיבי נע השבוע יותר לכיוון כאוס.")
        
        # Harm pressure insight
        if changes['harm_pressure_change'] < -5:
            insights.append("לחץ הנזק ירד ביחס לתקופה הקודמת.")
        elif changes['harm_pressure_change'] > 5:
            insights.append("לחץ הנזק עלה ביחס לתקופה הקודמת.")
        
        # Recovery stability insight
        if changes['recovery_stability_change'] > 5:
            insights.append("יש עלייה בהתאוששות הקולקטיבית.")
        elif changes['recovery_stability_change'] < -5:
            insights.append("יש ירידה בהתאוששות הקולקטיבית.")
        
        # Collective drift insight
        if changes['collective_drift_change'] > 3:
            insights.append("הכיוון הקולקטיבי מתחזק.")
        elif changes['collective_drift_change'] < -3:
            insights.append("יש ירידה בכיוון הקולקטיבי.")
        
        # Activity insight
        if changes['decisions_percent'] > 20:
            insights.append("פעילות גבוהה יותר השבוע.")
        elif changes['decisions_percent'] < -20:
            insights.append("פעילות נמוכה יותר השבוע.")
        
        # Stability insight
        if not insights:
            insights.append("השדה הקולקטיבי יציב יחסית לתקופה הקודמת.")
        
        return CollectiveTrendsResponse(
            success=True,
            daily_trends=daily_trends,
            comparison=comparison,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Get collective trends error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ORIENTATION FIELD - Collective Navigation System
# ============================================================

class OrientationFieldResponse(BaseModel):
    success: bool
    field_distribution: Dict[str, float] = {}  # direction -> percentage
    field_center: Dict[str, float] = {}        # x, y coordinates of collective center
    total_users: int = 0
    total_decisions: int = 0
    dominant_direction: Optional[str] = None
    field_momentum: Optional[str] = None       # stabilizing, drifting, balancing
    field_insight: Optional[str] = None

class UserOrientationResponse(BaseModel):
    success: bool
    user_position: Dict[str, float] = {}       # x, y coordinates
    collective_center: Dict[str, float] = {}   # x, y coordinates
    alignment_score: float = 0.0               # 0-100, how aligned with collective
    drift_pattern: Optional[str] = None        # drift detection result
    momentum: Optional[str] = None             # user's momentum
    momentum_direction: Optional[str] = None   # which direction momentum is toward
    insights: List[str] = []

class DriftDetectionResponse(BaseModel):
    success: bool
    drift_detected: bool = False
    drift_type: Optional[str] = None           # chaos, isolation, order, contribution
    drift_strength: float = 0.0                # 0-100
    recent_pattern: List[str] = []             # last 7 days pattern
    insight: Optional[str] = None

@api_router.get("/orientation/field", response_model=OrientationFieldResponse)
async def get_orientation_field():
    """
    Get the collective orientation field - distribution of all users across directions.
    This is the main view of the collective navigation system.
    """
    try:
        # Aggregate all decisions from the last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Get all decisions
        decisions = await db.decisions.find({
            "timestamp": {"$gte": thirty_days_ago.isoformat()}
        }, {"_id": 0}).to_list(10000)
        
        # Also get learning records for more data
        learning_records = await db.path_learning.find({}, {"_id": 0}).to_list(5000)
        
        # Count directions
        direction_counts = {
            'recovery': 0,
            'order': 0,
            'contribution': 0,
            'exploration': 0,
            'harm': 0,
            'avoidance': 0
        }
        
        # Track unique users
        unique_users = set()
        total_ego_collective = 0
        total_chaos_order = 0
        count_with_positions = 0
        
        # Process decisions
        for d in decisions:
            tag = d.get('value_tag')
            if tag and tag in direction_counts:
                direction_counts[tag] += 1
            
            user_id = d.get('user_id')
            if user_id:
                unique_users.add(user_id)
            
            # Collect position data
            if d.get('ego_collective') is not None:
                total_ego_collective += d.get('ego_collective', 0)
                count_with_positions += 1
            if d.get('chaos_order') is not None:
                total_chaos_order += d.get('chaos_order', 0)
        
        # Process learning records for value tags
        for lr in learning_records:
            tag = lr.get('actual_value_tag')
            if tag and tag in direction_counts:
                direction_counts[tag] += 1
        
        total_decisions = sum(direction_counts.values())
        
        # Calculate distribution percentages
        field_distribution = {}
        if total_decisions > 0:
            for direction, count in direction_counts.items():
                field_distribution[direction] = round((count / total_decisions) * 100, 1)
        
        # Calculate collective center position
        # Map directions to compass positions
        direction_positions = {
            'recovery': (30, 65),
            'order': (30, 25),
            'contribution': (70, 25),
            'exploration': (70, 65),
            'harm': (15, 85),
            'avoidance': (50, 90)
        }
        
        # Weighted average of positions based on distribution
        center_x = 50
        center_y = 50
        if total_decisions > 0:
            weighted_x = 0
            weighted_y = 0
            for direction, pct in field_distribution.items():
                if direction in direction_positions:
                    pos = direction_positions[direction]
                    weighted_x += pos[0] * (pct / 100)
                    weighted_y += pos[1] * (pct / 100)
            center_x = round(weighted_x, 1)
            center_y = round(weighted_y, 1)
        
        field_center = {"x": center_x, "y": center_y}
        
        # Determine dominant direction
        dominant_direction = None
        max_pct = 0
        positive_directions = ['recovery', 'order', 'contribution', 'exploration']
        for direction in positive_directions:
            if field_distribution.get(direction, 0) > max_pct:
                max_pct = field_distribution.get(direction, 0)
                dominant_direction = direction
        
        # Calculate field momentum
        # Get last 7 days vs previous 7 days
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
        
        recent_decisions = [d for d in decisions if d.get('timestamp', '') >= seven_days_ago.isoformat()]
        previous_decisions = [d for d in decisions if fourteen_days_ago.isoformat() <= d.get('timestamp', '') < seven_days_ago.isoformat()]
        
        recent_positive = sum(1 for d in recent_decisions if d.get('value_tag') in positive_directions)
        previous_positive = sum(1 for d in previous_decisions if d.get('value_tag') in positive_directions)
        
        field_momentum = "stable"
        if len(recent_decisions) > 0 and len(previous_decisions) > 0:
            recent_ratio = recent_positive / len(recent_decisions) if recent_decisions else 0
            previous_ratio = previous_positive / len(previous_decisions) if previous_decisions else 0
            
            if recent_ratio > previous_ratio + 0.1:
                field_momentum = "stabilizing"
            elif recent_ratio < previous_ratio - 0.1:
                field_momentum = "drifting"
            else:
                field_momentum = "balancing"
        
        # Generate field insight
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        field_insight = None
        if dominant_direction and dominant_direction in direction_labels:
            if field_momentum == "stabilizing":
                field_insight = f"השדה הקולקטיבי מראה נטייה חזקה ל{direction_labels[dominant_direction]} ומתייצב."
            elif field_momentum == "drifting":
                field_insight = f"השדה הקולקטיבי נוטה ל{direction_labels[dominant_direction]} אך יש סחף מהאיזון."
            else:
                field_insight = f"השדה הקולקטיבי היום מראה נטייה ל{direction_labels[dominant_direction]}."
        
        return OrientationFieldResponse(
            success=True,
            field_distribution=field_distribution,
            field_center=field_center,
            total_users=len(unique_users),
            total_decisions=total_decisions,
            dominant_direction=dominant_direction,
            field_momentum=field_momentum,
            field_insight=field_insight
        )
        
    except Exception as e:
        logger.error(f"Get orientation field error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/user/{user_id}", response_model=UserOrientationResponse)
async def get_user_orientation(user_id: str):
    """
    Get user's position relative to the collective field.
    Includes drift detection and momentum calculation.
    """
    try:
        # Get user's decisions
        user_decisions = await db.decisions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
        if not user_decisions:
            return UserOrientationResponse(
                success=True,
                user_position={"x": 50, "y": 50},
                collective_center={"x": 50, "y": 50},
                alignment_score=50,
                insights=["אין מספיק נתונים. בצע פעולות כדי לראות את המיקום שלך."]
            )
        
        # Get collective field data
        field_data = await get_orientation_field()
        collective_center = field_data.field_center
        
        # Calculate user position based on recent decisions
        direction_positions = {
            'recovery': (30, 65),
            'order': (30, 25),
            'contribution': (70, 25),
            'exploration': (70, 65),
            'harm': (15, 85),
            'avoidance': (50, 90)
        }
        
        # Weight recent decisions more
        weighted_x = 0
        weighted_y = 0
        total_weight = 0
        
        for idx, d in enumerate(user_decisions[:20]):
            tag = d.get('value_tag')
            if tag and tag in direction_positions:
                weight = max(0.1, 1 - (idx * 0.05))  # Recent decisions weighted more
                pos = direction_positions[tag]
                weighted_x += pos[0] * weight
                weighted_y += pos[1] * weight
                total_weight += weight
        
        user_x = round(weighted_x / total_weight, 1) if total_weight > 0 else 50
        user_y = round(weighted_y / total_weight, 1) if total_weight > 0 else 50
        
        user_position = {"x": user_x, "y": user_y}
        
        # Calculate alignment score (distance from collective center)
        distance = ((user_x - collective_center["x"])**2 + (user_y - collective_center["y"])**2)**0.5
        max_distance = 70  # Max possible distance on compass
        alignment_score = round(max(0, 100 - (distance / max_distance * 100)), 1)
        
        # Drift detection
        drift_pattern = None
        recent_tags = [d.get('value_tag') for d in user_decisions[:10] if d.get('value_tag')]
        
        harm_count = recent_tags.count('harm')
        avoidance_count = recent_tags.count('avoidance')
        order_count = recent_tags.count('order')
        contribution_count = recent_tags.count('contribution')
        
        if harm_count + avoidance_count >= 4:
            drift_pattern = "drift_toward_chaos"
        elif order_count >= 5 and contribution_count == 0:
            drift_pattern = "drift_toward_isolation"
        elif order_count >= 4:
            drift_pattern = "stabilization_toward_order"
        elif contribution_count >= 3:
            drift_pattern = "movement_toward_contribution"
        
        # Calculate momentum (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent = [d for d in user_decisions if d.get('timestamp', '') >= seven_days_ago.isoformat()]
        
        momentum = "stable"
        momentum_direction = None
        
        if len(recent) >= 3:
            positive_directions = ['recovery', 'order', 'contribution', 'exploration']
            recent_positive = sum(1 for d in recent if d.get('value_tag') in positive_directions)
            positive_ratio = recent_positive / len(recent)
            
            if positive_ratio > 0.7:
                momentum = "stabilizing"
                # Find which positive direction is strongest
                pos_counts = {d: recent.count(d) for d in positive_directions}
                momentum_direction = max(pos_counts, key=lambda k: sum(1 for r in recent if r.get('value_tag') == k))
            elif positive_ratio < 0.4:
                momentum = "drifting"
            else:
                momentum = "balancing"
        
        # Generate insights
        insights = []
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה',
            'harm': 'נזק',
            'avoidance': 'הימנעות'
        }
        
        # Position insight
        if alignment_score > 70:
            insights.append("אתה מיושר היטב עם השדה הקולקטיבי.")
        elif alignment_score < 40:
            insights.append("יש מרחק בין המיקום שלך לבין מרכז השדה הקולקטיבי.")
        
        # Drift insight
        if drift_pattern == "drift_toward_chaos":
            insights.append("נראה סחף לכיוון כאוס. מומלץ לשקול פעולת התאוששות או סדר.")
        elif drift_pattern == "drift_toward_isolation":
            insights.append("יש נטייה לבידוד. כדאי לשקול פעולת תרומה.")
        elif drift_pattern == "stabilization_toward_order":
            insights.append("אתה מתייצב לכיוון סדר אחרי תקופה של הימנעות.")
        elif drift_pattern == "movement_toward_contribution":
            insights.append("יש תנועה חיובית לכיוון תרומה.")
        
        # Momentum insight
        if momentum == "stabilizing" and momentum_direction:
            insights.append(f"המומנטום שלך חיובי לכיוון {direction_labels.get(momentum_direction, momentum_direction)}.")
        elif momentum == "drifting":
            insights.append("המומנטום מראה סחף מהאיזון. כדאי לבדוק את הכיוון.")
        
        return UserOrientationResponse(
            success=True,
            user_position=user_position,
            collective_center=dict(collective_center),
            alignment_score=alignment_score,
            drift_pattern=drift_pattern,
            momentum=momentum,
            momentum_direction=momentum_direction,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Get user orientation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/drift/{user_id}", response_model=DriftDetectionResponse)
async def detect_drift(user_id: str):
    """
    Detailed drift detection for a user.
    Analyzes patterns over the last 7 days.
    """
    try:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        user_decisions = await db.decisions.find(
            {
                "user_id": user_id,
                "timestamp": {"$gte": seven_days_ago.isoformat()}
            },
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
        if len(user_decisions) < 3:
            return DriftDetectionResponse(
                success=True,
                drift_detected=False,
                insight="אין מספיק נתונים לזיהוי דפוס. המשך לבצע פעולות."
            )
        
        # Extract pattern
        recent_pattern = [d.get('value_tag', 'unknown') for d in user_decisions[:7]]
        
        # Count directions
        counts = {}
        for tag in recent_pattern:
            counts[tag] = counts.get(tag, 0) + 1
        
        # Detect drift
        drift_detected = False
        drift_type = None
        drift_strength = 0
        insight = None
        
        total = len(recent_pattern)
        
        # Check for chaos drift (harm + avoidance)
        chaos_count = counts.get('harm', 0) + counts.get('avoidance', 0)
        if chaos_count >= total * 0.5:
            drift_detected = True
            drift_type = "chaos"
            drift_strength = round((chaos_count / total) * 100, 1)
            if counts.get('harm', 0) > counts.get('avoidance', 0):
                insight = "זוהה סחף לכיוון נזק. מומלץ לאזן עם התאוששות."
            else:
                insight = "זוהה סחף לכיוון הימנעות. מומלץ לאזן עם סדר."
        
        # Check for isolation drift (only order, no contribution/exploration)
        elif counts.get('order', 0) >= 3 and counts.get('contribution', 0) == 0 and counts.get('exploration', 0) == 0:
            drift_detected = True
            drift_type = "isolation"
            drift_strength = round((counts.get('order', 0) / total) * 100, 1)
            insight = "זוהה דפוס של בידוד (סדר ללא תרומה). מומלץ לפתוח לכיוון תרומה."
        
        # Check for positive stabilization
        elif counts.get('order', 0) + counts.get('contribution', 0) >= total * 0.6:
            drift_detected = False
            drift_type = "stabilization"
            drift_strength = round(((counts.get('order', 0) + counts.get('contribution', 0)) / total) * 100, 1)
            insight = "נראה דפוס של התייצבות חיובית. המשך בכיוון זה."
        
        # Check for contribution movement
        elif counts.get('contribution', 0) >= 2:
            drift_detected = False
            drift_type = "contribution_movement"
            drift_strength = round((counts.get('contribution', 0) / total) * 100, 1)
            insight = "יש תנועה חיובית לכיוון תרומה."
        
        if not insight:
            insight = "הדפוס הנוכחי מאוזן יחסית."
        
        return DriftDetectionResponse(
            success=True,
            drift_detected=drift_detected,
            drift_type=drift_type,
            drift_strength=drift_strength,
            recent_pattern=recent_pattern,
            insight=insight
        )
        
    except Exception as e:
        logger.error(f"Detect drift error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
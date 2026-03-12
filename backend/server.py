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
    field_momentum: Optional[str] = None       # stabilizing, drifting, shifting
    momentum_direction: Optional[str] = None   # which direction the field is moving toward
    momentum_strength: float = 0.0             # 0-100, strength of momentum
    momentum_arrow: Dict[str, float] = {}      # from_x, from_y, to_x, to_y for visualization
    field_insight: Optional[str] = None
    momentum_insight: Optional[str] = None     # specific insight about momentum

class WeeklyFieldSnapshot(BaseModel):
    week_label: str                            # "שבוע 1", "שבוע 2", etc.
    week_start: str                            # ISO date
    center_x: float
    center_y: float
    dominant_direction: Optional[str] = None
    positive_ratio: float = 0.0                # 0-100, % of positive directions
    total_actions: int = 0

class FieldHistoryResponse(BaseModel):
    success: bool
    weekly_snapshots: List[WeeklyFieldSnapshot] = []  # Last 4 weeks
    sparkline_data: List[float] = []           # positive_ratio for each week (for sparkline)
    trend_type: Optional[str] = None           # stabilizing, drifting, shifting_recovery, etc.
    trend_direction: Optional[str] = None      # Which direction trend is moving
    trend_insight: Optional[str] = None        # Hebrew insight about the trend
    weeks_analyzed: int = 0

class FieldTodayResponse(BaseModel):
    success: bool
    distribution: Dict[str, float] = {}        # direction -> percentage (only 4 positive directions)
    total_actions: int = 0
    active_users: int = 0
    dominant_direction: Optional[str] = None
    insight: Optional[str] = None              # Hebrew insight

class WeeklyInsightResponse(BaseModel):
    success: bool
    user_id: str
    distribution: Dict[str, int] = {}          # direction -> count
    distribution_percent: Dict[str, float] = {} # direction -> percentage
    total_actions: int = 0
    dominant_direction: Optional[str] = None
    insight_he: Optional[str] = None
    trend: Optional[str] = None                # improving, stable, declining

class ShareCardResponse(BaseModel):
    success: bool
    user_id: str
    orientation: Optional[str] = None          # Current dominant orientation
    message_he: Optional[str] = None           # Hebrew message for sharing
    streak: int = 0
    compass_position: Dict[str, float] = {}    # x, y for compass visualization

class OrientationIndexResponse(BaseModel):
    success: bool
    distribution: Dict[str, float] = {}        # Global distribution percentages
    dominant_direction: Optional[str] = None
    total_users: int = 0
    total_actions_today: int = 0
    yesterday_dominant: Optional[str] = None
    direction_change: Optional[str] = None     # same, shifted_to_X
    headline_he: Optional[str] = None

class DirectionPercentile(BaseModel):
    direction: str
    user_count: int                            # User's action count in this direction
    percentile: float                          # 0-100, user's percentile (higher = more focused)
    rank_label: Optional[str] = None           # "עליון 10%", "עליון 25%", etc.

class UserComparisonResponse(BaseModel):
    success: bool
    user_id: str
    total_user_actions: int = 0
    direction_percentiles: List[DirectionPercentile] = []  # Percentile for each direction
    dominant_direction: Optional[str] = None   # User's most frequent direction
    dominant_percentile: float = 0.0           # Percentile in dominant direction
    comparison_insight: Optional[str] = None   # Hebrew insight about user's position
    week_comparison: Dict[str, float] = {}     # This week vs collective average

class DecisionPathResponse(BaseModel):
    success: bool
    user_id: str
    current_state: Optional[str] = None        # Current imbalance or state
    drift_type: Optional[str] = None           # harm, avoidance, isolation, rigidity
    recommended_direction: Optional[str] = None # recovery, order, contribution, exploration
    headline: Optional[str] = None             # Short Hebrew headline
    recommended_step: Optional[str] = None     # Practical recommendation
    concrete_action: Optional[str] = None      # Specific action to take
    theory_basis: Optional[str] = None         # Why this recommendation (theory link)
    session_id: Optional[str] = None           # For tracking one per session

class OrientationSnapshot(BaseModel):
    user_id: str
    timestamp: str
    dominant_direction: Optional[str] = None
    direction_counts: Dict[str, int] = {}
    positive_ratio: float = 0.0
    avoidance_ratio: float = 0.0
    momentum: Optional[str] = None

class OrientationIdentityResponse(BaseModel):
    success: bool
    user_id: str
    identity_type: Optional[str] = None        # The computed identity type
    identity_label: Optional[str] = None       # Hebrew label for identity
    identity_description: Optional[str] = None # Hebrew description
    is_warning_state: bool = False             # True for avoidance loop
    
    # Computation inputs
    dominant_direction: Optional[str] = None
    momentum: Optional[str] = None             # stabilizing, drifting, shifting, stable
    time_in_direction: int = 0                 # Days in current dominant direction
    avoidance_ratio: float = 0.0               # 0-100, percentage of avoidance actions
    previous_dominant: Optional[str] = None    # Previous dominant direction (for transitions)
    
    # Additional context
    direction_counts: Dict[str, int] = {}
    total_actions: int = 0
    weeks_analyzed: int = 0
    insight: Optional[str] = None              # Supportive Hebrew insight

class DailyQuestionResponse(BaseModel):
    success: bool
    user_id: str
    identity: Optional[str] = None             # Current orientation identity
    question_he: Optional[str] = None          # Hebrew question based on identity
    suggested_direction: Optional[str] = None  # Direction the question aims for
    question_id: Optional[str] = None          # For tracking responses
    already_answered_today: bool = False       # If user already answered today
    streak: int = 0                            # Current consecutive days streak
    longest_streak: int = 0                    # User's longest streak ever

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

@api_router.get("/orientation/field-today", response_model=FieldTodayResponse)
async def get_field_today():
    """
    Get today's orientation field - distribution of all users' actions in last 24 hours.
    Returns only the 4 positive directions: Contribution, Recovery, Order, Exploration.
    """
    try:
        # Get all user sessions
        all_sessions = await db.philos_sessions.find({}, {"_id": 0}).to_list(1000)
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['contribution', 'recovery', 'order', 'exploration']
        
        # Time boundary - last 24 hours
        now = datetime.now(timezone.utc)
        twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
        
        # Count directions from last 24 hours
        direction_counts = {d: 0 for d in positive_directions}
        active_users = set()
        
        for session in all_sessions:
            user_id = session.get('user_id')
            history = session.get('history', [])
            
            user_active_today = False
            for h in history:
                ts = h.get('timestamp', '')
                if ts >= twenty_four_hours_ago:
                    tag = h.get('value_tag')
                    if tag in positive_directions:
                        direction_counts[tag] += 1
                        user_active_today = True
            
            if user_active_today and user_id:
                active_users.add(user_id)
        
        total_actions = sum(direction_counts.values())
        
        # Calculate distribution percentages
        distribution = {}
        if total_actions > 0:
            for direction in positive_directions:
                distribution[direction] = round((direction_counts[direction] / total_actions) * 100, 1)
        else:
            # Default equal distribution if no data
            for direction in positive_directions:
                distribution[direction] = 25.0
        
        # Find dominant direction
        dominant_direction = None
        max_pct = 0
        for direction, pct in distribution.items():
            if pct > max_pct:
                max_pct = pct
                dominant_direction = direction
        
        # Generate insight
        insight = None
        if total_actions > 0 and dominant_direction:
            insight = f"היום השדה נוטה לכיוון {direction_labels.get(dominant_direction, dominant_direction)}."
        else:
            insight = "השדה מאוזן היום."
        
        return FieldTodayResponse(
            success=True,
            distribution=distribution,
            total_actions=total_actions,
            active_users=len(active_users),
            dominant_direction=dominant_direction,
            insight=insight
        )
        
    except Exception as e:
        logger.error(f"Get field today error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/field", response_model=OrientationFieldResponse)
async def get_orientation_field():
    """
    Get the collective orientation field - distribution of all users across directions.
    Includes momentum calculation from last 7 days of activity.
    """
    try:
        # Get all user sessions to aggregate data
        all_sessions = await db.philos_sessions.find({}, {"_id": 0}).to_list(1000)
        
        # Direction positions for compass mapping
        direction_positions = {
            'recovery': (30, 65),
            'order': (30, 25),
            'contribution': (70, 25),
            'exploration': (70, 65),
            'harm': (15, 85),
            'avoidance': (50, 90)
        }
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['recovery', 'order', 'contribution', 'exploration']
        
        # Time boundaries for momentum calculation
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        fourteen_days_ago = (now - timedelta(days=14)).isoformat()
        
        # Count directions - overall and by time period
        overall_counts = {d: 0 for d in direction_positions.keys()}
        recent_counts = {d: 0 for d in direction_positions.keys()}  # Last 7 days
        previous_counts = {d: 0 for d in direction_positions.keys()}  # 7-14 days ago
        
        # Track unique users
        unique_users = set()
        
        # Process each user's session data
        for session in all_sessions:
            user_id = session.get('user_id')
            if user_id:
                unique_users.add(user_id)
            
            # Get history from session
            history = session.get('history', [])
            for h in history:
                tag = h.get('value_tag')
                if tag and tag in overall_counts:
                    overall_counts[tag] += 1
                    
                    # Categorize by time
                    ts = h.get('timestamp', '')
                    if ts >= seven_days_ago:
                        recent_counts[tag] += 1
                    elif ts >= fourteen_days_ago:
                        previous_counts[tag] += 1
            
            # Also count from global_stats for overall (legacy data)
            gs = session.get('global_stats', {})
            for direction in overall_counts:
                overall_counts[direction] += gs.get(direction, 0)
        
        total_decisions = sum(overall_counts.values())
        total_recent = sum(recent_counts.values())
        total_previous = sum(previous_counts.values())
        
        # Calculate distribution percentages
        field_distribution = {}
        if total_decisions > 0:
            for direction, count in overall_counts.items():
                field_distribution[direction] = round((count / total_decisions) * 100, 1)
        
        # Calculate collective center position
        center_x = 50
        center_y = 50
        if total_decisions > 0:
            weighted_x = 0
            weighted_y = 0
            total_weight = 0
            for direction, pct in field_distribution.items():
                if direction in direction_positions and pct > 0:
                    pos = direction_positions[direction]
                    weighted_x += pos[0] * (pct / 100)
                    weighted_y += pos[1] * (pct / 100)
                    total_weight += pct / 100
            if total_weight > 0:
                center_x = round(weighted_x / total_weight, 1)
                center_y = round(weighted_y / total_weight, 1)
        
        field_center = {"x": center_x, "y": center_y}
        
        # Determine dominant direction (positive only)
        dominant_direction = None
        max_pct = 0
        for direction in positive_directions:
            if field_distribution.get(direction, 0) > max_pct:
                max_pct = field_distribution.get(direction, 0)
                dominant_direction = direction
        
        # === MOMENTUM CALCULATION (Last 7 days vs Previous 7 days) ===
        field_momentum = "stable"
        momentum_direction = None
        momentum_strength = 0.0
        momentum_arrow = {}
        momentum_insight = None
        
        # Calculate recent center vs previous center
        recent_center_x = 50
        recent_center_y = 50
        previous_center_x = 50
        previous_center_y = 50
        
        if total_recent > 0:
            rwx, rwy, rwt = 0, 0, 0
            for direction, count in recent_counts.items():
                if direction in direction_positions and count > 0:
                    pos = direction_positions[direction]
                    weight = count / total_recent
                    rwx += pos[0] * weight
                    rwy += pos[1] * weight
                    rwt += weight
            if rwt > 0:
                recent_center_x = round(rwx / rwt, 1)
                recent_center_y = round(rwy / rwt, 1)
        
        if total_previous > 0:
            pwx, pwy, pwt = 0, 0, 0
            for direction, count in previous_counts.items():
                if direction in direction_positions and count > 0:
                    pos = direction_positions[direction]
                    weight = count / total_previous
                    pwx += pos[0] * weight
                    pwy += pos[1] * weight
                    pwt += weight
            if pwt > 0:
                previous_center_x = round(pwx / pwt, 1)
                previous_center_y = round(pwy / pwt, 1)
        
        # Calculate movement vector
        dx = recent_center_x - previous_center_x
        dy = recent_center_y - previous_center_y
        movement_distance = (dx**2 + dy**2)**0.5
        
        # Determine momentum characteristics
        if total_recent >= 3 and total_previous >= 3:
            # Calculate direction shift
            recent_positive = sum(recent_counts.get(d, 0) for d in positive_directions)
            previous_positive = sum(previous_counts.get(d, 0) for d in positive_directions)
            recent_ratio = recent_positive / total_recent if total_recent > 0 else 0
            previous_ratio = previous_positive / total_previous if total_previous > 0 else 0
            
            # Find which direction gained most
            direction_changes = {}
            for direction in positive_directions:
                recent_pct = (recent_counts.get(direction, 0) / total_recent * 100) if total_recent > 0 else 0
                previous_pct = (previous_counts.get(direction, 0) / total_previous * 100) if total_previous > 0 else 0
                direction_changes[direction] = recent_pct - previous_pct
            
            max_gain_direction = max(direction_changes, key=direction_changes.get)
            max_gain = direction_changes[max_gain_direction]
            
            # Classify momentum
            if recent_ratio > previous_ratio + 0.15:
                field_momentum = "stabilizing"
                momentum_strength = min(100, (recent_ratio - previous_ratio) * 200)
            elif recent_ratio < previous_ratio - 0.15:
                field_momentum = "drifting"
                momentum_strength = min(100, (previous_ratio - recent_ratio) * 200)
            elif abs(max_gain) > 10:
                field_momentum = "shifting"
                momentum_direction = max_gain_direction
                momentum_strength = min(100, abs(max_gain) * 2)
            else:
                field_momentum = "stable"
                momentum_strength = 30
            
            # Create momentum arrow for visualization
            if movement_distance > 3:
                # Normalize and extend for visualization
                scale = min(15, movement_distance)
                norm_dx = (dx / movement_distance) * scale if movement_distance > 0 else 0
                norm_dy = (dy / movement_distance) * scale if movement_distance > 0 else 0
                
                momentum_arrow = {
                    "from_x": round(center_x - norm_dx * 0.3, 1),
                    "from_y": round(center_y - norm_dy * 0.3, 1),
                    "to_x": round(center_x + norm_dx * 0.7, 1),
                    "to_y": round(center_y + norm_dy * 0.7, 1)
                }
            
            # Generate momentum insight
            if field_momentum == "stabilizing":
                momentum_insight = "השדה הקולקטיבי מתייצב ונע לכיוון איזון חיובי."
            elif field_momentum == "drifting":
                momentum_insight = "השדה הקולקטיבי נסחף מהאיזון בימים האחרונים."
            elif field_momentum == "shifting" and momentum_direction:
                momentum_insight = f"השדה הקולקטיבי נע בהדרגה לכיוון {direction_labels.get(momentum_direction, momentum_direction)}."
            else:
                momentum_insight = "השדה הקולקטיבי יציב ומאוזן."
        else:
            # Not enough data for momentum
            momentum_insight = "אין מספיק נתונים לחישוב מומנטום."
        
        # Generate field insight (overall state)
        field_insight = None
        if dominant_direction and dominant_direction in direction_labels:
            if field_momentum == "stabilizing":
                field_insight = f"השדה הקולקטיבי מראה נטייה חזקה ל{direction_labels[dominant_direction]} ומתייצב."
            elif field_momentum == "drifting":
                field_insight = f"השדה הקולקטיבי נוטה ל{direction_labels[dominant_direction]} אך יש סחף מהאיזון."
            elif field_momentum == "shifting":
                field_insight = f"השדה הקולקטיבי נוטה ל{direction_labels[dominant_direction]} ומשנה כיוון."
            else:
                field_insight = f"השדה הקולקטיבי מראה נטייה ל{direction_labels[dominant_direction]}."
        
        return OrientationFieldResponse(
            success=True,
            field_distribution=field_distribution,
            field_center=field_center,
            total_users=len(unique_users),
            total_decisions=total_decisions,
            dominant_direction=dominant_direction,
            field_momentum=field_momentum,
            momentum_direction=momentum_direction,
            momentum_strength=round(momentum_strength, 1),
            momentum_arrow=momentum_arrow,
            field_insight=field_insight,
            momentum_insight=momentum_insight
        )
        
    except Exception as e:
        logger.error(f"Get orientation field error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/history", response_model=FieldHistoryResponse)
async def get_field_history():
    """
    Get historical momentum tracking for the collective field (last 4 weeks).
    Returns weekly snapshots with trend analysis.
    """
    try:
        # Get all user sessions
        all_sessions = await db.philos_sessions.find({}, {"_id": 0}).to_list(1000)
        
        # Direction positions for compass mapping
        direction_positions = {
            'recovery': (30, 65),
            'order': (30, 25),
            'contribution': (70, 25),
            'exploration': (70, 65),
            'harm': (15, 85),
            'avoidance': (50, 90)
        }
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['recovery', 'order', 'contribution', 'exploration']
        
        # Calculate week boundaries (last 4 weeks)
        now = datetime.now(timezone.utc)
        week_boundaries = []
        for i in range(4):
            week_end = now - timedelta(days=i * 7)
            week_start = week_end - timedelta(days=7)
            week_boundaries.append({
                'start': week_start.isoformat(),
                'end': week_end.isoformat(),
                'label': f'שבוע {4 - i}' if i > 0 else 'השבוע'
            })
        week_boundaries.reverse()  # Oldest first
        
        # Collect actions by week
        weekly_data = []
        for week in week_boundaries:
            week_counts = {d: 0 for d in direction_positions.keys()}
            week_total = 0
            
            # Process each user's session data
            for session in all_sessions:
                history = session.get('history', [])
                for h in history:
                    ts = h.get('timestamp', '')
                    if week['start'] <= ts < week['end']:
                        tag = h.get('value_tag')
                        if tag and tag in week_counts:
                            week_counts[tag] += 1
                            week_total += 1
            
            # Calculate week center position
            center_x = 50
            center_y = 50
            if week_total > 0:
                weighted_x = 0
                weighted_y = 0
                total_weight = 0
                for direction, count in week_counts.items():
                    if direction in direction_positions and count > 0:
                        pos = direction_positions[direction]
                        weight = count / week_total
                        weighted_x += pos[0] * weight
                        weighted_y += pos[1] * weight
                        total_weight += weight
                if total_weight > 0:
                    center_x = round(weighted_x / total_weight, 1)
                    center_y = round(weighted_y / total_weight, 1)
            
            # Calculate positive ratio
            positive_count = sum(week_counts.get(d, 0) for d in positive_directions)
            positive_ratio = round((positive_count / week_total * 100) if week_total > 0 else 50, 1)
            
            # Find dominant direction
            dominant = None
            max_count = 0
            for direction in positive_directions:
                if week_counts.get(direction, 0) > max_count:
                    max_count = week_counts.get(direction, 0)
                    dominant = direction
            
            weekly_data.append(WeeklyFieldSnapshot(
                week_label=week['label'],
                week_start=week['start'][:10],  # Just date
                center_x=center_x,
                center_y=center_y,
                dominant_direction=dominant,
                positive_ratio=positive_ratio,
                total_actions=week_total
            ))
        
        # Create sparkline data (positive ratios)
        sparkline_data = [w.positive_ratio for w in weekly_data]
        
        # Analyze trend across weeks
        trend_type = "stable"
        trend_direction = None
        trend_insight = None
        
        weeks_with_data = [w for w in weekly_data if w.total_actions > 0]
        
        if len(weeks_with_data) >= 2:
            # Check positive ratio trend
            first_ratio = weeks_with_data[0].positive_ratio
            last_ratio = weeks_with_data[-1].positive_ratio
            ratio_change = last_ratio - first_ratio
            
            # Check direction changes
            direction_trends = {}
            for direction in positive_directions:
                first_dominant = weeks_with_data[0].dominant_direction
                last_dominant = weeks_with_data[-1].dominant_direction
                direction_trends[direction] = {
                    'first': first_dominant == direction,
                    'last': last_dominant == direction
                }
            
            # Find consistent direction shift
            consistent_direction = None
            direction_counts = {}
            for w in weeks_with_data:
                if w.dominant_direction:
                    direction_counts[w.dominant_direction] = direction_counts.get(w.dominant_direction, 0) + 1
            
            if direction_counts:
                most_common = max(direction_counts, key=direction_counts.get)
                if direction_counts[most_common] >= len(weeks_with_data) * 0.5:
                    consistent_direction = most_common
            
            # Determine trend type
            if ratio_change > 10:
                trend_type = "stabilizing"
                trend_insight = "השדה הקולקטיבי מתייצב בשבועות האחרונים."
            elif ratio_change < -10:
                trend_type = "drifting"
                trend_insight = "השדה הקולקטיבי נסחף מהאיזון בשבועות האחרונים."
            elif consistent_direction:
                trend_type = f"shifting_{consistent_direction}"
                trend_direction = consistent_direction
                trend_insight = f"השדה הקולקטיבי נע בהדרגה לכיוון {direction_labels.get(consistent_direction, consistent_direction)} בשבועות האחרונים."
            else:
                trend_type = "stable"
                trend_insight = "השדה הקולקטיבי יציב ומאוזן בשבועות האחרונים."
            
            # More specific insights based on movement
            if len(weeks_with_data) >= 3:
                centers = [(w.center_x, w.center_y) for w in weeks_with_data]
                
                # Check for consistent movement direction
                movements = []
                for i in range(1, len(centers)):
                    dx = centers[i][0] - centers[i-1][0]
                    dy = centers[i][1] - centers[i-1][1]
                    movements.append((dx, dy))
                
                # Check for upward movement (toward order)
                avg_dy = sum(m[1] for m in movements) / len(movements)
                avg_dx = sum(m[0] for m in movements) / len(movements)
                
                if avg_dy < -3:  # Moving up (toward order)
                    if avg_dx > 3:
                        trend_direction = "contribution"
                        trend_insight = "השדה הקולקטיבי נע לכיוון תרומה וסדר בשבועות האחרונים."
                    elif avg_dx < -3:
                        trend_direction = "order"
                        trend_insight = "השדה הקולקטיבי נע לכיוון סדר בשבועות האחרונים."
                elif avg_dy > 3:  # Moving down (toward chaos)
                    if avg_dx > 3:
                        trend_direction = "exploration"
                        trend_insight = "השדה הקולקטיבי נע לכיוון חקירה בשבועות האחרונים."
                    elif avg_dx < -3:
                        trend_direction = "recovery"
                        trend_insight = "השדה הקולקטיבי נע לכיוון התאוששות בשבועות האחרונים."
        else:
            trend_insight = "אין מספיק נתונים היסטוריים לזיהוי מגמה."
        
        return FieldHistoryResponse(
            success=True,
            weekly_snapshots=weekly_data,
            sparkline_data=sparkline_data,
            trend_type=trend_type,
            trend_direction=trend_direction,
            trend_insight=trend_insight,
            weeks_analyzed=len(weeks_with_data)
        )
        
    except Exception as e:
        logger.error(f"Get field history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/compare/{user_id}", response_model=UserComparisonResponse)
async def get_user_comparison(user_id: str):
    """
    Calculate user's percentile ranking within each direction.
    Compares user to all other users in the collective.
    """
    try:
        # Get all user sessions
        all_sessions = await db.philos_sessions.find({}, {"_id": 0}).to_list(1000)
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['recovery', 'order', 'contribution', 'exploration']
        
        # Time boundary - last 7 days
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        # Calculate direction counts for each user
        user_direction_counts = {}  # user_id -> {direction -> count}
        
        for session in all_sessions:
            session_user_id = session.get('user_id')
            if not session_user_id:
                continue
                
            counts = {d: 0 for d in positive_directions}
            history = session.get('history', [])
            
            for h in history:
                ts = h.get('timestamp', '')
                if ts >= seven_days_ago:
                    tag = h.get('value_tag')
                    if tag and tag in counts:
                        counts[tag] += 1
            
            user_direction_counts[session_user_id] = counts
        
        # Get current user's counts
        user_counts = user_direction_counts.get(user_id, {d: 0 for d in positive_directions})
        total_user_actions = sum(user_counts.values())
        
        if total_user_actions == 0:
            return UserComparisonResponse(
                success=True,
                user_id=user_id,
                total_user_actions=0,
                direction_percentiles=[],
                comparison_insight="אין מספיק נתונים השבוע. בצע פעולות כדי להשוות את עצמך לאחרים."
            )
        
        # Calculate percentiles for each direction
        direction_percentiles = []
        
        for direction in positive_directions:
            user_count = user_counts.get(direction, 0)
            
            # Get all user counts for this direction
            all_counts = [counts.get(direction, 0) for counts in user_direction_counts.values()]
            all_counts = [c for c in all_counts if c > 0]  # Only users with activity
            
            if not all_counts:
                percentile = 50.0
            else:
                # Calculate percentile: how many users have LESS activity than this user
                users_below = sum(1 for c in all_counts if c < user_count)
                users_equal = sum(1 for c in all_counts if c == user_count)
                percentile = round((users_below + users_equal * 0.5) / len(all_counts) * 100, 1)
            
            # Generate rank label
            rank_label = None
            if user_count > 0:
                if percentile >= 90:
                    rank_label = "עליון 10%"
                elif percentile >= 75:
                    rank_label = "עליון 25%"
                elif percentile >= 50:
                    rank_label = "מעל הממוצע"
                else:
                    rank_label = "פעיל"
            
            direction_percentiles.append(DirectionPercentile(
                direction=direction,
                user_count=user_count,
                percentile=percentile,
                rank_label=rank_label
            ))
        
        # Find user's dominant direction
        dominant_direction = None
        dominant_count = 0
        dominant_percentile = 0.0
        
        for dp in direction_percentiles:
            if dp.user_count > dominant_count:
                dominant_count = dp.user_count
                dominant_direction = dp.direction
                dominant_percentile = dp.percentile
        
        # Calculate week comparison (user's distribution vs collective)
        week_comparison = {}
        if total_user_actions > 0:
            for direction in positive_directions:
                user_pct = round(user_counts.get(direction, 0) / total_user_actions * 100, 1)
                week_comparison[direction] = user_pct
        
        # Generate comparison insight
        comparison_insight = None
        
        if dominant_direction and dominant_percentile >= 75:
            comparison_insight = f"אתה בין ה-{100 - int(dominant_percentile)}% המובילים במיקוד על {direction_labels.get(dominant_direction, dominant_direction)} השבוע."
        elif dominant_direction and dominant_percentile >= 50:
            comparison_insight = f"אתה מעל הממוצע במיקוד על {direction_labels.get(dominant_direction, dominant_direction)}."
        elif dominant_direction:
            comparison_insight = f"הכיוון המוביל שלך השבוע הוא {direction_labels.get(dominant_direction, dominant_direction)}."
        
        # Add balance insight if user is well-distributed
        if total_user_actions >= 4:
            counts_above_zero = [dp.user_count for dp in direction_percentiles if dp.user_count > 0]
            if len(counts_above_zero) >= 3:
                max_count = max(counts_above_zero)
                min_count = min(counts_above_zero)
                if max_count - min_count <= 2:
                    comparison_insight = "המיקוד שלך מאוזן בין הכיוונים. זהו סימן טוב לאיזון."
        
        return UserComparisonResponse(
            success=True,
            user_id=user_id,
            total_user_actions=total_user_actions,
            direction_percentiles=direction_percentiles,
            dominant_direction=dominant_direction,
            dominant_percentile=dominant_percentile,
            comparison_insight=comparison_insight,
            week_comparison=week_comparison
        )
        
    except Exception as e:
        logger.error(f"Get user comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/decision-path/{user_id}", response_model=DecisionPathResponse)
async def get_decision_path(user_id: str):
    """
    Decision Path Engine: Generate a concrete action recommendation
    based on user's current position and imbalance.
    
    Theory-based recommendations:
    - harm → recovery: "יצאת מהמסלול. הצעד הבא: התאוששות."
    - avoidance → order: "נסחפת להימנעות. הצעד הבא: ליצור מבנה."
    - isolation → contribution: "מיקוד עצמי גבוה. הצעד הבא: לתרום לאחרים."
    - rigidity → exploration: "יש קיפאון. הצעד הבא: לפתוח לחדש."
    """
    try:
        # Get user's session data
        user_session = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        user_history = user_session.get('history', []) if user_session else []
        
        # Direction labels in Hebrew
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה',
            'harm': 'נזק',
            'avoidance': 'הימנעות'
        }
        
        # Concrete actions for each direction (Hebrew)
        concrete_actions = {
            'recovery': [
                "קח הפסקה של 5 דקות ונשום עמוק.",
                "שתה כוס מים ושב בשקט לרגע.",
                "צא להליכה קצרה של 10 דקות.",
                "כתוב 3 דברים שאתה אסיר תודה עליהם.",
                "האזן לשיר אחד שאתה אוהב."
            ],
            'order': [
                "בחר משימה קטנה אחת והשלם אותה עכשיו.",
                "סדר פינה אחת בחדר שלך.",
                "כתוב רשימה של 3 דברים לעשות היום.",
                "קבע זמן קבוע למשימה שדחית.",
                "מחק 5 הודעות ישנות מהטלפון."
            ],
            'contribution': [
                "שלח הודעה חיובית למישהו שאכפת לך ממנו.",
                "הצע עזרה קטנה למישהו קרוב.",
                "הקשב למישהו במשך 5 דקות בלי להפריע.",
                "שתף משהו מועיל עם אחרים.",
                "תן מחמאה כנה למישהו."
            ],
            'exploration': [
                "נסה משהו חדש שלא עשית קודם.",
                "קרא מאמר על נושא שמעניין אותך.",
                "שאל שאלה שלא שאלת קודם.",
                "לך בדרך אחרת מהרגיל.",
                "התחל שיחה עם מישהו חדש."
            ]
        }
        
        # Recommended steps for each imbalance (Hebrew)
        recommended_steps = {
            'harm': "הצעד הבא: התאוששות. חזור לאיזון.",
            'avoidance': "הצעד הבא: ליצור מבנה וסדר.",
            'isolation': "הצעד הבא: לתרום לאחרים.",
            'rigidity': "הצעד הבא: להיפתח לחדש."
        }
        
        # Theory basis for each path
        theory_basis = {
            'harm': "נזק → התאוששות: כשיש נזק, הדרך חזרה היא דרך התאוששות.",
            'avoidance': "הימנעות → סדר: הימנעות מאוזנת על ידי יצירת מבנה.",
            'isolation': "בידוד → תרומה: מיקוד עצמי מאוזן על ידי תרומה לאחרים.",
            'rigidity': "נוקשות → חקירה: קיפאון מאוזן על ידי פתיחות וחקירה."
        }
        
        # Headlines for each imbalance
        headlines = {
            'harm': "יצאת מהמסלול.",
            'avoidance': "נסחפת להימנעות.",
            'isolation': "מיקוד עצמי גבוה.",
            'rigidity': "יש קיפאון.",
            'positive': "אתה על המסלול הנכון.",
            'new_user': "ברוך הבא למסע."
        }
        
        # Default response for new users
        if not user_history:
            import random
            action = random.choice(concrete_actions['recovery'])
            return DecisionPathResponse(
                success=True,
                user_id=user_id,
                current_state="new_user",
                drift_type=None,
                recommended_direction="recovery",
                headline=headlines['new_user'],
                recommended_step="התחל עם פעולת התאוששות.",
                concrete_action=action,
                theory_basis="התאוששות היא נקודת הפתיחה הטובה ביותר.",
                session_id=str(uuid.uuid4())[:8]
            )
        
        # Filter to last 7 days
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        recent_history = [h for h in user_history if h.get('timestamp', '') >= seven_days_ago]
        if not recent_history:
            recent_history = user_history[:10]  # Fallback to recent 10
        
        # Count value tags
        tag_counts = {}
        for h in recent_history:
            tag = h.get('value_tag')
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        total_actions = sum(tag_counts.values())
        
        # Detect imbalance type
        drift_type = None
        recommended_direction = None
        current_state = None
        
        harm_count = tag_counts.get('harm', 0)
        avoidance_count = tag_counts.get('avoidance', 0)
        order_count = tag_counts.get('order', 0)
        contribution_count = tag_counts.get('contribution', 0)
        recovery_count = tag_counts.get('recovery', 0)
        exploration_count = tag_counts.get('exploration', 0)
        
        negative_count = harm_count + avoidance_count
        
        # Priority 1: Recent harm
        last_tag = recent_history[0].get('value_tag') if recent_history else None
        
        if last_tag == 'harm' or harm_count >= 2:
            drift_type = 'harm'
            recommended_direction = 'recovery'
            current_state = 'drift_toward_harm'
        
        # Priority 2: Avoidance pattern
        elif last_tag == 'avoidance' or avoidance_count >= 3:
            drift_type = 'avoidance'
            recommended_direction = 'order'
            current_state = 'drift_toward_avoidance'
        
        # Priority 3: Isolation (no contribution, self-focused)
        elif total_actions >= 4 and contribution_count == 0:
            drift_type = 'isolation'
            recommended_direction = 'contribution'
            current_state = 'isolation_detected'
        
        # Priority 4: Rigidity (too much order, no exploration)
        elif order_count >= 4 and exploration_count == 0:
            drift_type = 'rigidity'
            recommended_direction = 'exploration'
            current_state = 'rigidity_detected'
        
        # Priority 5: Positive state - reinforce or suggest adjacent
        else:
            current_state = 'positive'
            # Find dominant positive direction
            positive_counts = {
                'recovery': recovery_count,
                'order': order_count,
                'contribution': contribution_count,
                'exploration': exploration_count
            }
            dominant = max(positive_counts, key=positive_counts.get)
            
            # Suggest adjacent direction for balance
            adjacent_map = {
                'recovery': 'order',
                'order': 'contribution',
                'contribution': 'exploration',
                'exploration': 'recovery'
            }
            recommended_direction = adjacent_map.get(dominant, 'recovery')
        
        # Select concrete action based on recommendation
        import random
        actions_list = concrete_actions.get(recommended_direction, concrete_actions['recovery'])
        
        # Use session-based seed for consistent action per session
        session_id = str(uuid.uuid4())[:8]
        random.seed(hash(user_id + session_id))
        concrete_action = random.choice(actions_list)
        random.seed()  # Reset seed
        
        # Build response
        if drift_type:
            headline = headlines.get(drift_type, headlines['new_user'])
            recommended_step = recommended_steps.get(drift_type, "המשך קדימה.")
            theory = theory_basis.get(drift_type, "")
        else:
            headline = headlines['positive']
            recommended_step = f"לאיזון מלא, נסה גם {direction_labels.get(recommended_direction, recommended_direction)}."
            theory = "איזון בין הכיוונים מחזק את ההתמצאות."
        
        return DecisionPathResponse(
            success=True,
            user_id=user_id,
            current_state=current_state,
            drift_type=drift_type,
            recommended_direction=recommended_direction,
            headline=headline,
            recommended_step=recommended_step,
            concrete_action=concrete_action,
            theory_basis=theory,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Get decision path error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/identity/{user_id}", response_model=OrientationIdentityResponse)
async def get_orientation_identity(user_id: str):
    """
    Orientation Identity Engine: Compute user's orientation identity based on:
    - dominant_direction
    - momentum
    - time_in_direction
    - avoidance_ratio
    - previous_dominant
    
    Identity types:
    - avoidance_loop: High avoidance pattern (warning state)
    - recovery_dominant: Focused on recovery
    - order_builder: Building structure and order
    - contribution_oriented: Contributing to others
    - exploration_driven: Exploring and growing
    - recovery_to_contribution: Transitioning from recovery to contribution
    - drifting_from_order: Was order-focused, now drifting
    """
    try:
        # Get user's session data
        user_session = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        user_history = user_session.get('history', []) if user_session else []
        
        # Direction labels in Hebrew
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה',
            'harm': 'נזק',
            'avoidance': 'הימנעות'
        }
        
        # Identity definitions
        identity_definitions = {
            'avoidance_loop': {
                'label': 'לולאת הימנעות',
                'description': 'נראה שאתה בדפוס של הימנעות. זה בסדר - זיהוי זה הצעד הראשון לשינוי.',
                'insight': 'הימנעות היא תגובה טבעית. הצעד הבא הוא ליצור מבנה קטן.'
            },
            'recovery_dominant': {
                'label': 'ממוקד בהתאוששות',
                'description': 'אתה בתהליך התאוששות פעיל. זה זמן חשוב לריפוי ואיזון.',
                'insight': 'התאוששות היא בסיס חיוני. כשתרגיש מוכן, נסה גם פעולות סדר.'
            },
            'order_builder': {
                'label': 'בונה סדר',
                'description': 'אתה יוצר מבנה וסדר בחיים שלך. זה סימן של התקדמות.',
                'insight': 'סדר מאפשר יציבות. השלב הבא יכול להיות תרומה לאחרים.'
            },
            'contribution_oriented': {
                'label': 'מכוון לתרומה',
                'description': 'אתה ממוקד בתרומה לאחרים. זה מעשיר אותך ואת הסביבה.',
                'insight': 'תרומה מחברת אותך לאחרים. זכור גם לדאוג לעצמך.'
            },
            'exploration_driven': {
                'label': 'מונע מחקירה',
                'description': 'אתה פתוח לחדש ולחקירה. זה מרחיב את האופקים שלך.',
                'insight': 'חקירה מביאה צמיחה. לפעמים כדאי גם לעצור וליצור סדר.'
            },
            'recovery_to_contribution': {
                'label': 'מעבר מהתאוששות לתרומה',
                'description': 'אתה עובר מהתאוששות לתרומה. זה מסע חיובי מאוד.',
                'insight': 'המעבר הזה מראה התקדמות משמעותית. המשך בקצב שלך.'
            },
            'drifting_from_order': {
                'label': 'סחף מסדר',
                'description': 'היית ממוקד בסדר אבל יש סחף. זה הזדמנות לבדוק מה השתנה.',
                'insight': 'סחף הוא טבעי. חזור ליצור מבנה קטן אחד.'
            },
            'balanced': {
                'label': 'מאוזן',
                'description': 'אתה מפזר את הפעולות שלך בין הכיוונים. זה מצב בריא.',
                'insight': 'איזון הוא מטרה טובה. המשך לשמור על מגוון.'
            },
            'new_user': {
                'label': 'מתחיל מסע',
                'description': 'ברוך הבא! אתה בתחילת המסע שלך.',
                'insight': 'כל מסע מתחיל בצעד אחד. התחל עם פעולת התאוששות.'
            }
        }
        
        # Default response for new users
        if not user_history:
            return OrientationIdentityResponse(
                success=True,
                user_id=user_id,
                identity_type='new_user',
                identity_label=identity_definitions['new_user']['label'],
                identity_description=identity_definitions['new_user']['description'],
                is_warning_state=False,
                insight=identity_definitions['new_user']['insight']
            )
        
        # Calculate time boundaries
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        fourteen_days_ago = (now - timedelta(days=14)).isoformat()
        twenty_one_days_ago = (now - timedelta(days=21)).isoformat()
        
        # Categorize history by time period
        recent_history = [h for h in user_history if h.get('timestamp', '') >= seven_days_ago]
        previous_history = [h for h in user_history if fourteen_days_ago <= h.get('timestamp', '') < seven_days_ago]
        older_history = [h for h in user_history if twenty_one_days_ago <= h.get('timestamp', '') < fourteen_days_ago]
        
        # If not enough recent data, use all history
        if len(recent_history) < 3:
            recent_history = user_history[:20]
        
        # Count directions for each period
        def count_directions(history_list):
            counts = {'recovery': 0, 'order': 0, 'contribution': 0, 'exploration': 0, 'harm': 0, 'avoidance': 0}
            for h in history_list:
                tag = h.get('value_tag')
                if tag and tag in counts:
                    counts[tag] += 1
            return counts
        
        recent_counts = count_directions(recent_history)
        previous_counts = count_directions(previous_history)
        
        # Calculate totals
        total_recent = sum(recent_counts.values())
        total_previous = sum(previous_counts.values())
        
        # Calculate avoidance ratio
        avoidance_count = recent_counts.get('avoidance', 0) + recent_counts.get('harm', 0)
        avoidance_ratio = round((avoidance_count / total_recent * 100) if total_recent > 0 else 0, 1)
        
        # Find dominant direction (recent)
        positive_directions = ['recovery', 'order', 'contribution', 'exploration']
        dominant_direction = None
        max_count = 0
        for direction in positive_directions:
            if recent_counts.get(direction, 0) > max_count:
                max_count = recent_counts.get(direction, 0)
                dominant_direction = direction
        
        # Find previous dominant direction
        previous_dominant = None
        prev_max = 0
        for direction in positive_directions:
            if previous_counts.get(direction, 0) > prev_max:
                prev_max = previous_counts.get(direction, 0)
                previous_dominant = direction
        
        # Calculate time in direction (approximate - based on streak)
        time_in_direction = 0
        if dominant_direction and dominant_direction == previous_dominant:
            time_in_direction = 14  # At least 2 weeks
            # Check older history too
            older_counts = count_directions(older_history)
            older_max_dir = max(positive_directions, key=lambda d: older_counts.get(d, 0))
            if older_max_dir == dominant_direction:
                time_in_direction = 21  # At least 3 weeks
        elif dominant_direction:
            time_in_direction = 7  # This week's dominant
        
        # Calculate momentum
        momentum = 'stable'
        if total_recent > 0 and total_previous > 0:
            recent_positive = sum(recent_counts.get(d, 0) for d in positive_directions)
            prev_positive = sum(previous_counts.get(d, 0) for d in positive_directions)
            recent_ratio = recent_positive / total_recent
            prev_ratio = prev_positive / total_previous
            
            if recent_ratio > prev_ratio + 0.15:
                momentum = 'stabilizing'
            elif recent_ratio < prev_ratio - 0.15:
                momentum = 'drifting'
            elif dominant_direction != previous_dominant and previous_dominant:
                momentum = 'shifting'
        
        # === IDENTITY COMPUTATION ===
        identity_type = 'balanced'
        is_warning_state = False
        
        # Priority 1: Avoidance Loop (warning state)
        if avoidance_ratio >= 40 or (recent_counts.get('avoidance', 0) >= 3 and total_recent >= 5):
            identity_type = 'avoidance_loop'
            is_warning_state = True
        
        # Priority 2: Drifting from Order (was order, now drifting)
        elif previous_dominant == 'order' and momentum == 'drifting':
            identity_type = 'drifting_from_order'
        
        # Priority 3: Transition (recovery → contribution)
        elif previous_dominant == 'recovery' and dominant_direction == 'contribution':
            identity_type = 'recovery_to_contribution'
        
        # Priority 4: Dominant direction identities
        elif dominant_direction:
            if dominant_direction == 'recovery' and max_count >= 3:
                identity_type = 'recovery_dominant'
            elif dominant_direction == 'order' and max_count >= 3:
                identity_type = 'order_builder'
            elif dominant_direction == 'contribution' and max_count >= 3:
                identity_type = 'contribution_oriented'
            elif dominant_direction == 'exploration' and max_count >= 3:
                identity_type = 'exploration_driven'
        
        # Priority 5: Check for balanced state
        if identity_type == 'balanced':
            # Check if user is well distributed
            active_directions = [d for d in positive_directions if recent_counts.get(d, 0) > 0]
            if len(active_directions) >= 3:
                identity_type = 'balanced'
            elif dominant_direction:
                # Default to dominant direction identity
                identity_map = {
                    'recovery': 'recovery_dominant',
                    'order': 'order_builder',
                    'contribution': 'contribution_oriented',
                    'exploration': 'exploration_driven'
                }
                identity_type = identity_map.get(dominant_direction, 'balanced')
        
        # Get identity details
        identity_info = identity_definitions.get(identity_type, identity_definitions['balanced'])
        
        # Save snapshot to database (for tracking over time)
        snapshot = {
            'user_id': user_id,
            'timestamp': now.isoformat(),
            'identity_type': identity_type,
            'dominant_direction': dominant_direction,
            'direction_counts': recent_counts,
            'avoidance_ratio': avoidance_ratio,
            'momentum': momentum,
            'time_in_direction': time_in_direction
        }
        
        # Upsert snapshot (one per day per user)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        await db.orientation_snapshots.update_one(
            {'user_id': user_id, 'date': today_start[:10]},
            {'$set': snapshot, '$setOnInsert': {'date': today_start[:10]}},
            upsert=True
        )
        
        return OrientationIdentityResponse(
            success=True,
            user_id=user_id,
            identity_type=identity_type,
            identity_label=identity_info['label'],
            identity_description=identity_info['description'],
            is_warning_state=is_warning_state,
            dominant_direction=dominant_direction,
            momentum=momentum,
            time_in_direction=time_in_direction,
            avoidance_ratio=avoidance_ratio,
            previous_dominant=previous_dominant,
            direction_counts=recent_counts,
            total_actions=total_recent,
            weeks_analyzed=1 if not previous_history else (2 if not older_history else 3),
            insight=identity_info['insight']
        )
        
    except Exception as e:
        logger.error(f"Get orientation identity error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/daily-question/{user_id}", response_model=DailyQuestionResponse)
async def get_daily_question(user_id: str):
    """
    Daily Orientation Question: Generate a question based on current orientation identity.
    The question aims to guide the user toward balance.
    Also calculates and returns streak information.
    """
    try:
        # First, get the user's current identity
        identity_response = await get_orientation_identity(user_id)
        current_identity = identity_response.identity_type
        dominant_direction = identity_response.dominant_direction
        
        # Check if user already answered today
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
        
        # Calculate streak from answered questions
        answered_questions = await db.daily_questions.find({
            'user_id': user_id,
            'answered': True
        }, {'_id': 0, 'date': 1}).sort('date', -1).to_list(100)
        
        # Calculate current streak
        current_streak = 0
        longest_streak = 0
        
        if answered_questions:
            # Get unique answered dates
            answered_dates = sorted(set(q.get('date') for q in answered_questions if q.get('date')), reverse=True)
            
            # Count consecutive days
            streak = 0
            expected_date = today_start
            
            # If today not answered yet, start from yesterday
            if answered_dates and answered_dates[0] != today_start:
                expected_date = yesterday_start
            
            for i, date in enumerate(answered_dates):
                check_date = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
                
                # Adjust if today is not answered
                if answered_dates[0] != today_start:
                    check_date = (now - timedelta(days=i+1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
                
                if date == check_date:
                    streak += 1
                else:
                    break
            
            current_streak = streak
            
            # Calculate longest streak
            temp_streak = 1
            for i in range(1, len(answered_dates)):
                prev_date = datetime.strptime(answered_dates[i-1], '%Y-%m-%d')
                curr_date = datetime.strptime(answered_dates[i], '%Y-%m-%d')
                if (prev_date - curr_date).days == 1:
                    temp_streak += 1
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
            longest_streak = max(longest_streak, temp_streak, current_streak)
        
        # Check if already answered today
        existing_answer = await db.daily_questions.find_one({
            'user_id': user_id,
            'date': today_start
        })
        
        if existing_answer:
            return DailyQuestionResponse(
                success=True,
                user_id=user_id,
                identity=current_identity,
                question_he=existing_answer.get('question_he'),
                suggested_direction=existing_answer.get('suggested_direction'),
                question_id=existing_answer.get('question_id'),
                already_answered_today=existing_answer.get('answered', False),
                streak=current_streak,
                longest_streak=longest_streak
            )
        
        # Questions based on identity type - each question aims for a balancing direction
        identity_questions = {
            'avoidance_loop': {
                'questions': [
                    "מה הדבר הקטן ביותר שאתה יכול לעשות עכשיו כדי ליצור סדר?",
                    "איזו משימה קטנה אתה יכול להשלים ב-5 דקות הקרובות?",
                    "מה הצעד הראשון שתוכל לעשות היום לקראת משהו שדחית?"
                ],
                'suggested_direction': 'order'
            },
            'recovery_dominant': {
                'questions': [
                    "מה הדבר הקטן שאתה יכול לעשות היום עבור מישהו אחר?",
                    "איך תוכל לתרום למישהו קרוב אליך היום?",
                    "מה תוכל לשתף עם אחרים מהניסיון שלך?"
                ],
                'suggested_direction': 'contribution'
            },
            'order_builder': {
                'questions': [
                    "מה משהו חדש שתוכל לנסות היום?",
                    "איזו שאלה חדשה תוכל לשאול היום?",
                    "מה הדבר שתמיד רצית לחקור אבל לא הספקת?"
                ],
                'suggested_direction': 'exploration'
            },
            'contribution_oriented': {
                'questions': [
                    "מה תעשה היום כדי לדאוג לעצמך?",
                    "איזו הפסקה קטנה מגיעה לך היום?",
                    "מה יעזור לך להתאושש ולהטען מחדש?"
                ],
                'suggested_direction': 'recovery'
            },
            'exploration_driven': {
                'questions': [
                    "איזו משימה תוכל לסיים היום כדי ליצור סדר?",
                    "מה הדבר שצריך ארגון בחיים שלך עכשיו?",
                    "איך תוכל ליצור מבנה קטן שיתמוך בך?"
                ],
                'suggested_direction': 'order'
            },
            'recovery_to_contribution': {
                'questions': [
                    "מה הצעד הבא שתעשה היום בכיוון של תרומה?",
                    "איך תוכל להמשיך את המומנטום החיובי שלך?",
                    "מה תוכל לעשות היום שירחיב את המעגל שלך?"
                ],
                'suggested_direction': 'contribution'
            },
            'drifting_from_order': {
                'questions': [
                    "מה המבנה הקטן שתוכל ליצור מחדש היום?",
                    "איזו הרגל טובה תוכל לחזור אליה?",
                    "מה יעזור לך להרגיש יותר מאורגן?"
                ],
                'suggested_direction': 'order'
            },
            'balanced': {
                'questions': [
                    "מה הכיוון שהכי מושך אותך היום?",
                    "באיזה תחום תרצה להתמקד היום?",
                    "מה יהפוך את היום הזה למשמעותי עבורך?"
                ],
                'suggested_direction': dominant_direction or 'recovery'
            },
            'new_user': {
                'questions': [
                    "מה הדבר הראשון שתעשה היום לטובת עצמך?",
                    "איך תרצה להתחיל את המסע שלך?",
                    "מה יגרום לך להרגיש טוב היום?"
                ],
                'suggested_direction': 'recovery'
            }
        }
        
        # Get questions for current identity (fallback to balanced)
        identity_data = identity_questions.get(current_identity, identity_questions['balanced'])
        questions = identity_data['questions']
        suggested_direction = identity_data['suggested_direction']

        # === BASE-INFLUENCED QUESTION OVERRIDE ===
        # If user chose a daily base, override with base-specific question
        today_base = await db.daily_bases.find_one(
            {"user_id": user_id, "date": today_start}, {"_id": 0, "base": 1}
        )
        if today_base and today_base.get("base"):
            base = today_base["base"]
            base_questions = {
                'body': {
                    'questions': [
                        "עשה פעולה פיזית קטנה שמסדרת משהו סביבך.",
                        "הזז את הגוף היום — אפילו הליכה קצרה.",
                        "סדר פינה אחת בסביבה שלך.",
                        "עשה משהו מעשי שדחית."
                    ],
                    'suggested_direction': 'order'
                },
                'heart': {
                    'questions': [
                        "שלח מילה טובה למישהו שלא ציפה לזה.",
                        "הקשב למישהו היום — באמת הקשב.",
                        "עשה משהו קטן עבור מישהו קרוב.",
                        "תן לעצמך רגע של חמלה היום."
                    ],
                    'suggested_direction': 'contribution'
                },
                'head': {
                    'questions': [
                        "מצא דבר אחד חדש שלא שמת לב אליו קודם.",
                        "ארגן רעיון אחד שמסתובב לך בראש.",
                        "למד משהו קטן שלא ידעת.",
                        "קבל החלטה אחת שדחית."
                    ],
                    'suggested_direction': 'exploration'
                }
            }
            if base in base_questions:
                questions = base_questions[base]['questions']
                suggested_direction = base_questions[base]['suggested_direction']
        
        # Select a question (use day-based seed for consistency within a day)
        import random
        day_seed = hash(user_id + today_start)
        random.seed(day_seed)
        selected_question = random.choice(questions)
        random.seed()  # Reset seed
        
        # Generate question ID
        question_id = str(uuid.uuid4())[:8]
        
        # Save to database
        question_doc = {
            'user_id': user_id,
            'date': today_start,
            'question_id': question_id,
            'question_he': selected_question,
            'identity': current_identity,
            'suggested_direction': suggested_direction,
            'created_at': now.isoformat(),
            'answered': False
        }
        
        await db.daily_questions.insert_one(question_doc)
        
        return DailyQuestionResponse(
            success=True,
            user_id=user_id,
            identity=current_identity,
            question_he=selected_question,
            suggested_direction=suggested_direction,
            question_id=question_id,
            already_answered_today=False,
            streak=current_streak,
            longest_streak=longest_streak
        )
        
    except Exception as e:
        logger.error(f"Get daily question error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class DailyQuestionAnswerRequest(BaseModel):
    question_id: str
    response_text: Optional[str] = None
    action_taken: bool = True


@api_router.post("/orientation/daily-answer/{user_id}")
async def submit_daily_answer(user_id: str, request: DailyQuestionAnswerRequest):
    """
    Submit answer to daily orientation question.
    Records the action and updates the user's state.
    """
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
        
        # Find the question
        question = await db.daily_questions.find_one({
            'user_id': user_id,
            'question_id': request.question_id
        })
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Calculate streak from answered questions
        answered_questions = await db.daily_questions.find({
            'user_id': user_id,
            'answered': True
        }, {'_id': 0, 'date': 1}).sort('date', -1).to_list(100)
        
        streak = 0
        if answered_questions:
            answered_dates = sorted(set(q.get('date') for q in answered_questions if q.get('date')), reverse=True)
            expected_date = today_start
            if answered_dates and answered_dates[0] != today_start:
                expected_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
            for i, date in enumerate(answered_dates):
                check_date = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
                if answered_dates[0] != today_start:
                    check_date = (now - timedelta(days=i+1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:10]
                if date == check_date:
                    streak += 1
                else:
                    break
        # Add 1 to streak if this is a new answer (streak will include today after this submission)
        if question.get('answered') != True:
            streak += 1
        
        suggested_direction = question.get('suggested_direction', 'recovery')
        
        # Mark question as answered
        await db.daily_questions.update_one(
            {'user_id': user_id, 'question_id': request.question_id},
            {
                '$set': {
                    'answered': True,
                    'answered_at': now.isoformat(),
                    'response_text': request.response_text,
                    'action_taken': request.action_taken
                }
            }
        )
        
        # If action was taken, record it in user's history
        if request.action_taken:
            # Get user's session
            user_session = await db.philos_sessions.find_one(
                {'user_id': user_id},
                {'_id': 0}
            )
            
            if user_session:
                # Add to history
                new_action = {
                    'id': str(uuid.uuid4()),
                    'action_text': f"השלמתי את השאלה היומית: {question.get('question_he', '')}",
                    'value_tag': suggested_direction,
                    'timestamp': now.isoformat(),
                    'source': 'daily_question',
                    'question_id': request.question_id
                }
                
                history = user_session.get('history', [])
                history.insert(0, new_action)
                
                # Update global stats
                global_stats = user_session.get('global_stats', {})
                global_stats[suggested_direction] = global_stats.get(suggested_direction, 0) + 1
                
                await db.philos_sessions.update_one(
                    {'user_id': user_id},
                    {'$set': {'history': history, 'global_stats': global_stats}}
                )
        
        # Calculate impact on field (percentage of today's actions)
        impact_percent = 0.0
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        if request.action_taken:
            # Get today's field data
            field_data = await get_field_today()
            total_today = field_data.total_actions + 1  # +1 for this action
            if total_today > 0:
                impact_percent = round((1 / total_today) * 100, 2)
        
        impact_message = None
        if request.action_taken and suggested_direction in direction_labels:
            impact_message = f"הפעולה שלך חיזקה היום את שדה ה{direction_labels[suggested_direction]}"
        
        # Increment mission participants if direction matches today's mission
        mission_contributed = False
        if request.action_taken:
            mission = await _get_or_create_mission_today()
            if mission.get("direction") == suggested_direction:
                today_str = now.strftime("%Y-%m-%d")
                await db.daily_missions.update_one(
                    {"date": today_str},
                    {"$inc": {"participants": 1}}
                )
                mission_contributed = True

        # Compute identity growth data for reward feedback
        niche_info = None
        identity_link = None
        if request.action_taken:
            session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "global_stats": 1})
            stats = session.get("global_stats", {}) if session else {}
            total_all = sum(stats.get(d, 0) for d in ['contribution', 'recovery', 'order', 'exploration'])
            # Check niche progress
            for nid, ndef in VALUE_NICHES.items():
                nd = ndef.get('dominant_direction')
                if nd and nd == suggested_direction:
                    current = stats.get(nd, 0)
                    threshold = ndef.get('threshold', 35)
                    remaining = max(0, threshold - current)
                    if remaining > 0:
                        niche_info = {'niche_he': ndef['label_he'], 'remaining': remaining, 'progress': min(round((current / threshold) * 100), 100)}
                    break
            identity_link = f"/profile/{user_id}"

        return {
            'success': True,
            'message': 'Answer recorded',
            'action_recorded': request.action_taken,
            'direction': suggested_direction,
            'impact_percent': impact_percent,
            'impact_message': impact_message,
            'impact_score': round(2.5 + streak * 0.5, 1),
            'mission_contributed': mission_contributed,
            'streak': streak,
            'niche_info': niche_info,
            'identity_link': identity_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit daily answer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/user/{user_id}", response_model=UserOrientationResponse)
async def get_user_orientation(user_id: str):
    """
    Get user's position relative to the collective field.
    Includes drift detection and momentum calculation.
    """
    try:
        # Get user's session data
        user_session = await db.philos_sessions.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        user_history = user_session.get('history', []) if user_session else []
        
        if not user_history:
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
        
        # Calculate user position based on recent decisions (last 7 days)
        direction_positions = {
            'recovery': (30, 65),
            'order': (30, 25),
            'contribution': (70, 25),
            'exploration': (70, 65),
            'harm': (15, 85),
            'avoidance': (50, 90)
        }
        
        # Filter to last 7 days
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        recent_history = [h for h in user_history if h.get('timestamp', '') >= seven_days_ago]
        if not recent_history:
            recent_history = user_history[:20]  # Fallback to most recent 20
        
        # Weight recent decisions more
        weighted_x = 0
        weighted_y = 0
        total_weight = 0
        
        for idx, h in enumerate(recent_history[:20]):
            tag = h.get('value_tag')
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
        
        # Drift detection based on recent tags
        drift_pattern = None
        recent_tags = [h.get('value_tag') for h in recent_history[:10] if h.get('value_tag')]
        
        harm_count = recent_tags.count('harm')
        avoidance_count = recent_tags.count('avoidance')
        order_count = recent_tags.count('order')
        contribution_count = recent_tags.count('contribution')
        recovery_count = recent_tags.count('recovery')
        exploration_count = recent_tags.count('exploration')
        
        if harm_count + avoidance_count >= 4:
            drift_pattern = "drift_toward_chaos"
        elif order_count >= 5 and contribution_count == 0 and exploration_count == 0:
            drift_pattern = "drift_toward_isolation"
        elif order_count >= 4:
            drift_pattern = "stabilization_toward_order"
        elif contribution_count >= 3:
            drift_pattern = "movement_toward_contribution"
        elif recovery_count >= 3:
            drift_pattern = "recovery_mode"
        
        # Calculate momentum
        momentum = "stable"
        momentum_direction = None
        
        if len(recent_tags) >= 3:
            positive_directions = ['recovery', 'order', 'contribution', 'exploration']
            recent_positive = sum(1 for t in recent_tags if t in positive_directions)
            positive_ratio = recent_positive / len(recent_tags)
            
            if positive_ratio > 0.7:
                momentum = "stabilizing"
                # Find which positive direction is strongest
                pos_counts = {d: recent_tags.count(d) for d in positive_directions}
                momentum_direction = max(pos_counts, key=pos_counts.get)
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
        
        # Position insight based on alignment
        if alignment_score > 70:
            insights.append("אתה מיושר היטב עם השדה הקולקטיבי.")
        elif alignment_score > 50:
            insights.append("המיקום שלך קרוב למרכז השדה הקולקטיבי.")
        elif alignment_score < 30:
            insights.append("אתה רחוק ממרכז השדה הקולקטיבי.")
        else:
            insights.append("יש מרחק בין המיקום שלך לבין מרכז השדה הקולקטיבי.")
        
        # Drift insight
        if drift_pattern == "drift_toward_chaos":
            insights.append("נראה סחף לכיוון כאוס. מומלץ לשקול פעולת התאוששות או סדר.")
        elif drift_pattern == "drift_toward_isolation":
            insights.append("יש נטייה לבידוד. כדאי לשקול פעולת תרומה.")
        elif drift_pattern == "stabilization_toward_order":
            insights.append("אתה מתייצב לכיוון סדר.")
        elif drift_pattern == "movement_toward_contribution":
            insights.append("יש תנועה חיובית לכיוון תרומה.")
        elif drift_pattern == "recovery_mode":
            insights.append("אתה במצב התאוששות.")
        
        # Momentum insight
        if momentum == "stabilizing" and momentum_direction:
            insights.append(f"המומנטום שלך חיובי לכיוון {direction_labels.get(momentum_direction, momentum_direction)}.")
        elif momentum == "drifting":
            insights.append("המומנטום מראה סחף מהאיזון.")
        
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


@api_router.get("/orientation/weekly-insight/{user_id}", response_model=WeeklyInsightResponse)
async def get_weekly_insight(user_id: str):
    """
    Weekly Orientation Insight: Aggregate last 7 days of user actions.
    Returns distribution and Hebrew insight about the week.
    """
    try:
        # Get user's session data
        user_session = await db.philos_sessions.find_one(
            {'user_id': user_id},
            {'_id': 0}
        )
        
        user_history = user_session.get('history', []) if user_session else []
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['contribution', 'recovery', 'order', 'exploration']
        
        # Filter to last 7 days
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        recent_history = [h for h in user_history if h.get('timestamp', '') >= seven_days_ago]
        
        # Count directions
        direction_counts = {d: 0 for d in positive_directions}
        for h in recent_history:
            tag = h.get('value_tag')
            if tag in direction_counts:
                direction_counts[tag] += 1
        
        total_actions = sum(direction_counts.values())
        
        # Calculate percentages
        distribution_percent = {}
        for direction, count in direction_counts.items():
            distribution_percent[direction] = round((count / total_actions * 100) if total_actions > 0 else 0, 1)
        
        # Find dominant direction
        dominant_direction = None
        max_count = 0
        for direction, count in direction_counts.items():
            if count > max_count:
                max_count = count
                dominant_direction = direction
        
        # Generate insight
        insight_he = None
        trend = 'stable'
        
        if total_actions == 0:
            insight_he = "אין מספיק נתונים השבוע. התחל עם פעולה אחת."
        elif total_actions < 3:
            insight_he = "שבוע שקט. כדאי להוסיף עוד פעולות."
        else:
            # Check for balance
            active_directions = [d for d in positive_directions if direction_counts.get(d, 0) > 0]
            
            if len(active_directions) >= 3:
                insight_he = "שבוע מאוזן! פעלת במגוון כיוונים."
                trend = 'improving'
            elif dominant_direction:
                label = direction_labels.get(dominant_direction, dominant_direction)
                pct = distribution_percent.get(dominant_direction, 0)
                
                if pct > 60:
                    insight_he = f"השבוע התמקדת מאוד ב{label}. כדאי לשקול גיוון."
                elif pct > 40:
                    insight_he = f"השבוע עברת מהתאוששות לפעולה. כיוון מוביל: {label}."
                    trend = 'improving'
                else:
                    insight_he = f"הכיוון המוביל שלך השבוע: {label}."
        
        return WeeklyInsightResponse(
            success=True,
            user_id=user_id,
            distribution=direction_counts,
            distribution_percent=distribution_percent,
            total_actions=total_actions,
            dominant_direction=dominant_direction,
            insight_he=insight_he,
            trend=trend
        )
        
    except Exception as e:
        logger.error(f"Get weekly insight error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/share/{user_id}", response_model=ShareCardResponse)
async def get_share_card(user_id: str):
    """
    Orientation Share Card: Get data for shareable orientation card.
    """
    try:
        # Get user's identity
        identity = await get_orientation_identity(user_id)
        
        # Get user's streak
        daily_question = await get_daily_question(user_id)
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        orientation = identity.dominant_direction
        orientation_label = direction_labels.get(orientation, 'איזון')
        
        message_he = f"היום אני באוריינטציית {orientation_label}"
        
        # Calculate compass position
        direction_positions = {
            'recovery': {'x': 30, 'y': 65},
            'order': {'x': 30, 'y': 25},
            'contribution': {'x': 70, 'y': 25},
            'exploration': {'x': 70, 'y': 65}
        }
        compass_position = direction_positions.get(orientation, {'x': 50, 'y': 50})
        
        return ShareCardResponse(
            success=True,
            user_id=user_id,
            orientation=orientation_label,
            message_he=message_he,
            streak=daily_question.streak,
            compass_position=compass_position
        )
        
    except Exception as e:
        logger.error(f"Get share card error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/index", response_model=OrientationIndexResponse)
async def get_orientation_index():
    """
    Orientation Index: Public page data showing global orientation distribution.
    Compares today vs yesterday.
    """
    try:
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        positive_directions = ['contribution', 'recovery', 'order', 'exploration']
        
        # Get all sessions
        all_sessions = await db.philos_sessions.find({}, {"_id": 0}).to_list(1000)
        
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Count today and yesterday
        today_counts = {d: 0 for d in positive_directions}
        yesterday_counts = {d: 0 for d in positive_directions}
        active_users = set()
        
        for session in all_sessions:
            user_id = session.get('user_id')
            history = session.get('history', [])
            
            for h in history:
                ts = h.get('timestamp', '')
                tag = h.get('value_tag')
                
                if tag in positive_directions:
                    if ts >= today_start:
                        today_counts[tag] += 1
                        if user_id:
                            active_users.add(user_id)
                    elif ts >= yesterday_start:
                        yesterday_counts[tag] += 1
        
        total_today = sum(today_counts.values())
        total_yesterday = sum(yesterday_counts.values())
        
        # Calculate percentages
        distribution = {}
        for direction in positive_directions:
            distribution[direction] = round((today_counts[direction] / total_today * 100) if total_today > 0 else 25, 1)
        
        # Find dominants
        dominant_today = max(positive_directions, key=lambda d: today_counts.get(d, 0)) if total_today > 0 else None
        dominant_yesterday = max(positive_directions, key=lambda d: yesterday_counts.get(d, 0)) if total_yesterday > 0 else None
        
        # Determine change
        direction_change = None
        if dominant_today and dominant_yesterday:
            if dominant_today == dominant_yesterday:
                direction_change = 'same'
            else:
                direction_change = f'shifted_to_{dominant_today}'
        
        # Generate headline
        headline_he = None
        if dominant_today:
            label = direction_labels.get(dominant_today, dominant_today)
            headline_he = f"מדד ההתמצאות היום: {label} מובילה"
            
            if direction_change and direction_change != 'same':
                yesterday_label = direction_labels.get(dominant_yesterday, dominant_yesterday)
                headline_he += f" (אתמול: {yesterday_label})"
        else:
            headline_he = "מדד ההתמצאות היום: מאוזן"
        
        return OrientationIndexResponse(
            success=True,
            distribution=distribution,
            dominant_direction=dominant_today,
            total_users=len(active_users),
            total_actions_today=total_today,
            yesterday_dominant=dominant_yesterday,
            direction_change=direction_change,
            headline_he=headline_he
        )
        
    except Exception as e:
        logger.error(f"Get orientation index error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# ==================== FIELD MISSION SYSTEM ====================

MISSION_DESCRIPTIONS = {
    'contribution': {
        'mission_he': 'משימת היום: תרומה',
        'description_he': 'עשה פעולה קטנה שתעזור למישהו אחר היום'
    },
    'recovery': {
        'mission_he': 'משימת היום: התאוששות',
        'description_he': 'קח רגע של מנוחה והטענה עצמית היום'
    },
    'order': {
        'mission_he': 'משימת היום: סדר',
        'description_he': 'ארגן דבר אחד קטן בסביבה שלך היום'
    },
    'exploration': {
        'mission_he': 'משימת היום: חקירה',
        'description_he': 'נסה משהו חדש או למד דבר אחד חדש היום'
    }
}

MISSION_TARGET = 5000


async def _get_or_create_mission_today():
    """Get today's mission or create one based on the day of week."""
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    mission = await db.daily_missions.find_one({"date": today_str}, {"_id": 0})
    if mission:
        return mission

    # Rotate direction daily based on day-of-year
    directions = ['contribution', 'recovery', 'order', 'exploration']
    day_index = now.timetuple().tm_yday % len(directions)
    direction = directions[day_index]

    mission = {
        "date": today_str,
        "direction": direction,
        "participants": 0,
        "target": MISSION_TARGET
    }
    await db.daily_missions.insert_one({**mission})
    return mission


@api_router.get("/orientation/mission-today")
async def get_mission_today():
    """Field Mission: today's community challenge."""
    try:
        mission = await _get_or_create_mission_today()
        direction = mission["direction"]
        meta = MISSION_DESCRIPTIONS.get(direction, MISSION_DESCRIPTIONS['contribution'])
        participants = mission.get("participants", 0)
        target = mission.get("target", MISSION_TARGET)
        progress = min(round((participants / target) * 100) if target > 0 else 0, 100)

        return {
            "success": True,
            "direction": direction,
            "mission_he": meta["mission_he"],
            "description_he": meta["description_he"],
            "participants": participants,
            "target": target,
            "progress_percent": progress
        }
    except Exception as e:
        logger.error(f"Get mission today error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/invite-report")
async def get_invite_report():
    """Invite tracking report: sent, opened, accepted, conversion %."""
    try:
        all_invites = await db.invites.find({}, {"_id": 0, "code": 1, "use_count": 1, "opened_count": 1, "created_at": 1}).to_list(10000)

        total_sent = len(all_invites)
        total_opened = sum(1 for inv in all_invites if inv.get("opened_count", 0) > 0)
        total_accepted = sum(inv.get("use_count", 0) for inv in all_invites)
        total_opens = sum(inv.get("opened_count", 0) for inv in all_invites)

        open_rate = round((total_opened / total_sent) * 100, 1) if total_sent > 0 else 0
        accept_rate = min(round((total_accepted / total_opened) * 100, 1), 100) if total_opened > 0 else 0
        overall_conversion = round((total_accepted / total_sent) * 100, 1) if total_sent > 0 else 0

        return {
            "success": True,
            "invites_sent": total_sent,
            "invites_opened": total_opened,
            "invites_accepted": total_accepted,
            "total_opens": total_opens,
            "open_rate": open_rate,
            "accept_rate": accept_rate,
            "overall_conversion": overall_conversion
        }
    except Exception as e:
        logger.error(f"Get invite report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMMUNITY LAYER ENDPOINTS ====================

@api_router.get("/orientation/active-users")
async def get_active_users():
    """Active Users Indicator: today's active users + users on streak."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "user_id": 1, "history": 1}).to_list(10000)

        active_today = set()
        for s in all_sessions:
            uid = s.get("user_id")
            for h in s.get("history", []):
                if h.get("timestamp", "") >= today_start:
                    active_today.add(uid)
                    break

        # Count users on streak (answered daily question on consecutive days)
        answered = await db.daily_questions.find(
            {"answered": True},
            {"_id": 0, "user_id": 1, "date": 1}
        ).to_list(50000)

        user_dates = {}
        for q in answered:
            uid = q.get("user_id")
            d = q.get("date")
            if uid and d:
                user_dates.setdefault(uid, set()).add(d)

        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        streak_users = sum(
            1 for dates in user_dates.values()
            if today_str in dates and yesterday_str in dates
        )

        return {
            "success": True,
            "active_users_today": len(active_today),
            "active_streak_users": streak_users
        }
    except Exception as e:
        logger.error(f"Get active users error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/relative-score/{user_id}")
async def get_relative_score(user_id: str):
    """Relative Orientation Score: user's percentile compared to all users today."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "user_id": 1, "history": 1}).to_list(10000)

        positive = ['contribution', 'recovery', 'order', 'exploration']
        user_counts = {}
        user_direction = {}

        for s in all_sessions:
            uid = s.get("user_id")
            count = 0
            dir_counts = {d: 0 for d in positive}
            for h in s.get("history", []):
                if h.get("timestamp", "") >= today_start and h.get("value_tag") in positive:
                    count += 1
                    dir_counts[h["value_tag"]] += 1
            user_counts[uid] = count
            if count > 0:
                user_direction[uid] = max(dir_counts, key=dir_counts.get)

        my_count = user_counts.get(user_id, 0)
        all_counts = sorted(user_counts.values())
        total = len(all_counts)

        if total <= 1:
            percentile = 50
        else:
            below = sum(1 for c in all_counts if c < my_count)
            percentile = round((below / total) * 100)

        direction = user_direction.get(user_id, "recovery")

        return {
            "success": True,
            "percentile": percentile,
            "direction": direction,
            "user_actions_today": my_count
        }
    except Exception as e:
        logger.error(f"Get relative score error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/circles")
async def get_orientation_circles():
    """Orientation Circles: user counts per direction (all-time)."""
    try:
        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "global_stats": 1, "user_id": 1}).to_list(10000)

        positive = ['contribution', 'recovery', 'order', 'exploration']
        direction_users = {d: 0 for d in positive}

        for s in all_sessions:
            stats = s.get("global_stats", {})
            for d in positive:
                if stats.get(d, 0) > 0:
                    direction_users[d] += 1

        return {
            "success": True,
            "contribution": direction_users["contribution"],
            "recovery": direction_users["recovery"],
            "order": direction_users["order"],
            "exploration": direction_users["exploration"]
        }
    except Exception as e:
        logger.error(f"Get orientation circles error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/streaks")
async def get_community_streaks():
    """Community Streak Overview: users on streak + longest streak today."""
    try:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        answered = await db.daily_questions.find(
            {"answered": True},
            {"_id": 0, "user_id": 1, "date": 1}
        ).to_list(50000)

        user_dates = {}
        for q in answered:
            uid = q.get("user_id")
            d = q.get("date")
            if uid and d:
                user_dates.setdefault(uid, []).append(d)

        users_on_streak = 0
        longest_streak_today = 0

        for uid, dates in user_dates.items():
            sorted_dates = sorted(set(dates), reverse=True)
            if not sorted_dates or sorted_dates[0] < yesterday_str:
                continue

            streak = 1
            for i in range(1, len(sorted_dates)):
                prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

            if streak >= 2:
                users_on_streak += 1
            longest_streak_today = max(longest_streak_today, streak)

        return {
            "success": True,
            "users_on_streak": users_on_streak,
            "longest_streak_today": longest_streak_today
        }
    except Exception as e:
        logger.error(f"Get community streaks error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/metrics-today")
async def get_metrics_today():
    """Admin metrics dashboard: core engagement KPIs."""
    try:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "user_id": 1, "history": 1}).to_list(10000)
        active_today = set()
        for s in all_sessions:
            uid = s.get("user_id")
            for h in s.get("history", []):
                if h.get("timestamp", "") >= today_start:
                    active_today.add(uid)
                    break
        active_users_today = len(active_today)

        questions_today = await db.daily_questions.find(
            {"date": today_str}, {"_id": 0, "user_id": 1, "answered": 1}
        ).to_list(50000)
        total_questions = len(questions_today)
        answered_questions = sum(1 for q in questions_today if q.get("answered"))
        daily_question_completion_rate = round((answered_questions / total_questions) * 100, 1) if total_questions > 0 else 0

        all_questions = await db.daily_questions.find({}, {"_id": 0, "user_id": 1, "date": 1}).to_list(50000)
        user_dates = {}
        for q in all_questions:
            uid = q.get("user_id")
            d = q.get("date")
            if uid and d:
                user_dates.setdefault(uid, set()).add(d)

        retained = 0
        eligible = 0
        for uid, dates in user_dates.items():
            sorted_d = sorted(dates)
            if sorted_d:
                first = sorted_d[0]
                next_day = (datetime.strptime(first, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                if next_day <= today_str:
                    eligible += 1
                    if next_day in dates:
                        retained += 1
        day2_retention = round((retained / eligible) * 100, 1) if eligible > 0 else 0

        mission = await db.daily_missions.find_one({"date": today_str}, {"_id": 0})
        mission_participants = mission.get("participants", 0) if mission else 0
        mission_participation_rate = round((mission_participants / active_users_today) * 100, 1) if active_users_today > 0 else 0

        answered_all = await db.daily_questions.find(
            {"answered": True}, {"_id": 0, "user_id": 1, "date": 1}
        ).to_list(50000)
        streak_user_dates = {}
        for q in answered_all:
            uid = q.get("user_id")
            d = q.get("date")
            if uid and d:
                streak_user_dates.setdefault(uid, set()).add(d)

        streaks = []
        for uid, dates in streak_user_dates.items():
            sorted_dates = sorted(dates, reverse=True)
            if not sorted_dates or sorted_dates[0] < yesterday_str:
                continue
            streak = 1
            for i in range(1, len(sorted_dates)):
                prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break
            if streak >= 1:
                streaks.append(streak)
        avg_streak = round(sum(streaks) / len(streaks), 1) if streaks else 0

        # --- invite_conversions ---
        all_invites = await db.invites.find({}, {"_id": 0, "use_count": 1}).to_list(10000)
        total_invites_sent = len(all_invites)
        total_accepted = sum(inv.get("use_count", 0) for inv in all_invites)
        invite_conversion = round((total_accepted / total_invites_sent) * 100, 1) if total_invites_sent > 0 else 0

        return {
            "success": True,
            "active_users_today": active_users_today,
            "daily_question_completion_rate": daily_question_completion_rate,
            "day2_retention": day2_retention,
            "mission_participation_rate": mission_participation_rate,
            "avg_streak": avg_streak,
            "invite_conversions": invite_conversion
        }
    except Exception as e:
        logger.error(f"Get metrics today error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/feed")
async def get_orientation_feed():
    """Real-time anonymous activity feed (real + demo events)."""
    try:
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(hours=2)).isoformat()

        # Real user actions
        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "history": 1}).to_list(10000)
        positive = ['contribution', 'recovery', 'order', 'exploration']
        recent_actions = []
        for s in all_sessions:
            for h in s.get("history", []):
                ts = h.get("timestamp", "")
                vt = h.get("value_tag", "")
                if ts >= cutoff and vt in positive:
                    recent_actions.append({"direction": vt, "timestamp": ts, "demo": False, "location": None})

        # Demo events
        demo_events = await db.demo_events.find(
            {"timestamp": {"$gte": cutoff}},
            {"_id": 0, "direction": 1, "timestamp": 1, "country": 1, "country_code": 1}
        ).to_list(500)
        for de in demo_events:
            recent_actions.append({
                "direction": de["direction"],
                "timestamp": de["timestamp"],
                "demo": True,
                "location": de.get("country"),
                "country_code": de.get("country_code")
            })

        recent_actions.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_actions = recent_actions[:40]

        feed = []
        for a in recent_actions:
            try:
                action_time = datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00"))
                diff = now - action_time
                minutes = int(diff.total_seconds() / 60)
                if minutes < 1:
                    time_str = "עכשיו"
                elif minutes < 60:
                    time_str = f"{minutes}ד"
                else:
                    hours = minutes // 60
                    time_str = f"{hours}ש"
            except Exception:
                time_str = ""
            item = {
                "type": "demo_action" if a["demo"] else "action",
                "direction": a["direction"],
                "time": time_str
            }
            if a.get("location"):
                item["location"] = a["location"]
            if a.get("country_code"):
                item["country_code"] = a["country_code"]
            feed.append(item)

        return {"success": True, "feed": feed}
    except Exception as e:
        logger.error(f"Get orientation feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/create-invite/{user_id}")
async def create_invite(user_id: str):
    """Create an invite code for a user."""
    try:
        import uuid
        code = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        await db.invites.insert_one({
            "code": code,
            "inviter_id": user_id,
            "created_at": now.isoformat(),
            "used_by": [],
            "use_count": 0
        })

        return {
            "success": True,
            "code": code,
            "invite_url": f"/invite/{code}"
        }
    except Exception as e:
        logger.error(f"Create invite error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/invite/{code}")
async def get_invite(code: str):
    """Validate and retrieve invite details. Also tracks 'opened' event."""
    try:
        invite = await db.invites.find_one({"code": code}, {"_id": 0})
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")

        # Track opened event
        await db.invites.update_one(
            {"code": code},
            {"$inc": {"opened_count": 1}}
        )

        return {
            "success": True,
            "code": invite["code"],
            "inviter_id": invite.get("inviter_id"),
            "use_count": invite.get("use_count", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get invite error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/accept-invite/{code}/{user_id}")
async def accept_invite(code: str, user_id: str):
    """Accept an invite and track it."""
    try:
        invite = await db.invites.find_one({"code": code}, {"_id": 0})
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")

        await db.invites.update_one(
            {"code": code},
            {"$push": {"used_by": user_id}, "$inc": {"use_count": 1}}
        )

        return {"success": True, "message": "Invite accepted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Accept invite error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/weekly-report/{user_id}")
async def get_weekly_report(user_id: str):
    """Weekly user report: distribution, insight, streak, mission participation."""
    try:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Distribution from daily questions this week
        questions = await db.daily_questions.find(
            {"user_id": user_id, "answered": True, "date": {"$gte": week_ago}},
            {"_id": 0, "suggested_direction": 1, "date": 1}
        ).to_list(100)

        directions = ['contribution', 'recovery', 'order', 'exploration']
        dist = {d: 0 for d in directions}
        dates_answered = set()
        for q in questions:
            d = q.get("suggested_direction")
            if d in dist:
                dist[d] += 1
            dates_answered.add(q.get("date"))

        total = sum(dist.values()) or 1
        distribution = {d: round((c / total) * 100) for d, c in dist.items()}

        # Dominant direction
        dominant = max(dist, key=dist.get) if sum(dist.values()) > 0 else None

        direction_labels_he = {
            'recovery': 'התאוששות', 'order': 'סדר',
            'contribution': 'תרומה', 'exploration': 'חקירה'
        }

        # Insight text
        if sum(dist.values()) == 0:
            insight_he = "אין מספיק נתונים השבוע. נסה לענות על השאלה היומית כל יום."
        elif dominant:
            insight_he = f"השבוע הכיוון המוביל שלך היה {direction_labels_he.get(dominant, dominant)} ({distribution[dominant]}%). המשך לפעול בכיוון זה או נסה לאזן."
        else:
            insight_he = "השבוע הייתה לך פעילות מאוזנת בכל הכיוונים."

        # Streak
        all_answered = await db.daily_questions.find(
            {"user_id": user_id, "answered": True},
            {"_id": 0, "date": 1}
        ).to_list(500)
        all_dates = sorted(set(q.get("date") for q in all_answered if q.get("date")), reverse=True)
        streak = 0
        if all_dates and all_dates[0] >= yesterday_str:
            streak = 1
            for i in range(1, len(all_dates)):
                prev = datetime.strptime(all_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(all_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

        # Mission participation this week
        missions = await db.daily_missions.find(
            {"date": {"$gte": week_ago}}, {"_id": 0, "date": 1, "direction": 1, "participants": 1}
        ).to_list(10)
        mission_days = len(missions)
        participated_days = 0
        for m in missions:
            mission_dir = m.get("direction")
            # Check if user answered with same direction on that day
            user_q = next((q for q in questions if q.get("date") == m.get("date") and q.get("suggested_direction") == mission_dir), None)
            if user_q:
                participated_days += 1
        mission_participation = round((participated_days / mission_days) * 100) if mission_days > 0 else 0

        return {
            "success": True,
            "user_id": user_id,
            "distribution": distribution,
            "dominant_direction": dominant,
            "insight_he": insight_he,
            "streak": streak,
            "mission_participation": mission_participation,
            "days_active": len(dates_answered),
            "total_actions": sum(dist.values())
        }
    except Exception as e:
        logger.error(f"Get weekly report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


ANONYMOUS_ALIASES = [
    "Explorer", "Builder", "Seeker", "Navigator", "Pioneer",
    "Guardian", "Visionary", "Pathfinder", "Strategist", "Catalyst",
    "Dreamer", "Architect", "Sentinel", "Wanderer", "Alchemist",
    "Sage", "Herald", "Beacon", "Anchor", "Voyager"
]

# ==================== FORCE PROFILE & VALUE VECTOR MAPPINGS ====================
# Each orientation direction maps to forces and value vectors
DIRECTION_FORCE_MAP = {
    'contribution': {'cognitive': 0.2, 'emotional': 0.4, 'physical': 0.1, 'personal': 0.1, 'social': 0.8, 'drives': 0.3},
    'recovery': {'cognitive': 0.3, 'emotional': 0.6, 'physical': 0.5, 'personal': 0.7, 'social': 0.1, 'drives': 0.2},
    'order': {'cognitive': 0.7, 'emotional': 0.2, 'physical': 0.3, 'personal': 0.4, 'social': 0.3, 'drives': 0.6},
    'exploration': {'cognitive': 0.8, 'emotional': 0.5, 'physical': 0.2, 'personal': 0.3, 'social': 0.4, 'drives': 0.7}
}

DIRECTION_VECTOR_MAP = {
    'contribution': {'internal': 0.2, 'external': 0.5, 'collective': 0.8},
    'recovery': {'internal': 0.8, 'external': 0.1, 'collective': 0.2},
    'order': {'internal': 0.5, 'external': 0.4, 'collective': 0.4},
    'exploration': {'internal': 0.4, 'external': 0.7, 'collective': 0.3}
}

FORCE_LABELS_HE = {
    'cognitive': 'קוגניטיבי', 'emotional': 'רגשי', 'physical': 'פיזי',
    'personal': 'אישי', 'social': 'חברתי', 'drives': 'דחפים'
}

VECTOR_LABELS_HE = {
    'internal': 'פנימי', 'external': 'חיצוני', 'collective': 'קולקטיבי'
}


DIRECTION_THEORY = {
    'contribution': {
        'label_he': 'תרומה',
        'symbol': 'נתינה',
        'explanation_he': 'כיוון התרומה מבטא את הרצון לתת, לעזור ולהשפיע על הסביבה. זהו הכוח שמחבר בין הפרט לקולקטיב.',
        'meaning_he': 'כשאתה פועל בכיוון התרומה, אתה מחזק את השדה הקולקטיבי ויוצר ערך שחורג מגבולות העצמי.',
        'symbolic_meaning_he': 'הסמל של התרומה הוא הנתינה — הזרימה כלפי חוץ. כמו נהר שמזין את השדות סביבו, פעולת התרומה יוצרת ערך שמתפשט מעבר לגבולות האדם הפועל.',
        'behavior_example_he': 'לעזור לחבר שנמצא במשבר, להתנדב בקהילה, לשתף ידע עם עמית, להקשיב למישהו שצריך אוזן קשבת.',
        'field_effect_he': 'פעולות תרומה מחזקות את הקשר בין חלקי השדה. ככל שיותר אנשים פועלים בכיוון התרומה, השדה הקולקטיבי הופך מחובר ויציב יותר.'
    },
    'recovery': {
        'label_he': 'התאוששות',
        'symbol': 'שיקום',
        'explanation_he': 'כיוון ההתאוששות מבטא את הצורך בהטענה, מנוחה ושיקום פנימי. זהו הכוח שמאפשר לחזור לאיזון.',
        'meaning_he': 'כשאתה פועל בכיוון ההתאוששות, אתה בונה את הבסיס הפנימי שממנו כל פעולה אחרת מתחילה.',
        'symbolic_meaning_he': 'הסמל של ההתאוששות הוא השיקום — התנועה פנימה. כמו עץ שמפיל עלים בסתיו כדי לשמור אנרגיה לאביב, ההתאוששות היא ההכנה לצמיחה הבאה.',
        'behavior_example_he': 'לקחת הפסקה אחרי יום עמוס, לישון כמו שצריך, לצאת לטיול בטבע, לשתות כוס תה בשקט, לסרב לבקשה כשאין כוח.',
        'field_effect_he': 'פעולות התאוששות מייצבות את הבסיס של השדה. כשאנשים מאפשרים לעצמם התאוששות, הם חוזרים לשדה עם יותר אנרגיה ובהירות.'
    },
    'order': {
        'label_he': 'סדר',
        'symbol': 'מבנה',
        'explanation_he': 'כיוון הסדר מבטא את הרצון לארגן, לתכנן וליצור מבנה. זהו הכוח שמביא יציבות ובהירות.',
        'meaning_he': 'כשאתה פועל בכיוון הסדר, אתה יוצר מסגרת שמאפשרת לכל הכיוונים האחרים לפעול בצורה יעילה.',
        'symbolic_meaning_he': 'הסמל של הסדר הוא המבנה — השלד שמחזיק הכול. כמו אדריכל שמתכנן בניין, הסדר יוצר את התשתית שעליה כל דבר אחר נבנה.',
        'behavior_example_he': 'לארגן את הלוח זמנים, לתכנן את השבוע, לסדר את חדר העבודה, לכתוב רשימת משימות, להגדיר יעדים ברורים.',
        'field_effect_he': 'פעולות סדר יוצרות מבנה בשדה הקולקטיבי. כשיש סדר, כל הכיוונים האחרים פועלים בצורה יעילה יותר — השדה הופך ברור וניתן לניווט.'
    },
    'exploration': {
        'label_he': 'חקירה',
        'symbol': 'גילוי',
        'explanation_he': 'כיוון החקירה מבטא את הסקרנות, הרצון ללמוד ולגלות. זהו הכוח שמניע שינוי וצמיחה.',
        'meaning_he': 'כשאתה פועל בכיוון החקירה, אתה פותח דלתות חדשות ומרחיב את גבולות ההכרה.',
        'symbolic_meaning_he': 'הסמל של החקירה הוא הגילוי — התנועה קדימה לעבר הלא נודע. כמו חוקר שמפליג לים הפתוח, החקירה דורשת אומץ ופתיחות.',
        'behavior_example_he': 'ללמוד נושא חדש, לנסות גישה שונה לבעיה, לשאול שאלות קשות, לצאת מאזור הנוחות, לפגוש אנשים חדשים.',
        'field_effect_he': 'פעולות חקירה מרחיבות את השדה. הן מוסיפות ממדים חדשים ואפשרויות שלא היו קיימות קודם — השדה הופך דינמי ומלא פוטנציאל.'
    }
}


@api_router.get("/orientation/daily-opening/{user_id}")
async def get_daily_opening(user_id: str):
    """Daily Opening: compass state, dominant force, suggested direction for the day."""
    try:
        now = datetime.now(timezone.utc)
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1, "global_stats": 1})
        stats = session.get("global_stats", {}) if session else {}
        history = session.get("history", []) if session else []

        dirs = ['contribution', 'recovery', 'order', 'exploration']
        dir_counts = {d: stats.get(d, 0) for d in dirs}
        total = sum(dir_counts.values())

        # Compass state: normalized distribution
        compass_state = {d: round((c / total) * 100) if total > 0 else 25 for d, c in dir_counts.items()}

        # Dominant force from all-time history
        forces = {f: 0.0 for f in FORCE_LABELS_HE}
        for h in history:
            d = h.get("value_tag", "")
            if d in DIRECTION_FORCE_MAP:
                for f, w in DIRECTION_FORCE_MAP[d].items():
                    forces[f] += w
        if total > 0:
            forces = {f: round(v / total, 2) for f, v in forces.items()}
        dominant_force = max(forces, key=forces.get) if total > 0 else 'cognitive'

        # Suggested direction: the least-used direction (balancing logic)
        if total > 0:
            suggested = min(dir_counts, key=dir_counts.get)
        else:
            # For new users, rotate by day
            day_idx = now.timetuple().tm_yday % 4
            suggested = dirs[day_idx]

        dir_labels = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}

        # Greeting based on time of day
        hour = now.hour
        if hour < 12:
            greeting = 'בוקר טוב'
        elif hour < 17:
            greeting = 'צהריים טובים'
        else:
            greeting = 'ערב טוב'

        return {
            "success": True,
            "user_id": user_id,
            "greeting_he": greeting,
            "compass_state": compass_state,
            "dominant_force": dominant_force,
            "dominant_force_he": FORCE_LABELS_HE.get(dominant_force, ''),
            "forces": forces,
            "suggested_direction": suggested,
            "suggested_direction_he": dir_labels.get(suggested, ''),
            "total_actions": total,
            "theory": DIRECTION_THEORY.get(suggested, {})
        }
    except Exception as e:
        logger.error(f"Get daily opening error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/day-summary/{user_id}")
async def get_day_summary(user_id: str):
    """End of Day Reflection: chosen direction, impact, streak, global effect."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1})
        dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        today_total = 0

        if session:
            for h in session.get("history", []):
                if h.get("timestamp", "") >= today_start:
                    d = h.get("value_tag", "")
                    if d in dir_counts:
                        dir_counts[d] += 1
                        today_total += 1

        chosen_direction = max(dir_counts, key=dir_counts.get) if today_total > 0 else None
        dir_labels = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}

        # Impact on field
        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "history": 1}).to_list(10000)
        total_field = sum(
            1 for s in all_sessions for h in s.get("history", [])
            if h.get("timestamp", "") >= today_start and h.get("value_tag", "") in dir_counts
        )
        impact_percent = round((today_total / total_field) * 100, 1) if total_field > 0 else 0

        # Streak
        answered = await db.daily_questions.find(
            {"user_id": user_id, "answered": True}, {"_id": 0, "date": 1}
        ).to_list(500)
        all_dates = sorted(set(q.get("date") for q in answered if q.get("date")), reverse=True)
        streak = 0
        if all_dates and all_dates[0] >= yesterday_str:
            streak = 1
            for i in range(1, len(all_dates)):
                prev = datetime.strptime(all_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(all_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

        # Global field effect: direction distribution of all today's actions
        field_dist = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        for s in all_sessions:
            for h in s.get("history", []):
                if h.get("timestamp", "") >= today_start:
                    d = h.get("value_tag", "")
                    if d in field_dist:
                        field_dist[d] += 1
        if total_field > 0:
            field_effect = {d: round((c / total_field) * 100) for d, c in field_dist.items()}
        else:
            field_effect = {d: 25 for d in field_dist}

        # Reflection text
        if today_total == 0:
            reflection_he = "היום עוד לא ביצעת פעולות. מחר יום חדש."
        else:
            reflection_he = f"היום פעלת {today_total} פעמים, בעיקר בכיוון {dir_labels.get(chosen_direction, '')}. ההשפעה שלך על השדה: {impact_percent}%."

        # Department allocation analysis
        today_base_doc = await db.daily_bases.find_one(
            {"user_id": user_id, "date": today_str}, {"_id": 0}
        )
        chosen_base = today_base_doc.get("base") if today_base_doc else None

        # Map today's directions to departments
        dept_alloc = {'heart': 0, 'head': 0, 'body': 0}
        for d, c in dir_counts.items():
            dept = DIRECTION_TO_DEPT.get(d, 'head')
            dept_alloc[dept] += c

        dept_total = sum(dept_alloc.values())
        dept_pct = {d: round((c / dept_total) * 100) if dept_total > 0 else 0 for d, c in dept_alloc.items()}
        most_used_dept = max(dept_alloc, key=dept_alloc.get) if dept_total > 0 else None
        neglected_dept = min(dept_alloc, key=dept_alloc.get) if dept_total > 0 else None

        # Historical preferred department (last 14 days)
        fourteen_days_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d")
        hist_bases = await db.daily_bases.find(
            {"user_id": user_id, "date": {"$gte": fourteen_days_ago}},
            {"_id": 0, "base": 1}
        ).to_list(14)
        hist_dept_counts = {'heart': 0, 'head': 0, 'body': 0}
        for hb in hist_bases:
            b = hb.get('base', '')
            if b in hist_dept_counts:
                hist_dept_counts[b] += 1
        preferred_dept = max(hist_dept_counts, key=hist_dept_counts.get) if sum(hist_dept_counts.values()) > 0 else None
        hist_neglected = min(hist_dept_counts, key=hist_dept_counts.get) if sum(hist_dept_counts.values()) > 0 else None

        # Base reflection — short observational sentence
        base_reflection_he = ""
        if chosen_base and most_used_dept and today_total > 0:
            chosen_he = DEPT_LABELS_HE.get(chosen_base, '')
            used_he = DEPT_LABELS_HE.get(most_used_dept, '')
            if chosen_base == most_used_dept:
                base_reflection_he = f"בחרת לפעול מה{chosen_he}, והפעולות שלך היום תאמו את הבחירה."
            else:
                base_reflection_he = f"בחרת לפעול מה{chosen_he}, אך רוב הפעולות היום נעו לכיוון ה{used_he}."

        return {
            "success": True,
            "user_id": user_id,
            "date": today_str,
            "chosen_direction": chosen_direction,
            "chosen_direction_he": dir_labels.get(chosen_direction, ''),
            "direction_counts": dir_counts,
            "total_actions": today_total,
            "impact_on_field": impact_percent,
            "streak": streak,
            "global_field_effect": field_effect,
            "reflection_he": reflection_he,
            "chosen_base": chosen_base,
            "chosen_base_he": DEPT_LABELS_HE.get(chosen_base, ''),
            "dept_allocation": dept_pct,
            "most_used_dept": most_used_dept,
            "most_used_dept_he": DEPT_LABELS_HE.get(most_used_dept, ''),
            "neglected_dept": neglected_dept,
            "neglected_dept_he": DEPT_LABELS_HE.get(neglected_dept, ''),
            "preferred_dept": preferred_dept,
            "preferred_dept_he": DEPT_LABELS_HE.get(preferred_dept, ''),
            "hist_neglected_dept": hist_neglected,
            "hist_neglected_dept_he": DEPT_LABELS_HE.get(hist_neglected, ''),
            "base_reflection_he": base_reflection_he
        }
    except Exception as e:
        logger.error(f"Get day summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══ DAILY BASE ALLOCATION SYSTEM ═══

BASE_DEFINITIONS = {
    'heart': {
        'name_he': 'לב',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['קשרים ומערכות יחסים', 'אמפתיה והקשבה', 'תרומה ונתינה', 'תיקון רגשי'],
        'allocations_keys': ['relationships', 'empathy', 'contribution', 'emotional_repair']
    },
    'head': {
        'name_he': 'ראש',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['סדר ותכנון', 'למידה וחקירה', 'קבלת החלטות', 'חשיבה אסטרטגית'],
        'allocations_keys': ['order', 'learning', 'decision_making', 'strategic_thinking']
    },
    'body': {
        'name_he': 'גוף',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['תנועה ובריאות', 'פעולה מעשית', 'משמעת ומחויבות', 'סדר פיזי'],
        'allocations_keys': ['movement', 'practical_action', 'discipline', 'physical_order']
    }
}

# Map existing directions to departments for end-of-day analysis
DIRECTION_TO_DEPT = {
    'contribution': 'heart',
    'recovery': 'body',
    'order': 'head',
    'exploration': 'head'
}

DEPT_LABELS_HE = {'heart': 'לב', 'head': 'ראש', 'body': 'גוף'}


@api_router.get("/orientation/daily-base/{user_id}")
async def get_daily_base(user_id: str):
    """Get today's base selection and historical department patterns."""
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Check if base was already selected today
        today_base = await db.daily_bases.find_one(
            {"user_id": user_id, "date": today_str}, {"_id": 0}
        )

        # Historical department usage (last 30 days)
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        history = await db.daily_bases.find(
            {"user_id": user_id, "date": {"$gte": thirty_days_ago}},
            {"_id": 0, "base": 1, "date": 1}
        ).to_list(30)

        dept_counts = {'heart': 0, 'head': 0, 'body': 0}
        for h in history:
            b = h.get('base', '')
            if b in dept_counts:
                dept_counts[b] += 1

        total_days = sum(dept_counts.values())
        most_used = max(dept_counts, key=dept_counts.get) if total_days > 0 else None
        neglected = min(dept_counts, key=dept_counts.get) if total_days > 0 else None

        return {
            "success": True,
            "base_selected": today_base is not None,
            "today_base": today_base.get("base") if today_base else None,
            "today_base_he": DEPT_LABELS_HE.get(today_base.get("base")) if today_base else None,
            "allocations_he": BASE_DEFINITIONS.get(today_base.get("base"), {}).get("allocations_he", []) if today_base else [],
            "bases": {k: {"name_he": v["name_he"], "allocations_he": v["allocations_he"]} for k, v in BASE_DEFINITIONS.items()},
            "dept_history": dept_counts,
            "most_used_dept": most_used,
            "most_used_dept_he": DEPT_LABELS_HE.get(most_used, ''),
            "neglected_dept": neglected,
            "neglected_dept_he": DEPT_LABELS_HE.get(neglected, ''),
            "total_days_tracked": total_days
        }
    except Exception as e:
        logger.error(f"Get daily base error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/daily-base/{user_id}")
async def set_daily_base(user_id: str, data: dict):
    """Set today's base selection."""
    try:
        base = data.get("base", "")
        if base not in BASE_DEFINITIONS:
            raise HTTPException(status_code=400, detail="Invalid base. Must be heart, head, or body.")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Upsert — allow changing base same day
        await db.daily_bases.update_one(
            {"user_id": user_id, "date": today_str},
            {"$set": {
                "user_id": user_id,
                "date": today_str,
                "base": base,
                "chosen_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )

        base_def = BASE_DEFINITIONS[base]
        return {
            "success": True,
            "base": base,
            "base_he": base_def["name_he"],
            "allocations_he": base_def["allocations_he"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set daily base error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@api_router.get("/orientation/directions")
async def get_directions():
    """Return the 4 directions with explanations and symbolic meanings."""
    return {
        "success": True,
        "directions": DIRECTION_THEORY
    }


@api_router.get("/orientation/force-profile/{user_id}")
async def get_force_profile(user_id: str):
    """Force Profile Engine: compute user's 6-force profile from action history."""
    try:
        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1, "global_stats": 1})

        forces = {f: 0.0 for f in FORCE_LABELS_HE}
        total = 0

        if session:
            for h in session.get("history", []):
                d = h.get("value_tag", "")
                if d in DIRECTION_FORCE_MAP:
                    total += 1
                    for f, weight in DIRECTION_FORCE_MAP[d].items():
                        forces[f] += weight

        if total > 0:
            forces = {f: round(v / total, 2) for f, v in forces.items()}

        dominant = max(forces, key=forces.get) if total > 0 else None

        return {
            "success": True,
            "user_id": user_id,
            "forces": forces,
            "dominant_force": dominant,
            "dominant_force_he": FORCE_LABELS_HE.get(dominant, ''),
            "total_actions": total
        }
    except Exception as e:
        logger.error(f"Get force profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/value-vectors/{user_id}")
async def get_value_vectors(user_id: str):
    """Value Vector System: track 3 value vectors from action history."""
    try:
        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1})

        vectors = {v: 0.0 for v in VECTOR_LABELS_HE}
        total = 0

        if session:
            for h in session.get("history", []):
                d = h.get("value_tag", "")
                if d in DIRECTION_VECTOR_MAP:
                    total += 1
                    for v, weight in DIRECTION_VECTOR_MAP[d].items():
                        vectors[v] += weight

        if total > 0:
            vectors = {v: round(val / total, 2) for v, val in vectors.items()}

        dominant = max(vectors, key=vectors.get) if total > 0 else None

        return {
            "success": True,
            "user_id": user_id,
            "vectors": vectors,
            "dominant_vector": dominant,
            "dominant_vector_he": VECTOR_LABELS_HE.get(dominant, ''),
            "total_actions": total
        }
    except Exception as e:
        logger.error(f"Get value vectors error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/daily-summary/{user_id}")
async def get_daily_summary(user_id: str):
    """Daily Summary: end-of-day overview of direction, force, vectors, and field impact."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1})

        dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        forces = {f: 0.0 for f in FORCE_LABELS_HE}
        vectors = {v: 0.0 for v in VECTOR_LABELS_HE}
        today_total = 0

        if session:
            for h in session.get("history", []):
                if h.get("timestamp", "") >= today_start:
                    d = h.get("value_tag", "")
                    if d in dir_counts:
                        dir_counts[d] += 1
                        today_total += 1
                        for f, w in DIRECTION_FORCE_MAP.get(d, {}).items():
                            forces[f] += w
                        for v, w in DIRECTION_VECTOR_MAP.get(d, {}).items():
                            vectors[v] += w

        if today_total > 0:
            forces = {f: round(v / today_total, 2) for f, v in forces.items()}
            vectors = {v: round(val / today_total, 2) for v, val in vectors.items()}

        dominant_dir = max(dir_counts, key=dir_counts.get) if today_total > 0 else None
        dominant_force = max(forces, key=forces.get) if today_total > 0 else None
        dominant_vector = max(vectors, key=vectors.get) if today_total > 0 else None

        dir_labels = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}

        # Field impact: what % of today's collective actions came from this user
        all_sessions = await db.philos_sessions.find({}, {"_id": 0, "history": 1}).to_list(10000)
        total_today = sum(
            1 for s in all_sessions for h in s.get("history", [])
            if h.get("timestamp", "") >= today_start and h.get("value_tag", "") in dir_counts
        )
        field_impact = round((today_total / total_today) * 100, 1) if total_today > 0 else 0

        # Build summary text
        if today_total == 0:
            summary_he = "עוד לא ביצעת פעולות היום. התחל את היום עם השאלה היומית."
        else:
            summary_he = f"היום ביצעת {today_total} פעולות. הכיוון המוביל: {dir_labels.get(dominant_dir, '')}. הכוח הדומיננטי: {FORCE_LABELS_HE.get(dominant_force, '')}."

        return {
            "success": True,
            "user_id": user_id,
            "date": now.strftime("%Y-%m-%d"),
            "total_actions": today_total,
            "direction_counts": dir_counts,
            "dominant_direction": dominant_dir,
            "dominant_direction_he": dir_labels.get(dominant_dir, ''),
            "forces": forces,
            "dominant_force": dominant_force,
            "dominant_force_he": FORCE_LABELS_HE.get(dominant_force, ''),
            "vectors": vectors,
            "dominant_vector": dominant_vector,
            "dominant_vector_he": VECTOR_LABELS_HE.get(dominant_vector, ''),
            "field_impact": field_impact,
            "summary_he": summary_he
        }
    except Exception as e:
        logger.error(f"Get daily summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Profile Page: alias, identity, streak, force profile, value vectors, recent actions, rank."""
    try:
        now = datetime.now(timezone.utc)
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Alias (deterministic from user_id)
        alias_index = hash(user_id) % len(ANONYMOUS_ALIASES)
        alias = ANONYMOUS_ALIASES[alias_index]

        # Session data
        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1, "global_stats": 1})
        history = session.get("history", []) if session else []
        stats = session.get("global_stats", {}) if session else {}

        # Identity
        dirs = ['contribution', 'recovery', 'order', 'exploration']
        dir_counts = {d: stats.get(d, 0) for d in dirs}
        total_actions = sum(dir_counts.values())
        dominant_dir = max(dir_counts, key=dir_counts.get) if total_actions > 0 else None
        dir_labels = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}
        identity = dir_labels.get(dominant_dir, 'חדש') + ' מוביל' if dominant_dir else 'משתמש חדש'

        # Streak
        answered = await db.daily_questions.find(
            {"user_id": user_id, "answered": True}, {"_id": 0, "date": 1}
        ).to_list(500)
        all_dates = sorted(set(q.get("date") for q in answered if q.get("date")), reverse=True)
        streak = 0
        if all_dates and all_dates[0] >= yesterday_str:
            streak = 1
            for i in range(1, len(all_dates)):
                prev = datetime.strptime(all_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(all_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

        # Force profile
        forces = {f: 0.0 for f in FORCE_LABELS_HE}
        for h in history:
            d = h.get("value_tag", "")
            if d in DIRECTION_FORCE_MAP:
                for f, w in DIRECTION_FORCE_MAP[d].items():
                    forces[f] += w
        if total_actions > 0:
            forces = {f: round(v / total_actions, 2) for f, v in forces.items()}

        # Value vectors
        vectors = {v: 0.0 for v in VECTOR_LABELS_HE}
        for h in history:
            d = h.get("value_tag", "")
            if d in DIRECTION_VECTOR_MAP:
                for v, w in DIRECTION_VECTOR_MAP[d].items():
                    vectors[v] += w
        if total_actions > 0:
            vectors = {v: round(val / total_actions, 2) for v, val in vectors.items()}

        # Recent actions (last 10)
        recent = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        recent_actions = [{
            "direction": a.get("value_tag", ""),
            "action": a.get("action", ""),
            "timestamp": a.get("timestamp", "")
        } for a in recent]

        # Community rank (by total actions)
        all_sessions_list = await db.philos_sessions.find({}, {"_id": 0, "user_id": 1, "global_stats": 1}).to_list(10000)
        all_totals = sorted([
            sum(s.get("global_stats", {}).get(d, 0) for d in dirs)
            for s in all_sessions_list
        ], reverse=True)
        my_rank = 1
        for i, t in enumerate(all_totals):
            if t <= total_actions:
                my_rank = i + 1
                break
        total_users = len(all_totals)

        return {
            "success": True,
            "user_id": user_id,
            "alias": alias,
            "identity": identity,
            "streak": streak,
            "total_actions": total_actions,
            "direction_distribution": dir_counts,
            "dominant_direction": dominant_dir,
            "forces": forces,
            "dominant_force": max(forces, key=forces.get) if total_actions > 0 else None,
            "vectors": vectors,
            "dominant_vector": max(vectors, key=vectors.get) if total_actions > 0 else None,
            "recent_actions": recent_actions,
            "community_rank": my_rank,
            "total_users": total_users
        }
    except Exception as e:
        logger.error(f"Get user profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


GLOBE_COUNTRY_COORDS = {
    "BR": {"lat": -14.2, "lng": -51.9, "name": "ברזיל"}, "IN": {"lat": 20.6, "lng": 78.9, "name": "הודו"},
    "DE": {"lat": 51.2, "lng": 10.5, "name": "גרמניה"}, "US": {"lat": 37.1, "lng": -95.7, "name": "ארה\"ב"},
    "JP": {"lat": 36.2, "lng": 138.3, "name": "יפן"}, "NG": {"lat": 9.1, "lng": 8.7, "name": "ניגריה"},
    "IL": {"lat": 31.0, "lng": 34.9, "name": "ישראל"}, "FR": {"lat": 46.2, "lng": 2.2, "name": "צרפת"},
    "AU": {"lat": -25.3, "lng": 133.8, "name": "אוסטרליה"}, "KR": {"lat": 35.9, "lng": 127.8, "name": "דרום קוריאה"},
    "MX": {"lat": 23.6, "lng": -102.6, "name": "מקסיקו"}, "GB": {"lat": 55.4, "lng": -3.4, "name": "בריטניה"},
    "CA": {"lat": 56.1, "lng": -106.3, "name": "קנדה"}, "IT": {"lat": 41.9, "lng": 12.6, "name": "איטליה"},
    "ES": {"lat": 40.5, "lng": -3.7, "name": "ספרד"}, "AR": {"lat": -38.4, "lng": -63.6, "name": "ארגנטינה"},
    "TR": {"lat": 39.0, "lng": 35.2, "name": "טורקיה"}, "TH": {"lat": 15.9, "lng": 100.5, "name": "תאילנד"},
    "PL": {"lat": 51.9, "lng": 19.1, "name": "פולין"}, "NL": {"lat": 52.1, "lng": 5.3, "name": "הולנד"}
}

GLOBE_COLOR_MAP = {
    'contribution': '#22c55e', 'recovery': '#3b82f6',
    'order': '#6366f1', 'exploration': '#f59e0b'
}

GLOBE_DIR_LABELS = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}


@api_router.get("/orientation/globe-activity")
async def get_globe_activity():
    """Globe-ready dataset with today stats and mission glow."""
    try:
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(hours=1)).isoformat()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        # Demo events
        demo_events = await db.demo_events.find(
            {"timestamp": {"$gte": cutoff}},
            {"_id": 0, "direction": 1, "timestamp": 1, "country": 1, "country_code": 1}
        ).to_list(200)

        # User-submitted globe points (last 3 hours)
        user_cutoff = (now - timedelta(hours=3)).isoformat()
        user_points = await db.user_globe_points.find(
            {"timestamp": {"$gte": user_cutoff}},
            {"_id": 0, "direction": 1, "timestamp": 1, "country_code": 1, "lat": 1, "lng": 1}
        ).to_list(100)

        points = []
        dir_counts_today = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}

        for e in demo_events:
            cc = e.get("country_code", "")
            coords = GLOBE_COUNTRY_COORDS.get(cc)
            if coords:
                d = e["direction"]
                points.append({
                    "lat": coords["lat"] + (_random.random() - 0.5) * 4,
                    "lng": coords["lng"] + (_random.random() - 0.5) * 4,
                    "direction": d,
                    "color": GLOBE_COLOR_MAP.get(d, "#8b5cf6"),
                    "country": e.get("country", ""),
                    "country_code": cc,
                    "timestamp": e["timestamp"],
                    "is_user": False
                })
                if e.get("timestamp", "") >= today_start and d in dir_counts_today:
                    dir_counts_today[d] += 1

        for up in user_points:
            d = up.get("direction", "")
            points.append({
                "lat": up["lat"],
                "lng": up["lng"],
                "direction": d,
                "color": GLOBE_COLOR_MAP.get(d, "#8b5cf6"),
                "country_code": up.get("country_code", "IL"),
                "country": GLOBE_COUNTRY_COORDS.get(up.get("country_code", "IL"), {}).get("name", ""),
                "timestamp": up["timestamp"],
                "is_user": True
            })
            if up.get("timestamp", "") >= today_start and d in dir_counts_today:
                dir_counts_today[d] += 1

        total_today = sum(dir_counts_today.values())
        dominant_today = max(dir_counts_today, key=dir_counts_today.get) if total_today > 0 else None

        # Mission glow
        mission = await _get_or_create_mission_today()
        mission_dir = mission.get("direction", "contribution")

        return {
            "success": True,
            "points": points,
            "total_points": len(points),
            "color_map": GLOBE_COLOR_MAP,
            "today_stats": {
                "total_actions": total_today,
                "dominant_direction": dominant_today,
                "dominant_direction_he": GLOBE_DIR_LABELS.get(dominant_today, ''),
                "direction_counts": dir_counts_today
            },
            "mission_glow": {
                "direction": mission_dir,
                "color": GLOBE_COLOR_MAP.get(mission_dir, "#6366f1")
            }
        }
    except Exception as e:
        logger.error(f"Get globe activity error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/globe-point")
async def add_globe_point(data: dict):
    """Add a user action point to the globe."""
    try:
        user_id = data.get("user_id", "")
        direction = data.get("direction", "contribution")
        country_code = data.get("country_code", "IL")

        coords = GLOBE_COUNTRY_COORDS.get(country_code, GLOBE_COUNTRY_COORDS["IL"])
        lat = coords["lat"] + (_random.random() - 0.5) * 2
        lng = coords["lng"] + (_random.random() - 0.5) * 2
        now = datetime.now(timezone.utc).isoformat()

        doc = {
            "user_id": user_id,
            "direction": direction,
            "country_code": country_code,
            "lat": lat,
            "lng": lng,
            "timestamp": now
        }
        await db.user_globe_points.insert_one(doc)

        return {
            "success": True,
            "point": {
                "lat": lat,
                "lng": lng,
                "direction": direction,
                "color": GLOBE_COLOR_MAP.get(direction, "#8b5cf6"),
                "country_code": country_code,
                "timestamp": now
            },
            "message_he": "הפעולה שלך נוספה לשדה האנושי"
        }
    except Exception as e:
        logger.error(f"Add globe point error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/globe-region/{country_code}")
async def get_globe_region(country_code: str):
    """Region details: dominant direction, recent count, trend."""
    try:
        now = datetime.now(timezone.utc)
        cutoff_3h = (now - timedelta(hours=3)).isoformat()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        cc = country_code.upper()

        coords = GLOBE_COUNTRY_COORDS.get(cc)
        if not coords:
            return {"success": False, "error": "Unknown region"}

        # Demo events for this region
        events = await db.demo_events.find(
            {"country_code": cc, "timestamp": {"$gte": cutoff_3h}},
            {"_id": 0, "direction": 1, "timestamp": 1}
        ).to_list(500)

        # User points for this region
        user_pts = await db.user_globe_points.find(
            {"country_code": cc, "timestamp": {"$gte": cutoff_3h}},
            {"_id": 0, "direction": 1, "timestamp": 1}
        ).to_list(100)

        dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        for e in events + user_pts:
            d = e.get("direction", "")
            if d in dir_counts:
                dir_counts[d] += 1

        total = sum(dir_counts.values())
        dominant = max(dir_counts, key=dir_counts.get) if total > 0 else None

        # Trend: compare last 1.5h vs previous 1.5h
        mid = (now - timedelta(hours=1, minutes=30)).isoformat()
        recent = sum(1 for e in events + user_pts if e.get("timestamp", "") >= mid)
        older = total - recent
        if older > 0:
            trend = "עולה" if recent > older else ("יורד" if recent < older else "יציב")
        else:
            trend = "חדש" if recent > 0 else "שקט"

        return {
            "success": True,
            "country_code": cc,
            "country_name_he": coords.get("name", cc),
            "total_actions": total,
            "dominant_direction": dominant,
            "dominant_direction_he": GLOBE_DIR_LABELS.get(dominant, ''),
            "direction_counts": dir_counts,
            "trend_he": trend
        }
    except Exception as e:
        logger.error(f"Get globe region error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/referral-leaderboard")
async def get_referral_leaderboard():
    """Referral leaderboard: top 10 inviters with anonymous aliases."""
    try:
        now = datetime.now(timezone.utc)
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        invites = await db.invites.find({}, {"_id": 0, "inviter_id": 1, "use_count": 1}).to_list(10000)

        user_invites = {}
        for inv in invites:
            uid = inv.get("inviter_id")
            count = inv.get("use_count", 0)
            if uid:
                user_invites[uid] = user_invites.get(uid, 0) + count

        # Calculate streaks per user
        answered_all = await db.daily_questions.find(
            {"answered": True}, {"_id": 0, "user_id": 1, "date": 1}
        ).to_list(50000)
        streak_dates = {}
        for q in answered_all:
            uid = q.get("user_id")
            d = q.get("date")
            if uid and d:
                streak_dates.setdefault(uid, set()).add(d)

        def calc_streak(uid):
            dates = streak_dates.get(uid, set())
            if not dates:
                return 0
            sorted_d = sorted(dates, reverse=True)
            if sorted_d[0] < yesterday_str:
                return 0
            streak = 1
            for i in range(1, len(sorted_d)):
                prev = datetime.strptime(sorted_d[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(sorted_d[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break
            return streak

        # Sort by invites descending, take top 10
        sorted_users = sorted(user_invites.items(), key=lambda x: x[1], reverse=True)[:10]

        # Assign deterministic anonymous aliases based on user_id hash
        leaderboard = []
        for i, (uid, count) in enumerate(sorted_users):
            if count == 0:
                continue
            alias_index = hash(uid) % len(ANONYMOUS_ALIASES)
            leaderboard.append({
                "user_alias": ANONYMOUS_ALIASES[alias_index],
                "invites_count": count,
                "streak": calc_streak(uid),
                "rank": i + 1
            })

        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        logger.error(f"Get referral leaderboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# CORS and logging setup (router included after all endpoints below)

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


# ==================== VALUE ENGINE + FEED + SUBSCRIPTION ====================
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from fastapi import Request as FastAPIRequest

VALUE_NICHES = {
    'builder_of_order': {
        'label_he': 'בונה הסדר', 'description_he': 'אתה יוצר מבנה ויציבות. הפעולות שלך מארגנות את השדה.',
        'dominant_direction': 'order', 'threshold': 35,
        'strengthening_actions_he': ['לתכנן את השבוע', 'לסדר סדרי עדיפויות', 'לכתוב רשימת משימות']
    },
    'explorer': {
        'label_he': 'חוקר', 'description_he': 'אתה פותח דלתות חדשות. הסקרנות שלך מרחיבה את השדה.',
        'dominant_direction': 'exploration', 'threshold': 35,
        'strengthening_actions_he': ['ללמוד משהו חדש', 'לשאול שאלה קשה', 'לנסות גישה שונה']
    },
    'contributor': {
        'label_he': 'תורם', 'description_he': 'אתה נותן לעולם. הנתינה שלך מחזקת את הקשר בשדה.',
        'dominant_direction': 'contribution', 'threshold': 35,
        'strengthening_actions_he': ['לעזור למישהו', 'לשתף ידע', 'להקשיב לחבר']
    },
    'regenerator': {
        'label_he': 'משקם', 'description_he': 'אתה בונה את הבסיס הפנימי. ההתאוששות שלך מייצבת את השדה.',
        'dominant_direction': 'recovery', 'threshold': 35,
        'strengthening_actions_he': ['לקחת הפסקה', 'לישון כמו שצריך', 'לצאת לטיול']
    },
    'social_connector': {
        'label_he': 'מחבר חברתי', 'description_he': 'אתה מגשר בין אנשים וכיוונים. הנוכחות שלך מאחדת את השדה.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['להזמין חבר', 'להשתתף במשימה קולקטיבית', 'לשתף את ההתמצאות']
    },
    'deep_thinker': {
        'label_he': 'הוגה עמוק', 'description_he': 'אתה מאזן בין כל הכיוונים. העומק שלך מעשיר את השדה.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['לשקול את הצעדים', 'לחזור על החלטה ישנה', 'לרשום תובנה']
    }
}

BADGES = [
    {'id': 'first_action', 'label_he': 'צעד ראשון', 'desc_he': 'ביצעת את הפעולה הראשונה', 'condition': lambda p: p.get('total_actions', 0) >= 1},
    {'id': 'first_globe_point', 'label_he': 'נקודה בשדה', 'desc_he': 'שלחת נקודה לגלובוס', 'condition': lambda p: p.get('globe_points', 0) >= 1},
    {'id': 'streak_3', 'label_he': 'רצף 3 ימים', 'desc_he': 'שמרת על רצף של 3 ימים', 'condition': lambda p: p.get('current_streak', 0) >= 3},
    {'id': 'streak_7', 'label_he': 'נוכחות שבועית', 'desc_he': '7 ימים רצופים בשדה', 'condition': lambda p: p.get('current_streak', 0) >= 7},
    {'id': 'streak_30', 'label_he': 'נוכחות חודשית', 'desc_he': '30 ימים רצופים', 'condition': lambda p: p.get('current_streak', 0) >= 30},
    {'id': 'actions_10', 'label_he': 'פעיל', 'desc_he': '10 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 10},
    {'id': 'actions_50', 'label_he': 'מחויב', 'desc_he': '50 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 50},
    {'id': 'actions_100', 'label_he': 'תורם קבוע', 'desc_he': '100 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 100},
    {'id': 'all_directions', 'label_he': 'רב-כיווני', 'desc_he': 'פעלת בכל 4 הכיוונים', 'condition': lambda p: all(p.get('dir_counts', {}).get(d, 0) > 0 for d in ['contribution', 'recovery', 'order', 'exploration'])},
    {'id': 'niche_found', 'label_he': 'מצאת את הנישה', 'desc_he': 'הנישה שלך זוהתה', 'condition': lambda p: p.get('dominant_niche') is not None},
]

SUBSCRIPTION_PLANS = {
    'free': {'label_he': 'חופשי', 'price': 0.0, 'features_he': ['התמצאות יומית', 'מצפן בסיסי', 'גלובוס', 'קהילה'], 'limits': {'feed_cards': 5, 'value_detail': False, 'niche_insights': False, 'weekly_report': False, 'globe_regions': 3}},
    'plus': {'label_he': 'פלוס', 'price': 9.99, 'features_he': ['כל תכונות חופשי', 'פיד מותאם אישית מלא', 'אנליטיקת ערך מלאה', 'דוח שבועי מעמיק', 'תובנות נישה'], 'limits': {'feed_cards': 50, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': 20}},
    'collective': {'label_he': 'קולקטיב', 'price': 24.99, 'features_he': ['כל תכונות פלוס', 'מעגלים פרטיים', 'תובנות גלובוס פרימיום', 'פרופיל מורחב', 'התקדמות נישה מלאה'], 'limits': {'feed_cards': -1, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': -1}}
}

FEED_ACTIONS_HE = ['ארגנתי את סביבת העבודה', 'עזרתי לחבר', 'למדתי נושא חדש', 'לקחתי הפסקה', 'תכננתי את השבוע', 'שיתפתי ידע', 'ניסיתי גישה שונה', 'ישנתי 8 שעות', 'כתבתי רשימת יעדים', 'פגשתי אדם חדש', 'התנדבתי בקהילה', 'יצאתי לטיול בטבע', 'קראתי מאמר', 'הקשבתי למישהו', 'סידרתי סדרי עדיפויות']
FEED_QUESTIONS_HE = ['איזה כוח מנחה אותך היום?', 'מה הצעד הבא שלך?', 'מה למדת על עצמך השבוע?', 'איפה אתה מרגיש שאתה תקוע?', 'מה תרצה לשנות מחר?']
FEED_REFLECTIONS_HE = ['שמתי לב שהכיוון שלי היה בעיקר פנימי. צריך לאזן.', 'השדה הגלובלי נע לכיוון תרומה — אולי זה הזמן להצטרף.', 'גיליתי שסדר עוזר לי יותר ממה שחשבתי.', 'ההתאוששות הייתה הכי חשובה השבוע.']


def _calculate_level(total_actions):
    thresholds = [0, 1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
    for i in range(len(thresholds) - 1, -1, -1):
        if total_actions >= thresholds[i]:
            return i
    return 0


def _determine_niche(dir_counts, total):
    if total < 3:
        return None
    pcts = {d: (c / total) * 100 for d, c in dir_counts.items()}
    max_dir = max(pcts, key=pcts.get)
    max_pct = pcts[max_dir]
    variance = max(pcts.values()) - min(pcts.values())
    if variance < 10 and total >= 10:
        return 'deep_thinker'
    for niche_id, niche in VALUE_NICHES.items():
        if niche['dominant_direction'] == max_dir and max_pct >= niche['threshold']:
            return niche_id
    return None


async def _build_value_profile(user_id):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    decisions = await db.philos_decisions.find({"user_id": user_id}, {"_id": 0}).to_list(500)
    globe_pts = await db.user_globe_points.count_documents({"user_id": user_id})
    invites = await db.invite_codes.count_documents({"created_by": user_id})
    events_count = await db.events.count_documents({"user_id": user_id})

    dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
    for d in decisions:
        dr = d.get('direction', d.get('value_tag', ''))
        if dr in dir_counts:
            dir_counts[dr] += 1

    total = sum(dir_counts.values())
    streak = user.get('current_streak', 0) if user else 0
    longest_streak = user.get('longest_streak', 0) if user else 0

    internal_value = (dir_counts['recovery'] * 3) + (dir_counts['order'] * 2)
    external_value = (dir_counts['contribution'] * 3) + (dir_counts['exploration'] * 2)
    collective_value = (globe_pts * 5) + (invites * 10) + (streak * 2) + (events_count * 1)
    total_value = internal_value + external_value + collective_value

    niche = _determine_niche(dir_counts, total)
    level = _calculate_level(total)

    consistency = 0
    if total >= 5:
        vals = list(dir_counts.values())
        mean = total / 4
        variance_val = sum((v - mean) ** 2 for v in vals) / 4
        consistency = max(0, min(100, int(100 - variance_val / max(total, 1) * 10)))

    profile = {
        'user_id': user_id, 'internal_value': internal_value, 'external_value': external_value,
        'collective_value': collective_value, 'total_value': total_value, 'dominant_niche': niche,
        'dominant_direction': max(dir_counts, key=dir_counts.get) if total > 0 else None,
        'dir_counts': dir_counts, 'total_actions': total, 'current_streak': streak,
        'longest_streak': longest_streak, 'globe_points': globe_pts, 'action_consistency': consistency,
        'level': level, 'leader_status': total_value >= 100, 'updated_at': datetime.now(timezone.utc).isoformat()
    }
    profile['badges'] = [b['id'] for b in BADGES if b['condition'](profile)]
    return profile


@api_router.get("/orientation/feed/for-you/{user_id}")
async def get_personalized_feed(user_id: str):
    try:
        profile = await _build_value_profile(user_id)
        dominant_dir = profile['dominant_direction'] or 'contribution'
        niche = profile['dominant_niche']

        demo_events = await db.demo_events.find({}, {"_id": 0, "direction": 1, "timestamp": 1, "country": 1, "country_code": 1}).sort("timestamp", -1).to_list(30)

        cards = []
        user_circles = [m['circle_id'] async for m in db.circle_memberships.find({"user_id": user_id}, {"_id": 0, "circle_id": 1})]

        for i, evt in enumerate(demo_events[:12]):
            d = evt['direction']
            alias = DEMO_ALIASES[i % len(DEMO_ALIASES)]
            demo_uid = f"demo_{i % len(DEMO_ALIASES)}"
            cc = evt.get('country_code', 'IL')
            country_name = GLOBE_COUNTRY_COORDS.get(cc, {}).get('name', cc)
            # Upgraded scoring: direction + niche + circle + regional relevance
            dir_score = 1.5 if d == dominant_dir else 0.5
            niche_score = 0.3 if niche and VALUE_NICHES.get(niche, {}).get('dominant_direction') == d else 0.0
            circle_match = any(CIRCLE_DEFS.get(c, {}).get('direction') == d for c in user_circles)
            circle_score = 0.3 if circle_match else 0.0
            total_relevance = dir_score + niche_score + circle_score
            cards.append({
                'type': 'action', 'alias': alias, 'user_id': demo_uid, 'country': country_name, 'country_code': cc,
                'direction': d, 'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'action_text': FEED_ACTIONS_HE[i % len(FEED_ACTIONS_HE)],
                'impact_score': round(total_relevance * _random.uniform(3, 10), 1),
                'niche_tag': VALUE_NICHES.get(_determine_niche({d: 10, **{x: 1 for x in ['contribution', 'recovery', 'order', 'exploration'] if x != d}}, 14), {}).get('label_he', ''),
                'leader': _random.random() > 0.8, 'timestamp': evt['timestamp']
            })

        cards.insert(1, {'type': 'mission', 'mission_direction': (await _get_or_create_mission_today()).get('direction', 'contribution'), 'mission_direction_he': GLOBE_DIR_LABELS.get((await _get_or_create_mission_today()).get('direction', ''), ''), 'participants': (await _get_or_create_mission_today()).get('participants', 0), 'target': (await _get_or_create_mission_today()).get('target', 50), 'timestamp': datetime.now(timezone.utc).isoformat()})
        cards.insert(3, {'type': 'question', 'question_he': FEED_QUESTIONS_HE[_random.randint(0, len(FEED_QUESTIONS_HE) - 1)], 'direction': dominant_dir, 'direction_he': GLOBE_DIR_LABELS.get(dominant_dir, ''), 'timestamp': datetime.now(timezone.utc).isoformat()})
        cards.insert(7, {'type': 'reflection', 'reflection_he': FEED_REFLECTIONS_HE[_random.randint(0, len(FEED_REFLECTIONS_HE) - 1)], 'direction': dominant_dir, 'direction_he': GLOBE_DIR_LABELS.get(dominant_dir, ''), 'timestamp': datetime.now(timezone.utc).isoformat()})
        if profile['total_value'] > 0:
            cards.insert(5, {'type': 'leader', 'alias': 'Atlas', 'user_id': 'demo_0', 'country': 'ישראל', 'country_code': 'IL', 'direction': 'contribution', 'direction_he': 'תרומה', 'total_value': 87, 'niche_tag': 'תורם', 'leader': True, 'timestamp': datetime.now(timezone.utc).isoformat()})

        return {'success': True, 'cards': cards, 'total': len(cards), 'user_direction': dominant_dir, 'user_niche': niche, 'user_niche_he': VALUE_NICHES.get(niche, {}).get('label_he', '') if niche else ''}
    except Exception as e:
        logger.error(f"Feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/value-profile/{user_id}")
async def get_value_profile(user_id: str):
    try:
        profile = await _build_value_profile(user_id)
        niche_id = profile['dominant_niche']
        niche_data = VALUE_NICHES.get(niche_id) if niche_id else None
        next_niche = None
        if niche_id:
            niche_keys = list(VALUE_NICHES.keys())
            idx = niche_keys.index(niche_id) if niche_id in niche_keys else 0
            next_niche_id = niche_keys[(idx + 1) % len(niche_keys)]
            next_niche = {'id': next_niche_id, 'label_he': VALUE_NICHES[next_niche_id]['label_he'], 'strengthening_actions_he': VALUE_NICHES[next_niche_id]['strengthening_actions_he']}

        level = profile['level']
        thresholds = [0, 1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
        next_threshold = thresholds[min(level + 1, 10)]
        level_progress = min(100, int((profile['total_actions'] / max(next_threshold, 1)) * 100))

        milestones = []
        for label, thresh in [('פעולה ראשונה', 1), ('10 פעולות', 10), ('50 פעולות', 50), ('שבוע רצוף', None)]:
            if thresh and profile['total_actions'] >= thresh: milestones.append({'label_he': label, 'achieved': True})
            elif not thresh and profile['current_streak'] >= 7: milestones.append({'label_he': label, 'achieved': True})

        return {
            'success': True, 'user_id': user_id,
            'value_scores': {'internal': profile['internal_value'], 'external': profile['external_value'], 'collective': profile['collective_value'], 'total': profile['total_value']},
            'dominant_niche': niche_id,
            'niche': {'id': niche_id, 'label_he': niche_data['label_he'], 'description_he': niche_data['description_he'], 'strengthening_actions_he': niche_data['strengthening_actions_he']} if niche_data else None,
            'next_niche': next_niche,
            'dominant_direction': profile['dominant_direction'], 'dominant_direction_he': GLOBE_DIR_LABELS.get(profile['dominant_direction'], ''),
            'leader_status': profile['leader_status'],
            'progression': {'level': level, 'level_progress': level_progress, 'next_level_at': next_threshold, 'total_actions': profile['total_actions'],
                'badges': [{'id': b['id'], 'label_he': b['label_he'], 'desc_he': b['desc_he']} for b in BADGES if b['id'] in profile['badges']],
                'milestones': milestones, 'next_milestone_he': '10 פעולות' if profile['total_actions'] < 10 else '50 פעולות' if profile['total_actions'] < 50 else '100 פעולות'},
            'stats': {'current_streak': profile['current_streak'], 'longest_streak': profile['longest_streak'], 'action_consistency': profile['action_consistency'], 'globe_points': profile['globe_points'], 'dir_counts': profile['dir_counts']}
        }
    except Exception as e:
        logger.error(f"Value profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/niches")
async def get_niches():
    return {'success': True, 'niches': {nid: {'label_he': n['label_he'], 'description_he': n['description_he'], 'dominant_direction': n['dominant_direction'], 'strengthening_actions_he': n['strengthening_actions_he']} for nid, n in VALUE_NICHES.items()}}


@api_router.get("/orientation/subscription/plans")
async def get_subscription_plans():
    return {'success': True, 'plans': {pid: {'label_he': p['label_he'], 'price': p['price'], 'features_he': p['features_he'], 'limits': p['limits']} for pid, p in SUBSCRIPTION_PLANS.items()}}


@api_router.get("/orientation/subscription/status/{user_id}")
async def get_subscription_status(user_id: str):
    try:
        sub = await db.subscriptions.find_one({"user_id": user_id, "status": "active"}, {"_id": 0})
        if not sub:
            plan = SUBSCRIPTION_PLANS['free']
            return {'success': True, 'plan': 'free', 'plan_he': plan['label_he'], 'status': 'active', 'limits': plan['limits'], 'features_he': plan['features_he']}
        plan_id = sub.get('plan', 'free')
        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS['free'])
        return {'success': True, 'plan': plan_id, 'plan_he': plan['label_he'], 'status': sub.get('status', 'active'), 'limits': plan['limits'], 'features_he': plan['features_he'], 'expires_at': sub.get('expires_at')}
    except Exception as e:
        logger.error(f"Subscription status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/subscription/checkout")
async def create_subscription_checkout(data: dict, request: FastAPIRequest):
    try:
        plan_id = data.get('plan_id', 'plus')
        user_id = data.get('user_id', '')
        origin_url = data.get('origin_url', '')
        if plan_id not in SUBSCRIPTION_PLANS or plan_id == 'free':
            raise HTTPException(status_code=400, detail="Invalid plan")
        if not origin_url:
            raise HTTPException(status_code=400, detail="Missing origin_url")

        plan = SUBSCRIPTION_PLANS[plan_id]
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        host_url = str(request.base_url).rstrip('/')
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

        success_url = f"{origin_url}?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_id}"
        cancel_url = origin_url
        checkout_req = CheckoutSessionRequest(amount=plan['price'], currency='usd', success_url=success_url, cancel_url=cancel_url, metadata={'user_id': user_id, 'plan_id': plan_id, 'source': 'philos_subscription'})
        session = await stripe_checkout.create_checkout_session(checkout_req)

        await db.payment_transactions.insert_one({'session_id': session.session_id, 'user_id': user_id, 'amount': plan['price'], 'currency': 'usd', 'plan': plan_id, 'status': 'initiated', 'payment_status': 'pending', 'created_at': datetime.now(timezone.utc).isoformat()})
        return {'success': True, 'checkout_url': session.url, 'session_id': session.session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/subscription/checkout-status/{session_id}")
async def get_checkout_status_endpoint(session_id: str):
    try:
        tx = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx.get('payment_status') == 'paid':
            return {'success': True, 'status': 'paid', 'plan': tx.get('plan')}
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        sc = StripeCheckout(api_key=stripe_key, webhook_url="")
        status = await sc.get_checkout_status(session_id)
        await db.payment_transactions.update_one({"session_id": session_id}, {"$set": {"status": status.status, "payment_status": status.payment_status}})
        if status.payment_status == 'paid' and tx.get('payment_status') != 'paid':
            await db.subscriptions.update_one({"user_id": tx['user_id']}, {"$set": {"plan": tx['plan'], "status": "active", "session_id": session_id, "activated_at": datetime.now(timezone.utc).isoformat(), "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}}, upsert=True)
        return {'success': True, 'status': status.payment_status, 'plan': tx.get('plan'), 'amount': tx.get('amount')}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: FastAPIRequest):
    try:
        body = await request.body()
        sig = request.headers.get("Stripe-Signature", "")
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        sc = StripeCheckout(api_key=stripe_key, webhook_url="")
        event = await sc.handle_webhook(body, sig)
        if event.payment_status == 'paid' and event.session_id:
            tx = await db.payment_transactions.find_one({"session_id": event.session_id})
            if tx and tx.get('payment_status') != 'paid':
                await db.payment_transactions.update_one({"session_id": event.session_id}, {"$set": {"status": "complete", "payment_status": "paid"}})
                await db.subscriptions.update_one({"user_id": tx['user_id']}, {"$set": {"plan": tx['plan'], "status": "active", "session_id": event.session_id, "activated_at": datetime.now(timezone.utc).isoformat(), "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}}, upsert=True)
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}


# ==================== SOCIAL FIELD EXPANSION ====================

CIRCLE_DEFS = {
    'builders_of_order': {'label_he': 'בוני הסדר', 'direction': 'order', 'color': '#6366f1', 'desc_he': 'קהילה של אנשים שיוצרים מבנה ויציבות בשדה.'},
    'explorers': {'label_he': 'חוקרים', 'direction': 'exploration', 'color': '#f59e0b', 'desc_he': 'קהילה של סקרנים שמרחיבים את גבולות השדה.'},
    'contributors': {'label_he': 'תורמים', 'direction': 'contribution', 'color': '#22c55e', 'desc_he': 'קהילה של נותנים שמחזקים את הקשר בשדה.'},
    'regenerators': {'label_he': 'משקמים', 'direction': 'recovery', 'color': '#3b82f6', 'desc_he': 'קהילה של אנשים שמייצבים את הבסיס הפנימי.'},
    'social_connectors': {'label_he': 'מחברים חברתיים', 'direction': None, 'color': '#ec4899', 'desc_he': 'קהילה של מגשרים שמאחדים כיוונים שונים.'},
    'deep_thinkers': {'label_he': 'הוגים עמוקים', 'direction': None, 'color': '#8b5cf6', 'desc_he': 'קהילה של אנשים שמאזנים בין כל הכיוונים.'}
}

COMPASS_SUGGESTIONS = {
    'order': {'weak': 'exploration', 'suggestion_he': 'נסה ללמוד משהו חדש לגמרי היום — לצאת מהמבנה הרגיל.'},
    'exploration': {'weak': 'order', 'suggestion_he': 'תן מבנה למה שגילית — כתוב רשימה או תכנן צעד הבא.'},
    'contribution': {'weak': 'recovery', 'suggestion_he': 'קח זמן לעצמך היום — גם נותנים צריכים להיטען.'},
    'recovery': {'weak': 'contribution', 'suggestion_he': 'עשה משהו קטן עבור מישהו אחר — נתינה מחזקת אחרי התאוששות.'}
}


def _generate_field_narrative(dominant, dir_counts, total, momentum, region_count):
    """Generate a single symbolic Hebrew sentence about the field state. No numbers."""
    import random as _rng

    if not dominant or total == 0:
        return 'השדה שקט. ממתין לפעולה ראשונה.'

    dir_he = GLOBE_DIR_LABELS.get(dominant, '')

    # Check if one direction is clearly dominant (>40%) or if balanced
    total_safe = max(total, 1)
    dominant_pct = dir_counts.get(dominant, 0) / total_safe

    # Check for rising secondary direction
    sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)
    secondary = sorted_dirs[1] if len(sorted_dirs) > 1 else None
    secondary_he = GLOBE_DIR_LABELS.get(secondary[0], '') if secondary else ''

    if momentum == 'עולה' and dominant_pct > 0.4:
        templates = [
            f'השדה נוטה ל{dir_he} — התנועה מתחזקת',
            f'גל של {dir_he} עובר בשדה',
            f'פעילות {dir_he} עולה ברחבי השדה',
        ]
    elif momentum == 'יורד':
        templates = [
            f'השדה נרגע — {dir_he} עדיין מוביל',
            f'התנועה מאטה, {dir_he} שומר על נוכחות',
            f'השדה שוקע לשקט, עם נטייה ל{dir_he}',
        ]
    elif dominant_pct > 0.5:
        templates = [
            f'השדה נוטה בבירור ל{dir_he}',
            f'{dir_he} שולט בשדה היום',
            f'כוח ה{dir_he} דומיננטי בשדה',
        ]
    elif dominant_pct < 0.3 and secondary:
        templates = [
            f'השדה מתפצל בין {dir_he} ל{secondary_he}',
            f'מתח בין {dir_he} ל{secondary_he} — השדה בתנועה',
            f'{dir_he} ו{secondary_he} מושכים את השדה לכיוונים שונים',
        ]
    elif region_count > 4:
        templates = [
            f'{dir_he} מתייצב במספר אזורים',
            f'השדה פעיל ברחבי העולם — {dir_he} מוביל',
            f'פעילות {dir_he} מתפשטת בין אזורים',
        ]
    else:
        templates = [
            f'השדה נוטה ל{dir_he} היום',
            f'תנועת {dir_he} נמשכת בשדה',
            f'השדה חי — {dir_he} מוביל את הכיוון',
        ]

    return _rng.choice(templates)



@api_router.get("/orientation/field-dashboard")
async def get_field_dashboard():
    """Global field state: dominant direction, total actions, active regions, momentum."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday_start = (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).isoformat()

        today_events = await db.demo_events.find({"timestamp": {"$gte": today_start}}, {"_id": 0, "direction": 1, "country_code": 1}).to_list(1000)
        today_user = await db.user_globe_points.find({"timestamp": {"$gte": today_start}}, {"_id": 0, "direction": 1, "country_code": 1}).to_list(200)
        yesterday_events = await db.demo_events.count_documents({"timestamp": {"$gte": yesterday_start, "$lt": today_start}})

        all_today = today_events + today_user
        dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        region_counts = {}
        for e in all_today:
            d = e.get('direction', '')
            if d in dir_counts:
                dir_counts[d] += 1
            cc = e.get('country_code', '')
            if cc:
                region_counts[cc] = region_counts.get(cc, 0) + 1

        total_today = sum(dir_counts.values())
        dominant = max(dir_counts, key=dir_counts.get) if total_today > 0 else None
        top_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        momentum = 'עולה' if total_today > yesterday_events else ('יורד' if total_today < yesterday_events * 0.8 else 'יציב')

        # Generate symbolic narrative — one short Hebrew sentence, no numbers
        narrative = _generate_field_narrative(dominant, dir_counts, total_today, momentum, len(region_counts))

        return {
            'success': True,
            'dominant_direction': dominant,
            'dominant_direction_he': GLOBE_DIR_LABELS.get(dominant, ''),
            'total_actions_today': total_today,
            'direction_counts': dir_counts,
            'active_regions': len(region_counts),
            'top_regions': [{'code': r[0], 'name': GLOBE_COUNTRY_COORDS.get(r[0], {}).get('name', r[0]), 'count': r[1]} for r in top_regions],
            'momentum_he': momentum,
            'yesterday_total': yesterday_events,
            'field_narrative_he': narrative
        }
    except Exception as e:
        logger.error(f"Field dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/missions")
async def get_missions():
    """Active and recent missions."""
    try:
        today_mission = await _get_or_create_mission_today()
        now = datetime.now(timezone.utc)

        missions = []
        for d in ['contribution', 'recovery', 'order', 'exploration']:
            is_today = today_mission.get('direction') == d
            demo_count = _random.randint(800, 5000)
            missions.append({
                'id': f'mission-{d}',
                'title_he': {'contribution': 'חזק את הקשר', 'recovery': 'שקם את הבסיס', 'order': 'שחזר סדר', 'exploration': 'הרחב את השדה'}.get(d, ''),
                'direction': d,
                'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'description_he': {'contribution': 'עשה פעולה אחת של נתינה היום', 'recovery': 'קח זמן אחד להתאוששות', 'order': 'ארגן דבר אחד בסביבה שלך', 'exploration': 'נסה דבר חדש אחד היום'}.get(d, ''),
                'participants': today_mission.get('participants', 0) if is_today else demo_count,
                'total_field_impact': (today_mission.get('participants', 0) * 4) if is_today else demo_count * 3,
                'status': 'active' if is_today else 'available',
                'is_today': is_today
            })

        missions.sort(key=lambda m: (0 if m['is_today'] else 1, -m['participants']))
        return {'success': True, 'missions': missions}
    except Exception as e:
        logger.error(f"Missions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/missions/join")
async def join_mission(data: dict):
    """Join a mission and record action."""
    try:
        user_id = data.get('user_id', '')
        mission_id = data.get('mission_id', '')
        direction = mission_id.replace('mission-', '') if mission_id.startswith('mission-') else 'contribution'

        await db.mission_participations.insert_one({'user_id': user_id, 'mission_id': mission_id, 'direction': direction, 'timestamp': datetime.now(timezone.utc).isoformat()})

        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await db.daily_missions.update_one({"date": today}, {"$inc": {"participants": 1}})

        return {'success': True, 'message_he': 'הצטרפת למשימה!'}
    except Exception as e:
        logger.error(f"Join mission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/value-circles")
async def get_value_circles():
    """All circles with member counts."""
    try:
        circles = []
        for cid, cdef in CIRCLE_DEFS.items():
            member_count = await db.circle_memberships.count_documents({"circle_id": cid})
            demo_count = _random.randint(120, 2000)
            circles.append({
                'id': cid, 'label_he': cdef['label_he'], 'direction': cdef['direction'],
                'color': cdef['color'], 'description_he': cdef['desc_he'],
                'member_count': member_count + demo_count
            })
        return {'success': True, 'circles': circles}
    except Exception as e:
        logger.error(f"Circles error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/value-circles/join")
async def join_value_circle(data: dict):
    """Join a circle."""
    try:
        user_id = data.get('user_id', '')
        circle_id = data.get('circle_id', '')
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=400, detail="Unknown circle")

        existing = await db.circle_memberships.find_one({"user_id": user_id, "circle_id": circle_id})
        if existing:
            return {'success': True, 'message_he': 'כבר חבר במעגל', 'already_member': True}

        await db.circle_memberships.insert_one({'user_id': user_id, 'circle_id': circle_id, 'joined_at': datetime.now(timezone.utc).isoformat()})
        return {'success': True, 'message_he': 'הצטרפת למעגל!', 'already_member': False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Join circle error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/value-circles/{circle_id}")
async def get_value_circle_detail(circle_id: str, user_id: str = ""):
    """Circle detail with feed, leaderboard, missions, and membership status."""
    try:
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=404, detail="Circle not found")
        cdef = CIRCLE_DEFS[circle_id]
        member_count = await db.circle_memberships.count_documents({"circle_id": circle_id})
        demo_count = _random.randint(120, 2000)

        is_member = False
        if user_id:
            existing = await db.circle_memberships.find_one({"user_id": user_id, "circle_id": circle_id})
            is_member = existing is not None

        feed = []
        for i in range(8):
            feed.append({
                'alias': DEMO_ALIASES[i % len(DEMO_ALIASES)],
                'action_he': FEED_ACTIONS_HE[i % len(FEED_ACTIONS_HE)],
                'direction': cdef['direction'] or DIRECTIONS[i % 4],
                'impact': round(_random.uniform(3, 10), 1),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        leaderboard = []
        for i in range(5):
            leaderboard.append({
                'rank': i + 1,
                'user_id': f'demo_{i}',
                'alias': DEMO_ALIASES[i],
                'country': list(GLOBE_COUNTRY_COORDS.values())[i % len(GLOBE_COUNTRY_COORDS)].get('name', ''),
                'impact': round(_random.uniform(50, 200), 0),
                'actions': _random.randint(20, 100)
            })

        circle_dir = cdef['direction']
        missions = []
        for d in ([circle_dir] if circle_dir else DIRECTIONS[:2]):
            demo_p = _random.randint(200, 2000)
            missions.append({
                'id': f'circle-mission-{circle_id}-{d}',
                'title_he': {'contribution': 'חזק את הקשר', 'recovery': 'שקם את הבסיס', 'order': 'שחזר סדר', 'exploration': 'הרחב את השדה'}.get(d, 'משימה'),
                'direction': d,
                'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'description_he': f"משימת מעגל: {cdef['label_he']}",
                'participants': demo_p,
                'target': demo_p + _random.randint(500, 2000),
                'status': 'active'
            })

        return {
            'success': True,
            'circle': {'id': circle_id, 'label_he': cdef['label_he'], 'direction': cdef['direction'], 'color': cdef['color'], 'description_he': cdef['desc_he'], 'member_count': member_count + demo_count},
            'is_member': is_member,
            'feed': feed,
            'leaderboard': leaderboard,
            'missions': missions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circle detail error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orientation/value-circles/leave")
async def leave_value_circle(data: dict):
    """Leave a circle."""
    try:
        user_id = data.get('user_id', '')
        circle_id = data.get('circle_id', '')
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=400, detail="Unknown circle")

        result = await db.circle_memberships.delete_one({"user_id": user_id, "circle_id": circle_id})
        if result.deleted_count == 0:
            return {'success': True, 'message_he': 'לא חבר במעגל', 'was_member': False}

        return {'success': True, 'message_he': 'עזבת את המעגל', 'was_member': True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Leave circle error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/leaders")
async def get_leaders():
    """Global and regional leaderboards."""
    try:
        global_leaders = []
        for i in range(10):
            cc = list(GLOBE_COUNTRY_COORDS.keys())[i % len(GLOBE_COUNTRY_COORDS)]
            niche_keys = list(VALUE_NICHES.keys())
            niche = niche_keys[i % len(niche_keys)]
            global_leaders.append({
                'rank': i + 1,
                'user_id': f'demo_{i}',
                'alias': DEMO_ALIASES[i],
                'country': GLOBE_COUNTRY_COORDS[cc].get('name', cc),
                'country_code': cc,
                'niche_he': VALUE_NICHES[niche]['label_he'],
                'impact_score': round(500 - i * 30 + _random.uniform(-10, 10), 0),
                'actions': _random.randint(50, 200),
                'leader': True
            })

        regional = {}
        for cc, data in list(GLOBE_COUNTRY_COORDS.items())[:8]:
            regional[cc] = {
                'country_name_he': data.get('name', cc),
                'leaders': [{'rank': j + 1, 'alias': DEMO_ALIASES[(hash(cc) + j) % len(DEMO_ALIASES)], 'impact_score': round(200 - j * 25 + _random.uniform(-5, 5), 0), 'actions': _random.randint(10, 80)} for j in range(3)]
            }

        return {'success': True, 'global_leaders': global_leaders, 'regional': regional}
    except Exception as e:
        logger.error(f"Leaders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/orientation/compass-ai/{user_id}")
async def get_compass_ai(user_id: str):
    """Personal compass AI analysis."""
    try:
        profile = await _build_value_profile(user_id)
        dominant = profile['dominant_direction']
        dir_counts = profile['dir_counts']
        total = profile['total_actions']

        if total == 0:
            return {
                'success': True, 'user_id': user_id,
                'dominant_direction': None, 'dominant_direction_he': None,
                'weak_direction': None, 'weak_direction_he': None,
                'suggestion_he': 'בצע את הפעולה הראשונה שלך כדי לקבל ניתוח מצפן.',
                'niche_he': None, 'streak': 0, 'balance_score': 0
            }

        weak = min(dir_counts, key=dir_counts.get)
        suggestion = COMPASS_SUGGESTIONS.get(dominant, {}).get('suggestion_he', 'המשך בכיוון שלך.')

        vals = list(dir_counts.values())
        mean = total / 4
        variance = sum((v - mean) ** 2 for v in vals) / 4
        balance = max(0, min(100, int(100 - variance / max(total, 1) * 10)))

        niche_id = profile['dominant_niche']
        niche_he = VALUE_NICHES.get(niche_id, {}).get('label_he', '') if niche_id else None

        return {
            'success': True, 'user_id': user_id,
            'dominant_direction': dominant,
            'dominant_direction_he': GLOBE_DIR_LABELS.get(dominant, ''),
            'weak_direction': weak,
            'weak_direction_he': GLOBE_DIR_LABELS.get(weak, ''),
            'suggestion_he': suggestion,
            'niche_he': niche_he,
            'streak': profile['current_streak'],
            'balance_score': balance,
            'dir_percentages': {d: round((c / total) * 100) for d, c in dir_counts.items()} if total > 0 else {}
        }
    except Exception as e:
        logger.error(f"Compass AI error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HUMAN ACTION RECORD (PUBLIC PROFILE) ====================

# Rule-based meaning interpretation for each direction
ACTION_MEANINGS = {
    'contribution': {
        'personal_he': 'פעולה שמרחיבה את הנוכחות שלך מעבר לעצמך',
        'social_he': 'חיזוק הקשר החברתי — נתינה שמחברת בין אנשים',
        'value_he': 'ערך התרומה — העולם נבנה מפעולות של נתינה',
        'system_he': 'כוח תרומה בשדה — מגביר את הכיוון הקולקטיבי'
    },
    'recovery': {
        'personal_he': 'פעולה שמחזקת את הבסיס הפנימי שלך',
        'social_he': 'מודל של טיפול עצמי — מראה לאחרים שמותר לעצור',
        'value_he': 'ערך ההתאוששות — בנייה דורשת מנוחה',
        'system_he': 'כוח איזון בשדה — ייצוב פנימי שמקרין החוצה'
    },
    'order': {
        'personal_he': 'פעולה שיוצרת מבנה ובהירות בחיים שלך',
        'social_he': 'תרומה למסגרת — סדר אישי משפיע על הסביבה',
        'value_he': 'ערך הסדר — יציבות כבסיס לצמיחה',
        'system_he': 'כוח ארגון בשדה — מגביר את היציבות הגלובלית'
    },
    'exploration': {
        'personal_he': 'פעולה שפותחת דלתות חדשות בעולם שלך',
        'social_he': 'הרחבת אופקים — סקרנות שמזמינה אחרים לגלות',
        'value_he': 'ערך החקירה — גילוי כמנוע לשינוי',
        'system_he': 'כוח הרחבה בשדה — מגדיל את מפת האפשרויות'
    }
}


@api_router.get("/profile/{user_id}/record")
async def get_human_action_record(user_id: str):
    """Public Human Action Record — value document for any user."""
    try:
        now = datetime.now(timezone.utc)
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Alias
        alias_index = hash(user_id) % len(ANONYMOUS_ALIASES)
        alias = ANONYMOUS_ALIASES[alias_index]

        # User data
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        created_at = user.get("created_at", now.isoformat()) if user else now.isoformat()

        # Session data (force profile, history)
        session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "history": 1, "global_stats": 1})
        history = session.get("history", []) if session else []
        stats = session.get("global_stats", {}) if session else {}

        dirs = ['contribution', 'recovery', 'order', 'exploration']
        dir_counts = {d: stats.get(d, 0) for d in dirs}
        total_actions = sum(dir_counts.values())
        dominant_dir = max(dir_counts, key=dir_counts.get) if total_actions > 0 else None

        # Globe points for country
        globe_pts = await db.user_globe_points.find(
            {"user_id": user_id}, {"_id": 0, "country_code": 1}
        ).to_list(100)
        country_code = "IL"
        if globe_pts:
            codes = [p.get("country_code", "IL") for p in globe_pts]
            country_code = max(set(codes), key=codes.count)
        country_name = GLOBE_COUNTRY_COORDS.get(country_code, {}).get("name", "ישראל")

        # Niche
        niche = None
        niche_label_he = None
        if total_actions >= 5:
            for nid, ndef in VALUE_NICHES.items():
                nd = ndef.get('dominant_direction')
                if nd and dir_counts.get(nd, 0) >= ndef.get('threshold', 35):
                    niche = nid
                    niche_label_he = ndef['label_he']
                    break
            if not niche:
                for nid, ndef in VALUE_NICHES.items():
                    if not ndef.get('dominant_direction') and total_actions >= ndef.get('threshold', 20):
                        niche = nid
                        niche_label_he = ndef['label_he']
                        break

        # Daily questions for additional action data
        daily_actions = await db.daily_questions.find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("answered_at", -1).to_list(200)

        # Build chronological action record with meanings
        action_record = []
        for q in daily_actions:
            direction = q.get("direction", "")
            if not direction:
                continue
            meanings = ACTION_MEANINGS.get(direction, ACTION_MEANINGS['contribution'])
            impact = round(_random.uniform(2.0, 9.5), 1)
            action_record.append({
                'date': q.get("answered_at", q.get("date", "")),
                'direction': direction,
                'direction_he': GLOBE_DIR_LABELS.get(direction, ''),
                'action_he': q.get("question_he", q.get("action_he", FEED_ACTIONS_HE[hash(str(q.get("answered_at", ""))) % len(FEED_ACTIONS_HE)])),
                'impact': impact,
                'source': q.get("source", "daily"),
                'meanings': {
                    'personal_he': meanings['personal_he'],
                    'social_he': meanings['social_he'],
                    'value_he': meanings['value_he'],
                    'system_he': meanings['system_he']
                }
            })

        # Also include session history actions
        for h in sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]:
            d = h.get("value_tag", "")
            if not d or d not in ACTION_MEANINGS:
                continue
            meanings = ACTION_MEANINGS[d]
            action_record.append({
                'date': h.get("timestamp", ""),
                'direction': d,
                'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'action_he': h.get("action", FEED_ACTIONS_HE[hash(str(h.get("timestamp", ""))) % len(FEED_ACTIONS_HE)]),
                'impact': round(_random.uniform(2.0, 9.5), 1),
                'source': 'session',
                'meanings': {
                    'personal_he': meanings['personal_he'],
                    'social_he': meanings['social_he'],
                    'value_he': meanings['value_he'],
                    'system_he': meanings['system_he']
                }
            })

        # Dedupe by date (keep first)
        seen_dates = set()
        unique_actions = []
        for a in action_record:
            key = a['date'][:16] if a['date'] else str(len(unique_actions))
            if key not in seen_dates:
                seen_dates.add(key)
                unique_actions.append(a)
        action_record = unique_actions[:50]

        # Opposition axes (computed from direction ratios)
        if total_actions > 0:
            order_score = dir_counts.get('order', 0) / total_actions
            chaos_score = dir_counts.get('exploration', 0) / total_actions
            chaos_order = round((order_score - chaos_score + 1) / 2 * 100)

            self_score = (dir_counts.get('recovery', 0) + dir_counts.get('exploration', 0) * 0.5) / total_actions
            collective_score = (dir_counts.get('contribution', 0) + dir_counts.get('order', 0) * 0.3) / total_actions
            ego_collective = round((collective_score - self_score + 1) / 2 * 100)

            explore_score = dir_counts.get('exploration', 0) / total_actions
            stable_score = (dir_counts.get('order', 0) + dir_counts.get('recovery', 0)) / total_actions
            exploration_stability = round((stable_score - explore_score + 1) / 2 * 100)
        else:
            chaos_order = 50
            ego_collective = 50
            exploration_stability = 50

        opposition_axes = {
            'chaos_order': min(max(chaos_order, 0), 100),
            'ego_collective': min(max(ego_collective, 0), 100),
            'exploration_stability': min(max(exploration_stability, 0), 100)
        }

        # Value growth
        circle_memberships = await db.circle_memberships.count_documents({"user_id": user_id})
        badges = await db.user_badges.find({"user_id": user_id}, {"_id": 0}).to_list(50)
        badge_list = [b.get("badge_id") for b in badges]

        level = _calculate_level(total_actions)
        thresholds = [0, 1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
        next_level_at = thresholds[level + 1] if level < len(thresholds) - 1 else thresholds[-1]
        level_progress = round((total_actions / max(next_level_at, 1)) * 100) if next_level_at > 0 else 100

        # Streak
        answered = await db.daily_questions.find(
            {"user_id": user_id, "answered": True}, {"_id": 0, "date": 1}
        ).to_list(500)
        all_dates = sorted(set(q.get("date") for q in answered if q.get("date")), reverse=True)
        streak = 0
        if all_dates and all_dates[0] >= yesterday_str:
            streak = 1
            for i in range(1, len(all_dates)):
                prev = datetime.strptime(all_dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(all_dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break

        return {
            'success': True,
            'identity': {
                'user_id': user_id,
                'alias': alias,
                'country': country_name,
                'country_code': country_code,
                'dominant_direction': dominant_dir,
                'dominant_direction_he': GLOBE_DIR_LABELS.get(dominant_dir, ''),
                'niche': niche,
                'niche_label_he': niche_label_he,
                'member_since': created_at
            },
            'action_record': action_record,
            'opposition_axes': opposition_axes,
            'value_growth': {
                'total_actions': total_actions,
                'impact_score': round(total_actions * 2.5 + streak * 5, 1),
                'level': level,
                'level_progress': min(level_progress, 100),
                'next_level_at': next_level_at,
                'niche_progress': min(round((dir_counts.get(VALUE_NICHES.get(niche, {}).get('dominant_direction', ''), 0) / max(VALUE_NICHES.get(niche, {}).get('threshold', 35), 1)) * 100), 100) if niche else 0,
                'circle_memberships': circle_memberships,
                'badges': badge_list,
                'streak': streak
            },
            'direction_distribution': dir_counts
        }
    except Exception as e:
        logger.error(f"Human action record error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN ANALYTICS ====================

@api_router.get("/admin/analytics")
async def get_admin_analytics():
    """Admin analytics: DAU, actions/user, D1/D7 retention."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # --- Daily Active Users (last 7 days) ---
        dau_data = []
        for i in range(7):
            day = today_start - timedelta(days=i)
            day_end = day + timedelta(days=1)
            day_str = day.strftime('%Y-%m-%d')

            active_users = await db.daily_questions.distinct("user_id", {
                "answered_at": {"$gte": day.isoformat(), "$lt": day_end.isoformat()}
            })
            real_count = len([u for u in active_users if u and not u.startswith('demo_')])

            actions_count = await db.daily_questions.count_documents({
                "answered_at": {"$gte": day.isoformat(), "$lt": day_end.isoformat()},
                "user_id": {"$not": {"$regex": "^demo_"}}
            })

            dau_data.append({
                'date': day_str,
                'active_users': real_count,
                'total_actions': actions_count,
                'actions_per_user': round(actions_count / max(real_count, 1), 1)
            })

        # --- Retention D1 / D7 ---
        async def calc_retention(days_ago):
            cohort_day = today_start - timedelta(days=days_ago)
            cohort_end = cohort_day + timedelta(days=1)
            cohort_users = await db.users.distinct("_id", {
                "created_at": {"$gte": cohort_day.isoformat(), "$lt": cohort_end.isoformat()}
            })
            cohort_ids = [str(u) for u in cohort_users]
            if not cohort_ids:
                return {'cohort_size': 0, 'returned': 0, 'rate': 0}

            # Check who returned today
            returned = 0
            for uid in cohort_ids:
                has_action = await db.daily_questions.find_one({
                    "user_id": uid,
                    "answered_at": {"$gte": today_start.isoformat()}
                })
                if has_action:
                    returned += 1

            return {
                'cohort_size': len(cohort_ids),
                'returned': returned,
                'rate': round((returned / len(cohort_ids)) * 100, 1) if cohort_ids else 0
            }

        retention_d1 = await calc_retention(1)
        retention_d7 = await calc_retention(7)

        # --- Totals ---
        total_users = await db.users.count_documents({})
        total_actions = await db.daily_questions.count_documents({})
        total_feedback = await db.feedback.count_documents({})

        return {
            'success': True,
            'dau': dau_data,
            'retention': {'d1': retention_d1, 'd7': retention_d7},
            'totals': {'users': total_users, 'actions': total_actions, 'feedback': total_feedback},
            'generated_at': now.isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/feedback")
async def get_all_feedback():
    """List all user feedback."""
    try:
        items = []
        async for f in db.feedback.find({}, {"_id": 0}).sort("created_at", -1).limit(100):
            items.append(f)
        return {'success': True, 'feedback': items, 'count': len(items)}
    except Exception as e:
        logger.error(f"Get feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FEEDBACK ====================

@api_router.post("/feedback")
async def submit_feedback(data: dict):
    """Store user feedback."""
    try:
        text = data.get('text', '').strip()
        if not text:
            raise HTTPException(status_code=400, detail="Feedback text required")

        doc = {
            'user_id': data.get('user_id', ''),
            'text': text,
            'page': data.get('page', ''),
            'type': data.get('type', 'general'),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.feedback.insert_one(doc)
        return {'success': True, 'message_he': 'תודה על המשוב!'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ONBOARDING FIRST ACTION ====================

@api_router.post("/onboarding/first-action")
async def onboarding_first_action(data: dict):
    """Record a user's first action during onboarding and add to globe."""
    try:
        user_id = data.get('user_id', '')
        direction = data.get('direction', 'contribution')
        if direction not in DIRECTIONS:
            direction = 'contribution'

        # Record as daily question answer
        now = datetime.now(timezone.utc)
        await db.daily_questions.insert_one({
            'user_id': user_id,
            'direction': direction,
            'answered_at': now.isoformat(),
            'source': 'onboarding'
        })

        # Add globe point
        coords = list(GLOBE_COUNTRY_COORDS.values())
        random_coord = coords[_random.randint(0, len(coords) - 1)]
        await db.user_globe_points.insert_one({
            'user_id': user_id,
            'direction': direction,
            'lat': random_coord['lat'] + _random.uniform(-3, 3),
            'lng': random_coord['lng'] + _random.uniform(-3, 3),
            'country_code': random_coord.get('code', 'IL'),
            'timestamp': now.isoformat()
        })

        return {'success': True, 'message_he': 'הפעולה הראשונה שלך נשלחה לשדה!', 'direction': direction}
    except Exception as e:
        logger.error(f"Onboarding first action error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router AFTER all endpoints are defined
app.include_router(api_router)


# ==================== DEMO AGENTS SYSTEM ====================
import asyncio
import random as _random

DEMO_COUNTRIES = [
    ("Brazil", "BR"), ("India", "IN"), ("Germany", "DE"), ("USA", "US"),
    ("Japan", "JP"), ("Nigeria", "NG"), ("Israel", "IL"), ("France", "FR"),
    ("Australia", "AU"), ("South Korea", "KR"), ("Mexico", "MX"), ("UK", "GB"),
    ("Canada", "CA"), ("Italy", "IT"), ("Spain", "ES"), ("Argentina", "AR"),
    ("Turkey", "TR"), ("Thailand", "TH"), ("Poland", "PL"), ("Netherlands", "NL")
]

DEMO_ALIASES = [
    "Atlas", "Nova", "Sage", "Drift", "Ember", "Coral", "Zenith", "Flux",
    "Prism", "Echo", "Nimbus", "Pulse", "Aether", "Crest", "Dusk", "Fern",
    "Glint", "Haven", "Iris", "Jade", "Kite", "Lumen", "Mist", "Nest",
    "Opal", "Pine", "Quill", "Reef", "Spark", "Thorn", "Ursa", "Vale",
    "Wren", "Zephyr", "Amber", "Brook", "Cedar", "Dawn", "Elm", "Frost",
    "Grove", "Haze", "Ivy", "Jet", "Kelp", "Lark", "Moss", "Nyx",
    "Orion", "Peak"
]

DIRECTIONS = ['contribution', 'recovery', 'order', 'exploration']


def _build_demo_agents():
    agents = []
    for i in range(50):
        country, code = DEMO_COUNTRIES[i % len(DEMO_COUNTRIES)]
        agents.append({
            "agent_id": f"demo-agent-{i:03d}",
            "alias": DEMO_ALIASES[i],
            "country": country,
            "country_code": code,
            "orientation_direction": DIRECTIONS[i % 4]
        })
    return agents


DEMO_AGENTS = _build_demo_agents()


async def _seed_demo_agents():
    """Seed demo agents into DB if not present."""
    existing = await db.demo_agents.count_documents({})
    if existing == 0:
        await db.demo_agents.insert_many([{**a} for a in DEMO_AGENTS])
        logger.info(f"Seeded {len(DEMO_AGENTS)} demo agents")


async def _generate_demo_events():
    """Generate a batch of demo activity events."""
    now = datetime.now(timezone.utc)
    # Pick 8-15 random agents to act
    batch_size = _random.randint(8, 15)
    acting = _random.sample(DEMO_AGENTS, min(batch_size, len(DEMO_AGENTS)))

    events = []
    for agent in acting:
        # 70% chance to use their primary direction, 30% random
        if _random.random() < 0.7:
            direction = agent["orientation_direction"]
        else:
            direction = _random.choice(DIRECTIONS)

        # Spread timestamps over the last 5 minutes
        offset_seconds = _random.randint(0, 290)
        ts = (now - timedelta(seconds=offset_seconds)).isoformat()

        events.append({
            "agent_id": agent["agent_id"],
            "alias": agent["alias"],
            "country": agent["country"],
            "country_code": agent["country_code"],
            "direction": direction,
            "timestamp": ts,
            "demo": True,
            "type": "demo_action"
        })

    if events:
        await db.demo_events.insert_many(events)
        # Clean events older than 3 hours
        cutoff = (now - timedelta(hours=3)).isoformat()
        await db.demo_events.delete_many({"timestamp": {"$lt": cutoff}})

    logger.info(f"Generated {len(events)} demo events")


async def _demo_event_loop():
    """Background loop: generate demo events every 5 minutes."""
    await asyncio.sleep(5)  # Wait for DB to be ready
    await _seed_demo_agents()
    # Generate an initial batch immediately
    await _generate_demo_events()
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            await _generate_demo_events()
        except Exception as e:
            logger.error(f"Demo event generation error: {str(e)}")


@app.on_event("startup")
async def start_demo_loop():
    asyncio.create_task(_demo_event_loop())
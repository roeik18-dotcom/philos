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

        return {
            'success': True,
            'message': 'Answer recorded',
            'action_recorded': request.action_taken,
            'direction': suggested_direction,
            'impact_percent': impact_percent,
            'impact_message': impact_message,
            'mission_contributed': mission_contributed
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
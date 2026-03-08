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
    Save a decision record to persistent storage.
    """
    try:
        now = datetime.now(timezone.utc)
        doc = {
            'id': str(uuid.uuid4()),
            'user_id': data.user_id,
            'action': data.action,
            'decision': data.decision,
            'chaos_order': data.chaos_order,
            'ego_collective': data.ego_collective,
            'balance_score': data.balance_score,
            'value_tag': data.value_tag,
            'time': now.strftime('%H:%M'),
            'timestamp': now.isoformat()
        }
        
        await db.philos_decisions.insert_one(doc)
        
        return {"success": True, "id": doc['id']}
        
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
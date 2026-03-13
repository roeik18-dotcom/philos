"""Authentication and status routes."""
from fastapi import APIRouter, HTTPException, Depends
from database import db
from auth_utils import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from models.schemas import (
    StatusCheck, StatusCheckCreate, UserRegister, UserLogin,
    UserResponse, AuthResponse
)
from typing import List
from datetime import datetime, timezone
import uuid
import logging
import random as _random
import string as _string

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

@router.post("/auth/register", response_model=AuthResponse)
async def register_user(data: UserRegister):
    """
    Register a new user. Optionally accepts an invite_code.
    """
    try:
        # Check if email already exists
        existing = await db.users.find_one({"email": data.email.lower()})
        if existing:
            return AuthResponse(
                success=False,
                message="כתובת האימייל כבר קיימת במערכת"  # Email already exists
            )

        # Validate invite code if provided
        inviter_id = None
        if data.invite_code:
            invite = await db.invites.find_one({"code": data.invite_code}, {"_id": 0})
            if not invite:
                return AuthResponse(success=False, message="קוד ההזמנה אינו תקף")
            inviter_id = invite.get("inviter_id")

        # Create new user
        now = datetime.now(timezone.utc).isoformat()
        user_id = str(uuid.uuid4())

        user_doc = {
            "id": user_id,
            "email": data.email.lower(),
            "password_hash": get_password_hash(data.password),
            "created_at": now,
            "last_login_at": now,
            "invited_by": inviter_id
        }

        await db.users.insert_one(user_doc)

        # If invite code was used, track it
        if data.invite_code and inviter_id:
            await db.invites.update_one(
                {"code": data.invite_code},
                {"$push": {"used_by": user_id}, "$inc": {"use_count": 1}}
            )

        # Auto-generate 5 invite codes for the new user
        import string as _string
        for _ in range(5):
            code = "PH-" + ''.join(_random.choices(_string.ascii_uppercase + _string.digits, k=4))
            await db.invites.insert_one({
                "code": code,
                "inviter_id": user_id,
                "created_at": now,
                "used_by": [],
                "use_count": 0,
                "opened_count": 0
            })

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


@router.post("/auth/login", response_model=AuthResponse)
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

        # Ensure user has invite codes (for existing users pre-invite system)
        existing_invites = await db.invites.count_documents({"inviter_id": user["id"]})
        if existing_invites == 0:
            import string as _string
            for _ in range(5):
                code = "PH-" + ''.join(_random.choices(_string.ascii_uppercase + _string.digits, k=4))
                await db.invites.insert_one({
                    "code": code,
                    "inviter_id": user["id"],
                    "created_at": now,
                    "used_by": [],
                    "use_count": 0,
                    "opened_count": 0
                })

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


@router.post("/auth/logout")
async def logout_user():
    """
    Logout a user (client-side token removal).
    """
    return {"success": True, "message": "התנתקת בהצלחה"}  # Logged out successfully


@router.get("/auth/me", response_model=AuthResponse)
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


@router.post("/auth/migrate-data")
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



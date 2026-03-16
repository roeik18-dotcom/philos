"""Authentication and status routes."""
from fastapi import APIRouter, HTTPException, Depends
from database import db
from auth_utils import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from services.trust_integration import on_invite_used
from services.analytics import log_event, log_session
from models.schemas import (
    StatusCheck, StatusCheckCreate, UserRegister, UserLogin,
    UserResponse, AuthResponse
)
from typing import List
from datetime import datetime, timezone
import uuid
import logging
import os
import random as _random
import string as _string

from pymongo import MongoClient as _SyncClient
_sync_client = _SyncClient(os.environ.get("MONGO_URL"))
_sync_db = _sync_client[os.environ.get("DB_NAME", "philos")]

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
                message="This email address is already registered"
            )

        # Validate invite code if provided (check both old and new collections)
        inviter_id = None
        invite_code_collection = None
        if data.invite_code:
            # Check new invite_codes collection first
            new_invite = await db.invite_codes.find_one({"code": data.invite_code, "status": "active"}, {"_id": 0})
            if new_invite:
                inviter_id = new_invite.get("owner_user_id")
                invite_code_collection = "new"
            else:
                # Fallback to legacy invites collection
                old_invite = await db.invites.find_one({"code": data.invite_code}, {"_id": 0})
                if old_invite:
                    inviter_id = old_invite.get("inviter_id")
                    invite_code_collection = "legacy"
                else:
                    return AuthResponse(success=False, message="Invalid invite code")

        # Create new user
        now = datetime.now(timezone.utc).isoformat()
        user_id = str(uuid.uuid4())

        user_doc = {
            "id": user_id,
            "email": data.email.lower(),
            "password_hash": get_password_hash(data.password),
            "created_at": now,
            "last_login_at": now,
            "invited_by": inviter_id,
            "referral_user_id": data.referral_user_id,
            "referral_action_id": data.referral_action_id,
        }

        await db.users.insert_one(user_doc)

        # Track referral if present (from share links)
        if data.referral_user_id:
            await db.referrals.insert_one({
                "inviter_id": data.referral_user_id,
                "invited_user_id": user_id,
                "action_id": data.referral_action_id or "",
                "source": "share_link",
                "created_at": now,
            })

        # If invite code was used, track it
        if data.invite_code and inviter_id:
            if invite_code_collection == "new":
                await db.invite_codes.update_one(
                    {"code": data.invite_code},
                    {"$set": {"status": "used", "used_at": now, "used_by_user_id": user_id}},
                )
            else:
                await db.invites.update_one(
                    {"code": data.invite_code},
                    {"$push": {"used_by": user_id}, "$inc": {"use_count": 1}}
                )
            await on_invite_used(inviter_id)
            await log_event(inviter_id, "invite_redeemed", {"code": data.invite_code, "redeemer_id": user_id})
            await log_event(user_id, "invite_accepted", {"code": data.invite_code, "inviter_id": inviter_id})

        # Auto-generate 2 invite codes for the new user (new system)
        import string as _string
        for _ in range(2):
            code = "PH-" + ''.join(_random.choices(_string.ascii_uppercase + _string.digits, k=5))
            await db.invite_codes.insert_one({
                "code": code,
                "owner_user_id": user_id,
                "status": "active",
                "created_at": now,
                "used_at": None,
                "used_by_user_id": None,
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
            message="Registration successful!"
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
                message="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(data.password, user["password_hash"]):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Update last login
        now = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"last_login_at": now}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})

        # === ANALYTICS: Log return session ===
        await log_session(user["id"])

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
            message="Logged in successfully!"
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/logout")
async def logout_user():
    """
    Logout a user (client-side token removal).
    """
    return {"success": True, "message": "Logged out successfully"}


@router.get("/auth/me", response_model=AuthResponse)
async def get_current_user_info(user = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    if not user:
        return AuthResponse(
            success=False,
            message="Not logged in"
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
            "message": "Data migrated successfully to your account",
            "new_user_id": authenticated_user_id
        }
        
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/referrals/{user_id}")
async def get_user_referrals(user_id: str):
    """Get referrals made by a user with status and enriched info."""
    referrals = await db.referrals.find(
        {"inviter_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    enriched = []
    active_count = 0
    pending_count = 0

    for ref in referrals:
        invited_id = ref.get("invited_user_id", "")

        # Get invited user info
        invited_user = await db.users.find_one(
            {"id": invited_id}, {"_id": 0, "email": 1, "created_at": 1}
        )
        display_name = invited_user["email"].split("@")[0] if invited_user else "Unknown"

        # Check if invited user has posted any actions
        action_count = _sync_db.impact_actions.count_documents({"user_id": invited_id})

        # Get invited user's trust score
        user_trust = 0.0
        if action_count > 0:
            actions = list(_sync_db.impact_actions.find({"user_id": invited_id}))
            for a in actions:
                user_trust += a.get("trust_signal", 0)

        status = "active" if action_count > 0 else "pending"
        if status == "active":
            active_count += 1
        else:
            pending_count += 1

        enriched.append({
            "invited_user_id": invited_id,
            "display_name": display_name,
            "action_id": ref.get("action_id", ""),
            "source": ref.get("source", "share_link"),
            "status": status,
            "action_count": action_count,
            "trust_score": round(user_trust, 1),
            "created_at": ref.get("created_at", ""),
        })

    referral_trust_bonus = active_count * 2

    return {
        "success": True,
        "user_id": user_id,
        "referrals": enriched,
        "total": len(enriched),
        "active_count": active_count,
        "pending_count": pending_count,
        "referral_trust_bonus": referral_trust_bonus,
    }

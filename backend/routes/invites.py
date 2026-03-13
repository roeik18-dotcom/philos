"""Invite system API routes — clean 1:1 code model with status tracking."""
import logging
import random
import string
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from database import db
from auth_utils import get_current_user
from services.trust_integration import on_invite_used
from services.analytics import log_event

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_ACTIVE_CODES = 2


def _generate_code() -> str:
    return "PH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


@router.get("/invites/me")
async def get_my_invites(user=Depends(get_current_user)):
    """Return current user's invite codes and usage status."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = user["id"]
    docs = await db.invite_codes.find(
        {"owner_user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(20)

    codes = []
    for d in docs:
        codes.append({
            "code": d["code"],
            "status": d.get("status", "active"),
            "created_at": d.get("created_at"),
            "used_at": d.get("used_at"),
            "used_by_user_id": d.get("used_by_user_id"),
        })

    active_count = sum(1 for c in codes if c["status"] == "active")
    used_count = sum(1 for c in codes if c["status"] == "used")

    await log_event(user_id, "invite_viewed", {"active": active_count, "used": used_count})

    return {
        "success": True,
        "user_id": user_id,
        "codes": codes,
        "active_count": active_count,
        "used_count": used_count,
        "can_generate": active_count < MAX_ACTIVE_CODES,
        "invite_url_template": "/join?invite={code}",
    }


@router.post("/invites/generate")
async def generate_invite(user=Depends(get_current_user)):
    """Generate missing invite codes up to MAX_ACTIVE_CODES."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = user["id"]
    active = await db.invite_codes.count_documents({"owner_user_id": user_id, "status": "active"})

    if active >= MAX_ACTIVE_CODES:
        return {"success": False, "message": "Already have maximum active codes", "active_count": active}

    generated = []
    now = datetime.now(timezone.utc).isoformat()
    to_create = MAX_ACTIVE_CODES - active

    for _ in range(to_create):
        code = _generate_code()
        doc = {
            "code": code,
            "owner_user_id": user_id,
            "status": "active",
            "created_at": now,
            "used_at": None,
            "used_by_user_id": None,
        }
        await db.invite_codes.insert_one(doc)
        generated.append(code)
        await log_event(user_id, "invite_generated", {"code": code})

    return {
        "success": True,
        "generated": generated,
        "active_count": active + len(generated),
    }


@router.post("/invites/redeem")
async def redeem_invite(data: dict, user=Depends(get_current_user)):
    """Redeem an invite code. Links new user to inviter, fires trust + analytics."""
    code = data.get("code", "").strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="code is required")

    invite = await db.invite_codes.find_one({"code": code}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite code not found")
    if invite.get("status") != "active":
        raise HTTPException(status_code=400, detail="Invite code already used or expired")

    # Determine redeemer
    redeemer_id = None
    if user:
        redeemer_id = user["id"]
    else:
        redeemer_id = data.get("user_id")
    if not redeemer_id:
        raise HTTPException(status_code=400, detail="user_id or authentication required")

    inviter_id = invite["owner_user_id"]

    # Prevent self-redeem
    if redeemer_id == inviter_id:
        raise HTTPException(status_code=400, detail="Cannot redeem your own invite code")

    now = datetime.now(timezone.utc).isoformat()

    # Mark code as used
    await db.invite_codes.update_one(
        {"code": code},
        {"$set": {"status": "used", "used_at": now, "used_by_user_id": redeemer_id}},
    )

    # Link redeemer to inviter in users collection
    await db.users.update_one(
        {"id": redeemer_id},
        {"$set": {"invited_by": inviter_id, "invite_redeemed_at": now}},
    )

    # Trust event for inviter
    await on_invite_used(inviter_id)

    # Analytics
    await log_event(inviter_id, "invite_redeemed", {"code": code, "redeemer_id": redeemer_id})
    await log_event(redeemer_id, "invite_accepted", {"code": code, "inviter_id": inviter_id})

    logger.info(f"Invite redeemed: code={code} inviter={inviter_id} redeemer={redeemer_id}")

    return {
        "success": True,
        "code": code,
        "inviter_id": inviter_id,
        "redeemer_id": redeemer_id,
        "redeemed_at": now,
    }


@router.post("/invites/share")
async def track_invite_share(data: dict, user=Depends(get_current_user)):
    """Track when a user shares an invite link."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    code = data.get("code", "")
    await log_event(user["id"], "invite_shared", {"code": code})
    return {"success": True}



@router.get("/invites/lookup/{code}")
async def lookup_invite(code: str):
    """Public lookup for invite code — checks new system first, falls back to legacy."""
    from constants import ANONYMOUS_ALIASES

    # New system
    invite = await db.invite_codes.find_one({"code": code}, {"_id": 0})
    if invite:
        inviter_id = invite.get("owner_user_id")
        alias_index = hash(inviter_id) % len(ANONYMOUS_ALIASES) if inviter_id else 0
        return {
            "success": True,
            "code": invite["code"],
            "status": invite.get("status", "active"),
            "inviter_id": inviter_id,
            "inviter_alias": ANONYMOUS_ALIASES[alias_index] if inviter_id else None,
            "use_count": 1 if invite.get("status") == "used" else 0,
        }

    # Legacy system
    old = await db.invites.find_one({"code": code}, {"_id": 0})
    if old:
        inviter_id = old.get("inviter_id")
        alias_index = hash(inviter_id) % len(ANONYMOUS_ALIASES) if inviter_id else 0
        return {
            "success": True,
            "code": old["code"],
            "status": "active" if old.get("use_count", 0) == 0 else "used",
            "inviter_id": inviter_id,
            "inviter_alias": ANONYMOUS_ALIASES[alias_index] if inviter_id else None,
            "use_count": old.get("use_count", 0),
        }

    raise HTTPException(status_code=404, detail="Invite code not found")

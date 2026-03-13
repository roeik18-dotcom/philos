"""Admin analytics, feedback, and onboarding routes."""
from fastapi import APIRouter, HTTPException
from database import db
from constants import GLOBE_DIR_LABELS, DIRECTIONS, GLOBE_COUNTRY_COORDS
from services.trust_integration import on_onboarding_action
from datetime import datetime, timezone, timedelta
import uuid
import logging
import random as _random

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/admin/analytics")
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


@router.get("/admin/feedback")
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

@router.post("/feedback")
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

@router.post("/onboarding/first-action")
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

        # === TRUST INTEGRATION: Record value event for first onboarding action ===
        if user_id:
            await on_onboarding_action(user_id, direction)

        return {'success': True, 'message_he': 'הפעולה הראשונה שלך נשלחה לשדה!', 'direction': direction}
    except Exception as e:
        logger.error(f"Onboarding first action error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



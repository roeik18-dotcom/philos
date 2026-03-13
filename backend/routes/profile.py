"""Human Action Record (public profile) routes."""
from fastapi import APIRouter, HTTPException
from database import db
from constants import (
    GLOBE_DIR_LABELS, GLOBE_COUNTRY_COORDS, ANONYMOUS_ALIASES,
    ACTION_MEANINGS, DIRECTIONS, VALUE_NICHES, FEED_ACTIONS_HE
)
from philos_ai import interpret_profile
from services.helpers import _calculate_level
from datetime import datetime, timezone, timedelta
import logging
import random as _random

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile/{user_id}/record")
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

        # Influence chain data
        invited_by_id = user.get("invited_by") if user else None
        invited_by_alias = None
        if invited_by_id:
            alias_index_inv = hash(invited_by_id) % len(ANONYMOUS_ALIASES)
            invited_by_alias = ANONYMOUS_ALIASES[alias_index_inv]

        user_invites = await db.invites.find({"inviter_id": user_id}, {"_id": 0, "used_by": 1}).to_list(10)
        invitee_ids = []
        for inv in user_invites:
            invitee_ids.extend(inv.get("used_by", []))

        # Count active invitees
        active_invitee_count = 0
        invitee_aliases = []
        for iid in invitee_ids[:10]:
            invitee_aliases.append(ANONYMOUS_ALIASES[hash(iid) % len(ANONYMOUS_ALIASES)])
            inv_answered = await db.daily_questions.count_documents({"user_id": iid, "answered": True})
            if inv_answered > 0:
                active_invitee_count += 1

        invite_credits = user.get("invite_credits", 0) if user else 0

        trust = await _get_field_trust(user_id)

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
                'member_since': created_at,
                'invited_by_alias': invited_by_alias,
                'invited_by_id': invited_by_id
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
                'streak': streak,
                'invitees_count': len(invitee_ids)
            },
            'direction_distribution': dir_counts,
            'field_contribution': {
                'total_actions': total_actions,
                'days_active': len(all_dates),
                'field_percentage': round((total_actions / max(await db.daily_questions.count_documents({"answered": True}), 1)) * 100, 1)
            },
            'influence_chain': {
                'invited_by_alias': invited_by_alias,
                'invitees': invitee_aliases,
                'active_invitees': active_invitee_count,
                'total_invited': len(invitee_ids),
                'invite_credits': invite_credits
            },
            'ai_profile_interpretation': await interpret_profile(
                alias, GLOBE_DIR_LABELS.get(dominant_dir, ''), total_actions, streak, len(invitee_ids),
                trust_data=trust
            ),
            'field_trust': trust
        }
    except Exception as e:
        logger.error(f"Human action record error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _get_field_trust(user_id: str) -> dict:
    """Get trust data for the profile, or return zeros if none exists."""
    state = await db.user_state.find_one({"user_id": user_id}, {"_id": 0})
    if not state:
        return {"value_score": 0, "risk_score": 0, "trust_score": 0}
    return {
        "value_score": round(state.get("value_score", 0), 1),
        "risk_score": round(state.get("risk_score", 0), 1),
        "trust_score": round(state.get("trust_score", 0), 1),
    }



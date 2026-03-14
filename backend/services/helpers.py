"""Shared helper functions used across route modules."""
import logging
import random as _rng
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from database import db
from constants import (
    GLOBE_DIR_LABELS, VALUE_NICHES, BADGES, MISSION_DESCRIPTIONS,
    MISSION_TARGET, DIRECTIONS, FEED_ACTIONS_HE, FEED_QUESTIONS_HE,
    FEED_REFLECTIONS_HE, ANONYMOUS_ALIASES
)

logger = logging.getLogger(__name__)

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
    
    tag_labels = {
        'contribution': 'Contribution',
        'recovery': 'Recovery',
        'order': 'Order',
        'harm': 'Harm',
        'avoidance': 'Avoidance'
    }
    
    # 1. Most explored alternative path insight
    if alt_counts:
        top_alt = max(alt_counts.items(), key=lambda x: x[1])
        if top_alt[1] > 0:
            percentage = round((top_alt[1] / total) * 100)
            insights.append(
                f"The most explored alternative path is {tag_labels.get(top_alt[0], top_alt[0])} ({percentage}% of replays)."
            )
    
    # 2. Top transition pattern insight
    if transitions and len(transitions) > 0:
        top_trans = transitions[0]
        from_label = tag_labels.get(top_trans['from'], top_trans['from'])
        to_label = tag_labels.get(top_trans['to'], top_trans['to'])
        count = top_trans['count']
        
        if top_trans['from'] in ['harm', 'avoidance'] and top_trans['to'] in ['contribution', 'recovery', 'order']:
            insights.append(
                f"You tend to explore {to_label} paths when choosing {from_label}. "
                f"This indicates awareness of positive alternatives ({count} times)."
            )
        elif top_trans['from'] == top_trans['to']:
            pass  # Skip same-to-same
        else:
            insights.append(
                f"Most common pattern: from {from_label} to {to_label} ({count} times)."
            )
    
    # 3. Most replayed original decision type
    if orig_counts:
        top_orig = max(orig_counts.items(), key=lambda x: x[1])
        if top_orig[1] > 2:  # Only if significant
            insights.append(
                f"You frequently explore alternatives for {tag_labels.get(top_orig[0], top_orig[0])} decisions."
            )
    
    # 4. Blind spot insight
    if blind_spots and len(blind_spots) > 0:
        spot = blind_spots[0]
        from_label = tag_labels.get(spot['from'], spot['from'])
        to_label = tag_labels.get(spot['to'], spot['to'])
        insights.append(
            f"Blind spot: you have never explored a {to_label} path after a {from_label} decision."
        )
    
    # 5. Recovery-specific insight
    if alt_counts.get('recovery', 0) > alt_counts.get('order', 0) * 1.5:
        insights.append(
            "You tend to explore Recovery paths — you may feel a need for rest that is not being met."
        )
    
    # 6. Harm avoidance insight
    if alt_counts.get('harm', 0) == 0 and total > 5:
        insights.append(
            "You avoid exploring Harm paths in replays — a positive sign of value awareness."
        )
    
    # Limit to 4 most relevant insights
    return insights[:4]


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


def _generate_field_narrative(dominant, dir_counts, total, momentum, region_count):
    """Generate a single symbolic Hebrew sentence about the field state. No numbers."""
    import random as _rng

    if not dominant or total == 0:
        return 'The field is quiet. Waiting for the first action.'

    dir_he = GLOBE_DIR_LABELS.get(dominant, '')

    # Check if one direction is clearly dominant (>40%) or if balanced
    total_safe = max(total, 1)
    dominant_pct = dir_counts.get(dominant, 0) / total_safe

    # Check for rising secondary direction
    sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)
    secondary = sorted_dirs[1] if len(sorted_dirs) > 1 else None
    secondary_he = GLOBE_DIR_LABELS.get(secondary[0], '') if secondary else ''

    if momentum == 'rising' and dominant_pct > 0.4:
        templates = [
            f'The field leans toward {dir_he} — momentum is building',
            f'A wave of {dir_he} is moving through the field',
            f'{dir_he} activity is rising across the field',
        ]
    elif momentum == 'falling':
        templates = [
            f'The field is calming — {dir_he} still leads',
            f'Movement is slowing, {dir_he} maintains presence',
            f'The field is settling into stillness, leaning toward {dir_he}',
        ]
    elif dominant_pct > 0.5:
        templates = [
            f'The field clearly leans toward {dir_he}',
            f'{dir_he} dominates the field today',
            f'{dir_he} force is dominant in the field',
        ]
    elif dominant_pct < 0.3 and secondary:
        templates = [
            f'The field is split between {dir_he} and {secondary_he}',
            f'Tension between {dir_he} and {secondary_he} — the field is in motion',
            f'{dir_he} and {secondary_he} pull the field in different directions',
        ]
    elif region_count > 4:
        templates = [
            f'{dir_he} is stabilizing across multiple regions',
            f'The field is active worldwide — {dir_he} leads',
            f'{dir_he} activity is spreading across regions',
        ]
    else:
        templates = [
            f'The field leans toward {dir_he} today',
            f'{dir_he} movement continues in the field',
            f'The field is alive — {dir_he} leads the way',
        ]

    return _rng.choice(templates)





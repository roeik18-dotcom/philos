"""Orientation system routes - field, daily questions, identity, globe, invites, community."""
from fastapi import APIRouter, HTTPException, Depends
from database import db
from auth_utils import get_current_user
from models.schemas import (
    OrientationFieldResponse, WeeklyFieldSnapshot, FieldHistoryResponse,
    FieldTodayResponse, WeeklyInsightResponse, ShareCardResponse,
    OrientationIndexResponse, DirectionPercentile, UserComparisonResponse,
    DecisionPathResponse, OrientationSnapshot, OrientationIdentityResponse,
    DailyQuestionResponse, UserOrientationResponse, DriftDetectionResponse,
    DailyQuestionAnswerRequest
)
from constants import (
    DIRECTION_FORCE_MAP, DIRECTION_VECTOR_MAP, FORCE_LABELS_HE, VECTOR_LABELS_HE,
    DIRECTION_THEORY, GLOBE_COUNTRY_COORDS, GLOBE_COLOR_MAP, GLOBE_DIR_LABELS,
    BASE_DEFINITIONS, DIRECTION_TO_DEPT, DEPT_LABELS_HE,
    MISSION_DESCRIPTIONS, MISSION_TARGET, MAX_INVITE_CODES,
    ANONYMOUS_ALIASES, DIRECTIONS, VALUE_NICHES
)
from services.helpers import _get_or_create_mission_today
from services.trust_integration import on_daily_action, on_globe_point
from services.analytics import log_event
from philos_ai import interpret_action, interpret_field, interpret_profile
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import logging
import random as _random
import string as _string
import math

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/orientation/field-today", response_model=FieldTodayResponse)
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


@router.get("/orientation/field", response_model=OrientationFieldResponse)
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


@router.get("/orientation/history", response_model=FieldHistoryResponse)
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


@router.get("/orientation/compare/{user_id}", response_model=UserComparisonResponse)
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


@router.get("/decision-path/{user_id}", response_model=DecisionPathResponse)
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


@router.get("/orientation/identity/{user_id}", response_model=OrientationIdentityResponse)
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


@router.get("/orientation/daily-question/{user_id}", response_model=DailyQuestionResponse)
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


@router.post("/orientation/daily-answer/{user_id}")
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
        today_str = now.strftime("%Y-%m-%d")  # Define here for use throughout function
        if request.action_taken:
            mission = await _get_or_create_mission_today()
            if mission.get("direction") == suggested_direction:
                await db.daily_missions.update_one(
                    {"date": today_str},
                    {"$inc": {"participants": 1}}
                )
                mission_contributed = True

        # Compute identity growth data for reward feedback
        niche_info = None
        identity_link = None
        invite_reward = None
        if request.action_taken:
            session = await db.philos_sessions.find_one({"user_id": user_id}, {"_id": 0, "global_stats": 1})
            stats = session.get("global_stats", {}) if session else {}
            total_all = sum(stats.get(d, 0) for d in ['contribution', 'recovery', 'order', 'exploration'])

            # === INVITE REWARD: Check if this is the user's first action ===
            answered_count = await db.daily_questions.count_documents({"user_id": user_id, "answered": True})
            if answered_count <= 1:  # This is the first answered question
                user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "invited_by": 1})
                inviter_id = user_doc.get("invited_by") if user_doc else None
                if inviter_id:
                    # Prevent double credit
                    existing_reward = await db.invite_rewards.find_one({"inviter_id": inviter_id, "invitee_id": user_id})
                    if not existing_reward:
                        await db.users.update_one(
                            {"id": inviter_id},
                            {"$inc": {"invite_credits": 1}}
                        )
                        await db.invite_rewards.insert_one({
                            "inviter_id": inviter_id,
                            "invitee_id": user_id,
                            "credited_at": now.isoformat(),
                            "direction": suggested_direction
                        })

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

        # Check if inviter earned a credit from THIS user's previous action
        if request.action_taken:
            user_doc_check = await db.users.find_one({"id": user_id}, {"_id": 0, "invited_by": 1})
            inviter_check = user_doc_check.get("invited_by") if user_doc_check else None
            if inviter_check:
                reward_exists = await db.invite_rewards.find_one(
                    {"inviter_id": inviter_check, "invitee_id": user_id}, {"_id": 0}
                )
                if reward_exists:
                    inviter_alias_idx = hash(inviter_check) % len(ANONYMOUS_ALIASES)
                    invite_reward = {
                        "inviter_alias": ANONYMOUS_ALIASES[inviter_alias_idx],
                        "message_he": f"הפעולה הראשונה שלך העניקה נקודת ערך ל{ANONYMOUS_ALIASES[inviter_alias_idx]}"
                    }

        # === TRUST INTEGRATION: Record value event for daily action ===
        if request.action_taken:
            await on_daily_action(user_id, suggested_direction, streak)
            await log_event(user_id, "daily_action", {"direction": suggested_direction, "streak": streak})

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
            'identity_link': identity_link,
            'invite_reward': invite_reward,
            'ai_interpretation': await interpret_action(GLOBE_DIR_LABELS.get(suggested_direction, ''), DEPT_LABELS_HE.get((await db.daily_bases.find_one({"user_id": user_id, "date": today_str}, {"_id": 0, "base": 1}) or {}).get("base"))) if request.action_taken else ""
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit daily answer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/user/{user_id}", response_model=UserOrientationResponse)
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


@router.get("/orientation/drift/{user_id}", response_model=DriftDetectionResponse)
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


@router.get("/orientation/weekly-insight/{user_id}", response_model=WeeklyInsightResponse)
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


@router.get("/orientation/share/{user_id}", response_model=ShareCardResponse)
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


@router.get("/orientation/index", response_model=OrientationIndexResponse)
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


@router.get("/orientation/mission-today")
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


@router.get("/orientation/invite-report")
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

@router.get("/orientation/active-users")
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


@router.get("/orientation/relative-score/{user_id}")
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


@router.get("/orientation/circles")
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


@router.get("/orientation/streaks")
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


@router.get("/orientation/metrics-today")
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


@router.get("/orientation/feed")
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


MAX_INVITE_CODES = 5

@router.post("/orientation/create-invite/{user_id}")
async def create_invite(user_id: str):
    """Create an invite code for a user. Limited to MAX_INVITE_CODES per user."""
    try:
        import string as _string
        existing_count = await db.invites.count_documents({"inviter_id": user_id})
        if existing_count >= MAX_INVITE_CODES:
            return {"success": False, "message": "הגעת למגבלת קודי ההזמנה"}

        code = "PH-" + ''.join(_random.choices(_string.ascii_uppercase + _string.digits, k=4))
        now = datetime.now(timezone.utc)

        await db.invites.insert_one({
            "code": code,
            "inviter_id": user_id,
            "created_at": now.isoformat(),
            "used_by": [],
            "use_count": 0,
            "opened_count": 0
        })

        return {
            "success": True,
            "code": code,
            "invite_url": f"/invite/{code}"
        }
    except Exception as e:
        logger.error(f"Create invite error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/invite/{code}")
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

        # Get inviter alias
        inviter_id = invite.get("inviter_id")
        inviter_alias = None
        if inviter_id:
            alias_index = hash(inviter_id) % len(ANONYMOUS_ALIASES)
            inviter_alias = ANONYMOUS_ALIASES[alias_index]

        return {
            "success": True,
            "code": invite["code"],
            "inviter_id": inviter_id,
            "inviter_alias": inviter_alias,
            "use_count": invite.get("use_count", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get invite error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/invite-stats/{user_id}")
async def get_invite_stats(user_id: str):
    """Get a user's invite codes, stats, and influence chain."""
    try:
        # Get all invite codes for this user
        user_invites = await db.invites.find(
            {"inviter_id": user_id}, {"_id": 0}
        ).to_list(MAX_INVITE_CODES + 5)

        codes = []
        total_used = 0
        for inv in user_invites:
            used = inv.get("use_count", 0)
            total_used += used
            codes.append({
                "code": inv["code"],
                "used": used > 0,
                "use_count": used
            })

        remaining = max(0, MAX_INVITE_CODES - len(user_invites))

        # Who invited this user?
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "invited_by": 1})
        invited_by_id = user_doc.get("invited_by") if user_doc else None
        invited_by_alias = None
        if invited_by_id:
            alias_index = hash(invited_by_id) % len(ANONYMOUS_ALIASES)
            invited_by_alias = ANONYMOUS_ALIASES[alias_index]

        # Who did this user invite? (influence chain)
        invitee_ids = []
        for inv in user_invites:
            invitee_ids.extend(inv.get("used_by", []))

        invitees = []
        for iid in invitee_ids[:20]:
            alias_index = hash(iid) % len(ANONYMOUS_ALIASES)
            # Check if invitee has taken at least one action
            invitee_answered = await db.daily_questions.count_documents(
                {"user_id": iid, "answered": True}
            )
            invitees.append({
                "user_id": iid,
                "alias": ANONYMOUS_ALIASES[alias_index],
                "active": invitee_answered > 0,
                "actions": invitee_answered
            })

        active_invitees = sum(1 for i in invitees if i["active"])

        # Invite credits
        user_credit_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "invite_credits": 1})
        invite_credits = user_credit_doc.get("invite_credits", 0) if user_credit_doc else 0

        return {
            "success": True,
            "codes": codes,
            "codes_remaining": remaining,
            "total_invites_used": total_used,
            "max_codes": MAX_INVITE_CODES,
            "invited_by_id": invited_by_id,
            "invited_by_alias": invited_by_alias,
            "invitees": invitees,
            "active_invitees": active_invitees,
            "invite_credits": invite_credits
        }
    except Exception as e:
        logger.error(f"Get invite stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orientation/accept-invite/{code}/{user_id}")
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


@router.get("/orientation/weekly-report/{user_id}")
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


@router.get("/orientation/daily-opening/{user_id}")
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


@router.get("/orientation/day-summary/{user_id}")
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


@router.get("/orientation/daily-base/{user_id}")
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


@router.post("/orientation/daily-base/{user_id}")
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



@router.get("/orientation/directions")
async def get_directions():
    """Return the 4 directions with explanations and symbolic meanings."""
    return {
        "success": True,
        "directions": DIRECTION_THEORY
    }


@router.get("/orientation/force-profile/{user_id}")
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


@router.get("/orientation/value-vectors/{user_id}")
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


@router.get("/orientation/daily-summary/{user_id}")
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


@router.get("/orientation/profile/{user_id}")
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


@router.get("/orientation/globe-activity")
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


@router.post("/orientation/globe-point")
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

        # === TRUST INTEGRATION: Record value event for globe contribution ===
        if user_id:
            await on_globe_point(user_id)
            await log_event(user_id, "globe_point", {"direction": direction, "country_code": country_code})

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


@router.get("/orientation/globe-region/{country_code}")
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


@router.get("/orientation/referral-leaderboard")
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

@router.get("/orientation/highlighted-records")
async def get_highlighted_records():
    """Return highlighted public Human Action Records for ambient discovery."""
    try:
        now = datetime.now(timezone.utc)
        seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

        # Find users who have been active in the last 7 days
        recent_answers = await db.daily_questions.find(
            {"answered": True, "date": {"$gte": seven_days_ago}},
            {"_id": 0, "user_id": 1}
        ).to_list(5000)

        active_user_ids = list(set(a.get("user_id") for a in recent_answers if a.get("user_id")))

        # Gather stats for each active user
        records = []
        for uid in active_user_ids[:30]:
            user = await db.users.find_one({"id": uid}, {"_id": 0, "id": 1, "email": 1, "invited_by": 1, "created_at": 1})
            if not user:
                continue

            # Alias
            alias_index = hash(uid) % len(ANONYMOUS_ALIASES)
            alias = ANONYMOUS_ALIASES[alias_index]

            # Direction stats
            all_answers = await db.daily_questions.find(
                {"user_id": uid, "answered": True}, {"_id": 0, "suggested_direction": 1}
            ).to_list(500)

            dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
            for a in all_answers:
                d = a.get("suggested_direction", "")
                if d in dir_counts:
                    dir_counts[d] += 1

            total_actions = sum(dir_counts.values())
            dominant_dir = max(dir_counts, key=dir_counts.get) if total_actions > 0 else 'contribution'

            # Impact score
            impact_score = min(100, total_actions * 3 + len(set(d for d, c in dir_counts.items() if c > 0)) * 10)

            # Invite count
            invites = await db.invites.find({"inviter_id": uid}, {"_id": 0, "use_count": 1}).to_list(10)
            invite_count = sum(i.get("use_count", 0) for i in invites)

            # Present in the field (active in last 24h)
            yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            recent = await db.daily_questions.count_documents(
                {"user_id": uid, "answered": True, "date": {"$gte": yesterday_str}}
            )

            records.append({
                "user_id": uid,
                "alias": alias,
                "dominant_direction": dominant_dir,
                "dominant_direction_he": GLOBE_DIR_LABELS.get(dominant_dir, ''),
                "impact_score": impact_score,
                "total_actions": total_actions,
                "invite_count": invite_count,
                "present": recent > 0
            })

        # Sort by impact score descending, take top 8
        records.sort(key=lambda x: x["impact_score"], reverse=True)

        return {"success": True, "records": records[:8]}
    except Exception as e:
        logger.error(f"Get highlighted records error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


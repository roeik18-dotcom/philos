"""Collective layer and trend analysis routes."""
from fastapi import APIRouter, HTTPException
from database import db
from models.schemas import (
    CollectiveLayerResponse, DayTrend, PeriodComparison,
    CollectiveTrendsResponse
)
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/collective/layer", response_model=CollectiveLayerResponse)
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
            'contribution': 'Contribution',
            'recovery': 'Recovery',
            'order': 'Order',
            'harm': 'Harm',
            'avoidance': 'Avoidance'
        }
        
        if dominant_value:
            top_values = sorted(positive_values.items(), key=lambda x: x[1], reverse=True)[:2]
            if len(top_values) >= 2 and top_values[1][1] > 0:
                insights.append(f"The collective field currently leans toward {value_labels.get(top_values[0][0], '')} and {value_labels.get(top_values[1][0], '')}.")
            elif top_values:
                insights.append(f"The collective field currently leans toward {value_labels.get(top_values[0][0], '')}.")
        
        # Harm pressure insight
        if avg_harm_pressure < 0:
            insights.append("Average harm pressure is low.")
        elif avg_harm_pressure > 10:
            insights.append("Average harm pressure is relatively high.")
        else:
            insights.append("Average harm pressure is moderate.")
        
        # Direction insight
        if dominant_direction == 'order':
            insights.append("There is a slight increase toward Order.")
        elif dominant_direction == 'collective':
            insights.append("There is a slight increase in collective direction.")
        elif dominant_direction == 'balanced':
            insights.append("The average direction is balanced.")
        
        # Recovery insight
        if avg_recovery_stability > 10:
            insights.append("Collective recovery stability is high.")
        
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

@router.get("/collective/trends", response_model=CollectiveTrendsResponse)

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
            insights.append("The collective field moved more toward Order this week.")
        elif changes['order_drift_change'] < -3:
            insights.append("The collective field moved more toward chaos this week.")
        
        # Harm pressure insight
        if changes['harm_pressure_change'] < -5:
            insights.append("Harm pressure has decreased compared to the previous period.")
        elif changes['harm_pressure_change'] > 5:
            insights.append("Harm pressure has increased compared to the previous period.")
        
        # Recovery stability insight
        if changes['recovery_stability_change'] > 5:
            insights.append("There is an increase in collective recovery.")
        elif changes['recovery_stability_change'] < -5:
            insights.append("There is a decrease in collective recovery.")
        
        # Collective drift insight
        if changes['collective_drift_change'] > 3:
            insights.append("The collective direction is strengthening.")
        elif changes['collective_drift_change'] < -3:
            insights.append("There is a decrease in collective direction.")
        
        # Activity insight
        if changes['decisions_percent'] > 20:
            insights.append("Higher activity this week.")
        elif changes['decisions_percent'] < -20:
            insights.append("Lower activity this week.")
        
        # Stability insight
        if not insights:
            insights.append("The collective field is relatively stable compared to the previous period.")
        
        return CollectiveTrendsResponse(
            success=True,
            daily_trends=daily_trends,
            comparison=comparison,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Get collective trends error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

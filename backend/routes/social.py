"""Value engine, subscription, social field, missions, circles, and compass routes."""
from fastapi import APIRouter, HTTPException, Request as FastAPIRequest
from database import db
from constants import (
    VALUE_NICHES, BADGES, SUBSCRIPTION_PLANS,
    FEED_ACTIONS_HE, FEED_QUESTIONS_HE, FEED_REFLECTIONS_HE,
    GLOBE_DIR_LABELS, GLOBE_COUNTRY_COORDS, GLOBE_COLOR_MAP,
    CIRCLE_DEFS, COMPASS_SUGGESTIONS,
    ANONYMOUS_ALIASES, DIRECTIONS, DEMO_ALIASES
)
from services.helpers import (
    _calculate_level, _determine_niche, _build_value_profile,
    _generate_field_narrative
)
from services.trust_integration import on_mission_joined
from services.analytics import log_event
from philos_ai import interpret_field
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging
import random as _random
import os

logger = logging.getLogger(__name__)
router = APIRouter()

from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

@router.get("/orientation/feed/for-you/{user_id}")
async def get_personalized_feed(user_id: str):
    try:
        profile = await _build_value_profile(user_id)
        dominant_dir = profile['dominant_direction'] or 'contribution'
        niche = profile['dominant_niche']

        demo_events = await db.demo_events.find({}, {"_id": 0, "direction": 1, "timestamp": 1, "country": 1, "country_code": 1}).sort("timestamp", -1).to_list(30)

        cards = []
        user_circles = [m['circle_id'] async for m in db.circle_memberships.find({"user_id": user_id}, {"_id": 0, "circle_id": 1})]

        for i, evt in enumerate(demo_events[:12]):
            d = evt['direction']
            alias = DEMO_ALIASES[i % len(DEMO_ALIASES)]
            demo_uid = f"demo_{i % len(DEMO_ALIASES)}"
            cc = evt.get('country_code', 'IL')
            country_name = GLOBE_COUNTRY_COORDS.get(cc, {}).get('name', cc)
            # Upgraded scoring: direction + niche + circle + regional relevance
            dir_score = 1.5 if d == dominant_dir else 0.5
            niche_score = 0.3 if niche and VALUE_NICHES.get(niche, {}).get('dominant_direction') == d else 0.0
            circle_match = any(CIRCLE_DEFS.get(c, {}).get('direction') == d for c in user_circles)
            circle_score = 0.3 if circle_match else 0.0
            total_relevance = dir_score + niche_score + circle_score
            cards.append({
                'type': 'action', 'alias': alias, 'user_id': demo_uid, 'country': country_name, 'country_code': cc,
                'direction': d, 'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'action_text': FEED_ACTIONS_HE[i % len(FEED_ACTIONS_HE)],
                'impact_score': round(total_relevance * _random.uniform(3, 10), 1),
                'niche_tag': VALUE_NICHES.get(_determine_niche({d: 10, **{x: 1 for x in ['contribution', 'recovery', 'order', 'exploration'] if x != d}}, 14), {}).get('label_he', ''),
                'leader': _random.random() > 0.8, 'timestamp': evt['timestamp']
            })

        cards.insert(1, {'type': 'mission', 'mission_direction': (await _get_or_create_mission_today()).get('direction', 'contribution'), 'mission_direction_he': GLOBE_DIR_LABELS.get((await _get_or_create_mission_today()).get('direction', ''), ''), 'participants': (await _get_or_create_mission_today()).get('participants', 0), 'target': (await _get_or_create_mission_today()).get('target', 50), 'timestamp': datetime.now(timezone.utc).isoformat()})
        cards.insert(3, {'type': 'question', 'question_he': FEED_QUESTIONS_HE[_random.randint(0, len(FEED_QUESTIONS_HE) - 1)], 'direction': dominant_dir, 'direction_he': GLOBE_DIR_LABELS.get(dominant_dir, ''), 'timestamp': datetime.now(timezone.utc).isoformat()})
        cards.insert(7, {'type': 'reflection', 'reflection_he': FEED_REFLECTIONS_HE[_random.randint(0, len(FEED_REFLECTIONS_HE) - 1)], 'direction': dominant_dir, 'direction_he': GLOBE_DIR_LABELS.get(dominant_dir, ''), 'timestamp': datetime.now(timezone.utc).isoformat()})
        if profile['total_value'] > 0:
            cards.insert(5, {'type': 'leader', 'alias': 'Atlas', 'user_id': 'demo_0', 'country': 'Israel', 'country_code': 'IL', 'direction': 'contribution', 'direction_he': 'Contribution', 'total_value': 87, 'niche_tag': 'Contributor', 'leader': True, 'timestamp': datetime.now(timezone.utc).isoformat()})

        return {'success': True, 'cards': cards, 'total': len(cards), 'user_direction': dominant_dir, 'user_niche': niche, 'user_niche_he': VALUE_NICHES.get(niche, {}).get('label_he', '') if niche else ''}
    except Exception as e:
        logger.error(f"Feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/value-profile/{user_id}")
async def get_value_profile(user_id: str):
    try:
        profile = await _build_value_profile(user_id)
        niche_id = profile['dominant_niche']
        niche_data = VALUE_NICHES.get(niche_id) if niche_id else None
        next_niche = None
        if niche_id:
            niche_keys = list(VALUE_NICHES.keys())
            idx = niche_keys.index(niche_id) if niche_id in niche_keys else 0
            next_niche_id = niche_keys[(idx + 1) % len(niche_keys)]
            next_niche = {'id': next_niche_id, 'label_he': VALUE_NICHES[next_niche_id]['label_he'], 'strengthening_actions_he': VALUE_NICHES[next_niche_id]['strengthening_actions_he']}

        level = profile['level']
        thresholds = [0, 1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
        next_threshold = thresholds[min(level + 1, 10)]
        level_progress = min(100, int((profile['total_actions'] / max(next_threshold, 1)) * 100))

        milestones = []
        for label, thresh in [('First action', 1), ('10 actions', 10), ('50 actions', 50), ('Consecutive week', None)]:
            if thresh and profile['total_actions'] >= thresh: milestones.append({'label_he': label, 'achieved': True})
            elif not thresh and profile['current_streak'] >= 7: milestones.append({'label_he': label, 'achieved': True})

        return {
            'success': True, 'user_id': user_id,
            'value_scores': {'internal': profile['internal_value'], 'external': profile['external_value'], 'collective': profile['collective_value'], 'total': profile['total_value']},
            'dominant_niche': niche_id,
            'niche': {'id': niche_id, 'label_he': niche_data['label_he'], 'description_he': niche_data['description_he'], 'strengthening_actions_he': niche_data['strengthening_actions_he']} if niche_data else None,
            'next_niche': next_niche,
            'dominant_direction': profile['dominant_direction'], 'dominant_direction_he': GLOBE_DIR_LABELS.get(profile['dominant_direction'], ''),
            'leader_status': profile['leader_status'],
            'progression': {'level': level, 'level_progress': level_progress, 'next_level_at': next_threshold, 'total_actions': profile['total_actions'],
                'badges': [{'id': b['id'], 'label_he': b['label_he'], 'desc_he': b['desc_he']} for b in BADGES if b['id'] in profile['badges']],
                'milestones': milestones, 'next_milestone': '10 actions' if profile['total_actions'] < 10 else '50 actions' if profile['total_actions'] < 50 else '100 actions'},
            'stats': {'current_streak': profile['current_streak'], 'longest_streak': profile['longest_streak'], 'action_consistency': profile['action_consistency'], 'globe_points': profile['globe_points'], 'dir_counts': profile['dir_counts']}
        }
    except Exception as e:
        logger.error(f"Value profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/niches")
async def get_niches():
    return {'success': True, 'niches': {nid: {'label_he': n['label_he'], 'description_he': n['description_he'], 'dominant_direction': n['dominant_direction'], 'strengthening_actions_he': n['strengthening_actions_he']} for nid, n in VALUE_NICHES.items()}}


@router.get("/orientation/subscription/plans")
async def get_subscription_plans():
    return {'success': True, 'plans': {pid: {'label_he': p['label_he'], 'price': p['price'], 'features_he': p['features_he'], 'limits': p['limits']} for pid, p in SUBSCRIPTION_PLANS.items()}}


@router.get("/orientation/subscription/status/{user_id}")
async def get_subscription_status(user_id: str):
    try:
        sub = await db.subscriptions.find_one({"user_id": user_id, "status": "active"}, {"_id": 0})
        if not sub:
            plan = SUBSCRIPTION_PLANS['free']
            return {'success': True, 'plan': 'free', 'plan_he': plan['label_he'], 'status': 'active', 'limits': plan['limits'], 'features_he': plan['features_he']}
        plan_id = sub.get('plan', 'free')
        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS['free'])
        return {'success': True, 'plan': plan_id, 'plan_he': plan['label_he'], 'status': sub.get('status', 'active'), 'limits': plan['limits'], 'features_he': plan['features_he'], 'expires_at': sub.get('expires_at')}
    except Exception as e:
        logger.error(f"Subscription status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orientation/subscription/checkout")
async def create_subscription_checkout(data: dict, request: FastAPIRequest):
    try:
        plan_id = data.get('plan_id', 'plus')
        user_id = data.get('user_id', '')
        origin_url = data.get('origin_url', '')
        if plan_id not in SUBSCRIPTION_PLANS or plan_id == 'free':
            raise HTTPException(status_code=400, detail="Invalid plan")
        if not origin_url:
            raise HTTPException(status_code=400, detail="Missing origin_url")

        plan = SUBSCRIPTION_PLANS[plan_id]
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        host_url = str(request.base_url).rstrip('/')
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

        success_url = f"{origin_url}?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_id}"
        cancel_url = origin_url
        checkout_req = CheckoutSessionRequest(amount=plan['price'], currency='usd', success_url=success_url, cancel_url=cancel_url, metadata={'user_id': user_id, 'plan_id': plan_id, 'source': 'philos_subscription'})
        session = await stripe_checkout.create_checkout_session(checkout_req)

        await db.payment_transactions.insert_one({'session_id': session.session_id, 'user_id': user_id, 'amount': plan['price'], 'currency': 'usd', 'plan': plan_id, 'status': 'initiated', 'payment_status': 'pending', 'created_at': datetime.now(timezone.utc).isoformat()})
        return {'success': True, 'checkout_url': session.url, 'session_id': session.session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/subscription/checkout-status/{session_id}")
async def get_checkout_status_endpoint(session_id: str):
    try:
        tx = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx.get('payment_status') == 'paid':
            return {'success': True, 'status': 'paid', 'plan': tx.get('plan')}
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        sc = StripeCheckout(api_key=stripe_key, webhook_url="")
        status = await sc.get_checkout_status(session_id)
        await db.payment_transactions.update_one({"session_id": session_id}, {"$set": {"status": status.status, "payment_status": status.payment_status}})
        if status.payment_status == 'paid' and tx.get('payment_status') != 'paid':
            await db.subscriptions.update_one({"user_id": tx['user_id']}, {"$set": {"plan": tx['plan'], "status": "active", "session_id": session_id, "activated_at": datetime.now(timezone.utc).isoformat(), "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}}, upsert=True)
        return {'success': True, 'status': status.payment_status, 'plan': tx.get('plan'), 'amount': tx.get('amount')}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/stripe")
async def stripe_webhook(request: FastAPIRequest):
    try:
        body = await request.body()
        sig = request.headers.get("Stripe-Signature", "")
        stripe_key = os.environ.get('STRIPE_API_KEY', '')
        sc = StripeCheckout(api_key=stripe_key, webhook_url="")
        event = await sc.handle_webhook(body, sig)
        if event.payment_status == 'paid' and event.session_id:
            tx = await db.payment_transactions.find_one({"session_id": event.session_id})
            if tx and tx.get('payment_status') != 'paid':
                await db.payment_transactions.update_one({"session_id": event.session_id}, {"$set": {"status": "complete", "payment_status": "paid"}})
                await db.subscriptions.update_one({"user_id": tx['user_id']}, {"$set": {"plan": tx['plan'], "status": "active", "session_id": event.session_id, "activated_at": datetime.now(timezone.utc).isoformat(), "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}}, upsert=True)
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}



@router.get("/orientation/field-dashboard")
async def get_field_dashboard():
    """Global field state: dominant direction, total actions, active regions, momentum."""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday_start = (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).isoformat()

        today_events = await db.demo_events.find({"timestamp": {"$gte": today_start}}, {"_id": 0, "direction": 1, "country_code": 1}).to_list(1000)
        today_user = await db.user_globe_points.find({"timestamp": {"$gte": today_start}}, {"_id": 0, "direction": 1, "country_code": 1}).to_list(200)
        yesterday_events = await db.demo_events.count_documents({"timestamp": {"$gte": yesterday_start, "$lt": today_start}})

        all_today = today_events + today_user
        dir_counts = {'contribution': 0, 'recovery': 0, 'order': 0, 'exploration': 0}
        region_counts = {}
        for e in all_today:
            d = e.get('direction', '')
            if d in dir_counts:
                dir_counts[d] += 1
            cc = e.get('country_code', '')
            if cc:
                region_counts[cc] = region_counts.get(cc, 0) + 1

        total_today = sum(dir_counts.values())
        dominant = max(dir_counts, key=dir_counts.get) if total_today > 0 else None
        top_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        momentum = 'rising' if total_today > yesterday_events else ('falling' if total_today < yesterday_events * 0.8 else 'stable')

        # Generate symbolic narrative — one short Hebrew sentence, no numbers
        narrative = _generate_field_narrative(dominant, dir_counts, total_today, momentum, len(region_counts))

        # AI field interpretation
        sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)
        secondary_he = GLOBE_DIR_LABELS.get(sorted_dirs[1][0]) if len(sorted_dirs) > 1 else None
        ai_field = await interpret_field(GLOBE_DIR_LABELS.get(dominant, ''), momentum, secondary_he, len(region_counts))

        return {
            'success': True,
            'dominant_direction': dominant,
            'dominant_direction_he': GLOBE_DIR_LABELS.get(dominant, ''),
            'total_actions_today': total_today,
            'direction_counts': dir_counts,
            'active_regions': len(region_counts),
            'top_regions': [{'code': r[0], 'name': GLOBE_COUNTRY_COORDS.get(r[0], {}).get('name', r[0]), 'count': r[1]} for r in top_regions],
            'momentum_he': momentum,
            'yesterday_total': yesterday_events,
            'field_narrative_he': narrative,
            'ai_field_interpretation': ai_field
        }
    except Exception as e:
        logger.error(f"Field dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/missions")
async def get_missions():
    """Active and recent missions."""
    try:
        today_mission = await _get_or_create_mission_today()
        now = datetime.now(timezone.utc)

        missions = []
        for d in ['contribution', 'recovery', 'order', 'exploration']:
            is_today = today_mission.get('direction') == d
            demo_count = _random.randint(800, 5000)
            missions.append({
                'id': f'mission-{d}',
                'title': {'contribution': 'Strengthen the bond', 'recovery': 'Rebuild the foundation', 'order': 'Restore order', 'exploration': 'Expand the field'}.get(d, ''),
                'direction': d,
                'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'description': {'contribution': 'Do one act of giving today', 'recovery': 'Take a moment to recover', 'order': 'Organize one thing in your environment', 'exploration': 'Try one new thing today'}.get(d, ''),
                'participants': today_mission.get('participants', 0) if is_today else demo_count,
                'total_field_impact': (today_mission.get('participants', 0) * 4) if is_today else demo_count * 3,
                'status': 'active' if is_today else 'available',
                'is_today': is_today
            })

        missions.sort(key=lambda m: (0 if m['is_today'] else 1, -m['participants']))
        return {'success': True, 'missions': missions}
    except Exception as e:
        logger.error(f"Missions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orientation/missions/join")
async def join_mission(data: dict):
    """Join a mission and record action."""
    try:
        user_id = data.get('user_id', '')
        mission_id = data.get('mission_id', '')
        direction = mission_id.replace('mission-', '') if mission_id.startswith('mission-') else 'contribution'

        await db.mission_participations.insert_one({'user_id': user_id, 'mission_id': mission_id, 'direction': direction, 'timestamp': datetime.now(timezone.utc).isoformat()})

        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await db.daily_missions.update_one({"date": today}, {"$inc": {"participants": 1}})

        # === TRUST INTEGRATION: Record value event for mission participation ===
        if user_id:
            await on_mission_joined(user_id)
            await log_event(user_id, "mission_joined", {"mission_id": mission_id, "direction": direction})

        return {'success': True, 'message': 'You have joined the mission!'}
    except Exception as e:
        logger.error(f"Join mission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/value-circles")
async def get_value_circles():
    """All circles with member counts."""
    try:
        circles = []
        for cid, cdef in CIRCLE_DEFS.items():
            member_count = await db.circle_memberships.count_documents({"circle_id": cid})
            demo_count = _random.randint(120, 2000)
            circles.append({
                'id': cid, 'label_he': cdef['label_he'], 'direction': cdef['direction'],
                'color': cdef['color'], 'description_he': cdef['desc_he'],
                'member_count': member_count + demo_count
            })
        return {'success': True, 'circles': circles}
    except Exception as e:
        logger.error(f"Circles error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orientation/value-circles/join")
async def join_value_circle(data: dict):
    """Join a circle."""
    try:
        user_id = data.get('user_id', '')
        circle_id = data.get('circle_id', '')
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=400, detail="Unknown circle")

        existing = await db.circle_memberships.find_one({"user_id": user_id, "circle_id": circle_id})
        if existing:
            return {'success': True, 'message': 'Already a member of the circle', 'already_member': True}

        await db.circle_memberships.insert_one({'user_id': user_id, 'circle_id': circle_id, 'joined_at': datetime.now(timezone.utc).isoformat()})
        return {'success': True, 'message': 'You have joined the circle!', 'already_member': False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Join circle error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/value-circles/{circle_id}")
async def get_value_circle_detail(circle_id: str, user_id: str = ""):
    """Circle detail with feed, leaderboard, missions, and membership status."""
    try:
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=404, detail="Circle not found")
        cdef = CIRCLE_DEFS[circle_id]
        member_count = await db.circle_memberships.count_documents({"circle_id": circle_id})
        demo_count = _random.randint(120, 2000)

        is_member = False
        if user_id:
            existing = await db.circle_memberships.find_one({"user_id": user_id, "circle_id": circle_id})
            is_member = existing is not None

        feed = []
        for i in range(8):
            feed.append({
                'alias': DEMO_ALIASES[i % len(DEMO_ALIASES)],
                'action_he': FEED_ACTIONS_HE[i % len(FEED_ACTIONS_HE)],
                'direction': cdef['direction'] or DIRECTIONS[i % 4],
                'impact': round(_random.uniform(3, 10), 1),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        leaderboard = []
        for i in range(5):
            leaderboard.append({
                'rank': i + 1,
                'user_id': f'demo_{i}',
                'alias': DEMO_ALIASES[i],
                'country': list(GLOBE_COUNTRY_COORDS.values())[i % len(GLOBE_COUNTRY_COORDS)].get('name', ''),
                'impact': round(_random.uniform(50, 200), 0),
                'actions': _random.randint(20, 100)
            })

        circle_dir = cdef['direction']
        missions = []
        for d in ([circle_dir] if circle_dir else DIRECTIONS[:2]):
            demo_p = _random.randint(200, 2000)
            missions.append({
                'id': f'circle-mission-{circle_id}-{d}',
                'title': {'contribution': 'Strengthen the bond', 'recovery': 'Rebuild the foundation', 'order': 'Restore order', 'exploration': 'Expand the field'}.get(d, 'Mission'),
                'direction': d,
                'direction_he': GLOBE_DIR_LABELS.get(d, ''),
                'description': f"Circle mission: {cdef.get('label', cdef.get('label_he', ''))}",
                'participants': demo_p,
                'target': demo_p + _random.randint(500, 2000),
                'status': 'active'
            })

        return {
            'success': True,
            'circle': {'id': circle_id, 'label_he': cdef['label_he'], 'direction': cdef['direction'], 'color': cdef['color'], 'description_he': cdef['desc_he'], 'member_count': member_count + demo_count},
            'is_member': is_member,
            'feed': feed,
            'leaderboard': leaderboard,
            'missions': missions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circle detail error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orientation/value-circles/leave")
async def leave_value_circle(data: dict):
    """Leave a circle."""
    try:
        user_id = data.get('user_id', '')
        circle_id = data.get('circle_id', '')
        if circle_id not in CIRCLE_DEFS:
            raise HTTPException(status_code=400, detail="Unknown circle")

        result = await db.circle_memberships.delete_one({"user_id": user_id, "circle_id": circle_id})
        if result.deleted_count == 0:
            return {'success': True, 'message': 'Not a member of the circle', 'was_member': False}

        return {'success': True, 'message': 'You have left the circle', 'was_member': True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Leave circle error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/leaders")
async def get_leaders():
    """Global and regional leaderboards."""
    try:
        global_leaders = []
        for i in range(10):
            cc = list(GLOBE_COUNTRY_COORDS.keys())[i % len(GLOBE_COUNTRY_COORDS)]
            niche_keys = list(VALUE_NICHES.keys())
            niche = niche_keys[i % len(niche_keys)]
            global_leaders.append({
                'rank': i + 1,
                'user_id': f'demo_{i}',
                'alias': DEMO_ALIASES[i],
                'country': GLOBE_COUNTRY_COORDS[cc].get('name', cc),
                'country_code': cc,
                'niche_he': VALUE_NICHES[niche]['label_he'],
                'impact_score': round(500 - i * 30 + _random.uniform(-10, 10), 0),
                'actions': _random.randint(50, 200),
                'leader': True
            })

        regional = {}
        for cc, data in list(GLOBE_COUNTRY_COORDS.items())[:8]:
            regional[cc] = {
                'country_name_he': data.get('name', cc),
                'leaders': [{'rank': j + 1, 'alias': DEMO_ALIASES[(hash(cc) + j) % len(DEMO_ALIASES)], 'impact_score': round(200 - j * 25 + _random.uniform(-5, 5), 0), 'actions': _random.randint(10, 80)} for j in range(3)]
            }

        return {'success': True, 'global_leaders': global_leaders, 'regional': regional}
    except Exception as e:
        logger.error(f"Leaders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orientation/compass-ai/{user_id}")
async def get_compass_ai(user_id: str):
    """Personal compass AI analysis."""
    try:
        profile = await _build_value_profile(user_id)
        dominant = profile['dominant_direction']
        dir_counts = profile['dir_counts']
        total = profile['total_actions']

        if total == 0:
            return {
                'success': True, 'user_id': user_id,
                'dominant_direction': None, 'dominant_direction_he': None,
                'weak_direction': None, 'weak_direction_he': None,
                'suggestion': 'Perform your first action to receive a compass analysis.',
                'niche_he': None, 'streak': 0, 'balance_score': 0
            }

        weak = min(dir_counts, key=dir_counts.get)
        suggestion = COMPASS_SUGGESTIONS.get(dominant, {}).get('suggestion_he', 'Keep going in your direction.')

        vals = list(dir_counts.values())
        mean = total / 4
        variance = sum((v - mean) ** 2 for v in vals) / 4
        balance = max(0, min(100, int(100 - variance / max(total, 1) * 10)))

        niche_id = profile['dominant_niche']
        niche_he = VALUE_NICHES.get(niche_id, {}).get('label_he', '') if niche_id else None

        return {
            'success': True, 'user_id': user_id,
            'dominant_direction': dominant,
            'dominant_direction_he': GLOBE_DIR_LABELS.get(dominant, ''),
            'weak_direction': weak,
            'weak_direction_he': GLOBE_DIR_LABELS.get(weak, ''),
            'suggestion_he': suggestion,
            'niche_he': niche_he,
            'streak': profile['current_streak'],
            'balance_score': balance,
            'dir_percentages': {d: round((c / total) * 100) for d, c in dir_counts.items()} if total > 0 else {}
        }
    except Exception as e:
        logger.error(f"Compass AI error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


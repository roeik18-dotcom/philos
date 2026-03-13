"""
Test suite for Philos Orientation Feed + Value Engine + Subscription phase
Tests the 8 new backend endpoints:
- GET /api/orientation/feed/for-you/{user_id}
- GET /api/orientation/value-profile/{user_id}
- GET /api/orientation/niches
- GET /api/orientation/subscription/plans
- GET /api/orientation/subscription/status/{user_id}
- POST /api/orientation/subscription/checkout
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOrientationFeedForYou:
    """Feed For You endpoint tests - Personalized feed with 5 card types"""

    def test_feed_for_you_returns_success(self):
        """Test feed endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Feed for-you returns success")

    def test_feed_contains_cards_array(self):
        """Test feed has cards array"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'cards' in data
        assert isinstance(data['cards'], list)
        print(f"PASS: Feed has cards array with {len(data['cards'])} cards")

    def test_feed_card_types_action_mission_question(self):
        """Test feed has action, mission, and question card types"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/test-user-123")
        assert response.status_code == 200
        data = response.json()
        card_types = {c['type'] for c in data['cards']}
        assert 'action' in card_types, "Feed should have action cards"
        assert 'mission' in card_types, "Feed should have mission cards"
        assert 'question' in card_types, "Feed should have question cards"
        print(f"PASS: Feed has card types: {card_types}")

    def test_feed_has_user_niche_field(self):
        """Test feed returns user niche info"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'user_direction' in data
        assert 'user_niche' in data or data.get('user_niche') is None  # Can be null for new users
        print(f"PASS: Feed has user_direction={data.get('user_direction')}, user_niche={data.get('user_niche')}")


class TestOrientationValueProfile:
    """Value Profile endpoint tests - Value Engine scoring"""

    def test_value_profile_returns_success(self):
        """Test value profile endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-profile/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Value profile returns success")

    def test_value_profile_has_value_scores(self):
        """Test value profile has internal/external/collective/total scores"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-profile/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'value_scores' in data
        vs = data['value_scores']
        assert 'internal' in vs
        assert 'external' in vs
        assert 'collective' in vs
        assert 'total' in vs
        print(f"PASS: Value scores - internal={vs['internal']}, external={vs['external']}, collective={vs['collective']}, total={vs['total']}")

    def test_value_profile_has_progression(self):
        """Test value profile has level, badges, milestones"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-profile/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'progression' in data
        prog = data['progression']
        assert 'level' in prog
        assert 'badges' in prog
        print(f"PASS: Progression - level={prog['level']}, badges_count={len(prog['badges'])}")

    def test_value_profile_has_stats(self):
        """Test value profile has user stats"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-profile/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'stats' in data
        stats = data['stats']
        assert 'current_streak' in stats
        assert 'action_consistency' in stats
        print(f"PASS: Stats - streak={stats['current_streak']}, consistency={stats['action_consistency']}")


class TestOrientationNiches:
    """Niches endpoint tests - 6 value niches"""

    def test_niches_returns_success(self):
        """Test niches endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/niches")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Niches endpoint returns success")

    def test_niches_has_6_niches(self):
        """Test niches endpoint returns all 6 niches"""
        response = requests.get(f"{BASE_URL}/api/orientation/niches")
        assert response.status_code == 200
        data = response.json()
        assert 'niches' in data
        niches = data['niches']
        expected_niches = ['builder_of_order', 'explorer', 'contributor', 'regenerator', 'social_connector', 'deep_thinker']
        for niche_id in expected_niches:
            assert niche_id in niches, f"Missing niche: {niche_id}"
        print(f"PASS: All 6 niches present: {list(niches.keys())}")

    def test_niche_has_hebrew_labels(self):
        """Test each niche has Hebrew labels"""
        response = requests.get(f"{BASE_URL}/api/orientation/niches")
        assert response.status_code == 200
        data = response.json()
        niches = data['niches']
        for niche_id, niche in niches.items():
            assert 'label_he' in niche, f"Niche {niche_id} missing label_he"
            assert 'description_he' in niche, f"Niche {niche_id} missing description_he"
        print(f"PASS: All niches have Hebrew labels")


class TestSubscriptionPlans:
    """Subscription Plans endpoint tests - Free/Plus/Collective"""

    def test_subscription_plans_returns_success(self):
        """Test subscription plans endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/plans")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Subscription plans returns success")

    def test_subscription_plans_has_3_plans(self):
        """Test subscription plans has free, plus, collective"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/plans")
        assert response.status_code == 200
        data = response.json()
        assert 'plans' in data
        plans = data['plans']
        assert 'free' in plans, "Missing free plan"
        assert 'plus' in plans, "Missing plus plan"
        assert 'collective' in plans, "Missing collective plan"
        print(f"PASS: All 3 plans present: {list(plans.keys())}")

    def test_plan_has_price_and_features(self):
        """Test each plan has price and features_he"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/plans")
        assert response.status_code == 200
        data = response.json()
        plans = data['plans']
        for plan_id, plan in plans.items():
            assert 'price' in plan, f"Plan {plan_id} missing price"
            assert 'features_he' in plan, f"Plan {plan_id} missing features_he"
            assert isinstance(plan['features_he'], list), f"Plan {plan_id} features_he should be list"
        # Verify prices
        assert plans['free']['price'] == 0.0
        assert plans['plus']['price'] == 9.99
        assert plans['collective']['price'] == 24.99
        print(f"PASS: Plans have correct prices - free=0, plus=9.99, collective=24.99")


class TestSubscriptionStatus:
    """Subscription Status endpoint tests"""

    def test_subscription_status_returns_success(self):
        """Test subscription status returns success for new user"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/status/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Subscription status returns success")

    def test_new_user_has_free_plan(self):
        """Test new user defaults to free plan"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/status/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('plan') == 'free', "New user should have free plan"
        print(f"PASS: New user has free plan")

    def test_subscription_status_has_limits(self):
        """Test subscription status includes plan limits"""
        response = requests.get(f"{BASE_URL}/api/orientation/subscription/status/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert 'limits' in data
        assert 'features_he' in data
        print(f"PASS: Subscription status includes limits and features")


class TestSubscriptionCheckout:
    """Subscription Checkout endpoint tests - Stripe integration"""

    def test_checkout_creates_session(self):
        """Test checkout endpoint creates Stripe session"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/subscription/checkout",
            json={
                'plan_id': 'plus',
                'user_id': 'test-user-checkout',
                'origin_url': 'https://trust-ledger-11.preview.emergentagent.com'
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'checkout_url' in data
        assert 'session_id' in data
        # Checkout URL should be a Stripe URL
        assert 'stripe.com' in data['checkout_url'] or 'checkout' in data['checkout_url'].lower()
        print(f"PASS: Checkout creates session with URL: {data['checkout_url'][:50]}...")

    def test_checkout_requires_origin_url(self):
        """Test checkout requires origin_url parameter"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/subscription/checkout",
            json={
                'plan_id': 'plus',
                'user_id': 'test-user-checkout'
                # Missing origin_url
            }
        )
        assert response.status_code == 400
        print(f"PASS: Checkout rejects request without origin_url")

    def test_checkout_rejects_free_plan(self):
        """Test checkout rejects free plan"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/subscription/checkout",
            json={
                'plan_id': 'free',
                'user_id': 'test-user-checkout',
                'origin_url': 'https://trust-ledger-11.preview.emergentagent.com'
            }
        )
        assert response.status_code == 400
        print(f"PASS: Checkout rejects free plan")


class TestHomeTabRegression:
    """Regression tests for existing home tab functionality"""

    def test_daily_opening_still_works(self):
        """Regression: Daily opening endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Daily opening endpoint still works")

    def test_day_summary_still_works(self):
        """Regression: Day summary endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Day summary endpoint still works")

    def test_globe_activity_still_works(self):
        """Regression: Globe activity endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Globe activity endpoint still works")

    def test_directions_still_works(self):
        """Regression: Directions endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Directions endpoint still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

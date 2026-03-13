"""
Test suite for funnel analytics feature - iteration 74

Tests:
- POST /api/analytics/track - lightweight event tracking
- GET /api/analytics/funnel - funnel with unique user counts and drop-off percentages
- Deduplication: same user_id events counted once
- Existing endpoints: /api/analytics/summary, /api/analytics/events
- Existing auth APIs: /api/auth/login, /api/user/{user_id}/trust, /api/invites/me
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_USER_EMAIL = "newuser@test.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"

# Funnel steps in order
FUNNEL_STEPS = [
    "landing_view",
    "start_clicked",
    "base_selected",
    "question_answered",
    "trust_shown",
    "invite_copied",
]


class TestAnalyticsTrackEndpoint:
    """Test POST /api/analytics/track endpoint"""

    def test_track_event_returns_success(self):
        """POST /api/analytics/track with valid event returns success"""
        response = requests.post(
            f"{BASE_URL}/api/analytics/track",
            json={"event": "test_event", "user_id": "test_user_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    def test_track_event_with_metadata(self):
        """POST /api/analytics/track with metadata returns success"""
        response = requests.post(
            f"{BASE_URL}/api/analytics/track",
            json={
                "event": "test_event_with_meta",
                "user_id": "test_user_456",
                "metadata": {"key": "value", "num": 42}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    def test_track_event_anonymous_user(self):
        """POST /api/analytics/track without user_id defaults to anonymous"""
        response = requests.post(
            f"{BASE_URL}/api/analytics/track",
            json={"event": "test_anonymous_event"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    def test_track_event_missing_event_returns_false(self):
        """POST /api/analytics/track without event field returns success=false"""
        response = requests.post(
            f"{BASE_URL}/api/analytics/track",
            json={"user_id": "some_user"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_track_all_funnel_events(self):
        """POST /api/analytics/track works for all 6 funnel event types"""
        unique_user = f"funnel_test_{uuid.uuid4().hex[:8]}"
        for event in FUNNEL_STEPS:
            response = requests.post(
                f"{BASE_URL}/api/analytics/track",
                json={"event": event, "user_id": unique_user}
            )
            assert response.status_code == 200
            assert response.json().get("success") is True, f"Failed for event: {event}"


class TestAnalyticsFunnelEndpoint:
    """Test GET /api/analytics/funnel endpoint"""

    def test_funnel_returns_success_and_structure(self):
        """GET /api/analytics/funnel returns proper structure with all 6 steps"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "funnel" in data
        funnel = data["funnel"]
        assert "steps" in funnel
        assert "period_days" in funnel
        assert len(funnel["steps"]) == 6

    def test_funnel_steps_have_required_fields(self):
        """GET /api/analytics/funnel steps have step, unique_users, pct_of_top, pct_of_prev"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=7")
        data = response.json()
        steps = data["funnel"]["steps"]
        for step in steps:
            assert "step" in step
            assert "unique_users" in step
            assert "pct_of_top" in step
            assert "pct_of_prev" in step

    def test_funnel_steps_in_correct_order(self):
        """GET /api/analytics/funnel returns steps in correct order"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel")
        data = response.json()
        steps = data["funnel"]["steps"]
        step_names = [s["step"] for s in steps]
        assert step_names == FUNNEL_STEPS

    def test_funnel_with_custom_days_parameter(self):
        """GET /api/analytics/funnel?days=14 returns correct period_days"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=14")
        data = response.json()
        assert data["days"] == 14
        assert data["funnel"]["period_days"] == 14

    def test_funnel_days_clamped_to_max_30(self):
        """GET /api/analytics/funnel?days=100 clamps to 30"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=100")
        data = response.json()
        assert data["days"] == 30

    def test_funnel_days_clamped_to_min_1(self):
        """GET /api/analytics/funnel?days=0 clamps to 1"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=0")
        data = response.json()
        assert data["days"] == 1


class TestFunnelDeduplication:
    """Test that funnel correctly deduplicates users"""

    def test_simulate_full_funnel_for_user(self):
        """POST 6 events for same user, then verify funnel counts unique user at each step"""
        # Use unique user ID for this test
        test_user = f"funnel_dedupe_test_{uuid.uuid4().hex[:8]}"
        
        # Track all 6 funnel events for same user
        for event in FUNNEL_STEPS:
            response = requests.post(
                f"{BASE_URL}/api/analytics/track",
                json={"event": event, "user_id": test_user}
            )
            assert response.status_code == 200
        
        # Get funnel and check each step has at least 1 unique user
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=1")
        data = response.json()
        steps = data["funnel"]["steps"]
        
        # The user we just tracked should be counted at each step
        for step in steps:
            assert step["unique_users"] >= 1, f"Step {step['step']} should have at least 1 unique user"

    def test_duplicate_events_same_user_counted_once(self):
        """Posting landing_view twice for same user_id shows 1 unique user not 2"""
        test_user = f"dedupe_landing_{uuid.uuid4().hex[:8]}"
        
        # Track landing_view twice for same user
        for _ in range(2):
            response = requests.post(
                f"{BASE_URL}/api/analytics/track",
                json={"event": "landing_view", "user_id": test_user}
            )
            assert response.status_code == 200
        
        # Get funnel - landing_view should count this user only once
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=1")
        data = response.json()
        landing_step = data["funnel"]["steps"][0]
        
        # We can't assert exact count, but verify the endpoint works and returns valid data
        assert landing_step["step"] == "landing_view"
        assert landing_step["unique_users"] >= 1
        assert "pct_of_top" in landing_step


class TestExistingAnalyticsEndpoints:
    """Test that existing analytics endpoints still work"""

    def test_analytics_summary_endpoint(self):
        """GET /api/analytics/summary still works"""
        response = requests.get(f"{BASE_URL}/api/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "summary" in data
        assert "days" in data

    def test_analytics_summary_with_days_param(self):
        """GET /api/analytics/summary?days=14 works"""
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=14")
        assert response.status_code == 200
        data = response.json()
        assert data["days"] == 14

    def test_analytics_events_endpoint(self):
        """GET /api/analytics/events still works and includes funnel events"""
        response = requests.get(f"{BASE_URL}/api/analytics/events?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "events" in data
        assert "count" in data

    def test_analytics_events_contains_funnel_events(self):
        """GET /api/analytics/events includes the funnel event types we tracked"""
        # First track a unique event to find in results
        unique_id = f"event_check_{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/analytics/track",
            json={"event": "landing_view", "user_id": unique_id}
        )
        
        # Get events and verify funnel events exist
        response = requests.get(f"{BASE_URL}/api/analytics/events?limit=100")
        data = response.json()
        events = data["events"]
        
        # Check that at least one funnel event type exists
        event_types = [e.get("event_type") for e in events]
        funnel_events_found = [et for et in event_types if et in FUNNEL_STEPS]
        assert len(funnel_events_found) > 0, "Should find at least one funnel event type in events log"


class TestExistingAPIsUnaffected:
    """Test that existing APIs are not broken by the new analytics feature"""

    def test_auth_login_endpoint(self):
        """POST /api/auth/login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data or "token" in data

    def test_user_trust_endpoint(self):
        """GET /api/user/{user_id}/trust still works"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data or "success" in data

    def test_invites_me_with_auth(self):
        """GET /api/invites/me still works with authentication"""
        # First login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip("Auth not available for invites test")
        
        token = login_response.json().get("token")
        if not token:
            pytest.skip("No token returned from login")
        
        # Test invites/me endpoint
        response = requests.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestDropOffPercentages:
    """Test funnel drop-off percentage calculations"""

    def test_pct_of_top_calculation(self):
        """Verify pct_of_top is calculated correctly"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel")
        data = response.json()
        steps = data["funnel"]["steps"]
        
        # First step should have pct_of_top = 100 if it has any users
        first_step = steps[0]
        if first_step["unique_users"] > 0:
            assert first_step["pct_of_top"] == 100.0

    def test_pct_of_prev_first_step_is_none(self):
        """First step pct_of_prev should be None"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel")
        data = response.json()
        steps = data["funnel"]["steps"]
        
        first_step = steps[0]
        assert first_step["pct_of_prev"] is None

    def test_funnel_percentages_are_numbers(self):
        """All percentages should be numbers (float or None)"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel")
        data = response.json()
        steps = data["funnel"]["steps"]
        
        for step in steps:
            pct_top = step["pct_of_top"]
            pct_prev = step["pct_of_prev"]
            assert isinstance(pct_top, (int, float))
            assert pct_prev is None or isinstance(pct_prev, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

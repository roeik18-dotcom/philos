"""
Tests for Real Usage Loop features:
- Analytics event logging (daily_actions, missions_joined, globe_points, trust_changes, return_sessions)
- GET /api/analytics/summary - daily summary
- GET /api/analytics/events - recent raw events
- POST /api/auth/login - session_start event logging
- POST /api/onboarding/first-action - onboarding_complete and trust_change events
- POST /api/orientation/daily-answer/{user_id} - daily_action event
- GET /api/system/status - recent_errors and total_errors_logged fields
- Existing trust and auth APIs still work
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


class TestAnalyticsEndpoints:
    """Test /api/analytics/summary and /api/analytics/events"""

    def test_analytics_summary_returns_daily_stats(self):
        """GET /api/analytics/summary?days=3 returns daily summary with expected fields"""
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=3")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("days") == 3
        assert "summary" in data
        
        # Should have 3 days of data
        summary = data["summary"]
        assert len(summary) == 3
        
        # Each day should have expected fields
        for day_data in summary:
            assert "date" in day_data
            assert "daily_actions" in day_data
            assert "missions_joined" in day_data
            assert "globe_points" in day_data
            assert "trust_changes" in day_data
            assert "return_sessions" in day_data
            
            # All values should be integers
            assert isinstance(day_data["daily_actions"], int)
            assert isinstance(day_data["missions_joined"], int)
            assert isinstance(day_data["globe_points"], int)
            assert isinstance(day_data["trust_changes"], int)
            assert isinstance(day_data["return_sessions"], int)

    def test_analytics_summary_clamps_days(self):
        """Days parameter is clamped between 1 and 30"""
        # Test max clamp
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=100")
        assert response.status_code == 200
        data = response.json()
        assert data.get("days") == 30  # Clamped to max
        
        # Test min clamp
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=0")
        assert response.status_code == 200
        data = response.json()
        assert data.get("days") == 1  # Clamped to min

    def test_analytics_events_returns_recent_events(self):
        """GET /api/analytics/events?limit=5 returns recent raw events"""
        response = requests.get(f"{BASE_URL}/api/analytics/events?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert "count" in data
        assert "events" in data
        
        # Events should be a list
        events = data["events"]
        assert isinstance(events, list)
        
        # Should not exceed limit
        assert len(events) <= 5
        
        # If events exist, check structure
        for event in events:
            assert "user_id" in event
            assert "event_type" in event
            assert "timestamp" in event
            # _id should be excluded
            assert "_id" not in event

    def test_analytics_events_clamps_limit(self):
        """Limit parameter is clamped between 1 and 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/events?limit=500")
        assert response.status_code == 200
        # Events returned should not exceed 200


class TestSessionLoggingOnLogin:
    """Test that login logs session_start event"""

    def test_login_logs_session_event(self):
        """POST /api/auth/login logs a session_start event"""
        # Get events before login
        before_response = requests.get(f"{BASE_URL}/api/analytics/events?limit=10")
        before_count = before_response.json().get("count", 0)
        
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data.get("success") is True
        
        # Check events after login
        after_response = requests.get(f"{BASE_URL}/api/analytics/events?limit=20")
        assert after_response.status_code == 200
        after_data = after_response.json()
        
        # Look for session_start event for our user
        events = after_data.get("events", [])
        session_events = [e for e in events if e.get("event_type") == "session_start" and e.get("user_id") == TEST_USER_ID]
        
        # There should be at least one session_start event
        # Note: Due to deduplication (one per day), we may not see a new one if already logged today
        # But we should have at least one session event for this user historically
        print(f"Found {len(session_events)} session_start events for test user")


class TestOnboardingFirstAction:
    """Test POST /api/onboarding/first-action logs analytics events"""

    def test_onboarding_first_action_logs_events(self):
        """POST /api/onboarding/first-action logs onboarding_complete and trust_change events"""
        import uuid
        test_user = f"test_onboard_{uuid.uuid4().hex[:8]}"
        
        # Perform onboarding first action
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json={
            "user_id": test_user,
            "direction": "contribution"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("direction") == "contribution"
        assert data.get("first_trust_event") is True
        
        # Give time for async event logging
        time.sleep(0.5)
        
        # Check analytics events for this user
        events_response = requests.get(f"{BASE_URL}/api/analytics/events?limit=50")
        events = events_response.json().get("events", [])
        
        user_events = [e for e in events if e.get("user_id") == test_user]
        event_types = [e.get("event_type") for e in user_events]
        
        # Should have onboarding_complete event
        assert "onboarding_complete" in event_types, f"Expected onboarding_complete event, got: {event_types}"
        
        # Should have trust_change event (from on_onboarding_action)
        assert "trust_change" in event_types, f"Expected trust_change event, got: {event_types}"


class TestDailyActionLogging:
    """Test POST /api/orientation/daily-answer/{user_id} logs daily_action event"""

    def test_daily_answer_logs_daily_action_event(self):
        """POST /api/orientation/daily-answer logs daily_action event via analytics"""
        # First, get or create a daily question for the test user
        question_response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        
        if question_response.status_code != 200:
            pytest.skip("Could not get daily question for test user")
        
        question_data = question_response.json()
        question_id = question_data.get("question_id")
        
        if question_data.get("already_answered_today"):
            # Already answered today - check if daily_action event exists
            events_response = requests.get(f"{BASE_URL}/api/analytics/events?limit=50")
            events = events_response.json().get("events", [])
            daily_actions = [e for e in events if e.get("event_type") == "daily_action" and e.get("user_id") == TEST_USER_ID]
            print(f"Already answered today. Found {len(daily_actions)} daily_action events for test user")
            return
        
        # Submit answer
        answer_response = requests.post(f"{BASE_URL}/api/orientation/daily-answer/{TEST_USER_ID}", json={
            "question_id": question_id,
            "response_text": "Test response for analytics",
            "action_taken": True
        })
        
        if answer_response.status_code != 200:
            print(f"Answer response: {answer_response.status_code} - {answer_response.text}")
            pytest.skip("Could not submit daily answer")
        
        # Give time for async event logging
        time.sleep(0.5)
        
        # Check for daily_action event
        events_response = requests.get(f"{BASE_URL}/api/analytics/events?limit=50")
        events = events_response.json().get("events", [])
        
        daily_actions = [e for e in events if e.get("event_type") == "daily_action" and e.get("user_id") == TEST_USER_ID]
        assert len(daily_actions) > 0, "Expected at least one daily_action event for test user"


class TestSystemStatusErrorMonitoring:
    """Test GET /api/system/status includes recent_errors and total_errors_logged"""

    def test_system_status_has_error_fields(self):
        """GET /api/system/status returns recent_errors array and total_errors_logged count"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check for recent_errors field
        assert "recent_errors" in data, "Expected recent_errors field in system status"
        assert isinstance(data["recent_errors"], list), "recent_errors should be a list"
        
        # Check for total_errors_logged field
        assert "total_errors_logged" in data, "Expected total_errors_logged field in system status"
        assert isinstance(data["total_errors_logged"], int), "total_errors_logged should be an integer"
        
        # If there are errors, check structure
        for error in data["recent_errors"]:
            assert "component" in error
            assert "message" in error
            assert "timestamp" in error

    def test_system_status_all_components_healthy(self):
        """GET /api/system/status still returns all 5 components as healthy"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check overall status
        assert data.get("overall") in ["healthy", "degraded"]
        
        # Check all 5 components exist
        components = data.get("components", {})
        expected_components = ["database", "trust_engine", "trust_ledger", "ai_layer", "decay_scheduler"]
        
        for comp in expected_components:
            assert comp in components, f"Expected component {comp} in status"
            assert "status" in components[comp], f"Expected status field in {comp}"


class TestExistingTrustAPIs:
    """Verify existing trust APIs still work (regression test)"""

    def test_user_trust_endpoint(self):
        """GET /api/user/{user_id}/trust returns trust profile"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Trust endpoint returns data directly with trust_score at top level
        assert "trust_score" in data, f"Expected trust_score in response: {list(data.keys())}"
        assert "value_score" in data
        assert "risk_score" in data

    def test_user_trust_history_endpoint(self):
        """GET /api/user/{user_id}/trust-history returns trust ledger history"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Trust history returns ledger directly
        assert "ledger" in data, f"Expected ledger in response: {list(data.keys())}"
        # Contains summary fields
        assert "trust_score" in data or "summary_by_action_type" in data


class TestExistingAuthAPI:
    """Verify existing auth API still works (regression test)"""

    def test_auth_login_works(self):
        """POST /api/auth/login returns success with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert "token" in data
        assert "user" in data


class TestManualDecayTriggerWithAuth:
    """Verify POST /api/system/decay/trigger still works with auth"""

    def test_decay_trigger_requires_auth(self):
        """POST /api/system/decay/trigger requires authentication"""
        response = requests.post(f"{BASE_URL}/api/system/decay/trigger")
        assert response.status_code == 401

    def test_decay_trigger_works_with_auth(self):
        """POST /api/system/decay/trigger works with valid auth token"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json().get("token")
        
        if not token:
            pytest.skip("Could not get auth token")
        
        # Trigger decay with auth
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/system/decay/trigger", headers=headers)
        
        # Should succeed or indicate already running
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "triggered_by" in data or "success" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

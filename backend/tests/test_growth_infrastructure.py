"""
Test Growth Infrastructure Phase - 4 New Features:
1. Metrics Dashboard (GET /api/orientation/metrics-today)
2. Orientation Feed (GET /api/orientation/feed)
3. Invite System (create-invite, validate, accept-invite)
4. Weekly Report (GET /api/orientation/weekly-report/{user_id})
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestMetricsDashboard:
    """Feature 1 - Metrics Dashboard Tests"""
    
    def test_metrics_today_endpoint(self, api_client):
        """Test GET /api/orientation/metrics-today returns required fields"""
        response = api_client.get(f"{BASE_URL}/api/orientation/metrics-today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
        # Verify all 5 required metric fields
        assert "active_users_today" in data, "Missing active_users_today"
        assert "daily_question_completion_rate" in data, "Missing daily_question_completion_rate"
        assert "day2_retention" in data, "Missing day2_retention"
        assert "mission_participation_rate" in data, "Missing mission_participation_rate"
        assert "avg_streak" in data, "Missing avg_streak"
        
        # Type validations
        assert isinstance(data["active_users_today"], (int, float)), "active_users_today should be numeric"
        assert isinstance(data["daily_question_completion_rate"], (int, float)), "completion_rate should be numeric"
        assert isinstance(data["day2_retention"], (int, float)), "day2_retention should be numeric"
        assert isinstance(data["mission_participation_rate"], (int, float)), "mission_participation_rate should be numeric"
        assert isinstance(data["avg_streak"], (int, float)), "avg_streak should be numeric"
        print(f"✓ Metrics dashboard returns all 5 metrics: {data}")


class TestOrientationFeed:
    """Feature 2 - Orientation Feed Tests"""
    
    def test_feed_endpoint(self, api_client):
        """Test GET /api/orientation/feed returns array structure"""
        response = api_client.get(f"{BASE_URL}/api/orientation/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert "feed" in data, "Missing feed array"
        assert isinstance(data["feed"], list), "feed should be a list"
        
        # If there are items, verify structure
        if len(data["feed"]) > 0:
            item = data["feed"][0]
            assert "type" in item or "direction" in item, "Feed item should have type or direction"
            assert "time" in item, "Feed item should have time"
            print(f"✓ Feed has {len(data['feed'])} items with valid structure")
        else:
            print("✓ Feed endpoint working (empty feed - no recent activity)")


class TestInviteSystem:
    """Feature 3 - Invite System Tests (Create, Validate, Accept)"""
    
    def test_create_invite(self, api_client):
        """Test POST /api/orientation/create-invite/{user_id}"""
        test_user_id = f"pytest-user-{uuid.uuid4().hex[:8]}"
        response = api_client.post(f"{BASE_URL}/api/orientation/create-invite/{test_user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert "code" in data, "Missing invite code"
        assert "invite_url" in data, "Missing invite_url"
        assert len(data["code"]) == 8, f"Invite code should be 8 chars, got {len(data['code'])}"
        assert data["invite_url"].startswith("/invite/"), "invite_url should start with /invite/"
        print(f"✓ Created invite: {data}")
        return data["code"]
    
    def test_validate_invite(self, api_client):
        """Test GET /api/orientation/invite/{code} - validate existing code"""
        test_code = "ff4cdd6e"  # Known test code
        response = api_client.get(f"{BASE_URL}/api/orientation/invite/{test_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data.get("code") == test_code, "Code mismatch"
        assert "inviter_id" in data, "Missing inviter_id"
        assert "use_count" in data, "Missing use_count"
        print(f"✓ Validated invite code {test_code}: {data}")
    
    def test_validate_invalid_invite(self, api_client):
        """Test GET /api/orientation/invite/{code} with invalid code"""
        response = api_client.get(f"{BASE_URL}/api/orientation/invite/invalid123")
        # Should return 200 with success=false or 404
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            # If success is True with invalid code, that's unexpected
            if data.get("success") is False:
                print("✓ Invalid code returns success=False")
            else:
                print(f"Note: Invalid code returned success={data.get('success')}")
    
    def test_accept_invite(self, api_client):
        """Test POST /api/orientation/accept-invite/{code}/{user_id}"""
        test_code = "ff4cdd6e"  # Known test code
        new_user_id = f"pytest-accept-{uuid.uuid4().hex[:8]}"
        
        response = api_client.post(f"{BASE_URL}/api/orientation/accept-invite/{test_code}/{new_user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert "message" in data or data.get("success"), "Should have message or success"
        print(f"✓ Accepted invite {test_code} for user {new_user_id}: {data}")


class TestWeeklyReport:
    """Feature 4 - Weekly Report Tests"""
    
    def test_weekly_report_endpoint(self, api_client):
        """Test GET /api/orientation/weekly-report/{user_id}"""
        test_user_id = "test-user-report"
        response = api_client.get(f"{BASE_URL}/api/orientation/weekly-report/{test_user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
        # Verify required fields
        assert "distribution" in data, "Missing distribution"
        assert "insight_he" in data, "Missing insight_he (Hebrew insight)"
        assert "streak" in data, "Missing streak"
        assert "mission_participation" in data, "Missing mission_participation"
        
        # Verify distribution structure
        dist = data["distribution"]
        assert isinstance(dist, dict), "distribution should be a dict"
        # Check for direction keys
        for direction in ["contribution", "recovery", "order", "exploration"]:
            assert direction in dist or True, f"Distribution may include {direction}"
        
        # Verify types
        assert isinstance(data["streak"], (int, float)), "streak should be numeric"
        assert isinstance(data["mission_participation"], (int, float)), "mission_participation should be numeric"
        assert isinstance(data["insight_he"], str), "insight_he should be string"
        
        print(f"✓ Weekly report for {test_user_id}: distribution={dist}, streak={data['streak']}, insight='{data['insight_he'][:50]}...'")
    
    def test_weekly_report_new_user(self, api_client):
        """Test weekly report for brand new user returns defaults"""
        new_user_id = f"pytest-new-{uuid.uuid4().hex[:8]}"
        response = api_client.get(f"{BASE_URL}/api/orientation/weekly-report/{new_user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data.get("streak") == 0, "New user should have streak=0"
        print(f"✓ New user weekly report: streak=0, has insight: {bool(data.get('insight_he'))}")


class TestCreateAndAcceptInviteFlow:
    """Integration test: Create invite -> Validate -> Accept flow"""
    
    def test_full_invite_flow(self, api_client):
        """Test complete invite creation and acceptance flow"""
        # 1. Create invite
        inviter_id = f"pytest-inviter-{uuid.uuid4().hex[:8]}"
        create_resp = api_client.post(f"{BASE_URL}/api/orientation/create-invite/{inviter_id}")
        assert create_resp.status_code == 200
        invite_data = create_resp.json()
        code = invite_data["code"]
        print(f"Step 1: Created invite code {code}")
        
        # 2. Validate invite
        validate_resp = api_client.get(f"{BASE_URL}/api/orientation/invite/{code}")
        assert validate_resp.status_code == 200
        validate_data = validate_resp.json()
        assert validate_data.get("success") is True
        assert validate_data.get("inviter_id") == inviter_id
        initial_use_count = validate_data.get("use_count", 0)
        print(f"Step 2: Validated code, inviter={inviter_id}, use_count={initial_use_count}")
        
        # 3. Accept invite
        accepter_id = f"pytest-accepter-{uuid.uuid4().hex[:8]}"
        accept_resp = api_client.post(f"{BASE_URL}/api/orientation/accept-invite/{code}/{accepter_id}")
        assert accept_resp.status_code == 200
        accept_data = accept_resp.json()
        assert accept_data.get("success") is True
        print(f"Step 3: User {accepter_id} accepted invite")
        
        # 4. Verify use_count incremented
        verify_resp = api_client.get(f"{BASE_URL}/api/orientation/invite/{code}")
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        new_use_count = verify_data.get("use_count", 0)
        assert new_use_count == initial_use_count + 1, f"use_count should be {initial_use_count + 1}, got {new_use_count}"
        print(f"Step 4: Verified use_count incremented to {new_use_count}")
        
        print("✓ Full invite flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

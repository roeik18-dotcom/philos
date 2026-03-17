"""
Test Position Status Layer - Tests for movement-based status calculation
Status types: Rising, Stable, Decaying, At Risk
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_1_EMAIL = "newuser@test.com"
TEST_USER_1_PASSWORD = "password123"
TEST_USER_2_EMAIL = "trust_fragile@test.com"
TEST_USER_2_PASSWORD = "password123"


@pytest.fixture(scope="module")
def session():
    """Create a session for API calls"""
    return requests.Session()


@pytest.fixture(scope="module")
def test_user_1_auth(session):
    """Login test user 1 (has active risk signals - At Risk)"""
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_1_EMAIL,
        "password": TEST_USER_1_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "user" in data, "No user in response"
    return {
        "user_id": data["user"]["id"],
        "token": data.get("token", ""),
        "user": data["user"]
    }


@pytest.fixture(scope="module")
def test_user_2_auth(session):
    """Login test user 2 (trust_fragile - also has risk signals)"""
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_2_EMAIL,
        "password": TEST_USER_2_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "user" in data, "No user in response"
    return {
        "user_id": data["user"]["id"],
        "token": data.get("token", ""),
        "user": data["user"]
    }


class TestPositionEndpointStatus:
    """Tests for GET /api/position/{user_id} - verify status object in response"""

    def test_position_endpoint_returns_status_object(self, session, test_user_1_auth):
        """Verify position endpoint returns status object with required fields"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200, f"Position request failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        
        # Verify status object exists
        assert "status" in data, "Missing 'status' object in response"
        status = data["status"]
        
        # Verify status object has required fields
        assert "status" in status, "Missing 'status' field in status object"
        assert "icon" in status, "Missing 'icon' field in status object"
        assert "label" in status, "Missing 'label' field in status object"
        assert "color" in status, "Missing 'color' field in status object"
        assert "reason" in status, "Missing 'reason' field in status object"
        
        print(f"Position status for user 1: {status}")

    def test_position_status_valid_values(self, session, test_user_1_auth):
        """Verify status values are valid"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        status = data["status"]
        
        # Valid status values
        valid_statuses = ["rising", "stable", "decaying", "atRisk"]
        assert status["status"] in valid_statuses, f"Invalid status: {status['status']}"
        
        # Valid icon values
        valid_icons = ["up", "right", "down", "warning"]
        assert status["icon"] in valid_icons, f"Invalid icon: {status['icon']}"
        
        # Valid labels
        valid_labels = ["Rising", "Stable", "Decaying", "At Risk"]
        assert status["label"] in valid_labels, f"Invalid label: {status['label']}"
        
        # Color should be a hex color
        assert status["color"].startswith("#"), f"Color should be hex: {status['color']}"

    def test_user_with_risk_signals_shows_at_risk(self, session, test_user_1_auth):
        """User with active risk signals should show 'atRisk' status"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        status = data["status"]
        
        # User 1 has active risk signals per test setup
        # So should be atRisk
        print(f"User 1 status: {status['status']} - {status['label']} - reason: {status['reason']}")
        
        # Per the main agent's note, both test users have risk signals
        assert status["status"] == "atRisk", f"Expected atRisk, got {status['status']}"
        assert status["label"] == "At Risk"
        assert status["icon"] == "warning"
        assert "risk" in status["reason"].lower(), f"Reason should mention risk: {status['reason']}"


class TestOrientationEndpointStatus:
    """Tests for GET /api/orientation/{user_id} - verify status object in response"""

    def test_orientation_endpoint_returns_status_object(self, session, test_user_1_auth):
        """Verify orientation endpoint returns status object"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/orientation/{user_id}")
        
        assert response.status_code == 200, f"Orientation request failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        
        # Verify status object exists
        assert "status" in data, "Missing 'status' object in response"
        status = data["status"]
        
        # Verify required fields
        assert "status" in status
        assert "icon" in status
        assert "label" in status
        assert "color" in status
        assert "reason" in status
        
        print(f"Orientation status for user 1: {status}")

    def test_orientation_message_for_at_risk_user(self, session, test_user_1_auth):
        """At Risk users should get status-aware message about risk signals"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/orientation/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        status = data["status"]
        message = data.get("message", "")
        
        print(f"Status: {status['status']}, Message: {message}")
        
        # If user has risk signals, message should mention them
        if status["status"] == "atRisk":
            assert "risk" in message.lower() or "inactive" in message.lower(), \
                f"At Risk message should mention risk or inactivity: {message}"

    def test_orientation_context_fields(self, session, test_user_1_auth):
        """Verify orientation endpoint returns context with position info"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/orientation/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify context object
        assert "context" in data
        context = data["context"]
        
        assert "position" in context
        assert "label" in context
        assert "public_actions" in context
        assert "private_actions" in context
        assert "days_inactive" in context
        assert "unique_reactors" in context
        assert "active_referrals" in context


class TestStatusCalculationLogic:
    """Tests to verify status calculation rules match specification"""

    def test_position_status_with_second_user(self, session, test_user_2_auth):
        """Test position status for second user (trust_fragile)"""
        user_id = test_user_2_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        status = data["status"]
        
        print(f"User 2 position: {data['position']}, label: {data['label']}")
        print(f"User 2 status: {status['status']} - {status['label']} - reason: {status['reason']}")
        
        # Verify status object structure
        assert "status" in status
        assert "icon" in status
        assert "label" in status
        assert "color" in status
        assert "reason" in status

    def test_position_factors_present(self, session, test_user_1_auth):
        """Verify position endpoint returns breakdown factors"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify factors breakdown
        assert "factors" in data
        factors = data["factors"]
        assert "actions" in factors
        assert "reactors" in factors
        assert "trust" in factors
        assert "referrals" in factors
        
        print(f"Position factors: {factors}")


class TestPositionSnapshotPersistence:
    """Tests for position snapshot collection"""

    def test_position_call_saves_snapshot(self, session, test_user_1_auth):
        """Calling position endpoint should save a snapshot"""
        user_id = test_user_1_auth["user_id"]
        
        # Call position endpoint twice
        response1 = session.get(f"{BASE_URL}/api/position/{user_id}")
        assert response1.status_code == 200
        
        # Call again - should update snapshot for today
        response2 = session.get(f"{BASE_URL}/api/position/{user_id}")
        assert response2.status_code == 200
        
        # Both should return same position (no change in between)
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["position"] == data2["position"], "Position should be consistent"


class TestCrossEndpointConsistency:
    """Tests to verify status is consistent between position and orientation"""

    def test_status_consistent_between_endpoints(self, session, test_user_1_auth):
        """Position and orientation should return same status"""
        user_id = test_user_1_auth["user_id"]
        
        pos_response = session.get(f"{BASE_URL}/api/position/{user_id}")
        ori_response = session.get(f"{BASE_URL}/api/orientation/{user_id}")
        
        assert pos_response.status_code == 200
        assert ori_response.status_code == 200
        
        pos_data = pos_response.json()
        ori_data = ori_response.json()
        
        pos_status = pos_data["status"]["status"]
        ori_status = ori_data["status"]["status"]
        
        print(f"Position status: {pos_status}, Orientation status: {ori_status}")
        
        # Both should return same status value
        assert pos_status == ori_status, \
            f"Status mismatch: position={pos_status}, orientation={ori_status}"


class TestStatusMetadata:
    """Tests to verify status metadata (icon, color, label) is correct"""

    def test_status_metadata_mapping(self, session, test_user_1_auth):
        """Verify status metadata matches expected values"""
        user_id = test_user_1_auth["user_id"]
        response = session.get(f"{BASE_URL}/api/position/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        status = data["status"]
        
        # Expected metadata per status type
        status_metadata = {
            "rising": {"icon": "up", "label": "Rising", "color": "#10b981"},
            "stable": {"icon": "right", "label": "Stable", "color": "#f59e0b"},
            "decaying": {"icon": "down", "label": "Decaying", "color": "#ef4444"},
            "atRisk": {"icon": "warning", "label": "At Risk", "color": "#dc2626"},
        }
        
        status_type = status["status"]
        expected = status_metadata.get(status_type)
        
        if expected:
            assert status["icon"] == expected["icon"], \
                f"Wrong icon for {status_type}: expected {expected['icon']}, got {status['icon']}"
            assert status["label"] == expected["label"], \
                f"Wrong label for {status_type}: expected {expected['label']}, got {status['label']}"
            assert status["color"] == expected["color"], \
                f"Wrong color for {status_type}: expected {expected['color']}, got {status['color']}"


class TestHealthCheck:
    """Basic health check tests"""
        
    def test_login_works(self, session):
        """Verify login endpoint works"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_1_EMAIL,
            "password": TEST_USER_1_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "user" in data

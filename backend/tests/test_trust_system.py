"""
Tests for the new Value + Risk + Trust system and backend refactor verification.
Tests POST /api/actions, POST /api/risk-signal, GET /api/user/{user_id}/trust
Plus existing endpoint regression tests.
"""
import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review_request
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_returns_valid_token(self):
        """POST /api/auth/login with valid credentials returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Login failed: {data}"
        assert "token" in data, "Token not found in response"
        assert len(data["token"]) > 20, "Token seems too short"
        assert "user" in data, "User object not found"
        print(f"✓ Login successful, token received")
        return data["token"]
    
    def test_login_returns_user_info(self):
        """Login response includes user details"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        user = data["user"]
        assert user.get("email") == TEST_EMAIL
        assert "id" in user
        print(f"✓ User info returned: id={user['id']}")


class TestActionsEndpoint:
    """Tests for POST /api/actions (value recording)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200 or not response.json().get("success"):
            pytest.skip("Authentication failed - skipping authenticated tests")
        return response.json()["token"]
    
    def test_actions_requires_authentication(self):
        """POST /api/actions rejects unauthenticated requests"""
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "help",
            "impact": 50,
            "authenticity": 0.9
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Actions endpoint correctly rejects unauthenticated requests")
    
    def test_actions_rejects_invalid_action_type(self, auth_token):
        """POST /api/actions rejects invalid action_type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "invalid_type",
            "impact": 50,
            "authenticity": 0.9
        }, headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Invalid action_type" in response.text or "invalid" in response.text.lower()
        print("✓ Actions endpoint correctly rejects invalid action_type")
    
    def test_actions_create_help_action(self, auth_token):
        """POST /api/actions with help action creates value record"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        impact = 50
        authenticity = 0.9
        expected_value = math.log(1 + impact) * authenticity  # ~3.53
        
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "help",
            "impact": impact,
            "authenticity": authenticity
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "id" in data, "Action ID not returned"
        assert data.get("action_type") == "help"
        assert data.get("impact") == impact
        assert data.get("authenticity") == authenticity
        assert "value" in data, "Value not calculated"
        
        # Verify value calculation: value = log(1 + impact) * authenticity
        actual_value = data["value"]
        assert abs(actual_value - expected_value) < 0.01, f"Expected value ~{expected_value}, got {actual_value}"
        print(f"✓ Help action created with value={actual_value} (expected ~{expected_value:.2f})")
    
    def test_actions_create_action(self, auth_token):
        """Test creating 'create' action type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "create",
            "impact": 30,
            "authenticity": 0.8
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("action_type") == "create"
        print("✓ Create action type works")
    
    def test_actions_explore_action(self, auth_token):
        """Test creating 'explore' action type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "explore",
            "impact": 20,
            "authenticity": 0.7
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("action_type") == "explore"
        print("✓ Explore action type works")
    
    def test_actions_contribute_action(self, auth_token):
        """Test creating 'contribute' action type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/actions", json={
            "action_type": "contribute",
            "impact": 80,
            "authenticity": 1.0
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("action_type") == "contribute"
        print("✓ Contribute action type works")


class TestRiskSignalEndpoint:
    """Tests for POST /api/risk-signal"""
    
    def test_risk_signal_creates_record(self):
        """POST /api/risk-signal with valid data creates risk record"""
        confidence = 0.3
        severity = 2.0
        expected_risk = confidence * severity  # 0.6
        
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "spam",
            "confidence": confidence,
            "severity": severity
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "id" in data, "Signal ID not returned"
        assert data.get("signal_type") == "spam"
        assert data.get("confidence") == confidence
        assert data.get("severity") == severity
        assert "risk" in data, "Risk not calculated"
        
        # Verify risk calculation: risk = confidence * severity
        actual_risk = data["risk"]
        assert abs(actual_risk - expected_risk) < 0.001, f"Expected risk={expected_risk}, got {actual_risk}"
        print(f"✓ Risk signal created with risk={actual_risk}")
    
    def test_risk_signal_rejects_invalid_signal_type(self):
        """POST /api/risk-signal rejects invalid signal_type"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "invalid_signal",
            "confidence": 0.5,
            "severity": 1.0
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Invalid signal_type" in response.text or "invalid" in response.text.lower()
        print("✓ Risk signal endpoint correctly rejects invalid signal_type")
    
    def test_risk_signal_rejects_nonexistent_user(self):
        """POST /api/risk-signal rejects non-existent user_id"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": "nonexistent-user-id-12345",
            "signal_type": "spam",
            "confidence": 0.5,
            "severity": 1.0
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Risk signal endpoint correctly rejects non-existent user")
    
    def test_risk_signal_manipulation_type(self):
        """Test 'manipulation' signal type"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "manipulation",
            "confidence": 0.2,
            "severity": 3.0
        })
        assert response.status_code == 200
        assert response.json().get("signal_type") == "manipulation"
        print("✓ Manipulation signal type works")
    
    def test_risk_signal_aggression_type(self):
        """Test 'aggression' signal type"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "aggression",
            "confidence": 0.4,
            "severity": 4.0
        })
        assert response.status_code == 200
        assert response.json().get("signal_type") == "aggression"
        print("✓ Aggression signal type works")
    
    def test_risk_signal_deception_type(self):
        """Test 'deception' signal type"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "deception",
            "confidence": 0.5,
            "severity": 2.5
        })
        assert response.status_code == 200
        assert response.json().get("signal_type") == "deception"
        print("✓ Deception signal type works")
    
    def test_risk_signal_disruption_type(self):
        """Test 'disruption' signal type"""
        response = requests.post(f"{BASE_URL}/api/risk-signal", json={
            "user_id": TEST_USER_ID,
            "signal_type": "disruption",
            "confidence": 0.6,
            "severity": 1.5
        })
        assert response.status_code == 200
        assert response.json().get("signal_type") == "disruption"
        print("✓ Disruption signal type works")


class TestTrustProfileEndpoint:
    """Tests for GET /api/user/{user_id}/trust"""
    
    def test_trust_profile_returns_data(self):
        """GET /api/user/{user_id}/trust returns trust profile"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("user_id") == TEST_USER_ID
        assert "value_score" in data, "value_score not in response"
        assert "risk_score" in data, "risk_score not in response"
        assert "trust_score" in data, "trust_score not in response"
        assert "total_actions" in data, "total_actions not in response"
        assert "total_risk_signals" in data, "total_risk_signals not in response"
        assert "recent_actions" in data, "recent_actions not in response"
        assert "recent_risk_signals" in data, "recent_risk_signals not in response"
        
        print(f"✓ Trust profile retrieved: value={data['value_score']}, risk={data['risk_score']}, trust={data['trust_score']}")
    
    def test_trust_score_calculation(self):
        """Trust score = value_score - risk_score"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200
        data = response.json()
        
        value_score = data.get("value_score", 0)
        risk_score = data.get("risk_score", 0)
        trust_score = data.get("trust_score", 0)
        
        expected_trust = value_score - risk_score
        assert abs(trust_score - expected_trust) < 0.01, f"Trust score mismatch: {trust_score} != {value_score} - {risk_score}"
        print(f"✓ Trust calculation verified: {trust_score} = {value_score} - {risk_score}")
    
    def test_trust_profile_nonexistent_user(self):
        """GET /api/user/{user_id}/trust returns 404 for non-existent user"""
        response = requests.get(f"{BASE_URL}/api/user/nonexistent-user-12345/trust")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Trust profile returns 404 for non-existent user")


class TestFieldDashboard:
    """Tests for GET /api/orientation/field-dashboard (AI Interpretation)"""
    
    def test_field_dashboard_returns_success(self):
        """Field dashboard returns success and AI interpretation"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True
        assert "ai_field_interpretation" in data, "ai_field_interpretation missing"
        assert "dominant_direction" in data
        assert "momentum_he" in data
        
        # AI interpretation should be Hebrew
        ai_text = data.get("ai_field_interpretation", "")
        if ai_text:  # May be empty if no API key
            # Check for Hebrew characters
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in ai_text)
            if has_hebrew:
                print(f"✓ Field dashboard with AI interpretation (Hebrew): '{ai_text[:60]}...'")
            else:
                print(f"✓ Field dashboard returned (non-Hebrew or empty): '{ai_text[:60]}'")
        else:
            print("✓ Field dashboard returned (AI interpretation empty - may need API key)")


class TestProfileRecord:
    """Tests for GET /api/profile/{user_id}/record (AI Profile Interpretation)"""
    
    def test_profile_record_returns_success(self):
        """Profile record returns success and AI interpretation"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True
        assert "ai_profile_interpretation" in data, "ai_profile_interpretation missing"
        assert "identity" in data
        
        identity = data.get("identity", {})
        assert "alias" in identity, "alias missing from identity"
        
        ai_text = data.get("ai_profile_interpretation", "")
        if ai_text:
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in ai_text)
            if has_hebrew:
                print(f"✓ Profile record with AI interpretation: '{ai_text[:60]}...'")
            else:
                print(f"✓ Profile record returned: '{ai_text[:60]}'")
        else:
            print("✓ Profile record returned (AI interpretation empty)")


class TestCollectiveEndpoints:
    """Tests for collective layer endpoints"""
    
    def test_collective_layer_returns_success(self):
        """GET /api/collective/layer returns success"""
        response = requests.get(f"{BASE_URL}/api/collective/layer")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Collective layer endpoint works")
    
    def test_collective_trends_returns_success(self):
        """GET /api/collective/trends returns success"""
        response = requests.get(f"{BASE_URL}/api/collective/trends")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Collective trends endpoint works")


class TestOrientationEndpoints:
    """Tests for orientation system endpoints"""
    
    def test_field_today_returns_success(self):
        """GET /api/orientation/field-today returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Field today endpoint works")
    
    def test_highlighted_records_returns_success(self):
        """GET /api/orientation/highlighted-records returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Highlighted records endpoint works")
    
    def test_orientation_profile_returns_alias(self):
        """GET /api/orientation/profile/{user_id} returns alias"""
        response = requests.get(f"{BASE_URL}/api/orientation/profile/{TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        assert "alias" in data, "alias missing from response"
        print(f"✓ Orientation profile returns alias: {data.get('alias')}")


class TestMemoryStats:
    """Tests for memory stats endpoint"""
    
    def test_memory_stats_returns_success(self):
        """GET /api/memory/stats/{user_id} returns success"""
        response = requests.get(f"{BASE_URL}/api/memory/stats/{TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Memory stats endpoint works")


class TestBackendRefactorRegression:
    """Regression tests to verify refactored backend still works"""
    
    def test_root_endpoint(self):
        """GET /api/ returns hello world"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✓ Root endpoint works")
    
    def test_status_endpoint(self):
        """GET /api/status returns status checks"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        print("✓ Status endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

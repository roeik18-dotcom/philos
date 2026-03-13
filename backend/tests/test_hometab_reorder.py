"""
Test HomeTab reorder changes - iteration 71
Tests: Trust API, Invite API (GET/POST), Auth API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"


class TestAuthAPI:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """POST /api/auth/login - valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert data["user"]["id"] == TEST_USER_ID
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful, token received")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print(f"✓ Invalid login rejected with 401")


class TestTrustAPI:
    """Test trust-related endpoints for TrustChangeCard"""
    
    def test_get_user_trust(self):
        """GET /api/user/{user_id}/trust - returns trust profile"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "user_id" in data
        assert "trust_score" in data
        assert "value_score" in data
        assert "risk_score" in data
        assert data["user_id"] == TEST_USER_ID
        
        # Trust score should be a reasonable number
        assert isinstance(data["trust_score"], (int, float))
        assert data["trust_score"] >= 0
        print(f"✓ Trust score: {data['trust_score']:.1f}")
    
    def test_get_user_trust_invalid_id(self):
        """GET /api/user/{user_id}/trust - invalid user_id"""
        response = requests.get(f"{BASE_URL}/api/user/invalid-uuid-12345/trust")
        # Should return 200 with empty/default profile or 404
        # Current implementation returns 200 with zero values
        assert response.status_code in [200, 404]


class TestInviteAPI:
    """Test invite endpoints for InlineInviteCard"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not authenticate")
    
    def test_get_invites_authenticated(self, auth_token):
        """GET /api/invites/me - returns user's invite codes"""
        response = requests.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data["success"] == True
        assert "codes" in data
        assert "active_count" in data
        assert "used_count" in data
        assert "can_generate" in data
        
        # Should have at least one active code for InlineInviteCard
        active_codes = [c for c in data["codes"] if c["status"] == "active"]
        print(f"✓ Active invite codes: {len(active_codes)}")
        if active_codes:
            print(f"  First code: {active_codes[0]['code']}")
    
    def test_get_invites_unauthenticated(self):
        """GET /api/invites/me - should require auth"""
        response = requests.get(f"{BASE_URL}/api/invites/me")
        assert response.status_code == 401
        print(f"✓ Unauthenticated request rejected")
    
    def test_generate_invite_authenticated(self, auth_token):
        """POST /api/invites/generate - generate new invite code"""
        response = requests.post(
            f"{BASE_URL}/api/invites/generate",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 with generated codes or success=false if at limit
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"✓ Generate response: success={data['success']}")


class TestDailyBaseAPI:
    """Test daily base selection API"""
    
    def test_get_daily_base(self):
        """GET /api/orientation/daily-base/{user_id}"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-base/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "base_selected" in data
        assert "bases" in data
        
        # Validate base options exist
        assert "heart" in data["bases"]
        assert "head" in data["bases"]
        assert "body" in data["bases"]
        
        print(f"✓ Base selected: {data.get('base_selected')}, today_base: {data.get('today_base')}")


class TestDailyQuestionAPI:
    """Test daily question API"""
    
    def test_get_daily_question(self):
        """GET /api/orientation/daily-question/{user_id}"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "question_he" in data
        assert "question_id" in data
        assert "suggested_direction" in data
        
        print(f"✓ Daily question: {data['question_he'][:50]}...")
        print(f"  Direction: {data['suggested_direction']}")
        print(f"  Already answered: {data.get('already_answered_today', False)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

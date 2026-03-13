"""
Backend API Tests for Iteration 73
Testing: Landing text changes, invite page, trust hint, full user loop
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-english.preview.emergentagent.com')

# Test users
FRESH_USER = {
    "email": "trust_restricted@test.com",
    "password": "password123",
    "user_id": "d6a4bffd-e689-4ea8-b8c4-57f630a3a01e"
}

COMPLETED_USER = {
    "email": "newuser@test.com", 
    "password": "password123",
    "user_id": "05d47b99-88f1-44b3-a879-6c995634eaa0"
}


class TestAuthentication:
    """Test auth endpoints"""
    
    def test_login_fresh_user(self):
        """Test login for fresh user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": FRESH_USER["email"], "password": FRESH_USER["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["id"] == FRESH_USER["user_id"]
        print(f"✓ Fresh user login successful")
    
    def test_login_completed_user(self):
        """Test login for completed user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": COMPLETED_USER["email"], "password": COMPLETED_USER["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["id"] == COMPLETED_USER["user_id"]
        print(f"✓ Completed user login successful")


class TestOrientationEndpoints:
    """Test daily orientation flow APIs"""
    
    def test_daily_base_fresh_user(self):
        """Test daily base selection API for fresh user"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-base/{FRESH_USER['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "bases" in data
        print(f"✓ Daily base API works - base_selected: {data.get('base_selected')}")
    
    def test_daily_base_completed_user(self):
        """Test daily base for user who already selected"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-base/{COMPLETED_USER['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["base_selected"] is True
        assert data["today_base"] in ["heart", "head", "body"]
        print(f"✓ Completed user base: {data['today_base']}")
    
    def test_daily_question_fresh_user(self):
        """Test daily question API"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{FRESH_USER['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "question_he" in data
        assert "question_id" in data
        assert "suggested_direction" in data
        print(f"✓ Daily question - already_answered: {data.get('already_answered_today')}")
    
    def test_daily_question_completed_user(self):
        """Test daily question for completed user"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{COMPLETED_USER['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["already_answered_today"] is True
        assert data["streak"] >= 1
        print(f"✓ Completed user streak: {data['streak']}")


class TestTrustEndpoints:
    """Test trust score APIs"""
    
    def test_user_trust_fresh(self):
        """Test trust score API for fresh user"""
        response = requests.get(f"{BASE_URL}/api/user/{FRESH_USER['user_id']}/trust")
        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data
        assert "value_score" in data
        print(f"✓ Fresh user trust_score: {data['trust_score']}")
    
    def test_user_trust_completed(self):
        """Test trust score API for completed user"""
        response = requests.get(f"{BASE_URL}/api/user/{COMPLETED_USER['user_id']}/trust")
        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data
        print(f"✓ Completed user trust_score: {data['trust_score']}")


class TestInviteEndpoints:
    """Test invite system APIs"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for completed user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": COMPLETED_USER["email"], "password": COMPLETED_USER["password"]}
        )
        return response.json().get("token")
    
    def test_get_invites(self, auth_token):
        """Test GET /api/invites/me"""
        response = requests.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "codes" in data
        active_codes = [c for c in data["codes"] if c["status"] == "active"]
        print(f"✓ User has {len(active_codes)} active invite codes")
        return active_codes
    
    def test_invite_lookup(self, auth_token):
        """Test invite lookup endpoint"""
        # First get an active code
        invites_response = requests.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        codes = invites_response.json().get("codes", [])
        active_codes = [c for c in codes if c["status"] == "active"]
        
        if active_codes:
            code = active_codes[0]["code"]
            response = requests.get(f"{BASE_URL}/api/invites/lookup/{code}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["code"] == code
            assert data["status"] == "active"
            print(f"✓ Invite lookup works for code: {code}")
        else:
            pytest.skip("No active invite codes to test")


class TestDailyAnswerEndpoint:
    """Test the daily answer submission endpoint"""
    
    def test_daily_answer_endpoint_exists(self):
        """Test that daily answer endpoint returns proper response"""
        # Create a test user to avoid modifying real user data
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": f"test_answer_{os.urandom(4).hex()}@test.com", "password": "password123"}
        )
        if response.status_code != 200:
            pytest.skip("Could not create test user")
        
        user_id = response.json()["user"]["id"]
        
        # Get question
        q_response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        assert q_response.status_code == 200
        question_id = q_response.json().get("question_id")
        
        # Select base first
        base_response = requests.post(
            f"{BASE_URL}/api/orientation/daily-base/{user_id}",
            json={"base": "heart"}
        )
        assert base_response.status_code == 200
        
        # Submit answer
        answer_response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{user_id}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert answer_response.status_code == 200
        data = answer_response.json()
        assert data["success"] is True
        print(f"✓ Daily answer endpoint works - impact_score: {data.get('impact_score')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

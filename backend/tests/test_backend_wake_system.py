"""
Backend Wake System Tests - Iteration 101
Tests for: Health endpoint, Auth flow, and core APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoint:
    """Test /api/health endpoint - critical for backend wake system"""
    
    def test_health_endpoint_returns_ok(self):
        """Health endpoint returns {ok: true}"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "ok" in data, "Response should contain 'ok' field"
        assert data["ok"] == True, "ok should be True"
    
    def test_health_endpoint_no_auth_required(self):
        """Health endpoint should work without authentication"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        # Should not return 401 or 403
        assert response.status_code not in [401, 403], "Health endpoint should not require auth"


class TestAuthFlow:
    """Test authentication APIs for wake system integration"""
    
    def test_login_success(self):
        """Test login with test credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Login should return success=true"
        assert "token" in data, "Login should return a token"
        assert "user" in data, "Login should return user data"
        assert data["user"]["email"] == "newuser@test.com"
    
    def test_auth_me_with_valid_token(self):
        """Test /api/auth/me endpoint with valid token - used after backend ready"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json().get("token")
        
        # Check /api/auth/me
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_response.status_code == 200, f"Auth/me failed: {me_response.text}"
        data = me_response.json()
        assert data.get("success") == True
        assert "user" in data
    
    def test_auth_me_without_token(self):
        """Test /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        # Should return 401 or similar error
        assert response.status_code in [401, 422, 400], f"Expected auth error, got {response.status_code}"
    
    def test_login_invalid_credentials(self):
        """Test login with wrong credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wronguser@test.com",
            "password": "wrongpassword"
        })
        # Should not return 200 with success
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") != True, "Should not succeed with wrong credentials"


class TestFeedAPI:
    """Test Feed API - should work after backend is ready"""
    
    def test_feed_public_access(self):
        """Feed should be accessible without auth for public actions"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200, f"Feed failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "actions" in data
    
    def test_feed_with_viewer_id(self):
        """Feed with viewer_id param"""
        # Login to get user id
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_response.json()["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/actions/feed?viewer_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


class TestPositionAPI:
    """Test Position API - used in ActionFlow"""
    
    def test_position_endpoint(self):
        """Get user position"""
        # Login to get user id
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_response.json()["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200, f"Position failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "position" in data


class TestOrientationAPI:
    """Test Orientation API - used in ActionFlow"""
    
    def test_orientation_endpoint(self):
        """Get user orientation"""
        # Login to get user id
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_response.json()["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/orientation/{user_id}")
        assert response.status_code == 200, f"Orientation failed: {response.text}"
        data = response.json()
        assert data.get("success") == True


class TestActionsPostAPI:
    """Test Actions Post API - used in ActionFlow"""
    
    def test_post_action_requires_auth(self):
        """Posting action requires authentication"""
        response = requests.post(f"{BASE_URL}/api/actions/post", json={
            "title": "Test action",
            "description": "Test description",
            "visibility": "public"
        })
        # Should require auth
        assert response.status_code in [401, 422, 400, 403], f"Should require auth, got {response.status_code}"
    
    def test_post_action_with_auth(self):
        """Post action with authentication"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        token = login_response.json().get("token")
        
        # Post action
        response = requests.post(f"{BASE_URL}/api/actions/post", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "TEST_backend_wake_action",
                "description": "Testing from backend wake test",
                "visibility": "private",
                "category": "community"
            }
        )
        assert response.status_code == 200, f"Post action failed: {response.text}"
        data = response.json()
        assert data.get("success") == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

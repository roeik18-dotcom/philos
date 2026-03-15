"""
Backend API tests for Product App MVP
Testing: Actions Feed, Post Action, Impact Map, Profile, Dashboard endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-mvp.preview.emergentagent.com')


class TestAuthLogin:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@test.com"
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpass"
        })
        # Should return 401 for invalid credentials
        assert response.status_code in [401, 400]


class TestActionsFeed:
    """Action Feed endpoint tests"""
    
    def test_feed_returns_actions(self):
        """Test that feed endpoint returns actions list"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "actions" in data
        assert isinstance(data["actions"], list)
    
    def test_feed_action_structure(self):
        """Test that actions have correct structure"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        data = response.json()
        if data["actions"]:
            action = data["actions"][0]
            # Verify required fields
            assert "id" in action
            assert "title" in action
            assert "description" in action
            assert "category" in action
            assert "user_name" in action
            assert "created_at" in action
    
    def test_feed_category_filter(self):
        """Test filtering feed by category"""
        # Test filtering by education category
        response = requests.get(f"{BASE_URL}/api/actions/feed?category=education")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        # All returned actions should be education category
        for action in data["actions"]:
            assert action["category"] == "education"
    
    def test_feed_community_filter(self):
        """Test filtering feed by community category"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?category=community")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


class TestActionsMap:
    """Impact Map endpoint tests"""
    
    def test_map_returns_points(self):
        """Test that map endpoint returns location points"""
        response = requests.get(f"{BASE_URL}/api/actions/map")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "points" in data
        assert isinstance(data["points"], list)
    
    def test_map_point_structure(self):
        """Test that map points have correct structure"""
        response = requests.get(f"{BASE_URL}/api/actions/map")
        data = response.json()
        if data["points"]:
            point = data["points"][0]
            # Verify required fields for map markers
            assert "id" in point
            assert "lat" in point
            assert "lng" in point
            assert "title" in point
            assert "category" in point
            assert "user_name" in point


class TestImpactProfile:
    """Impact Profile endpoint tests"""
    
    @pytest.fixture
    def user_id(self):
        """Get user ID from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        return response.json()["user"]["id"]
    
    def test_profile_returns_data(self, user_id):
        """Test that profile endpoint returns user profile"""
        response = requests.get(f"{BASE_URL}/api/impact/profile/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "profile" in data
    
    def test_profile_structure(self, user_id):
        """Test that profile has correct structure"""
        response = requests.get(f"{BASE_URL}/api/impact/profile/{user_id}")
        data = response.json()
        profile = data["profile"]
        # Verify required profile fields
        assert "user_id" in profile
        assert "total_actions" in profile
        assert "impact_score" in profile
        assert "fields" in profile
        assert "communities" in profile


class TestImpactDashboard:
    """Daily Dashboard endpoint tests"""
    
    @pytest.fixture
    def user_id(self):
        """Get user ID from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        return response.json()["user"]["id"]
    
    def test_dashboard_returns_data(self, user_id):
        """Test that dashboard endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/impact/dashboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
    
    def test_dashboard_structure(self, user_id):
        """Test that dashboard has correct structure"""
        response = requests.get(f"{BASE_URL}/api/impact/dashboard/{user_id}")
        data = response.json()
        # Verify required dashboard sections
        assert "profile_summary" in data
        assert "network_activity" in data
        assert "suggested_actions" in data
        
        # Verify profile_summary structure
        summary = data["profile_summary"]
        assert "impact_score" in summary
        assert "total_actions" in summary
        assert "verified_count" in summary


class TestPostAction:
    """Post Action endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        return response.json()["token"]
    
    def test_post_action_requires_auth(self):
        """Test that posting action requires authentication"""
        response = requests.post(f"{BASE_URL}/api/actions/post", json={
            "title": "Test Action",
            "description": "Testing without auth"
        })
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]
    
    def test_post_action_success(self, auth_token):
        """Test successful action post"""
        response = requests.post(
            f"{BASE_URL}/api/actions/post",
            json={
                "title": "TEST_Automated Test Action",
                "description": "This is an automated test action for backend testing",
                "category": "education",
                "community": "Test Community",
                "location_name": "Test City",
                "location_lat": 40.7128,
                "location_lng": -74.0060
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "action_id" in data
    
    def test_posted_action_appears_in_feed(self, auth_token):
        """Test that posted action appears in feed"""
        # First post an action
        post_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            json={
                "title": "TEST_Feed Verification Action",
                "description": "This action should appear in the feed",
                "category": "technology"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert post_response.status_code == 200
        
        # Then verify it appears in feed
        feed_response = requests.get(f"{BASE_URL}/api/actions/feed")
        data = feed_response.json()
        titles = [a["title"] for a in data["actions"]]
        assert "TEST_Feed Verification Action" in titles
    
    def test_posted_action_with_location_appears_on_map(self, auth_token):
        """Test that action with location appears on map"""
        # Post action with location
        post_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            json={
                "title": "TEST_Map Verification Action",
                "description": "This action should appear on the map",
                "category": "environment",
                "location_name": "Test Location",
                "location_lat": 51.5074,
                "location_lng": -0.1278
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert post_response.status_code == 200
        
        # Verify it appears on map
        map_response = requests.get(f"{BASE_URL}/api/actions/map")
        data = map_response.json()
        titles = [p["title"] for p in data["points"]]
        assert "TEST_Map Verification Action" in titles


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

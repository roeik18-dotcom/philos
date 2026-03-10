"""
Community Layer Endpoints Test Suite
Tests the 4 new community engagement features:
1. Active Users Indicator - GET /api/orientation/active-users
2. Relative Orientation Score - GET /api/orientation/relative-score/{user_id}
3. Orientation Circles - GET /api/orientation/circles
4. Community Streak Overview - GET /api/orientation/streaks
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestActiveUsers:
    """Feature 1: Active Users Indicator Tests"""
    
    def test_active_users_endpoint_returns_success(self):
        """Test that active-users endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/active-users")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_active_users_returns_required_fields(self):
        """Test that active-users returns active_users_today and active_streak_users"""
        response = requests.get(f"{BASE_URL}/api/orientation/active-users")
        assert response.status_code == 200
        data = response.json()
        assert "active_users_today" in data
        assert "active_streak_users" in data
        assert isinstance(data["active_users_today"], int)
        assert isinstance(data["active_streak_users"], int)
    
    def test_active_users_values_are_non_negative(self):
        """Test that active user counts are >= 0"""
        response = requests.get(f"{BASE_URL}/api/orientation/active-users")
        data = response.json()
        assert data["active_users_today"] >= 0
        assert data["active_streak_users"] >= 0


class TestRelativeScore:
    """Feature 2: Relative Orientation Score Tests"""
    
    def test_relative_score_endpoint_returns_success(self):
        """Test that relative-score endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/relative-score/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_relative_score_returns_percentile(self):
        """Test that relative-score returns percentile field"""
        response = requests.get(f"{BASE_URL}/api/orientation/relative-score/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert "percentile" in data
        assert isinstance(data["percentile"], int)
        assert 0 <= data["percentile"] <= 100
    
    def test_relative_score_returns_direction(self):
        """Test that relative-score returns direction field"""
        response = requests.get(f"{BASE_URL}/api/orientation/relative-score/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert "direction" in data
        assert data["direction"] in ["contribution", "recovery", "order", "exploration"]
    
    def test_relative_score_returns_user_actions_today(self):
        """Test that relative-score returns user_actions_today field"""
        response = requests.get(f"{BASE_URL}/api/orientation/relative-score/test-user-123")
        assert response.status_code == 200
        data = response.json()
        assert "user_actions_today" in data
        assert isinstance(data["user_actions_today"], int)


class TestOrientationCircles:
    """Feature 3: Orientation Circles Tests"""
    
    def test_circles_endpoint_returns_success(self):
        """Test that circles endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/circles")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_circles_returns_all_directions(self):
        """Test that circles returns counts for all 4 directions"""
        response = requests.get(f"{BASE_URL}/api/orientation/circles")
        assert response.status_code == 200
        data = response.json()
        assert "contribution" in data
        assert "recovery" in data
        assert "order" in data
        assert "exploration" in data
    
    def test_circles_values_are_integers(self):
        """Test that circle counts are integers"""
        response = requests.get(f"{BASE_URL}/api/orientation/circles")
        data = response.json()
        assert isinstance(data["contribution"], int)
        assert isinstance(data["recovery"], int)
        assert isinstance(data["order"], int)
        assert isinstance(data["exploration"], int)
    
    def test_circles_values_are_non_negative(self):
        """Test that circle counts are >= 0"""
        response = requests.get(f"{BASE_URL}/api/orientation/circles")
        data = response.json()
        assert data["contribution"] >= 0
        assert data["recovery"] >= 0
        assert data["order"] >= 0
        assert data["exploration"] >= 0


class TestCommunityStreaks:
    """Feature 4: Community Streak Overview Tests"""
    
    def test_streaks_endpoint_returns_success(self):
        """Test that streaks endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/streaks")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_streaks_returns_users_on_streak(self):
        """Test that streaks returns users_on_streak field"""
        response = requests.get(f"{BASE_URL}/api/orientation/streaks")
        assert response.status_code == 200
        data = response.json()
        assert "users_on_streak" in data
        assert isinstance(data["users_on_streak"], int)
        assert data["users_on_streak"] >= 0
    
    def test_streaks_returns_longest_streak_today(self):
        """Test that streaks returns longest_streak_today field"""
        response = requests.get(f"{BASE_URL}/api/orientation/streaks")
        assert response.status_code == 200
        data = response.json()
        assert "longest_streak_today" in data
        assert isinstance(data["longest_streak_today"], int)
        assert data["longest_streak_today"] >= 0


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

"""
Regression tests for Landing Page Redesign + PWA Routes
Tests: Landing page, /app/* routes, and backend APIs
Previous: iteration_83.json tested Trust Integrity Layer (100% pass)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestBackendAPIs:
    """Backend API regression tests for all /api/* endpoints"""

    def test_actions_feed(self):
        """GET /api/actions/feed returns actions array"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "actions" in data
        assert isinstance(data["actions"], list)
        # Verify action structure
        if data["actions"]:
            action = data["actions"][0]
            assert "id" in action
            assert "title" in action
            assert "reactions" in action
            assert "verification_level" in action

    def test_leaderboard(self):
        """GET /api/leaderboard returns leaders array"""
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "leaders" in data
        assert isinstance(data["leaders"], list)
        if data["leaders"]:
            leader = data["leaders"][0]
            assert "rank" in leader
            assert "trust_score" in leader
            assert "user_name" in leader

    def test_community_funds(self):
        """GET /api/community-funds returns funds array"""
        response = requests.get(f"{BASE_URL}/api/community-funds")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "funds" in data
        assert isinstance(data["funds"], list)
        if data["funds"]:
            fund = data["funds"][0]
            assert "community" in fund
            assert "total_raised" in fund
            assert "current_balance" in fund

    def test_opportunities(self):
        """GET /api/opportunities returns opportunities"""
        response = requests.get(f"{BASE_URL}/api/opportunities")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "opportunities" in data
        assert isinstance(data["opportunities"], list)
        if data["opportunities"]:
            opp = data["opportunities"][0]
            assert "id" in opp
            assert "title" in opp
            assert "min_trust_score" in opp

    def test_trust_integrity_stats(self):
        """GET /api/trust/integrity-stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/trust/integrity-stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "stats" in data
        stats = data["stats"]
        assert "total_actions" in stats
        assert "self_reported" in stats
        assert "community_verified" in stats


class TestAuthFlow:
    """Authentication endpoint tests"""

    def test_login_success(self):
        """POST /api/auth/login works with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@test.com"

    def test_login_invalid(self):
        """POST /api/auth/login rejects invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        # API returns 200 with success=false for invalid credentials
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert data.get("token") is None


class TestWeeklyReport:
    """Weekly report endpoint tests (requires user_id)"""

    def test_weekly_report_leaderboard(self):
        """GET /api/weekly-report/{user_id} returns report"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/weekly-report/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "report" in data
        report = data["report"]
        assert "period" in report
        assert "week_actions" in report
        assert "total_trust_score" in report

    def test_weekly_insight(self):
        """GET /api/orientation/weekly-report/{user_id} returns insight"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-report/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "distribution" in data


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")

    def test_auth_me(self, auth_token):
        """GET /api/auth/me returns user info with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "user" in data


class TestLiveStatsData:
    """Tests for landing page live stats data sources"""

    def test_feed_for_stats(self):
        """Actions feed provides count for live stats"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=50")
        assert response.status_code == 200
        data = response.json()
        actions_count = len(data.get("actions", []))
        assert actions_count >= 0  # Can be 0 if empty

    def test_leaderboard_for_stats(self):
        """Leaderboard provides contributor count and trust sum"""
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        leaders = data.get("leaders", [])
        total_trust = sum(l.get("trust_score", 0) for l in leaders)
        assert total_trust >= 0

    def test_community_funds_for_stats(self):
        """Community funds provides community count"""
        response = requests.get(f"{BASE_URL}/api/community-funds")
        assert response.status_code == 200
        data = response.json()
        funds_count = len(data.get("funds", []))
        assert funds_count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

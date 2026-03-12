"""
Tests for Engagement Loop Phase Features (Iteration 47)
- Field Dashboard API
- Compass AI API
- Daily Answer API with enriched reward data
- Quick Action (onboarding first-action) API
- Day Summary API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestFieldDashboard:
    """GlobalFieldDashboard backend API tests"""
    
    def test_field_dashboard_returns_success(self):
        """Test /api/orientation/field-dashboard returns required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "dominant_direction" in data
        assert "dominant_direction_he" in data
        assert "total_actions_today" in data
        assert "direction_counts" in data
        assert "active_regions" in data
        assert "top_regions" in data
        assert "momentum_he" in data
        print(f"✓ Field dashboard: {data['total_actions_today']} actions today, dominant: {data['dominant_direction_he']}")


class TestCompassAI:
    """Compass AI API tests for EntryLayer"""
    
    def test_compass_ai_returns_user_force(self):
        """Test /api/orientation/compass-ai/{userId} returns user force data"""
        user_id = "demo_0"
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "dominant_direction" in data
        assert "dominant_direction_he" in data
        # suggested_action_he may be suggestion_he in older API
        assert "suggestion_he" in data or "suggested_action_he" in data
        print(f"✓ Compass AI for {user_id}: dominant={data.get('dominant_direction_he')}")


class TestDailyAnswerReward:
    """Daily Answer API with enriched reward data (impact_score, streak, niche_info, identity_link)"""
    
    def test_daily_answer_returns_reward_fields(self):
        """Test POST /api/orientation/daily-answer returns enriched reward data"""
        # First get a question for the user
        user_id = "test_engagement_user"
        
        # Get daily question
        q_response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        assert q_response.status_code == 200
        
        q_data = q_response.json()
        assert q_data.get("success") == True
        question_id = q_data.get("question_id")
        
        if q_data.get("already_answered_today"):
            print(f"✓ User already answered today, streak: {q_data.get('streak')}")
            return
        
        # Submit answer
        response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{user_id}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        # Check enriched reward fields
        assert "impact_score" in data, "impact_score missing from response"
        assert "streak" in data, "streak missing from response"
        assert "niche_info" in data, "niche_info missing from response"
        assert "identity_link" in data, "identity_link missing from response"
        
        print(f"✓ Daily answer reward: impact_score={data['impact_score']}, streak={data['streak']}")
        print(f"  niche_info={data.get('niche_info')}, identity_link={data.get('identity_link')}")


class TestQuickAction:
    """Quick Action (fast 3-tap loop) API tests"""
    
    def test_first_action_sends_and_returns_success(self):
        """Test POST /api/onboarding/first-action for quick action"""
        response = requests.post(
            f"{BASE_URL}/api/onboarding/first-action",
            json={"user_id": "quick_action_test_user", "direction": "contribution"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "message_he" in data or "message" in data
        print(f"✓ Quick action sent successfully")


class TestDaySummary:
    """Day Summary API for ClosingLayer"""
    
    def test_day_summary_returns_required_fields(self):
        """Test /api/orientation/day-summary/{userId} returns tension/return-hook data structure"""
        user_id = "demo_0"
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "chosen_direction" in data
        assert "total_actions" in data
        assert "streak" in data
        assert "impact_on_field" in data
        assert "reflection_he" in data
        assert "global_field_effect" in data
        
        print(f"✓ Day summary: total_actions={data['total_actions']}, streak={data['streak']}")
        print(f"  reflection: {data['reflection_he'][:50]}...")


class TestGlobeActivity:
    """Globe Activity API for FieldGlobeSection"""
    
    def test_globe_activity_returns_points(self):
        """Test /api/orientation/globe-activity returns globe data"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "points" in data
        assert "total_points" in data
        print(f"✓ Globe activity: {data['total_points']} total points")


class TestRegression:
    """Regression tests for existing endpoints"""
    
    def test_auth_login(self):
        """Test login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Auth login works")
    
    def test_philos_sync(self):
        """Test philos sync still works"""
        response = requests.get(f"{BASE_URL}/api/philos/sync/demo_0")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Philos sync works")
    
    def test_collective_layer(self):
        """Test collective layer still works"""
        response = requests.get(f"{BASE_URL}/api/collective/layer")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Collective layer works")
    
    def test_user_profile(self):
        """Test user profile still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/demo_0")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ User profile works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

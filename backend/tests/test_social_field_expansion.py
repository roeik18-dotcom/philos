"""
Test suite for Social Field Expansion phase
Tests all new backend APIs:
- /api/orientation/field-dashboard
- /api/orientation/missions (GET and POST /join)
- /api/orientation/value-circles (GET and POST /join)
- /api/orientation/leaders
- /api/orientation/compass-ai/{user_id}
- /api/orientation/feed/for-you/{user_id}
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user ID for consistent testing
TEST_USER_ID = f"test-user-{uuid.uuid4().hex[:8]}"


class TestFieldDashboard:
    """Tests for /api/orientation/field-dashboard endpoint"""
    
    def test_field_dashboard_returns_success(self):
        """Field dashboard should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True, "Field dashboard should return success=True"
    
    def test_field_dashboard_has_dominant_direction(self):
        """Field dashboard should include dominant direction"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        data = response.json()
        assert 'dominant_direction' in data, "Missing dominant_direction"
        assert 'dominant_direction_he' in data, "Missing dominant_direction_he (Hebrew)"
        # Valid directions
        valid_directions = ['contribution', 'recovery', 'order', 'exploration']
        assert data['dominant_direction'] in valid_directions
    
    def test_field_dashboard_has_total_actions(self):
        """Field dashboard should include total actions today"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        data = response.json()
        assert 'total_actions_today' in data, "Missing total_actions_today"
        assert isinstance(data['total_actions_today'], int)
        assert data['total_actions_today'] >= 0
    
    def test_field_dashboard_has_active_regions(self):
        """Field dashboard should include active regions"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        data = response.json()
        assert 'active_regions' in data, "Missing active_regions"
        assert isinstance(data['active_regions'], int)
    
    def test_field_dashboard_has_direction_counts(self):
        """Field dashboard should include direction counts"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        data = response.json()
        assert 'direction_counts' in data, "Missing direction_counts"
        counts = data['direction_counts']
        assert 'contribution' in counts
        assert 'recovery' in counts
        assert 'order' in counts
        assert 'exploration' in counts
    
    def test_field_dashboard_has_top_regions(self):
        """Field dashboard should include top regions"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        data = response.json()
        assert 'top_regions' in data, "Missing top_regions"
        if len(data['top_regions']) > 0:
            region = data['top_regions'][0]
            assert 'code' in region
            assert 'name' in region
            assert 'count' in region


class TestMissions:
    """Tests for /api/orientation/missions endpoint"""
    
    def test_missions_returns_success(self):
        """Missions endpoint should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_missions_has_missions_array(self):
        """Missions endpoint should return missions array"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        data = response.json()
        assert 'missions' in data
        assert isinstance(data['missions'], list)
        assert len(data['missions']) > 0, "Should have at least one mission"
    
    def test_mission_has_required_fields(self):
        """Each mission should have required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        data = response.json()
        mission = data['missions'][0]
        assert 'id' in mission
        assert 'title_he' in mission
        assert 'direction' in mission
        assert 'direction_he' in mission
        assert 'description_he' in mission
        assert 'participants' in mission
        assert 'total_field_impact' in mission
        assert 'is_today' in mission
    
    def test_mission_has_today_mission(self):
        """Should have at least one mission marked as today"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        data = response.json()
        today_missions = [m for m in data['missions'] if m.get('is_today')]
        assert len(today_missions) >= 1, "Should have at least one today mission"


class TestMissionsJoin:
    """Tests for /api/orientation/missions/join endpoint"""
    
    def test_join_mission_returns_success(self):
        """Joining a mission should return success"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/missions/join",
            json={"user_id": TEST_USER_ID, "mission_id": "mission-exploration"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'message_he' in data


class TestValueCircles:
    """Tests for /api/orientation/value-circles endpoint"""
    
    def test_value_circles_returns_success(self):
        """Value circles endpoint should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_value_circles_has_circles_array(self):
        """Value circles endpoint should return circles array"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        data = response.json()
        assert 'circles' in data
        assert isinstance(data['circles'], list)
        assert len(data['circles']) > 0, "Should have at least one circle"
    
    def test_circle_has_required_fields(self):
        """Each circle should have required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        data = response.json()
        circle = data['circles'][0]
        assert 'id' in circle
        assert 'label_he' in circle
        assert 'color' in circle
        assert 'description_he' in circle
        assert 'member_count' in circle
    
    def test_has_six_circles(self):
        """Should have 6 value circles"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        data = response.json()
        assert len(data['circles']) == 6, f"Expected 6 circles, got {len(data['circles'])}"


class TestValueCirclesJoin:
    """Tests for /api/orientation/value-circles/join endpoint"""
    
    def test_join_circle_returns_success(self):
        """Joining a circle should return success"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/join",
            json={"user_id": TEST_USER_ID, "circle_id": "explorers"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'message_he' in data


class TestLeaders:
    """Tests for /api/orientation/leaders endpoint"""
    
    def test_leaders_returns_success(self):
        """Leaders endpoint should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_leaders_has_global_leaders(self):
        """Leaders endpoint should return global_leaders array"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        data = response.json()
        assert 'global_leaders' in data
        assert isinstance(data['global_leaders'], list)
        assert len(data['global_leaders']) > 0
    
    def test_leader_has_required_fields(self):
        """Each leader should have required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        data = response.json()
        leader = data['global_leaders'][0]
        assert 'rank' in leader
        assert 'alias' in leader
        assert 'country' in leader
        assert 'niche_he' in leader
        assert 'impact_score' in leader
        assert 'actions' in leader
    
    def test_leaders_sorted_by_rank(self):
        """Leaders should be sorted by rank"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        data = response.json()
        leaders = data['global_leaders']
        for i, leader in enumerate(leaders):
            assert leader['rank'] == i + 1, f"Leader at position {i} has wrong rank"


class TestCompassAI:
    """Tests for /api/orientation/compass-ai/{user_id} endpoint"""
    
    def test_compass_ai_returns_success(self):
        """Compass AI endpoint should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_compass_ai_has_user_id(self):
        """Compass AI should return user_id"""
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{TEST_USER_ID}")
        data = response.json()
        assert 'user_id' in data
        assert data['user_id'] == TEST_USER_ID
    
    def test_compass_ai_has_suggestion(self):
        """Compass AI should include suggestion in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{TEST_USER_ID}")
        data = response.json()
        assert 'suggestion_he' in data
        assert isinstance(data['suggestion_he'], str)
    
    def test_compass_ai_has_balance_score(self):
        """Compass AI should include balance score"""
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{TEST_USER_ID}")
        data = response.json()
        assert 'balance_score' in data


class TestFeedForYou:
    """Tests for /api/orientation/feed/for-you/{user_id} endpoint"""
    
    def test_feed_returns_success(self):
        """Feed for you endpoint should return success"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_feed_has_cards_array(self):
        """Feed should return cards array"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/{TEST_USER_ID}")
        data = response.json()
        assert 'cards' in data
        assert isinstance(data['cards'], list)
    
    def test_feed_has_multiple_card_types(self):
        """Feed should contain multiple card types"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/{TEST_USER_ID}")
        data = response.json()
        card_types = set(card.get('type') for card in data['cards'])
        # Should have at least action and mission types
        assert 'action' in card_types, "Feed should have action cards"
        assert 'mission' in card_types, "Feed should have mission cards"
    
    def test_feed_action_card_has_required_fields(self):
        """Action cards should have required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/{TEST_USER_ID}")
        data = response.json()
        action_cards = [c for c in data['cards'] if c.get('type') == 'action']
        if action_cards:
            card = action_cards[0]
            assert 'alias' in card
            assert 'country' in card
            assert 'direction' in card
            assert 'direction_he' in card
            assert 'action_text' in card
            assert 'impact_score' in card


class TestHomeTabRegression:
    """Regression tests to ensure existing Home tab APIs still work"""
    
    def test_daily_opening_still_works(self):
        """Daily opening endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_day_summary_still_works(self):
        """Day summary endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
    
    def test_directions_still_works(self):
        """Directions endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

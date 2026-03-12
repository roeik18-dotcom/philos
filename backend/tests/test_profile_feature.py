"""
Test suite for Human Action Record (Profile Page) feature - Iteration 45

Tests:
- Profile page API GET /api/profile/{user_id}/record
- Identity header: alias, country, member_since
- Opposition axes: chaos_order, ego_collective, exploration_stability
- Value growth: impact_score, level, circles count
- Direction distribution
- Feed cards with user_id (profile links)
- Leaders with user_id
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProfileAPIBasics:
    """Test GET /api/profile/{user_id}/record endpoint"""
    
    def test_profile_demo_0_returns_success(self):
        """Profile endpoint for demo_0 should return success"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Profile API returns success for demo_0")
    
    def test_profile_has_identity_section(self):
        """Profile should have identity section with required fields"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        data = response.json()
        
        assert 'identity' in data
        identity = data['identity']
        
        # Required fields
        assert 'user_id' in identity
        assert 'alias' in identity
        assert 'country' in identity
        assert 'member_since' in identity
        
        # user_id should match request
        assert identity['user_id'] == 'demo_0'
        
        # alias should be non-empty
        assert len(identity['alias']) > 0
        
        print(f"PASS: Identity section complete - alias: {identity['alias']}, country: {identity['country']}")
    
    def test_profile_has_opposition_axes(self):
        """Profile should have opposition axes with 3 axis values"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        data = response.json()
        
        assert 'opposition_axes' in data
        axes = data['opposition_axes']
        
        # All 3 axes required
        assert 'chaos_order' in axes
        assert 'ego_collective' in axes
        assert 'exploration_stability' in axes
        
        # All values should be 0-100
        for key, val in axes.items():
            assert 0 <= val <= 100, f"{key} should be between 0-100, got {val}"
        
        print(f"PASS: Opposition axes - chaos_order: {axes['chaos_order']}, ego_collective: {axes['ego_collective']}, exploration_stability: {axes['exploration_stability']}")
    
    def test_profile_has_value_growth(self):
        """Profile should have value growth section with key metrics"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        data = response.json()
        
        assert 'value_growth' in data
        growth = data['value_growth']
        
        # Required fields
        assert 'total_actions' in growth
        assert 'impact_score' in growth
        assert 'level' in growth
        assert 'circle_memberships' in growth
        
        # Types check
        assert isinstance(growth['total_actions'], int)
        assert isinstance(growth['level'], int)
        assert growth['level'] >= 0
        
        print(f"PASS: Value growth - impact: {growth['impact_score']}, level: {growth['level']}, circles: {growth['circle_memberships']}")
    
    def test_profile_has_direction_distribution(self):
        """Profile should have direction distribution"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        data = response.json()
        
        assert 'direction_distribution' in data
        dist = data['direction_distribution']
        
        # All 4 directions required
        for dir_key in ['contribution', 'recovery', 'order', 'exploration']:
            assert dir_key in dist
            assert isinstance(dist[dir_key], int)
            assert dist[dir_key] >= 0
        
        print(f"PASS: Direction distribution - {dist}")
    
    def test_profile_has_action_record(self):
        """Profile should have action_record array"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        data = response.json()
        
        assert 'action_record' in data
        assert isinstance(data['action_record'], list)
        
        print(f"PASS: Action record is list with {len(data['action_record'])} items")


class TestProfileDifferentUsers:
    """Test profile for different demo users"""
    
    def test_profile_demo_1(self):
        """Profile for demo_1 should return success"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_1/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data['identity']['user_id'] == 'demo_1'
        print(f"PASS: Profile demo_1 - alias: {data['identity']['alias']}")
    
    def test_profile_demo_5(self):
        """Profile for demo_5 should return success"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_5/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data['identity']['user_id'] == 'demo_5'
        print(f"PASS: Profile demo_5 - alias: {data['identity']['alias']}")
    
    def test_profile_demo_10(self):
        """Profile for demo_10 should return success"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_10/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"PASS: Profile demo_10 - alias: {data['identity']['alias']}")


class TestFeedWithUserIds:
    """Test that feed cards include user_id for profile links"""
    
    def test_personalized_feed_action_cards_have_user_id(self):
        """Action cards in personalized feed should have user_id"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/demo_0")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        cards = data.get('cards', [])
        action_cards = [c for c in cards if c.get('type') == 'action']
        
        assert len(action_cards) > 0, "Should have action cards"
        
        for card in action_cards[:5]:
            assert 'user_id' in card, f"Action card should have user_id: {card}"
            assert 'alias' in card, f"Action card should have alias: {card}"
        
        print(f"PASS: {len(action_cards)} action cards have user_id")
    
    def test_personalized_feed_leader_card_has_user_id(self):
        """Leader card in personalized feed should have user_id"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/demo_0")
        data = response.json()
        
        cards = data.get('cards', [])
        leader_cards = [c for c in cards if c.get('type') == 'leader']
        
        if leader_cards:
            for card in leader_cards:
                assert 'user_id' in card, f"Leader card should have user_id: {card}"
            print(f"PASS: Leader card has user_id: {leader_cards[0].get('user_id')}")
        else:
            print("SKIP: No leader cards in feed (user may have 0 total_value)")


class TestLeadersWithUserIds:
    """Test that leaders endpoint includes user_id"""
    
    def test_global_leaders_have_user_id(self):
        """Global leaders should have user_id field"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        leaders = data.get('global_leaders', [])
        assert len(leaders) > 0, "Should have at least one leader"
        
        for leader in leaders:
            assert 'user_id' in leader, f"Leader should have user_id: {leader}"
            assert 'alias' in leader
            # user_id format check
            assert leader['user_id'].startswith('demo_'), f"Demo leader user_id should start with 'demo_': {leader['user_id']}"
        
        print(f"PASS: {len(leaders)} leaders have user_id - first: {leaders[0]['user_id']}")


class TestProfileOppositionAxesValues:
    """Test that opposition axes values are correctly bounded"""
    
    def test_axes_values_bounded_0_100(self):
        """All axes values should be between 0 and 100"""
        # Test multiple users
        for user in ['demo_0', 'demo_3', 'demo_7']:
            response = requests.get(f"{BASE_URL}/api/profile/{user}/record")
            data = response.json()
            
            axes = data.get('opposition_axes', {})
            for key, val in axes.items():
                assert 0 <= val <= 100, f"User {user}, axis {key} should be 0-100, got {val}"
        
        print("PASS: All axes values are bounded 0-100")


class TestRegression:
    """Regression tests for existing features"""
    
    def test_field_today_still_works(self):
        """GET /api/orientation/field-today should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Field today endpoint works")
    
    def test_field_dashboard_still_works(self):
        """GET /api/orientation/field-dashboard should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Field dashboard endpoint works")
    
    def test_value_circles_still_works(self):
        """GET /api/orientation/value-circles should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Value circles endpoint works")
    
    def test_missions_still_works(self):
        """GET /api/orientation/missions should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Missions endpoint works")
    
    def test_globe_activity_still_works(self):
        """GET /api/orientation/globe-activity should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Globe activity endpoint works")
    
    def test_orientation_field_still_works(self):
        """GET /api/orientation/field should work"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Orientation field endpoint works")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

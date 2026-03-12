"""
Test suite for Clarity & Meaning refinement phase features:
- field_narrative_he in field-dashboard (symbolic sentence, no numbers)
- opposition_axes in profile record endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"


class TestFieldDashboardNarrative:
    """Tests for /api/orientation/field-dashboard - field_narrative_he field"""

    def test_field_dashboard_returns_narrative(self):
        """Verify field-dashboard returns field_narrative_he field"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'field_narrative_he' in data
        assert isinstance(data['field_narrative_he'], str)
        assert len(data['field_narrative_he']) > 0

    def test_field_narrative_has_no_numbers(self):
        """Verify field_narrative_he is symbolic (no numbers)"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        narrative = data.get('field_narrative_he', '')
        
        # Check that narrative contains no digits
        has_digits = any(char.isdigit() for char in narrative)
        assert not has_digits, f"Narrative should not contain numbers, got: {narrative}"

    def test_field_dashboard_has_direction_data(self):
        """Verify field-dashboard returns direction_counts for direction bar"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert 'dominant_direction' in data
        assert 'direction_counts' in data
        
        dir_counts = data['direction_counts']
        assert 'contribution' in dir_counts
        assert 'recovery' in dir_counts
        assert 'order' in dir_counts
        assert 'exploration' in dir_counts


class TestOppositionAxes:
    """Tests for /api/profile/{user_id}/record - opposition_axes field"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token and user_id for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('token'), data['user']['id']
        pytest.skip("Authentication failed")
    
    def test_profile_record_returns_opposition_axes(self, auth_token):
        """Verify profile record endpoint returns opposition_axes"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/profile/{user_id}/record")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'opposition_axes' in data

    def test_opposition_axes_has_three_tensions(self, auth_token):
        """Verify opposition_axes contains chaos_order, ego_collective, exploration_stability"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/profile/{user_id}/record")
        assert response.status_code == 200
        
        data = response.json()
        axes = data.get('opposition_axes', {})
        
        # Should have all 3 tension axes
        assert 'chaos_order' in axes
        assert 'ego_collective' in axes
        assert 'exploration_stability' in axes
        
        # Values should be numeric (0-100 range)
        for key, value in axes.items():
            assert isinstance(value, (int, float))
            assert 0 <= value <= 100, f"{key} should be 0-100, got {value}"


class TestCompassAI:
    """Tests for /api/orientation/compass-ai/{user_id}"""
    
    @pytest.fixture
    def user_id(self):
        """Get user_id from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['user']['id']
        pytest.skip("Authentication failed")
    
    def test_compass_ai_returns_direction(self, user_id):
        """Verify compass-ai endpoint returns direction data"""
        response = requests.get(f"{BASE_URL}/api/orientation/compass-ai/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'dominant_direction' in data
        assert 'suggested_action_he' in data


class TestGlobeActivity:
    """Tests for /api/orientation/globe-activity"""
    
    def test_globe_activity_returns_points(self):
        """Verify globe-activity returns points array"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'points' in data
        assert isinstance(data['points'], list)
        
    def test_globe_activity_has_color_map(self):
        """Verify globe-activity returns color_map for direction colors"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        
        data = response.json()
        assert 'color_map' in data


class TestGlobeRegion:
    """Tests for /api/orientation/globe-region/{country_code}"""
    
    def test_globe_region_returns_details(self):
        """Verify globe-region returns country details for IL (Israel)"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'country_name_he' in data
        assert 'total_actions' in data
        assert 'direction_counts' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

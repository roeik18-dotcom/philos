"""
Regression tests for PhilosDashboard refactor (iteration 37)
Testing: Tab component extraction and DecisionTreeSection SVG fix
Backend APIs tested: daily-opening, day-summary, globe-activity, directions
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDailyOpeningEndpoint:
    """Test /api/orientation/daily-opening/{user_id}"""
    
    def test_daily_opening_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        assert response.status_code == 200
    
    def test_daily_opening_has_success(self):
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert data.get('success') == True
    
    def test_daily_opening_has_compass_state(self):
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert 'compass_state' in data
        compass = data['compass_state']
        assert 'contribution' in compass
        assert 'recovery' in compass
        assert 'order' in compass
        assert 'exploration' in compass
    
    def test_daily_opening_has_suggested_direction(self):
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert 'suggested_direction' in data
        assert 'suggested_direction_he' in data

class TestDaySummaryEndpoint:
    """Test /api/orientation/day-summary/{user_id}"""
    
    def test_day_summary_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        assert response.status_code == 200
    
    def test_day_summary_has_success(self):
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert data.get('success') == True
    
    def test_day_summary_has_direction_counts(self):
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert 'direction_counts' in data
        counts = data['direction_counts']
        assert 'contribution' in counts
        assert 'recovery' in counts
        assert 'order' in counts
        assert 'exploration' in counts
    
    def test_day_summary_has_reflection(self):
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert 'reflection_he' in data

class TestGlobeActivityEndpoint:
    """Test /api/orientation/globe-activity"""
    
    def test_globe_activity_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
    
    def test_globe_activity_has_success(self):
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert data.get('success') == True
    
    def test_globe_activity_has_points(self):
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert 'points' in data
        assert isinstance(data['points'], list)
    
    def test_globe_activity_points_have_required_fields(self):
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        if len(data['points']) > 0:
            point = data['points'][0]
            assert 'lat' in point
            assert 'lng' in point
            assert 'direction' in point
            assert 'color' in point

class TestDirectionsEndpoint:
    """Test /api/orientation/directions"""
    
    def test_directions_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        assert response.status_code == 200
    
    def test_directions_has_success(self):
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        assert data.get('success') == True
    
    def test_directions_has_4_directions(self):
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        assert 'directions' in data
        directions = data['directions']
        assert 'contribution' in directions
        assert 'recovery' in directions
        assert 'order' in directions
        assert 'exploration' in directions
    
    def test_direction_has_hebrew_content(self):
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        contribution = data['directions']['contribution']
        assert 'label_he' in contribution
        assert 'explanation_he' in contribution
        assert 'symbolic_meaning_he' in contribution


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

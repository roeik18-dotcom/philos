"""
Tests for GET /api/orientation/field-today endpoint
Tests the Orientation Field Today feature that shows distribution of user activity directions in last 24h
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestFieldTodayEndpoint:
    """Tests for the basic endpoint response"""
    
    def test_endpoint_returns_success(self):
        """Verify endpoint returns 200 and success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('success') is True, "Expected success=true"
        print(f"PASS: Endpoint returns success=true")
    
    def test_response_has_distribution(self):
        """Verify response has distribution field with 4 directions"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert 'distribution' in data, "Missing distribution field"
        distribution = data['distribution']
        
        expected_directions = ['contribution', 'recovery', 'order', 'exploration']
        for direction in expected_directions:
            assert direction in distribution, f"Missing direction: {direction}"
            assert isinstance(distribution[direction], (int, float)), f"{direction} should be a number"
        
        print(f"PASS: Distribution contains all 4 directions: {distribution}")
    
    def test_distribution_sums_to_100(self):
        """Verify distribution percentages sum to approximately 100"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        distribution = data['distribution']
        total = sum(distribution.values())
        # Allow small rounding error
        assert 99 <= total <= 101, f"Distribution should sum to ~100, got {total}"
        print(f"PASS: Distribution sums to {total}%")
    
    def test_response_has_active_users_count(self):
        """Verify response has active_users field"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert 'active_users' in data, "Missing active_users field"
        assert isinstance(data['active_users'], int), "active_users should be an integer"
        assert data['active_users'] >= 0, "active_users should be non-negative"
        print(f"PASS: active_users={data['active_users']}")
    
    def test_response_has_total_actions_count(self):
        """Verify response has total_actions field"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert 'total_actions' in data, "Missing total_actions field"
        assert isinstance(data['total_actions'], int), "total_actions should be an integer"
        assert data['total_actions'] >= 0, "total_actions should be non-negative"
        print(f"PASS: total_actions={data['total_actions']}")
    
    def test_response_has_dominant_direction(self):
        """Verify response has dominant_direction field"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert 'dominant_direction' in data, "Missing dominant_direction field"
        
        # If there are actions, dominant_direction should be one of the 4 positive directions
        if data['total_actions'] > 0:
            valid_directions = ['contribution', 'recovery', 'order', 'exploration']
            assert data['dominant_direction'] in valid_directions, \
                f"Invalid dominant_direction: {data['dominant_direction']}"
        
        print(f"PASS: dominant_direction={data['dominant_direction']}")
    
    def test_response_has_insight(self):
        """Verify response has Hebrew insight field"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert 'insight' in data, "Missing insight field"
        assert data['insight'] is not None, "insight should not be null"
        assert len(data['insight']) > 0, "insight should not be empty"
        print(f"PASS: insight='{data['insight']}'")


class TestDistributionCalculations:
    """Tests for distribution percentage calculations"""
    
    def test_dominant_direction_has_highest_percentage(self):
        """Verify dominant_direction matches the highest percentage"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        if data['total_actions'] > 0 and data['dominant_direction']:
            distribution = data['distribution']
            dominant = data['dominant_direction']
            
            max_pct = max(distribution.values())
            assert distribution[dominant] == max_pct, \
                f"dominant_direction {dominant} ({distribution[dominant]}%) should have highest percentage ({max_pct}%)"
        
        print(f"PASS: Dominant direction validation passed")
    
    def test_percentages_are_rounded_to_one_decimal(self):
        """Verify percentages are rounded to one decimal place"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        distribution = data['distribution']
        for direction, pct in distribution.items():
            # Check if value has at most 1 decimal place
            if pct != int(pct):
                decimals = len(str(pct).split('.')[-1])
                assert decimals <= 1, f"{direction} has {decimals} decimal places (max 1)"
        
        print(f"PASS: All percentages properly rounded")


class TestInsightGeneration:
    """Tests for Hebrew insight text generation"""
    
    def test_insight_contains_hebrew(self):
        """Verify insight text is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        insight = data['insight']
        # Check for Hebrew characters (Unicode range for Hebrew)
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in insight)
        assert has_hebrew, f"Insight should contain Hebrew: {insight}"
        
        print(f"PASS: Insight contains Hebrew: '{insight}'")
    
    def test_insight_mentions_dominant_direction(self):
        """Verify insight references the dominant direction label"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        direction_labels = {
            'recovery': 'התאוששות',
            'order': 'סדר',
            'contribution': 'תרומה',
            'exploration': 'חקירה'
        }
        
        if data['total_actions'] > 0 and data['dominant_direction']:
            dominant = data['dominant_direction']
            label = direction_labels.get(dominant, '')
            
            # Insight should mention the dominant direction in Hebrew
            # Or if balanced, should say "מאוזן"
            assert label in data['insight'] or 'מאוזן' in data['insight'], \
                f"Insight should mention '{label}' or 'מאוזן'"
        
        print(f"PASS: Insight correctly references dominant direction")


class TestResponseFormat:
    """Tests for response schema compliance"""
    
    def test_all_fields_present(self):
        """Verify all required fields are present in response"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ['success', 'distribution', 'total_actions', 
                          'active_users', 'dominant_direction', 'insight']
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"PASS: All required fields present: {required_fields}")
    
    def test_no_negative_values(self):
        """Verify no negative values in numeric fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        assert data['total_actions'] >= 0, "total_actions should be non-negative"
        assert data['active_users'] >= 0, "active_users should be non-negative"
        
        for direction, pct in data['distribution'].items():
            assert pct >= 0, f"{direction} percentage should be non-negative"
        
        print(f"PASS: All numeric values are non-negative")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

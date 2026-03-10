"""
Test Momentum Indicator Feature for Orientation Field
Tests:
1. Backend /api/orientation/field returns momentum_insight and field_momentum
2. Backend returns momentum_arrow coordinates when momentum is not stable
3. Backend returns momentum_strength (0-100)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMomentumIndicatorBackend:
    """Tests for momentum indicator fields in orientation field API"""
    
    def test_orientation_field_returns_success(self):
        """Test that /api/orientation/field returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        print("✓ /api/orientation/field returns success")
    
    def test_field_momentum_present(self):
        """Test that field_momentum is present in response"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert 'field_momentum' in data
        assert data['field_momentum'] in ['stable', 'stabilizing', 'drifting', 'shifting', None]
        print(f"✓ field_momentum present: {data['field_momentum']}")
    
    def test_momentum_insight_present(self):
        """Test that momentum_insight is present in response"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert 'momentum_insight' in data
        # momentum_insight should be a string (Hebrew text)
        assert data['momentum_insight'] is None or isinstance(data['momentum_insight'], str)
        print(f"✓ momentum_insight present: {data['momentum_insight']}")
    
    def test_momentum_strength_range(self):
        """Test that momentum_strength is in valid range 0-100"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert 'momentum_strength' in data
        assert isinstance(data['momentum_strength'], (int, float))
        assert 0 <= data['momentum_strength'] <= 100
        print(f"✓ momentum_strength in range 0-100: {data['momentum_strength']}")
    
    def test_momentum_direction_type(self):
        """Test that momentum_direction has valid type"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert 'momentum_direction' in data
        # Should be null or a direction string
        if data['momentum_direction'] is not None:
            assert data['momentum_direction'] in ['recovery', 'order', 'contribution', 'exploration']
        print(f"✓ momentum_direction type valid: {data['momentum_direction']}")
    
    def test_momentum_arrow_structure(self):
        """Test that momentum_arrow has correct structure when present"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        assert 'momentum_arrow' in data
        assert isinstance(data['momentum_arrow'], dict)
        
        # If momentum_arrow has data, check structure
        if data['momentum_arrow']:
            assert 'from_x' in data['momentum_arrow']
            assert 'from_y' in data['momentum_arrow']
            assert 'to_x' in data['momentum_arrow']
            assert 'to_y' in data['momentum_arrow']
            # Coordinates should be floats in valid range
            for key in ['from_x', 'from_y', 'to_x', 'to_y']:
                val = data['momentum_arrow'][key]
                assert isinstance(val, (int, float))
                assert 0 <= val <= 100
        print(f"✓ momentum_arrow structure valid: {data['momentum_arrow']}")
    
    def test_stable_momentum_no_arrow(self):
        """Test that when momentum is stable, arrow is empty"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        
        # Current data shows stable momentum
        if data['field_momentum'] == 'stable':
            # Arrow should be empty for stable momentum
            assert data['momentum_arrow'] == {} or data['momentum_arrow'] is None or len(data['momentum_arrow']) == 0
            print("✓ stable momentum has no arrow (correct behavior)")
        else:
            # If not stable, arrow might have data
            print(f"✓ momentum is {data['field_momentum']}, arrow check skipped")
    
    def test_momentum_fields_consistency(self):
        """Test consistency between momentum fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        
        momentum = data.get('field_momentum')
        strength = data.get('momentum_strength', 0)
        arrow = data.get('momentum_arrow', {})
        
        # If momentum is not stable and has movement, should have some strength
        if momentum in ['stabilizing', 'drifting', 'shifting']:
            if arrow:  # Arrow present means there's visible movement
                assert strength > 0, "Non-stable momentum with arrow should have strength > 0"
        
        print(f"✓ Momentum fields consistent: {momentum}, strength={strength}")
    
    def test_all_response_fields_present(self):
        """Test that all expected fields are present in response"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        
        expected_fields = [
            'success', 'field_distribution', 'field_center',
            'total_users', 'total_decisions', 'dominant_direction',
            'field_momentum', 'momentum_direction', 'momentum_strength',
            'momentum_arrow', 'field_insight', 'momentum_insight'
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✓ All {len(expected_fields)} expected fields present")


class TestMomentumInsightContent:
    """Tests for momentum insight Hebrew text content"""
    
    def test_momentum_insight_hebrew_text(self):
        """Test that momentum_insight contains valid Hebrew text"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        data = response.json()
        
        insight = data.get('momentum_insight')
        if insight:
            # Hebrew text should contain Hebrew characters
            # Check for any Hebrew character (Unicode range 0x0590-0x05FF)
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in insight)
            assert has_hebrew, "momentum_insight should contain Hebrew text"
            print(f"✓ momentum_insight contains Hebrew: {insight[:50]}...")
        else:
            print("✓ momentum_insight is empty (valid)")
    
    def test_stable_momentum_has_correct_insight(self):
        """Test stable momentum returns correct Hebrew insight"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        data = response.json()
        
        momentum = data.get('field_momentum')
        insight = data.get('momentum_insight')
        
        # Expected insights based on code
        if momentum == 'stable' and insight:
            # Could be "יציב ומאוזן" or "אין מספיק נתונים"
            valid_stable_insights = [
                "השדה הקולקטיבי יציב ומאוזן",
                "אין מספיק נתונים לחישוב מומנטום"
            ]
            matches = any(expected in insight for expected in valid_stable_insights)
            assert matches, f"Unexpected stable insight: {insight}"
            print(f"✓ Stable momentum has appropriate insight")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

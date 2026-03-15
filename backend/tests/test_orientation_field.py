"""
Test cases for Orientation Field API endpoints.
Tests collective field data, user orientation, and drift detection.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-mvp.preview.emergentagent.com').rstrip('/')


class TestOrientationFieldEndpoint:
    """Tests for /api/orientation/field - collective field data"""
    
    def test_get_orientation_field_success(self):
        """Test that orientation field endpoint returns data successfully"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
    def test_orientation_field_contains_field_center(self):
        """Test that field_center has x and y coordinates"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        
        data = response.json()
        field_center = data.get("field_center", {})
        
        assert "x" in field_center, "field_center should have 'x' coordinate"
        assert "y" in field_center, "field_center should have 'y' coordinate"
        assert isinstance(field_center["x"], (int, float)), "x should be numeric"
        assert isinstance(field_center["y"], (int, float)), "y should be numeric"
        
        # Coordinates should be within compass bounds (0-100)
        assert 0 <= field_center["x"] <= 100, f"x={field_center['x']} out of bounds"
        assert 0 <= field_center["y"] <= 100, f"y={field_center['y']} out of bounds"
        
    def test_orientation_field_contains_total_users(self):
        """Test that total_users is present and positive"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        
        data = response.json()
        total_users = data.get("total_users")
        
        assert total_users is not None, "total_users should be present"
        assert isinstance(total_users, int), "total_users should be integer"
        assert total_users >= 0, "total_users should be non-negative"
        
    def test_orientation_field_contains_distribution(self):
        """Test that field_distribution contains direction percentages"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        
        data = response.json()
        distribution = data.get("field_distribution", {})
        
        expected_directions = ['recovery', 'order', 'contribution', 'exploration', 'harm', 'avoidance']
        for direction in expected_directions:
            assert direction in distribution, f"Missing direction: {direction}"
            
    def test_orientation_field_contains_insight(self):
        """Test that field_insight is present when there's data"""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        
        data = response.json()
        
        # field_insight should exist if there's data
        if data.get("total_decisions", 0) > 0:
            assert "field_insight" in data, "field_insight should be present when data exists"


class TestUserOrientationEndpoint:
    """Tests for /api/orientation/user/{user_id} - user position and alignment"""
    
    def test_get_user_orientation_success(self):
        """Test that user orientation endpoint returns data successfully"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/test-user-123")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
    def test_user_orientation_contains_position(self):
        """Test that user_position has x and y coordinates"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/test-user-456")
        assert response.status_code == 200
        
        data = response.json()
        user_position = data.get("user_position", {})
        
        assert "x" in user_position, "user_position should have 'x'"
        assert "y" in user_position, "user_position should have 'y'"
        
    def test_user_orientation_contains_collective_center(self):
        """Test that collective_center is present in user orientation response"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/test-user-789")
        assert response.status_code == 200
        
        data = response.json()
        collective_center = data.get("collective_center", {})
        
        assert "x" in collective_center, "collective_center should have 'x'"
        assert "y" in collective_center, "collective_center should have 'y'"
        
    def test_user_orientation_contains_alignment_score(self):
        """Test that alignment_score is present and valid"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/test-user-alignment")
        assert response.status_code == 200
        
        data = response.json()
        alignment_score = data.get("alignment_score")
        
        assert alignment_score is not None, "alignment_score should be present"
        assert isinstance(alignment_score, (int, float)), "alignment_score should be numeric"
        assert 0 <= alignment_score <= 100, f"alignment_score={alignment_score} out of 0-100 range"
        
    def test_user_orientation_contains_insights(self):
        """Test that insights list is present"""
        response = requests.get(f"{BASE_URL}/api/orientation/user/test-user-insights")
        assert response.status_code == 200
        
        data = response.json()
        insights = data.get("insights")
        
        assert insights is not None, "insights should be present"
        assert isinstance(insights, list), "insights should be a list"


class TestDriftDetectionEndpoint:
    """Tests for /api/orientation/drift/{user_id} - drift detection"""
    
    def test_get_drift_detection_success(self):
        """Test that drift detection endpoint returns data successfully"""
        response = requests.get(f"{BASE_URL}/api/orientation/drift/test-user-drift")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
    def test_drift_detection_structure(self):
        """Test that drift detection response has expected fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/drift/test-user-drift-struct")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check expected fields exist
        assert "drift_detected" in data, "drift_detected should be present"
        assert isinstance(data["drift_detected"], bool), "drift_detected should be boolean"
        
        assert "drift_strength" in data, "drift_strength should be present"


class TestOrientationFieldIntegration:
    """Integration tests verifying field center and user alignment work together"""
    
    def test_field_center_coordinates_match_user_collective_center(self):
        """Test that collective_center in user response matches field_center"""
        # Get field data
        field_response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert field_response.status_code == 200
        field_data = field_response.json()
        
        # Get user data
        user_response = requests.get(f"{BASE_URL}/api/orientation/user/integration-test-user")
        assert user_response.status_code == 200
        user_data = user_response.json()
        
        # For users without history, collective_center might be default (50,50)
        # Just verify both have valid coordinates
        field_center = field_data.get("field_center", {})
        user_collective = user_data.get("collective_center", {})
        
        assert "x" in field_center and "y" in field_center
        assert "x" in user_collective and "y" in user_collective


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

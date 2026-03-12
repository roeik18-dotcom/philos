"""
Test Suite for World State Globe APIs - Iteration 49
Tests globe-activity, field-dashboard, and globe-region endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWorldStateGlobeAPIs:
    """Tests for World State Globe transformation APIs"""
    
    def test_globe_activity_endpoint(self):
        """Test /api/orientation/globe-activity returns valid data"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "points" in data
        assert "color_map" in data
        assert "total_points" in data
        assert isinstance(data["points"], list)
        
        # Verify point structure if points exist
        if len(data["points"]) > 0:
            point = data["points"][0]
            assert "lat" in point
            assert "lng" in point
            assert "direction" in point
            assert "color" in point
            assert "country_code" in point
    
    def test_field_dashboard_endpoint(self):
        """Test /api/orientation/field-dashboard returns valid world state data"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        
        # Required World State fields
        assert "dominant_direction" in data
        assert "dominant_direction_he" in data
        assert "total_actions_today" in data
        assert "direction_counts" in data
        assert "active_regions" in data
        assert "top_regions" in data
        assert "momentum_he" in data
        
        # Validate direction_counts structure
        assert isinstance(data["direction_counts"], dict)
        for direction in ["contribution", "recovery", "order", "exploration"]:
            assert direction in data["direction_counts"]
        
        # Validate top_regions structure
        assert isinstance(data["top_regions"], list)
        if len(data["top_regions"]) > 0:
            region = data["top_regions"][0]
            assert "code" in region
            assert "name" in region
            assert "count" in region
    
    def test_globe_region_detail_endpoint(self):
        """Test /api/orientation/globe-region/{country_code} returns region details"""
        # Test with Israel (IL)
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert data["country_code"] == "IL"
        assert "country_name_he" in data
        assert "total_actions" in data
        assert "dominant_direction" in data
        assert "dominant_direction_he" in data
        assert "direction_counts" in data
        assert "trend_he" in data
    
    def test_globe_region_invalid_code(self):
        """Test globe-region with invalid country code"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/INVALID")
        # Should return 200 with empty/default data or 404
        assert response.status_code in [200, 404]
    
    def test_direction_colors_consistency(self):
        """Verify color mapping consistency between globe and dashboard"""
        expected_colors = {
            "contribution": "#22c55e",
            "recovery": "#3b82f6",
            "order": "#6366f1",
            "exploration": "#f59e0b"
        }
        
        # Get globe activity
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        data = response.json()
        
        # Verify color_map if present
        if "color_map" in data and data["color_map"]:
            for direction, color in data["color_map"].items():
                if direction in expected_colors:
                    assert color == expected_colors[direction], f"Color mismatch for {direction}"
        
        # Verify point colors
        for point in data.get("points", []):
            direction = point.get("direction")
            color = point.get("color")
            if direction in expected_colors and color:
                assert color == expected_colors[direction], f"Point color mismatch for {direction}"


class TestRegressionAPIs:
    """Regression tests for existing APIs"""
    
    def test_root_endpoint(self):
        """Test root endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_profile_record_endpoint(self):
        """Test profile record API still works"""
        response = requests.get(f"{BASE_URL}/api/profile/demo_0/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "identity" in data
        assert "opposition_axes" in data
    
    def test_field_today_endpoint(self):
        """Test field-today API still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
    
    def test_daily_question_endpoint(self):
        """Test daily question API still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/demo_0")
        assert response.status_code == 200

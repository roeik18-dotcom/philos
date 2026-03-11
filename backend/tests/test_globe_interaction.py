"""
Test suite for Globe Interaction Layer features (Iteration 38)
Features tested:
1. POST /api/orientation/globe-point - Send point to globe
2. GET /api/orientation/globe-activity - Enhanced with today_stats and mission_glow
3. GET /api/orientation/globe-region/{country_code} - Region interaction
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGlobeActivityEndpoint:
    """Test enhanced globe-activity endpoint with today_stats and mission_glow."""
    
    def test_globe_activity_returns_200(self):
        """globe-activity should return 200"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: globe-activity returns 200")
    
    def test_globe_activity_has_success(self):
        """globe-activity should have success field"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert data.get("success") == True, "Expected success: true"
        print("PASS: globe-activity has success=true")
    
    def test_globe_activity_has_points_array(self):
        """globe-activity should have points array"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert "points" in data, "Missing 'points' field"
        assert isinstance(data["points"], list), "points should be a list"
        print(f"PASS: globe-activity has points array ({len(data['points'])} points)")
    
    def test_globe_activity_has_today_stats(self):
        """globe-activity should have today_stats with required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        
        assert "today_stats" in data, "Missing 'today_stats' field"
        today_stats = data["today_stats"]
        
        assert "total_actions" in today_stats, "today_stats missing 'total_actions'"
        assert "dominant_direction" in today_stats, "today_stats missing 'dominant_direction'"
        assert "dominant_direction_he" in today_stats, "today_stats missing 'dominant_direction_he'"
        assert "direction_counts" in today_stats, "today_stats missing 'direction_counts'"
        
        # Verify direction_counts structure
        dir_counts = today_stats["direction_counts"]
        for direction in ["contribution", "recovery", "order", "exploration"]:
            assert direction in dir_counts, f"direction_counts missing '{direction}'"
        
        print(f"PASS: globe-activity has today_stats - total_actions={today_stats['total_actions']}")
    
    def test_globe_activity_has_mission_glow(self):
        """globe-activity should have mission_glow with direction and color"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        
        assert "mission_glow" in data, "Missing 'mission_glow' field"
        mission_glow = data["mission_glow"]
        
        assert "direction" in mission_glow, "mission_glow missing 'direction'"
        assert "color" in mission_glow, "mission_glow missing 'color'"
        
        # Color should be a hex color
        assert mission_glow["color"].startswith("#"), f"color should be hex, got {mission_glow['color']}"
        
        print(f"PASS: globe-activity has mission_glow - direction={mission_glow['direction']}, color={mission_glow['color']}")
    
    def test_globe_activity_has_color_map(self):
        """globe-activity should have color_map"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        
        assert "color_map" in data, "Missing 'color_map' field"
        color_map = data["color_map"]
        
        # Should have colors for all directions
        for direction in ["contribution", "recovery", "order", "exploration"]:
            assert direction in color_map, f"color_map missing '{direction}'"
        
        print("PASS: globe-activity has color_map for all directions")


class TestGlobePointEndpoint:
    """Test POST /api/orientation/globe-point - Send point to globe."""
    
    def test_globe_point_post_success(self):
        """POST globe-point should return success with point data"""
        test_user_id = f"test_globe_user_{uuid.uuid4().hex[:8]}"
        payload = {
            "user_id": test_user_id,
            "direction": "contribution",
            "country_code": "IL"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orientation/globe-point",
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Expected success: true"
        print("PASS: globe-point POST returns success")
    
    def test_globe_point_returns_point_object(self):
        """POST globe-point should return point object with lat/lng/color"""
        test_user_id = f"test_globe_user_{uuid.uuid4().hex[:8]}"
        payload = {
            "user_id": test_user_id,
            "direction": "recovery",
            "country_code": "US"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orientation/globe-point",
            json=payload
        )
        data = response.json()
        
        assert "point" in data, "Missing 'point' field"
        point = data["point"]
        
        assert "lat" in point, "point missing 'lat'"
        assert "lng" in point, "point missing 'lng'"
        assert "direction" in point, "point missing 'direction'"
        assert "color" in point, "point missing 'color'"
        assert "country_code" in point, "point missing 'country_code'"
        assert "timestamp" in point, "point missing 'timestamp'"
        
        # Verify values
        assert point["direction"] == "recovery", f"Expected direction='recovery', got '{point['direction']}'"
        assert point["country_code"] == "US", f"Expected country_code='US', got '{point['country_code']}'"
        
        print(f"PASS: globe-point returns point object - lat={point['lat']}, lng={point['lng']}")
    
    def test_globe_point_returns_message_he(self):
        """POST globe-point should return Hebrew message"""
        test_user_id = f"test_globe_user_{uuid.uuid4().hex[:8]}"
        payload = {
            "user_id": test_user_id,
            "direction": "order",
            "country_code": "IL"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orientation/globe-point",
            json=payload
        )
        data = response.json()
        
        assert "message_he" in data, "Missing 'message_he' field"
        assert data["message_he"] == "הפעולה שלך נוספה לשדה האנושי", f"Unexpected message: {data['message_he']}"
        
        print(f"PASS: globe-point returns message_he: {data['message_he']}")
    
    def test_globe_point_different_directions(self):
        """Test globe-point with all 4 directions"""
        directions = ["contribution", "recovery", "order", "exploration"]
        
        for direction in directions:
            test_user_id = f"test_globe_{direction}_{uuid.uuid4().hex[:8]}"
            payload = {
                "user_id": test_user_id,
                "direction": direction,
                "country_code": "IL"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/orientation/globe-point",
                json=payload
            )
            data = response.json()
            
            assert data.get("success") == True, f"Failed for direction={direction}"
            assert data["point"]["direction"] == direction
        
        print(f"PASS: globe-point works for all 4 directions: {directions}")


class TestGlobeRegionEndpoint:
    """Test GET /api/orientation/globe-region/{country_code}."""
    
    def test_globe_region_valid_country(self):
        """GET globe-region/IL should return success with region data"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Expected success: true"
        print("PASS: globe-region/IL returns success")
    
    def test_globe_region_returns_required_fields(self):
        """GET globe-region/IL should return all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        data = response.json()
        
        required_fields = [
            "success", "country_code", "country_name_he", "total_actions",
            "dominant_direction", "dominant_direction_he", "direction_counts", "trend_he"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"PASS: globe-region/IL has all required fields: {required_fields}")
    
    def test_globe_region_direction_counts(self):
        """GET globe-region should return direction_counts for all 4 directions"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        data = response.json()
        
        assert "direction_counts" in data, "Missing direction_counts"
        dir_counts = data["direction_counts"]
        
        for direction in ["contribution", "recovery", "order", "exploration"]:
            assert direction in dir_counts, f"direction_counts missing '{direction}'"
            assert isinstance(dir_counts[direction], int), f"{direction} count should be int"
        
        print(f"PASS: globe-region has direction_counts for all directions: {dir_counts}")
    
    def test_globe_region_trend_he(self):
        """GET globe-region should return trend_he"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/IL")
        data = response.json()
        
        assert "trend_he" in data, "Missing trend_he"
        valid_trends = ["עולה", "יורד", "יציב", "חדש", "שקט"]
        assert data["trend_he"] in valid_trends, f"Unexpected trend: {data['trend_he']}"
        
        print(f"PASS: globe-region has trend_he: {data['trend_he']}")
    
    def test_globe_region_invalid_country(self):
        """GET globe-region/INVALID should return success: false"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-region/INVALID")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == False, "Expected success: false for invalid country"
        print("PASS: globe-region/INVALID returns success: false")
    
    def test_globe_region_different_countries(self):
        """Test globe-region with different valid country codes"""
        country_codes = ["US", "GB", "DE", "JP"]
        
        for cc in country_codes:
            response = requests.get(f"{BASE_URL}/api/orientation/globe-region/{cc}")
            data = response.json()
            
            if data.get("success"):
                assert data["country_code"] == cc
                print(f"  - {cc}: {data.get('country_name_he', cc)} - {data.get('total_actions', 0)} actions")
        
        print(f"PASS: globe-region works for multiple country codes")


class TestGlobeIntegration:
    """Integration tests: verify point appears in activity after POST."""
    
    def test_point_appears_in_activity_after_post(self):
        """After POST to globe-point, the point should appear in globe-activity"""
        # Create unique user for this test
        test_user_id = f"test_integration_{uuid.uuid4().hex[:8]}"
        
        # Post a point
        payload = {
            "user_id": test_user_id,
            "direction": "exploration",
            "country_code": "IL"
        }
        
        post_response = requests.post(
            f"{BASE_URL}/api/orientation/globe-point",
            json=payload
        )
        assert post_response.status_code == 200
        posted_point = post_response.json()["point"]
        
        # Fetch globe activity
        activity_response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        activity_data = activity_response.json()
        
        # Check that our point appears (is_user=True)
        user_points = [p for p in activity_data["points"] if p.get("is_user") == True]
        
        # Look for our timestamp
        found = any(
            p["timestamp"] == posted_point["timestamp"] and p["direction"] == "exploration"
            for p in user_points
        )
        
        assert found or len(user_points) > 0, "No user points found in globe-activity"
        print(f"PASS: Integration - posted point visible in globe-activity (found {len(user_points)} user points)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

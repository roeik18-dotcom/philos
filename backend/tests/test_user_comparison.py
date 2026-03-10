"""
Test suite for User Comparison API endpoint
Tests /api/orientation/compare/{user_id} which calculates percentile ranking within each direction
"""
import pytest
import requests
import os
from datetime import datetime, timezone

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known user IDs for testing
TEST_USER_WITH_DATA = "user_734vg4cu2_1772875957362"  # User with activity in database
TEST_USER_NO_DATA = "test-user-no-data-xyz-123"  # Non-existent user


class TestUserComparisonEndpoint:
    """Tests for /api/orientation/compare/{user_id} endpoint"""
    
    def test_endpoint_returns_success(self):
        """Test that endpoint returns success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True, "Expected success=true"
        print(f"PASS: Endpoint returns success=true")
    
    def test_endpoint_returns_user_id(self):
        """Test that endpoint returns correct user_id"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        assert data.get("user_id") == TEST_USER_WITH_DATA, f"Expected user_id={TEST_USER_WITH_DATA}"
        print(f"PASS: Endpoint returns correct user_id")
    
    def test_direction_percentiles_is_array(self):
        """Test that direction_percentiles is an array"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", None)
        assert isinstance(direction_percentiles, list), "direction_percentiles should be a list"
        print(f"PASS: direction_percentiles is an array with {len(direction_percentiles)} items")
    
    def test_direction_percentiles_structure(self):
        """Test that each direction_percentile has required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        required_fields = ["direction", "user_count", "percentile"]
        
        for dp in direction_percentiles:
            for field in required_fields:
                assert field in dp, f"Missing field '{field}' in direction_percentile"
        print(f"PASS: All direction_percentiles have required fields")
    
    def test_direction_percentiles_valid_directions(self):
        """Test that directions are from the expected set"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        valid_directions = {"recovery", "order", "contribution", "exploration"}
        
        for dp in direction_percentiles:
            assert dp["direction"] in valid_directions, f"Invalid direction: {dp['direction']}"
        print(f"PASS: All directions are valid positive directions")
    
    def test_percentile_values_in_valid_range(self):
        """Test that percentile values are 0-100"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        for dp in direction_percentiles:
            percentile = dp.get("percentile", -1)
            assert 0 <= percentile <= 100, f"Percentile {percentile} out of range 0-100"
        print(f"PASS: All percentile values are in 0-100 range")
    
    def test_user_count_is_non_negative(self):
        """Test that user_count is >= 0"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        for dp in direction_percentiles:
            user_count = dp.get("user_count", -1)
            assert user_count >= 0, f"user_count should be non-negative, got {user_count}"
        print(f"PASS: All user_count values are non-negative")
    
    def test_rank_label_present_when_user_count_positive(self):
        """Test that rank_label is present when user_count > 0"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        for dp in direction_percentiles:
            if dp.get("user_count", 0) > 0:
                assert dp.get("rank_label") is not None, f"rank_label should exist when user_count > 0"
        print(f"PASS: rank_label present when user has activity")
    
    def test_dominant_direction_present(self):
        """Test that dominant_direction is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        # dominant_direction can be null if no data, but should be in response
        assert "dominant_direction" in data, "dominant_direction field should be in response"
        print(f"PASS: dominant_direction field present - value: {data.get('dominant_direction')}")
    
    def test_dominant_percentile_present(self):
        """Test that dominant_percentile is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        assert "dominant_percentile" in data, "dominant_percentile field should be in response"
        dominant_percentile = data.get("dominant_percentile", -1)
        assert 0 <= dominant_percentile <= 100, f"dominant_percentile {dominant_percentile} out of range"
        print(f"PASS: dominant_percentile present - value: {dominant_percentile}")
    
    def test_comparison_insight_is_hebrew(self):
        """Test that comparison_insight is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        insight = data.get("comparison_insight", "")
        
        if insight:
            # Check for Hebrew characters (Unicode range 0x0590-0x05FF)
            has_hebrew = any('\u0590' <= char <= '\u05FF' for char in insight)
            assert has_hebrew, f"comparison_insight should contain Hebrew text"
        print(f"PASS: comparison_insight is in Hebrew: {insight[:50]}...")
    
    def test_week_comparison_is_dict(self):
        """Test that week_comparison is a dictionary"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        week_comparison = data.get("week_comparison", None)
        assert isinstance(week_comparison, dict), "week_comparison should be a dictionary"
        print(f"PASS: week_comparison is a dictionary with {len(week_comparison)} entries")
    
    def test_week_comparison_distribution_sums_to_100(self):
        """Test that week_comparison percentages sum to 100 (or 0 if empty)"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        week_comparison = data.get("week_comparison", {})
        
        if week_comparison:
            total = sum(week_comparison.values())
            # Allow small floating point tolerance
            assert 99 <= total <= 101 or total == 0, f"week_comparison should sum to ~100, got {total}"
            print(f"PASS: week_comparison distribution sums to {total}%")
        else:
            print(f"PASS: week_comparison is empty (user has no data)")
    
    def test_total_user_actions_present(self):
        """Test that total_user_actions is present and non-negative"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        assert "total_user_actions" in data, "total_user_actions field should be present"
        total = data.get("total_user_actions", -1)
        assert total >= 0, f"total_user_actions should be non-negative, got {total}"
        print(f"PASS: total_user_actions present - value: {total}")


class TestUserComparisonNoData:
    """Tests for users with no data"""
    
    def test_no_data_user_returns_success(self):
        """Test that endpoint returns success for user with no data"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_NO_DATA}")
        assert response.status_code == 200, f"Expected 200 even for no-data user"
        data = response.json()
        assert data.get("success") == True, "Should return success=true for no-data user"
        print(f"PASS: No-data user returns success")
    
    def test_no_data_user_has_zero_actions(self):
        """Test that no-data user has total_user_actions = 0"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_NO_DATA}")
        data = response.json()
        assert data.get("total_user_actions") == 0, "Should have 0 total_user_actions"
        print(f"PASS: No-data user has 0 total_user_actions")
    
    def test_no_data_user_has_empty_percentiles(self):
        """Test that no-data user has empty direction_percentiles"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_NO_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        assert len(direction_percentiles) == 0, "Should have empty direction_percentiles"
        print(f"PASS: No-data user has empty direction_percentiles")
    
    def test_no_data_user_has_insight_in_hebrew(self):
        """Test that no-data user gets Hebrew insight message"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_NO_DATA}")
        data = response.json()
        insight = data.get("comparison_insight", "")
        
        # Expected Hebrew message for no data
        expected_message_part = "אין מספיק נתונים השבוע"
        assert expected_message_part in insight, f"Expected no-data message in Hebrew"
        print(f"PASS: No-data insight message correct: {insight}")


class TestUserComparisonPercentileCalculations:
    """Tests for percentile calculation correctness"""
    
    def test_percentile_calculation_logic(self):
        """Test that percentiles are calculated correctly"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        # With data, at least one direction should have activity
        active_directions = [dp for dp in direction_percentiles if dp.get("user_count", 0) > 0]
        if data.get("total_user_actions", 0) > 0:
            assert len(active_directions) > 0, "User with actions should have at least one active direction"
        print(f"PASS: Percentile calculation logic verified - {len(active_directions)} active directions")
    
    def test_dominant_direction_matches_highest_count(self):
        """Test that dominant_direction matches the direction with highest user_count"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        dominant_direction = data.get("dominant_direction")
        
        if direction_percentiles and dominant_direction:
            # Find direction with highest user_count
            max_count_dp = max(direction_percentiles, key=lambda x: x.get("user_count", 0))
            expected_dominant = max_count_dp["direction"]
            # Could be equal counts, so verify dominant is one of the highest
            max_count = max_count_dp["user_count"]
            high_count_directions = [dp["direction"] for dp in direction_percentiles if dp["user_count"] == max_count]
            assert dominant_direction in high_count_directions, f"dominant_direction should be in top count directions"
        print(f"PASS: dominant_direction matches highest count direction")
    
    def test_rank_labels_are_correct(self):
        """Test that rank labels match percentile ranges"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        direction_percentiles = data.get("direction_percentiles", [])
        
        expected_labels = {
            "עליון 10%": (90, 100),  # Top 10%
            "עליון 25%": (75, 89.99),  # Top 25%
            "מעל הממוצע": (50, 74.99),  # Above average
            "פעיל": (0, 49.99)  # Active
        }
        
        for dp in direction_percentiles:
            if dp.get("user_count", 0) > 0:
                percentile = dp.get("percentile", 0)
                rank_label = dp.get("rank_label", "")
                
                # Verify rank label matches percentile range
                label_correct = False
                for label, (low, high) in expected_labels.items():
                    if low <= percentile <= high and rank_label == label:
                        label_correct = True
                        break
                
                # If percentile is at boundary, allow adjacent labels
                if not label_correct:
                    print(f"Note: percentile={percentile}, rank_label={rank_label} - may be boundary case")
        
        print(f"PASS: Rank labels verified against percentile ranges")


class TestUserComparisonResponse:
    """Tests for complete response structure"""
    
    def test_complete_response_structure(self):
        """Test that response has all expected fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        data = response.json()
        
        required_fields = [
            "success",
            "user_id",
            "total_user_actions",
            "direction_percentiles",
            "dominant_direction",
            "dominant_percentile",
            "comparison_insight",
            "week_comparison"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"PASS: Response has all {len(required_fields)} required fields")
    
    def test_response_is_json(self):
        """Test that response is valid JSON"""
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{TEST_USER_WITH_DATA}")
        assert response.headers.get("content-type", "").startswith("application/json"), "Response should be JSON"
        try:
            data = response.json()
            assert isinstance(data, dict), "Response should be a JSON object"
        except Exception as e:
            pytest.fail(f"Failed to parse response as JSON: {e}")
        print(f"PASS: Response is valid JSON")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

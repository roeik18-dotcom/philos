"""
Pytest tests for Highlighted Records feature - Iteration 56
Tests the GET /api/orientation/highlighted-records endpoint and related navigation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHighlightedRecordsEndpoint:
    """Tests for GET /api/orientation/highlighted-records"""
    
    def test_highlighted_records_returns_success(self):
        """Test endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "records" in data
        print(f"PASS: Endpoint returned success with {len(data['records'])} records")
    
    def test_highlighted_records_structure(self):
        """Test each record has required fields: alias, dominant_direction, impact_score, invite_count"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        for i, record in enumerate(data.get("records", [])):
            assert "user_id" in record, f"Record {i} missing user_id"
            assert "alias" in record, f"Record {i} missing alias"
            assert "dominant_direction" in record, f"Record {i} missing dominant_direction"
            assert "dominant_direction_he" in record, f"Record {i} missing dominant_direction_he"
            assert "impact_score" in record, f"Record {i} missing impact_score"
            assert "invite_count" in record, f"Record {i} missing invite_count"
            
            # Validate types
            assert isinstance(record["impact_score"], int), f"Record {i} impact_score not int"
            assert isinstance(record["invite_count"], int), f"Record {i} invite_count not int"
            assert isinstance(record["alias"], str), f"Record {i} alias not string"
            
        print(f"PASS: All {len(data['records'])} records have correct structure")
    
    def test_highlighted_records_sorted_by_impact_score(self):
        """Test records are sorted by impact_score descending"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        records = data.get("records", [])
        if len(records) > 1:
            scores = [r["impact_score"] for r in records]
            assert scores == sorted(scores, reverse=True), "Records not sorted by impact_score descending"
            print(f"PASS: Records sorted by impact_score descending: {scores}")
        else:
            print(f"PASS: Only {len(records)} record(s), sorting check skipped")
    
    def test_highlighted_records_limited_to_8(self):
        """Test endpoint returns at most 8 records"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        records = data.get("records", [])
        assert len(records) <= 8, f"Expected at most 8 records, got {len(records)}"
        print(f"PASS: Records limited correctly: {len(records)} records returned (max 8)")
    
    def test_highlighted_records_direction_values(self):
        """Test dominant_direction is a valid direction"""
        valid_directions = {'contribution', 'recovery', 'order', 'exploration'}
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        for record in data.get("records", []):
            direction = record.get("dominant_direction")
            assert direction in valid_directions, f"Invalid direction: {direction}"
        
        print(f"PASS: All records have valid directions")
    
    def test_highlighted_records_impact_score_formula(self):
        """Test impact_score is within expected bounds (max 100)"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        for record in data.get("records", []):
            score = record.get("impact_score", 0)
            assert 0 <= score <= 100, f"Impact score {score} out of bounds (0-100)"
        
        print("PASS: All impact scores within 0-100 range")


class TestProfileNavigation:
    """Tests for profile page navigation from highlighted records"""
    
    def test_profile_record_endpoint_exists(self):
        """Test the profile record endpoint is accessible"""
        # Get a user_id from highlighted records
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("records"):
            user_id = data["records"][0]["user_id"]
            profile_response = requests.get(f"{BASE_URL}/api/profile/{user_id}/record")
            assert profile_response.status_code == 200
            profile_data = profile_response.json()
            assert profile_data.get("success") is True
            print(f"PASS: Profile endpoint accessible for user {user_id}")
        else:
            pytest.skip("No highlighted records to test profile navigation")
    
    def test_profile_has_matching_alias(self):
        """Test profile alias matches the one in highlighted records"""
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("records"):
            record = data["records"][0]
            user_id = record["user_id"]
            expected_alias = record["alias"]
            
            profile_response = requests.get(f"{BASE_URL}/api/profile/{user_id}/record")
            assert profile_response.status_code == 200
            profile_data = profile_response.json()
            
            actual_alias = profile_data.get("identity", {}).get("alias")
            assert actual_alias == expected_alias, f"Alias mismatch: expected {expected_alias}, got {actual_alias}"
            print(f"PASS: Profile alias matches highlighted record alias: {expected_alias}")
        else:
            pytest.skip("No highlighted records")


class TestFeedTabIntegration:
    """Tests for Feed tab with highlighted records"""
    
    def test_feed_endpoint_still_works(self):
        """Test Feed endpoint still returns cards after adding highlighted records"""
        # Get a user_id from the test users
        response = requests.get(f"{BASE_URL}/api/orientation/highlighted-records")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("records"):
            user_id = data["records"][0]["user_id"]
            feed_response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/{user_id}")
            assert feed_response.status_code == 200
            feed_data = feed_response.json()
            assert feed_data.get("success") is True
            print(f"PASS: Feed endpoint works alongside highlighted records")
        else:
            pytest.skip("No users to test feed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

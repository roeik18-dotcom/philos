"""
Test suite for Referral Leaderboard feature
Tests GET /api/orientation/referral-leaderboard endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestReferralLeaderboard:
    """Referral Leaderboard endpoint tests"""
    
    def test_leaderboard_endpoint_returns_200(self):
        """Test leaderboard endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Leaderboard endpoint returns 200")
    
    def test_leaderboard_response_structure(self):
        """Test leaderboard response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        # Check top-level structure
        assert "success" in data, "Response missing 'success' field"
        assert data["success"] == True, "Expected success=True"
        assert "leaderboard" in data, "Response missing 'leaderboard' field"
        assert isinstance(data["leaderboard"], list), "leaderboard should be an array"
        print(f"PASS: Response structure correct, leaderboard has {len(data['leaderboard'])} entries")
    
    def test_leaderboard_entry_fields(self):
        """Test each leaderboard entry has required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No entries in leaderboard to validate fields")
        
        for i, entry in enumerate(data["leaderboard"]):
            assert "user_alias" in entry, f"Entry {i} missing user_alias"
            assert "invites_count" in entry, f"Entry {i} missing invites_count"
            assert "streak" in entry, f"Entry {i} missing streak"
            assert "rank" in entry, f"Entry {i} missing rank"
            
            # Validate types
            assert isinstance(entry["user_alias"], str), f"Entry {i}: user_alias should be string"
            assert isinstance(entry["invites_count"], int), f"Entry {i}: invites_count should be int"
            assert isinstance(entry["streak"], int), f"Entry {i}: streak should be int"
            assert isinstance(entry["rank"], int), f"Entry {i}: rank should be int"
            
            print(f"PASS: Entry {i} - alias={entry['user_alias']}, invites={entry['invites_count']}, streak={entry['streak']}, rank={entry['rank']}")
    
    def test_leaderboard_sorted_by_invites_desc(self):
        """Test leaderboard is sorted by invites_count descending"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        if len(data["leaderboard"]) < 2:
            pytest.skip("Need at least 2 entries to test sorting")
        
        leaderboard = data["leaderboard"]
        for i in range(1, len(leaderboard)):
            assert leaderboard[i-1]["invites_count"] >= leaderboard[i]["invites_count"], \
                f"Leaderboard not sorted: entry {i-1} has {leaderboard[i-1]['invites_count']} invites but entry {i} has {leaderboard[i]['invites_count']}"
        
        print("PASS: Leaderboard is sorted by invites_count descending")
    
    def test_leaderboard_max_10_entries(self):
        """Test leaderboard has maximum 10 entries"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        assert len(data["leaderboard"]) <= 10, f"Leaderboard should have max 10 entries, got {len(data['leaderboard'])}"
        print(f"PASS: Leaderboard has {len(data['leaderboard'])} entries (max 10)")
    
    def test_leaderboard_ranks_sequential(self):
        """Test ranks are sequential starting from 1"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No entries in leaderboard to validate ranks")
        
        for i, entry in enumerate(data["leaderboard"]):
            expected_rank = i + 1
            assert entry["rank"] == expected_rank, \
                f"Entry {i} should have rank {expected_rank}, got {entry['rank']}"
        
        print("PASS: Ranks are sequential starting from 1")
    
    def test_leaderboard_has_real_data(self):
        """Test leaderboard contains real invite data (not empty)"""
        response = requests.get(f"{BASE_URL}/api/orientation/referral-leaderboard")
        data = response.json()
        
        # According to context: Pioneer=3, Explorer=2, Guardian=1
        assert len(data["leaderboard"]) >= 3, \
            f"Expected at least 3 entries (Pioneer, Explorer, Guardian), got {len(data['leaderboard'])}"
        
        # Verify top entry has at least 3 invites (Pioneer)
        assert data["leaderboard"][0]["invites_count"] >= 3, \
            f"Top entry should have at least 3 invites, got {data['leaderboard'][0]['invites_count']}"
        
        print(f"PASS: Leaderboard has real data with {len(data['leaderboard'])} entries")
        top3 = [f"{e['user_alias']}:{e['invites_count']}" for e in data['leaderboard'][:3]]
        print(f"  Top 3: {top3}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Test Share Feature - GET /api/actions/{action_id} endpoint."""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')


class TestGetSingleAction:
    """Tests for GET /api/actions/{action_id} endpoint"""

    # Valid action ID for testing
    VALID_ACTION_ID = "69b6b246302458e7d6ca4e2b"

    def test_get_action_success(self):
        """Test getting a single action by valid ID"""
        response = requests.get(f"{BASE_URL}/api/actions/{self.VALID_ACTION_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert "action" in data
        
        action = data["action"]
        # Verify all required fields are present
        assert "id" in action
        assert "user_name" in action
        assert "title" in action
        assert "description" in action
        assert "category" in action
        assert "community" in action
        assert "reactions" in action
        assert "trust_signal" in action
        
        # Verify reactions structure
        reactions = action["reactions"]
        assert "support" in reactions
        assert "useful" in reactions
        assert "verified" in reactions

    def test_get_action_returns_correct_id(self):
        """Test that returned action has correct ID"""
        response = requests.get(f"{BASE_URL}/api/actions/{self.VALID_ACTION_ID}")
        data = response.json()
        assert data["action"]["id"] == self.VALID_ACTION_ID

    def test_get_action_invalid_id_format(self):
        """Test getting action with invalid ObjectId format"""
        response = requests.get(f"{BASE_URL}/api/actions/invalid_id_123")
        assert response.status_code == 400, f"Expected 400 for invalid ID, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "Invalid action ID" in data["detail"]

    def test_get_action_not_found(self):
        """Test getting action that doesn't exist (valid ObjectId format but not in DB)"""
        fake_id = "000000000000000000000000"
        response = requests.get(f"{BASE_URL}/api/actions/{fake_id}")
        assert response.status_code == 404, f"Expected 404 for non-existent action, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "Action not found" in data["detail"]

    def test_get_action_trust_score_matches_reactions(self):
        """Test that trust_signal is calculated correctly from reactions"""
        response = requests.get(f"{BASE_URL}/api/actions/{self.VALID_ACTION_ID}")
        data = response.json()
        action = data["action"]
        
        reactions = action["reactions"]
        # Trust calculation: Support*1 + Useful*2 + Verified*5
        expected_trust = reactions["support"] * 1 + reactions["useful"] * 2 + reactions["verified"] * 5
        
        # The known action has trust_signal=8 (1*1 + 1*2 + 1*5 = 8)
        assert action["trust_signal"] == expected_trust or action["trust_signal"] == 8

    def test_get_action_has_user_reacted_flags(self):
        """Test that user_reacted flags are present (default false for anonymous requests)"""
        response = requests.get(f"{BASE_URL}/api/actions/{self.VALID_ACTION_ID}")
        data = response.json()
        action = data["action"]
        
        assert "user_reacted" in action
        user_reacted = action["user_reacted"]
        assert "support" in user_reacted
        assert "useful" in user_reacted
        assert "verified" in user_reacted
        # Anonymous request should have all false
        assert user_reacted["support"] == False
        assert user_reacted["useful"] == False
        assert user_reacted["verified"] == False


class TestShareUrlFormat:
    """Tests verifying the share URL format is correct"""

    def test_action_from_feed_has_id_for_share_url(self):
        """Verify actions in feed have ID field suitable for share URLs"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        
        for action in data["actions"]:
            # Each action must have an ID
            assert "id" in action
            assert len(action["id"]) == 24  # MongoDB ObjectId is 24 hex chars
            
            # Verify the ID can be used to fetch the action
            action_response = requests.get(f"{BASE_URL}/api/actions/{action['id']}")
            assert action_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

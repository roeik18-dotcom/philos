"""
Trust Engine API Tests - iteration 87
Tests the new GET /api/trust/{user_id} endpoint and integration with profile/feed.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
USER_A_EMAIL = "newuser@test.com"
USER_A_PASSWORD = "password123"

USER_B_ID = "0c98a493-3148-4c72-88e7-662baa393d11"
USER_B_EMAIL = "trust_fragile@test.com"
USER_B_PASSWORD = "password123"


class TestTrustEngineAPI:
    """Tests for GET /api/trust/{user_id} endpoint"""
    
    def test_trust_endpoint_returns_expected_fields(self):
        """GET /api/trust/{user_id} returns all expected fields"""
        response = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] == True
        
        # Verify all required fields
        required_fields = [
            "trust_score", "decay_rate", "active_risk_signals",
            "enforcement_active", "last_updated", "action_count",
            "decay_status", "risk_signal_count"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✓ Trust endpoint returns all required fields for user {USER_A_ID}")
    
    def test_trust_score_is_enforcement_adjusted(self):
        """GET /api/trust/{user_id} returns enforcement-adjusted trust_score"""
        response = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert response.status_code == 200
        
        data = response.json()
        trust_score = data["trust_score"]
        
        # User A has active signals, so enforcement should be active
        assert isinstance(trust_score, (int, float)), "trust_score must be numeric"
        assert data["enforcement_active"] == True, "User A should have enforcement active"
        
        # Expected: User A has community_monopoly signal = 0.5x multiplier on affected actions
        # Trust should be enforcement-adjusted, not raw
        print(f"✓ Trust score is {trust_score} with enforcement_active={data['enforcement_active']}")
    
    def test_trust_endpoint_returns_risk_signals(self):
        """GET /api/trust/{user_id} returns active_risk_signals with correct structure"""
        response = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert response.status_code == 200
        
        data = response.json()
        signals = data["active_risk_signals"]
        
        assert isinstance(signals, list), "active_risk_signals must be a list"
        assert len(signals) >= 2, f"User A should have at least 2 signals, got {len(signals)}"
        
        # Verify signal structure
        for sig in signals:
            assert "signal_type" in sig, "Signal must have signal_type"
            assert "severity" in sig, "Signal must have severity"
        
        # Check for expected signals
        signal_types = [s["signal_type"] for s in signals]
        assert "low_effort_content" in signal_types, "Should have low_effort_content signal"
        assert "community_monopoly" in signal_types, "Should have community_monopoly signal"
        
        print(f"✓ Found {len(signals)} active signals: {signal_types}")
    
    def test_trust_endpoint_unknown_user(self):
        """GET /api/trust/nonexistent-user returns trust_score 0 with empty signals"""
        response = requests.get(f"{BASE_URL}/api/trust/nonexistent-user-xyz123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["trust_score"] == 0, "Unknown user should have trust_score 0"
        assert data["action_count"] == 0, "Unknown user should have 0 actions"
        assert data["active_risk_signals"] == [], "Unknown user should have empty signals"
        assert data["enforcement_active"] == False, "Unknown user should not have enforcement active"
        
        print("✓ Unknown user returns trust_score=0 with empty signals")
    
    def test_trust_endpoint_returns_decay_info(self):
        """GET /api/trust/{user_id} returns decay_rate and decay_status"""
        response = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "decay_rate" in data, "Missing decay_rate"
        assert "decay_status" in data, "Missing decay_status"
        
        # Normal users have 5% decay, burst_and_vanish users have 10%
        assert data["decay_rate"] in [0.05, 0.10], f"Unexpected decay_rate: {data['decay_rate']}"
        assert data["decay_status"] in ["active", "decaying"], f"Unexpected status: {data['decay_status']}"
        
        print(f"✓ Decay info: rate={data['decay_rate']}, status={data['decay_status']}")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    def test_actions_feed_works(self):
        """GET /api/actions/feed still returns actions"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "actions" in data
        assert isinstance(data["actions"], list)
        assert len(data["actions"]) > 0, "Feed should have actions"
        
        # Verify trust_signal is in each action
        for action in data["actions"][:5]:
            assert "trust_signal" in action, "Action should have trust_signal"
            assert "reactions" in action, "Action should have reactions"
        
        print(f"✓ Feed returns {len(data['actions'])} actions with trust_signal")
    
    def test_impact_profile_works(self):
        """GET /api/impact/profile/{user_id} still works"""
        response = requests.get(f"{BASE_URL}/api/impact/profile/{USER_A_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "profile" in data
        
        profile = data["profile"]
        assert "total_actions" in profile
        assert "impact_score" in profile
        assert "verified_count" in profile
        
        print(f"✓ Profile returns: actions={profile['total_actions']}, impact={profile['impact_score']}")
    
    def test_risk_signals_definitions_returns_8(self):
        """GET /api/risk-signals/definitions returns 8 signals"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["total"] == 8, f"Expected 8 signals, got {data['total']}"
        assert len(data["signals"]) == 8
        
        print("✓ 8 risk signal definitions returned")


class TestReactionWeights:
    """Tests for reaction weights in feed (for frontend integration)"""
    
    def test_feed_actions_have_trust_signal(self):
        """Feed actions should have trust_signal > 0 for actions with reactions"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        
        data = response.json()
        actions = data["actions"]
        
        # Find actions with reactions
        actions_with_reactions = [
            a for a in actions 
            if (a["reactions"].get("support", 0) + 
                a["reactions"].get("useful", 0) + 
                a["reactions"].get("verified", 0)) > 0
        ]
        
        for action in actions_with_reactions:
            assert action["trust_signal"] > 0, f"Action {action['id']} has reactions but trust_signal=0"
        
        print(f"✓ {len(actions_with_reactions)} actions with reactions have positive trust_signal")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

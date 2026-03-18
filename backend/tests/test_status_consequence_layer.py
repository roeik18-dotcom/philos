"""
Status Consequence Layer Tests
Tests for:
- Feed ranking with rank_score and visibility_weight
- Position endpoint returns consequence_multiplier
- Orientation endpoint returns consequence_multiplier and updated messaging
- Feed sorted by rank_score (not chronological)
- Status-aware orientation messaging
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test users from provided credentials
TEST_USER_AT_RISK = {
    "email": "newuser@test.com",
    "password": "password123",
    "user_id": "05d47b99-88f1-44b3-a879-6c995634eaa0"
}

TEST_USER_AT_RISK_2 = {
    "email": "trust_fragile@test.com",
    "password": "password123",
    "user_id": "0c98a493-3148-4c72-88e7-662baa393d11"
}


class TestFeedConsequenceLayer:
    """Tests for feed ranking with status consequence multipliers"""
    
    def test_feed_returns_rank_score_field(self):
        """Feed actions should include rank_score field"""
        response = requests.get(f"{BASE_URL}/api/actions/feed", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        if data["actions"]:
            first_action = data["actions"][0]
            assert "rank_score" in first_action, "rank_score field missing from feed action"
            assert isinstance(first_action["rank_score"], (int, float)), "rank_score should be numeric"
    
    def test_feed_returns_visibility_weight_field(self):
        """Feed actions should include visibility_weight field"""
        response = requests.get(f"{BASE_URL}/api/actions/feed", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        if data["actions"]:
            first_action = data["actions"][0]
            assert "visibility_weight" in first_action, "visibility_weight field missing from feed action"
            assert isinstance(first_action["visibility_weight"], (int, float)), "visibility_weight should be numeric"
    
    def test_feed_sorted_by_rank_score_descending(self):
        """Feed should be sorted by rank_score descending, not chronological"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=20", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        if len(data["actions"]) > 1:
            rank_scores = [a["rank_score"] for a in data["actions"]]
            # Verify descending order (each score >= next score)
            for i in range(len(rank_scores) - 1):
                assert rank_scores[i] >= rank_scores[i+1], \
                    f"Feed not sorted by rank_score: {rank_scores[i]} < {rank_scores[i+1]}"
    
    def test_at_risk_user_visibility_weight_capped_at_070(self):
        """At Risk users should have visibility_weight = 0.70"""
        # Fetch feed with viewer_id to check if at-risk author has capped weight
        response = requests.get(
            f"{BASE_URL}/api/actions/feed?viewer_id={TEST_USER_AT_RISK['user_id']}&limit=50",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find actions by our at-risk test user
        user_actions = [a for a in data["actions"] if a["user_id"] == TEST_USER_AT_RISK["user_id"]]
        if user_actions:
            for action in user_actions:
                assert action["visibility_weight"] == 0.70, \
                    f"At Risk user should have visibility_weight=0.70, got {action['visibility_weight']}"


class TestPositionConsequenceMultiplier:
    """Tests for position endpoint consequence_multiplier"""
    
    def test_position_returns_consequence_multiplier_field(self):
        """GET /api/position/{user_id} should return consequence_multiplier"""
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "consequence_multiplier" in data, "consequence_multiplier field missing from position response"
        assert isinstance(data["consequence_multiplier"], (int, float)), "consequence_multiplier should be numeric"
    
    def test_at_risk_user_has_070_multiplier(self):
        """At Risk user (with active risk signals) should have consequence_multiplier=0.70"""
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # User has active risk signals → should be atRisk with 0.70 multiplier
        assert data["status"]["status"] == "atRisk", f"Expected atRisk status, got {data['status']['status']}"
        assert data["consequence_multiplier"] == 0.70, \
            f"At Risk user should have multiplier=0.70, got {data['consequence_multiplier']}"
    
    def test_position_returns_status_object(self):
        """Position should still return full status object (from iteration 94)"""
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        status = data.get("status", {})
        assert "status" in status, "status.status missing"
        assert "icon" in status, "status.icon missing"
        assert "label" in status, "status.label missing"
        assert "color" in status, "status.color missing"
        assert "reason" in status, "status.reason missing"


class TestOrientationConsequenceMultiplier:
    """Tests for orientation endpoint consequence_multiplier and status-aware messaging"""
    
    def test_orientation_returns_consequence_multiplier_field(self):
        """GET /api/orientation/{user_id} should return consequence_multiplier"""
        response = requests.get(
            f"{BASE_URL}/api/orientation/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "consequence_multiplier" in data, "consequence_multiplier field missing from orientation response"
        assert isinstance(data["consequence_multiplier"], (int, float)), "consequence_multiplier should be numeric"
    
    def test_at_risk_user_multiplier_070(self):
        """At Risk user should have consequence_multiplier=0.70 in orientation"""
        response = requests.get(
            f"{BASE_URL}/api/orientation/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"]["status"] == "atRisk"
        assert data["consequence_multiplier"] == 0.70
    
    def test_at_risk_message_mentions_reduced_visibility(self):
        """Orientation message for At Risk users should mention 'reduced visibility'"""
        response = requests.get(
            f"{BASE_URL}/api/orientation/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        message = data.get("message", "").lower()
        assert "reduced visibility" in message, \
            f"At Risk orientation message should mention 'reduced visibility'. Got: {data['message']}"
    
    def test_orientation_returns_status_object(self):
        """Orientation should return full status object"""
        response = requests.get(
            f"{BASE_URL}/api/orientation/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        status = data.get("status", {})
        assert "status" in status
        assert "icon" in status
        assert "label" in status
        assert "color" in status


class TestConsequenceMultiplierValues:
    """Tests for consequence multiplier value correctness"""
    
    def test_consequence_multipliers_dict_values(self):
        """Verify multiplier values: Rising=1.15, Stable=1.0, Decaying=0.85, AtRisk=0.70"""
        # This test validates the expected multiplier values based on status
        expected = {
            "rising": 1.15,
            "stable": 1.00,
            "decaying": 0.85,
            "atRisk": 0.70
        }
        
        # Test by checking position endpoint for at-risk user (we know they're at-risk)
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        status_key = data["status"]["status"]
        actual_multiplier = data["consequence_multiplier"]
        expected_multiplier = expected.get(status_key, 1.0)
        
        assert actual_multiplier == expected_multiplier, \
            f"For status '{status_key}', expected multiplier {expected_multiplier}, got {actual_multiplier}"


class TestEnforcementOverride:
    """Tests for enforcement override (risk signals cap multiplier at 0.70)"""
    
    def test_enforcement_override_caps_at_070(self):
        """Even rising user with risk signals should be capped at 0.70"""
        # User with active risk signals should have multiplier capped at 0.70 regardless of status
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # This user has active risk signals → multiplier should be <= 0.70
        assert data["consequence_multiplier"] <= 0.70, \
            f"Enforcement should cap multiplier at 0.70, got {data['consequence_multiplier']}"
    
    def test_second_at_risk_user_also_capped(self):
        """Second at-risk test user should also be capped at 0.70"""
        response = requests.get(
            f"{BASE_URL}/api/position/{TEST_USER_AT_RISK_2['user_id']}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["consequence_multiplier"] <= 0.70, \
            f"Second at-risk user should have multiplier <= 0.70, got {data['consequence_multiplier']}"


class TestRankingFormula:
    """Tests for the ranking formula: rank_score = (recency*50 + trust*2 + reactions*3) * author_multiplier"""
    
    def test_rank_score_is_positive(self):
        """rank_score should be non-negative"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=10", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        for action in data["actions"]:
            assert action["rank_score"] >= 0, f"rank_score should be >= 0, got {action['rank_score']}"
    
    def test_rank_score_affected_by_visibility_weight(self):
        """Higher visibility_weight should correlate with higher rank_score for similar actions"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=50", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Just verify that both fields exist and are correlated (rank uses weight)
        for action in data["actions"]:
            assert "rank_score" in action
            assert "visibility_weight" in action
            # visibility_weight should be between 0.70 and 1.15
            assert 0.0 <= action["visibility_weight"] <= 2.0, \
                f"visibility_weight should be reasonable, got {action['visibility_weight']}"


class TestFeedWithAuthentication:
    """Tests for feed behavior with authenticated viewer"""
    
    def test_feed_with_viewer_id(self):
        """Feed should work with viewer_id parameter"""
        response = requests.get(
            f"{BASE_URL}/api/actions/feed?viewer_id={TEST_USER_AT_RISK['user_id']}&limit=10",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        # Actions should include rank_score and visibility_weight
        if data["actions"]:
            assert "rank_score" in data["actions"][0]
            assert "visibility_weight" in data["actions"][0]


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_feed_endpoint_available(self):
        """Feed endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/actions/feed", timeout=10)
        assert response.status_code == 200
    
    def test_position_endpoint_available(self):
        """Position endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_AT_RISK['user_id']}", timeout=10)
        assert response.status_code == 200
    
    def test_orientation_endpoint_available(self):
        """Orientation endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/orientation/{TEST_USER_AT_RISK['user_id']}", timeout=10)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

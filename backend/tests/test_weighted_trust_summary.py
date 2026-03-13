"""
Test Suite: Weighted Causality Trust Summary - Iteration 66
Tests the upgraded trust-history API with summary_by_source containing total_value_delta and total_risk_delta
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test users per spec
STABLE_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"  # trust~45, manual value+risk+globe
BUILDING_USER_ID = "2f49d593-1c59-4074-b5b0-edd75d1ccb8c"  # trust~7, daily_action+mission_join
FRAGILE_USER_ID = "0c98a493-3148-4c72-88e7-662baa393d11"  # trust~0.3, only decay
RESTRICTED_USER_ID = "d6a4bffd-e689-4ea8-b8c4-57f630a3a01e"  # trust~-2, high risk


class TestTrustHistoryWeightedSummary:
    """Tests for the upgraded trust-history API with weighted causality summaries"""
    
    def test_stable_user_has_summary_by_source_with_value_delta(self):
        """Stable user (05d47...) should have summary_by_source with total_value_delta"""
        response = requests.get(f"{BASE_URL}/api/user/{STABLE_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "summary_by_source" in data, "Missing summary_by_source field"
        
        summary = data["summary_by_source"]
        assert len(summary) > 0, "summary_by_source is empty"
        
        # Check that each source has total_value_delta and total_risk_delta
        for source, stats in summary.items():
            assert "total_value_delta" in stats, f"Source {source} missing total_value_delta"
            assert "total_risk_delta" in stats, f"Source {source} missing total_risk_delta"
            assert "count" in stats, f"Source {source} missing count"
    
    def test_stable_user_has_manual_and_globe_sources(self):
        """Stable user should have manual and globe_point sources with positive value"""
        response = requests.get(f"{BASE_URL}/api/user/{STABLE_USER_ID}/trust-history?limit=10")
        data = response.json()
        
        summary = data["summary_by_source"]
        
        # Should have manual entries with positive value
        assert "manual" in summary, "Stable user should have manual source"
        assert summary["manual"]["total_value_delta"] > 0, "Manual should have positive value delta"
        
        # Should have globe_point entries
        assert "globe_point" in summary, "Stable user should have globe_point source"
        assert summary["globe_point"]["total_value_delta"] > 0, "Globe_point should have positive value delta"
        
        # Should also have risk from manual (per spec)
        assert summary["manual"]["total_risk_delta"] > 0, "Manual should have positive risk delta"
    
    def test_building_user_has_daily_action_and_mission(self):
        """Building user should have daily_action and mission_join sources"""
        response = requests.get(f"{BASE_URL}/api/user/{BUILDING_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        summary = data["summary_by_source"]
        
        # Should have daily_action
        assert "daily_action" in summary, "Building user should have daily_action source"
        assert summary["daily_action"]["total_value_delta"] > 0, "daily_action should have positive value"
        
        # Should have mission_join  
        assert "mission_join" in summary, "Building user should have mission_join source"
        assert summary["mission_join"]["total_value_delta"] > 0, "mission_join should have positive value"
    
    def test_fragile_user_only_has_decay(self):
        """Fragile user should only have decay entries (no positive sources)"""
        response = requests.get(f"{BASE_URL}/api/user/{FRAGILE_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        summary = data["summary_by_source"]
        
        # Should only have decay
        assert "decay" in summary, "Fragile user should have decay source"
        
        # Should NOT have positive sources
        positive_sources = [k for k in summary.keys() if k != "decay"]
        assert len(positive_sources) == 0, f"Fragile user should only have decay, found: {positive_sources}"
        
        # Verify trust score is fragile (< 5)
        assert data["trust_score"] < 5, f"Fragile user trust should be < 5, got {data['trust_score']}"
    
    def test_restricted_user_has_negative_trust(self):
        """Restricted user should have trust_score <= 0"""
        response = requests.get(f"{BASE_URL}/api/user/{RESTRICTED_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        
        # Trust should be <= 0 for restricted state
        assert data["trust_score"] <= 0, f"Restricted user trust should be <= 0, got {data['trust_score']}"
    
    def test_all_users_have_required_fields(self):
        """All test users should have required fields in trust-history response"""
        user_ids = [STABLE_USER_ID, BUILDING_USER_ID, FRAGILE_USER_ID, RESTRICTED_USER_ID]
        
        for user_id in user_ids:
            response = requests.get(f"{BASE_URL}/api/user/{user_id}/trust-history?limit=10")
            assert response.status_code == 200, f"User {user_id} returned {response.status_code}"
            
            data = response.json()
            
            # Required top-level fields
            assert "user_id" in data
            assert "value_score" in data
            assert "risk_score" in data
            assert "trust_score" in data
            assert "ledger" in data
            assert "summary_by_source" in data
            assert "summary_by_action_type" in data
    
    def test_ledger_entries_have_correct_structure(self):
        """Ledger entries should have source_flow, action_type, computed deltas"""
        response = requests.get(f"{BASE_URL}/api/user/{STABLE_USER_ID}/trust-history?limit=10")
        data = response.json()
        
        ledger = data["ledger"]
        assert len(ledger) > 0, "Ledger should not be empty"
        
        for entry in ledger:
            assert "source_flow" in entry, "Entry missing source_flow"
            assert "action_type" in entry, "Entry missing action_type"
            assert "computed_value_delta" in entry, "Entry missing computed_value_delta"
            assert "computed_risk_delta" in entry, "Entry missing computed_risk_delta"
            assert "timestamp" in entry, "Entry missing timestamp"


class TestRegression:
    """Regression tests for existing endpoints"""
    
    def test_auth_login_endpoint(self):
        """Auth login should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "token" in data or "user" in data
    
    def test_profile_record_endpoint(self):
        """Profile record endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/profile/{STABLE_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "identity" in data
        assert "field_trust" in data
    
    def test_user_trust_history_endpoint(self):
        """User trust-history endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/user/{STABLE_USER_ID}/trust-history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        assert "summary_by_source" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

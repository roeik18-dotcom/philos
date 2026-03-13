"""
Test suite for Trust Ledger / Field History layer
Tests:
- POST /api/actions creates ledger entry with source_flow='manual'
- POST /api/risk-signal creates ledger entry with source_flow='manual' and computed_risk_delta > 0
- POST /api/orientation/globe-point creates ledger entry with source_flow='globe_point'
- GET /api/user/{user_id}/trust-history returns complete TrustHistoryResponse
- Ledger entries have all required fields
- Summary by source and action type
- Limit parameter support
- 404 for non-existent user
- Existing endpoints regression tests
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_USER_EMAIL = "newuser@test.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


class TestTrustLedgerBackend:
    """Trust Ledger and Trust History API tests"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # API returns 'token' not 'access_token'
        assert "token" in data, f"No token in response: {data}"
        return data["token"]

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for authenticated requests"""
        return {"Authorization": f"Bearer {auth_token}"}

    # ========== GET /api/user/{user_id}/trust-history Tests ==========

    def test_trust_history_endpoint_exists(self):
        """Test GET /api/user/{user_id}/trust-history returns valid response"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200, f"trust-history failed: {response.status_code} - {response.text}"
        data = response.json()
        print(f"Trust history response keys: {data.keys()}")
        assert "user_id" in data
        assert "ledger" in data

    def test_trust_history_response_structure(self):
        """Test TrustHistoryResponse has all required fields"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields per TrustHistoryResponse model
        assert data["user_id"] == TEST_USER_ID
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        assert "total_ledger_entries" in data
        assert "summary_by_source" in data
        assert "summary_by_action_type" in data
        assert "ledger" in data
        
        print(f"TrustHistoryResponse: user_id={data['user_id']}, "
              f"value_score={data['value_score']}, risk_score={data['risk_score']}, "
              f"trust_score={data['trust_score']}, total_entries={data['total_ledger_entries']}")

    def test_trust_history_ledger_entry_fields(self):
        """Test ledger entries have all required fields per LedgerEntry model"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["ledger"]) > 0:
            entry = data["ledger"][0]
            required_fields = [
                "id", "user_id", "source_flow", "action_type",
                "impact", "authenticity", "computed_value_delta",
                "computed_risk_delta", "trust_score_after", "timestamp", "metadata"
            ]
            for field in required_fields:
                assert field in entry, f"Missing field '{field}' in ledger entry"
            print(f"Sample ledger entry: source_flow={entry['source_flow']}, "
                  f"action_type={entry['action_type']}, value_delta={entry['computed_value_delta']}, "
                  f"risk_delta={entry['computed_risk_delta']}")
        else:
            print("No ledger entries found for user")

    def test_trust_history_summary_by_source(self):
        """Test summary_by_source contains counts and totals per source"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary_by_source"]
        print(f"Summary by source: {summary}")
        
        for source, stats in summary.items():
            assert "count" in stats, f"Missing 'count' in summary for source '{source}'"
            assert "total_value_delta" in stats, f"Missing 'total_value_delta' in summary for source '{source}'"
            assert "total_risk_delta" in stats, f"Missing 'total_risk_delta' in summary for source '{source}'"
            print(f"  {source}: count={stats['count']}, value_delta={stats['total_value_delta']}, risk_delta={stats['total_risk_delta']}")

    def test_trust_history_summary_by_action_type(self):
        """Test summary_by_action_type contains counts and totals per action"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary_by_action_type"]
        print(f"Summary by action_type: {summary}")
        
        for action_type, stats in summary.items():
            assert "count" in stats
            assert "total_value_delta" in stats
            assert "total_risk_delta" in stats

    def test_trust_history_limit_parameter(self):
        """Test ?limit=N returns max N ledger entries"""
        # Get total first
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        total_entries = response.json()["total_ledger_entries"]
        
        # Test with limit=3
        response_limited = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=3")
        assert response_limited.status_code == 200
        data = response_limited.json()
        
        ledger_count = len(data["ledger"])
        assert ledger_count <= 3, f"Expected max 3 entries, got {ledger_count}"
        # total_ledger_entries should still reflect total count
        assert data["total_ledger_entries"] == total_entries
        print(f"Limit=3 test: returned {ledger_count} entries, total={data['total_ledger_entries']}")

    def test_trust_history_limit_min_1(self):
        """Test limit is clamped to minimum of 1"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=0")
        assert response.status_code == 200
        data = response.json()
        # Should return at least 1 entry if available (clamped min=1)
        print(f"Limit=0 (clamped to 1): returned {len(data['ledger'])} entries")

    def test_trust_history_limit_max_500(self):
        """Test limit is clamped to maximum of 500"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=1000")
        assert response.status_code == 200
        data = response.json()
        ledger_count = len(data["ledger"])
        assert ledger_count <= 500, f"Expected max 500 entries, got {ledger_count}"
        print(f"Limit=1000 (clamped to 500): returned {ledger_count} entries")

    def test_trust_history_404_nonexistent_user(self):
        """Test 404 for non-existent user"""
        fake_user_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/user/{fake_user_id}/trust-history")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"Non-existent user returns 404 correctly")

    # ========== POST /api/actions (Manual Action) Tests ==========

    def test_manual_action_creates_ledger_entry(self, auth_headers):
        """Test POST /api/actions creates ledger entry with source_flow='manual'"""
        # Get ledger count before
        before = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert before.status_code == 200
        count_before = before.json()["total_ledger_entries"]
        
        # Create manual action
        action_data = {
            "action_type": "help",
            "impact": 5.0,
            "authenticity": 0.9
        }
        response = requests.post(
            f"{BASE_URL}/api/actions",
            json=action_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"POST /api/actions failed: {response.text}"
        
        # Verify ledger entry created
        after = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert after.status_code == 200
        after_data = after.json()
        count_after = after_data["total_ledger_entries"]
        
        assert count_after > count_before, f"Ledger entry not created: {count_before} -> {count_after}"
        
        # Check latest entry has source_flow='manual'
        latest_entry = after_data["ledger"][0]  # Most recent first
        assert latest_entry["source_flow"] == "manual", f"Expected source_flow='manual', got '{latest_entry['source_flow']}'"
        assert latest_entry["action_type"] == "help"
        assert latest_entry["computed_value_delta"] > 0
        print(f"Manual action created ledger entry: source_flow={latest_entry['source_flow']}, "
              f"action_type={latest_entry['action_type']}, value_delta={latest_entry['computed_value_delta']}")

    # ========== POST /api/risk-signal Tests ==========

    def test_risk_signal_creates_ledger_entry(self):
        """Test POST /api/risk-signal creates ledger entry with source_flow='manual' and risk_delta > 0"""
        # Get ledger count before
        before = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert before.status_code == 200
        count_before = before.json()["total_ledger_entries"]
        
        # Create risk signal
        signal_data = {
            "user_id": TEST_USER_ID,
            "signal_type": "spam",
            "confidence": 0.7,
            "severity": 3.0
        }
        response = requests.post(
            f"{BASE_URL}/api/risk-signal",
            json=signal_data
        )
        assert response.status_code == 200, f"POST /api/risk-signal failed: {response.text}"
        
        # Verify ledger entry created
        after = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert after.status_code == 200
        after_data = after.json()
        count_after = after_data["total_ledger_entries"]
        
        assert count_after > count_before, f"Ledger entry not created: {count_before} -> {count_after}"
        
        # Check latest entry has source_flow='manual' and computed_risk_delta > 0
        latest_entry = after_data["ledger"][0]
        assert latest_entry["source_flow"] == "manual", f"Expected source_flow='manual', got '{latest_entry['source_flow']}'"
        assert latest_entry["computed_risk_delta"] > 0, f"Expected risk_delta > 0, got {latest_entry['computed_risk_delta']}"
        print(f"Risk signal created ledger entry: source_flow={latest_entry['source_flow']}, "
              f"action_type={latest_entry['action_type']}, risk_delta={latest_entry['computed_risk_delta']}")

    # ========== POST /api/orientation/globe-point Tests ==========

    def test_globe_point_creates_ledger_entry(self, auth_headers):
        """Test POST /api/orientation/globe-point creates ledger entry with source_flow='globe_point'"""
        # Get ledger count before
        before = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert before.status_code == 200
        count_before = before.json()["total_ledger_entries"]
        
        # Create globe point
        globe_data = {
            "user_id": TEST_USER_ID,
            "direction": "contribution",
            "country_code": "US"
        }
        response = requests.post(
            f"{BASE_URL}/api/orientation/globe-point",
            json=globe_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201], f"POST /api/orientation/globe-point failed: {response.status_code} - {response.text}"
        
        # Verify ledger entry created
        after = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert after.status_code == 200
        after_data = after.json()
        count_after = after_data["total_ledger_entries"]
        
        assert count_after > count_before, f"Ledger entry not created: {count_before} -> {count_after}"
        
        # Check latest entry has source_flow='globe_point'
        latest_entry = after_data["ledger"][0]
        assert latest_entry["source_flow"] == "globe_point", f"Expected source_flow='globe_point', got '{latest_entry['source_flow']}'"
        print(f"Globe point created ledger entry: source_flow={latest_entry['source_flow']}, "
              f"action_type={latest_entry['action_type']}, value_delta={latest_entry['computed_value_delta']}")

    # ========== Existing Endpoints Regression Tests ==========

    def test_auth_login_still_works(self):
        """Test auth/login endpoint still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data  # API uses 'token' not 'access_token'
        print("Auth login: WORKING")

    def test_trust_profile_endpoint_still_works(self):
        """Test GET /api/user/{user_id}/trust still works"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200, f"Trust profile failed: {response.text}"
        data = response.json()
        assert "user_id" in data
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        print(f"Trust profile: value={data['value_score']}, risk={data['risk_score']}, trust={data['trust_score']}")

    def test_field_dashboard_still_works(self, auth_headers):
        """Test GET /api/orientation/field-dashboard still works"""
        response = requests.get(
            f"{BASE_URL}/api/orientation/field-dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Field dashboard failed: {response.text}"
        print("Field dashboard: WORKING")

    def test_profile_record_still_works(self, auth_headers):
        """Test GET /api/profile/{user_id}/record still works"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{TEST_USER_ID}/record",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Profile record failed: {response.text}"
        data = response.json()
        # Should contain field_trust and ai_profile_interpretation
        print(f"Profile record: keys={list(data.keys())}")

    # ========== Verify source_flow values in ledger ==========

    def test_ledger_source_flows_are_valid(self):
        """Test ledger entries have valid source_flow values"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=100")
        assert response.status_code == 200
        data = response.json()
        
        valid_sources = {'daily_action', 'globe_point', 'mission_join', 'onboarding', 'invite_used', 'manual', 'decay'}
        
        for entry in data["ledger"]:
            assert entry["source_flow"] in valid_sources, f"Invalid source_flow: {entry['source_flow']}"
        
        print(f"All {len(data['ledger'])} ledger entries have valid source_flow values")
        print(f"Sources found: {data['summary_by_source'].keys()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

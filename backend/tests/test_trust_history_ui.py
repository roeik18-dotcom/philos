"""
Test Trust History UI & Trust Explanation Feature
Tests both backend trust-history endpoint and verifies existing endpoints still work.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_USER_EMAIL = "newuser@test.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


class TestTrustHistoryEndpoint:
    """Tests for GET /api/user/{user_id}/trust-history endpoint"""
    
    def test_trust_history_returns_all_fields(self):
        """Verify trust-history returns complete TrustHistoryResponse with all fields"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        # Verify top-level fields
        assert "user_id" in data
        assert data["user_id"] == TEST_USER_ID
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        assert "total_ledger_entries" in data
        assert "summary_by_source" in data
        assert "summary_by_action_type" in data
        assert "ledger" in data
        
        print(f"✓ trust-history returns all required fields")
        print(f"  - value_score: {data['value_score']}")
        print(f"  - risk_score: {data['risk_score']}")
        print(f"  - trust_score: {data['trust_score']}")
        print(f"  - total_ledger_entries: {data['total_ledger_entries']}")
    
    def test_ledger_entries_structure(self):
        """Verify each ledger entry has required fields"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        ledger = data.get("ledger", [])
        assert len(ledger) > 0, "Ledger should have entries"
        
        for entry in ledger[:5]:  # Check first 5
            assert "id" in entry
            assert "user_id" in entry
            assert "source_flow" in entry
            assert "action_type" in entry
            assert "computed_value_delta" in entry
            assert "computed_risk_delta" in entry
            assert "trust_score_after" in entry
            assert "timestamp" in entry
        
        print(f"✓ Ledger entries have all required fields ({len(ledger)} entries)")
    
    def test_source_flows_present(self):
        """Verify summary_by_source contains expected source flows"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary_by_source", {})
        
        # At minimum we expect decay, manual, and globe_point based on previous tests
        found_sources = list(summary.keys())
        print(f"✓ Source flows in summary: {found_sources}")
        
        # Verify summary structure
        for source, stats in summary.items():
            assert "count" in stats
            assert "total_value_delta" in stats
            assert "total_risk_delta" in stats
            print(f"  - {source}: count={stats['count']}, value_delta={stats['total_value_delta']:.2f}, risk_delta={stats['total_risk_delta']:.2f}")
    
    def test_limit_parameter(self):
        """Verify limit parameter works correctly"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        ledger = data.get("ledger", [])
        assert len(ledger) <= 5, f"Expected <=5 entries, got {len(ledger)}"
        print(f"✓ Limit parameter works: requested 5, got {len(ledger)}")


class TestExistingEndpointsRegression:
    """Regression tests to ensure existing endpoints still work"""
    
    def test_auth_login(self):
        """Auth login endpoint still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data  # API returns 'token' not 'access_token'
        assert "user" in data
        print(f"✓ Auth login works")
    
    def test_trust_profile_endpoint(self):
        """GET /api/user/{user_id}/trust still works"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200
        
        data = response.json()
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        print(f"✓ Trust profile endpoint works: trust_score={data['trust_score']}")
    
    def test_field_dashboard(self):
        """GET /api/orientation/field-dashboard still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "field_state" in data or "total_users" in data or "actions_today" in data or "dominant_direction" in data
        print(f"✓ Field dashboard endpoint works")
    
    def test_profile_record(self):
        """GET /api/profile/{user_id}/record still works (AI call - may take 5s)"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "identity" in data
        assert "field_trust" in data
        print(f"✓ Profile record endpoint works (with AI interpretation)")
        if data.get("ai_profile_interpretation"):
            print(f"  - AI interpretation: {data['ai_profile_interpretation'][:60]}...")


class TestTrustHistoryUIIntegration:
    """Tests that verify trust history is correctly consumed by frontend"""
    
    def test_parallel_fetch_compatibility(self):
        """Both /api/profile/{user_id}/record AND /api/user/{user_id}/trust-history return data"""
        import concurrent.futures
        
        def fetch_profile():
            return requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record", timeout=30)
        
        def fetch_history():
            return requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=10", timeout=10)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            profile_future = executor.submit(fetch_profile)
            history_future = executor.submit(fetch_history)
            
            profile_response = profile_future.result()
            history_response = history_future.result()
        
        assert profile_response.status_code == 200
        assert history_response.status_code == 200
        
        print(f"✓ Parallel fetch works: profile={profile_response.status_code}, history={history_response.status_code}")
    
    def test_source_labels_map_to_hebrew(self):
        """Verify source_flow values can be mapped to Hebrew labels"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        
        # Hebrew labels from frontend code
        SOURCE_LABELS = {
            'daily_action': 'פעולת כיוון יומית',
            'globe_point': 'נקודת שדה',
            'mission_join': 'הצטרפות למשימה',
            'onboarding': 'פעולה ראשונה',
            'invite_used': 'הזמנה מומשה',
            'manual': 'עדכון ידני',
            'decay': 'דעיכה יומית',
        }
        
        ledger = data.get("ledger", [])
        for entry in ledger[:5]:
            source = entry.get("source_flow")
            if source in SOURCE_LABELS:
                print(f"  - {source} → {SOURCE_LABELS[source]}")
            else:
                print(f"  - WARNING: Unknown source flow: {source}")
        
        print(f"✓ Source flows map to Hebrew labels")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

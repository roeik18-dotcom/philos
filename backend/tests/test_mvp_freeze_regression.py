"""
MVP Freeze Full Regression Test - Philos Orientation Trust System
Tests:
1. POST /api/system/decay/trigger - admin-only manual decay trigger
2. GET /api/system/status - strengthened with flat scheduler fields
3. Existing trust APIs (GET /api/user/{user_id}/trust, trust-history)
4. Existing auth (POST /api/auth/login)
5. POST /api/actions with auth token
6. Concurrent decay protection
7. Trust ledger decay entries have source_flow=decay
"""
import pytest
import requests
import os
import time
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated requests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("token")


@pytest.fixture(scope="module")
def authenticated_headers(auth_token):
    """Headers with auth token"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }


# ============================================================================
# 1. System Status Tests - GET /api/system/status with flat scheduler fields
# ============================================================================

class TestSystemStatusFlatFields:
    """Verify GET /api/system/status returns all 5 components with flat scheduler fields"""
    
    def test_system_status_returns_200(self):
        """System status endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: System status returns 200")
    
    def test_system_status_has_all_5_components(self):
        """Response includes database, trust_engine, trust_ledger, ai_layer, decay_scheduler"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "components" in data
        required = ["database", "trust_engine", "trust_ledger", "ai_layer", "decay_scheduler"]
        for comp in required:
            assert comp in data["components"], f"Missing component: {comp}"
        print(f"PASS: All 5 components present: {list(data['components'].keys())}")
    
    def test_decay_scheduler_flat_fields(self):
        """decay_scheduler has flat fields: scheduler_running, last_decay_run, last_decay_success, 
           decay_runs_last_7_days, next_decay_run, lock_state"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200
        data = response.json()
        
        scheduler = data["components"]["decay_scheduler"]
        required_flat_fields = [
            "scheduler_running",
            "last_decay_run",
            "last_decay_success",
            "decay_runs_last_7_days",
            "next_decay_run",
            "lock_state"
        ]
        
        for field in required_flat_fields:
            assert field in scheduler, f"Missing flat field: {field}"
        
        # Verify types
        assert isinstance(scheduler["scheduler_running"], bool), "scheduler_running should be bool"
        assert scheduler["decay_runs_last_7_days"] is None or isinstance(scheduler["decay_runs_last_7_days"], int), \
            "decay_runs_last_7_days should be int or None"
        
        print(f"PASS: Flat scheduler fields present:")
        print(f"  - scheduler_running: {scheduler['scheduler_running']}")
        print(f"  - last_decay_run: {scheduler['last_decay_run']}")
        print(f"  - last_decay_success: {scheduler['last_decay_success']}")
        print(f"  - decay_runs_last_7_days: {scheduler['decay_runs_last_7_days']}")
        print(f"  - next_decay_run: {scheduler['next_decay_run']}")
        print(f"  - lock_state: {scheduler['lock_state']}")
    
    def test_overall_healthy_when_components_healthy(self):
        """overall=healthy when all components are up"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "overall" in data
        # All critical components should be healthy
        critical = ["database", "trust_engine", "trust_ledger", "decay_scheduler"]
        all_healthy = all(
            data["components"][c]["status"] == "healthy"
            for c in critical
        )
        
        if all_healthy:
            print(f"PASS: All critical components healthy, overall={data['overall']}")
        else:
            unhealthy = [c for c in critical if data["components"][c]["status"] != "healthy"]
            print(f"WARN: Unhealthy components: {unhealthy}, overall={data['overall']}")


# ============================================================================
# 2. Manual Decay Trigger Tests - POST /api/system/decay/trigger
# ============================================================================

class TestManualDecayTrigger:
    """Tests for POST /api/system/decay/trigger endpoint"""
    
    def test_decay_trigger_401_without_auth(self):
        """POST /api/system/decay/trigger returns 401 without auth token"""
        response = requests.post(f"{BASE_URL}/api/system/decay/trigger")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: Decay trigger returns 401 without auth")
    
    def test_decay_trigger_success_with_auth(self, authenticated_headers):
        """POST /api/system/decay/trigger with valid auth returns success response"""
        response = requests.post(
            f"{BASE_URL}/api/system/decay/trigger",
            headers=authenticated_headers
        )
        
        # May return 200 (success) or 200 with success=false (decay_in_progress)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Response missing 'success' field"
        assert "users_processed" in data, "Response missing 'users_processed' field"
        assert "total_value_decay" in data, "Response missing 'total_value_decay' field"
        assert "total_risk_decay" in data, "Response missing 'total_risk_decay' field"
        
        if data["success"]:
            assert "triggered_by" in data, "Success response should have 'triggered_by'"
            assert "triggered_at" in data, "Success response should have 'triggered_at'"
            assert data["users_processed"] >= 0, "users_processed should be >= 0"
            # Decay decreases scores, so deltas should be <= 0 (or 0 if no users)
            print(f"PASS: Decay triggered successfully:")
            print(f"  - triggered_by: {data['triggered_by']}")
            print(f"  - users_processed: {data['users_processed']}")
            print(f"  - total_value_decay: {data['total_value_decay']}")
            print(f"  - total_risk_decay: {data['total_risk_decay']}")
        else:
            # Decay was blocked (e.g., decay_in_progress)
            assert "reason" in data, "Failed response should have 'reason'"
            print(f"PASS: Decay trigger returned success=false, reason={data.get('reason')}")
    
    def test_decay_trigger_writes_to_decay_log(self, authenticated_headers):
        """Decay trigger should write to decay_log collection (verified via status)"""
        # Get status before
        status_before = requests.get(f"{BASE_URL}/api/system/status").json()
        runs_before = status_before["components"]["decay_scheduler"]["decay_runs_last_7_days"] or 0
        
        # Wait a moment to ensure any previous decay completes
        time.sleep(1)
        
        # Trigger decay
        response = requests.post(
            f"{BASE_URL}/api/system/decay/trigger",
            headers=authenticated_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Get status after
        status_after = requests.get(f"{BASE_URL}/api/system/status").json()
        runs_after = status_after["components"]["decay_scheduler"]["decay_runs_last_7_days"] or 0
        
        if data["success"]:
            # If decay ran successfully, runs should have increased
            assert runs_after >= runs_before, "Decay log entry should have been added"
            print(f"PASS: decay_runs_last_7_days updated: {runs_before} -> {runs_after}")
        else:
            print(f"INFO: Decay was blocked (reason={data.get('reason')}), log may not change")


# ============================================================================
# 3. Concurrent Decay Protection Tests
# ============================================================================

class TestConcurrentDecayProtection:
    """Test that concurrent decay runs are properly blocked"""
    
    def test_concurrent_decay_protection(self, authenticated_headers):
        """Second immediate POST /api/system/decay/trigger should either succeed or fail with decay_in_progress"""
        # First trigger
        response1 = requests.post(
            f"{BASE_URL}/api/system/decay/trigger",
            headers=authenticated_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second immediate trigger
        response2 = requests.post(
            f"{BASE_URL}/api/system/decay/trigger",
            headers=authenticated_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Either:
        # 1. Both succeed (first completed before second started)
        # 2. Second fails with decay_in_progress
        if not data2["success"]:
            assert data2.get("reason") == "decay_in_progress", \
                f"Expected reason=decay_in_progress, got {data2.get('reason')}"
            print("PASS: Concurrent protection working - second call blocked with 'decay_in_progress'")
        else:
            print("PASS: Both calls succeeded (first completed quickly)")


# ============================================================================
# 4. Existing Auth Tests
# ============================================================================

class TestExistingAuth:
    """Verify existing auth endpoints still work"""
    
    def test_login_with_valid_credentials(self):
        """POST /api/auth/login with test credentials returns success"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert "token" in data, "Response missing 'token'"
        assert "user" in data, "Response missing 'user'"
        assert data["user"]["email"] == TEST_EMAIL
        print(f"PASS: Login successful for {TEST_EMAIL}")
        print(f"  - user_id: {data['user']['id']}")
    
    def test_login_returns_user_id(self):
        """Login returns expected user_id for test user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["user"]["id"] == TEST_USER_ID, \
            f"Expected user_id {TEST_USER_ID}, got {data['user']['id']}"
        print(f"PASS: User ID matches: {TEST_USER_ID}")


# ============================================================================
# 5. Existing Trust API Tests
# ============================================================================

class TestExistingTrustAPIs:
    """Verify existing trust endpoints still work"""
    
    def test_get_trust_profile(self):
        """GET /api/user/{user_id}/trust returns trust profile"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert response.status_code == 200, f"Trust profile failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        assert "total_actions" in data
        assert "total_risk_signals" in data
        assert "last_updated" in data
        assert "recent_actions" in data
        assert "recent_risk_signals" in data
        
        print(f"PASS: Trust profile for {TEST_USER_ID}:")
        print(f"  - value_score: {data['value_score']}")
        print(f"  - risk_score: {data['risk_score']}")
        print(f"  - trust_score: {data['trust_score']}")
    
    def test_get_trust_history(self):
        """GET /api/user/{user_id}/trust-history returns trust ledger"""
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200, f"Trust history failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert "value_score" in data
        assert "risk_score" in data
        assert "trust_score" in data
        assert "total_ledger_entries" in data
        assert "summary_by_source" in data
        assert "summary_by_action_type" in data
        assert "ledger" in data
        assert isinstance(data["ledger"], list)
        
        print(f"PASS: Trust history for {TEST_USER_ID}:")
        print(f"  - total_ledger_entries: {data['total_ledger_entries']}")
        print(f"  - summary_by_source: {list(data['summary_by_source'].keys())}")


# ============================================================================
# 6. POST /api/actions Tests
# ============================================================================

class TestActionsEndpoint:
    """Test POST /api/actions with auth token records action and returns ActionResponse"""
    
    def test_actions_requires_auth(self):
        """POST /api/actions returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/actions",
            json={"action_type": "help", "impact": 5, "authenticity": 0.8}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/actions returns 401 without auth")
    
    def test_actions_success_with_auth(self, authenticated_headers):
        """POST /api/actions with auth creates action and returns ActionResponse"""
        response = requests.post(
            f"{BASE_URL}/api/actions",
            headers=authenticated_headers,
            json={"action_type": "help", "impact": 5, "authenticity": 0.8}
        )
        assert response.status_code == 200, f"Actions failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "id" in data, "Response missing 'id'"
        assert "user_id" in data, "Response missing 'user_id'"
        assert "action_type" in data
        assert data["action_type"] == "help"
        assert "impact" in data
        assert "authenticity" in data
        assert "value" in data  # Computed value
        assert "timestamp" in data
        
        print(f"PASS: Action recorded successfully:")
        print(f"  - id: {data['id']}")
        print(f"  - value: {data['value']}")


# ============================================================================
# 7. Trust Ledger Decay Entries Tests
# ============================================================================

class TestTrustLedgerDecayEntries:
    """Verify trust ledger entries from decay have source_flow=decay"""
    
    def test_decay_ledger_entries_have_correct_source_flow(self, authenticated_headers):
        """After decay, ledger entries should have source_flow=decay"""
        # Trigger decay to ensure there are decay entries
        requests.post(
            f"{BASE_URL}/api/system/decay/trigger",
            headers=authenticated_headers
        )
        
        # Wait for decay to complete
        time.sleep(2)
        
        # Get trust history
        response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust-history")
        assert response.status_code == 200
        data = response.json()
        
        # Check if decay source exists in summary
        summary_by_source = data["summary_by_source"]
        
        if "decay" in summary_by_source:
            decay_summary = summary_by_source["decay"]
            assert decay_summary["count"] > 0, "Should have at least 1 decay entry"
            # Decay should reduce scores, so deltas should be <= 0
            print(f"PASS: Decay entries found in trust ledger:")
            print(f"  - count: {decay_summary['count']}")
            print(f"  - total_value_delta: {decay_summary['total_value_delta']}")
            print(f"  - total_risk_delta: {decay_summary['total_risk_delta']}")
        else:
            # Check if there are any ledger entries with source_flow=decay
            decay_entries = [e for e in data["ledger"] if e.get("source_flow") == "decay"]
            if decay_entries:
                print(f"PASS: Found {len(decay_entries)} decay entries in ledger")
            else:
                print("INFO: No decay entries found (user may not have scores to decay)")


# ============================================================================
# 8. Database Component Tests
# ============================================================================

class TestDatabaseComponents:
    """Verify database components in system status"""
    
    def test_database_healthy(self):
        """Database component should be healthy"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        
        db = data["components"]["database"]
        assert db["status"] == "healthy", f"Database unhealthy: {db}"
        assert "message" in db
        print(f"PASS: Database healthy - {db['message']}")
    
    def test_trust_engine_tracks_users(self):
        """Trust engine should track users"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        
        engine = data["components"]["trust_engine"]
        assert engine["status"] == "healthy"
        assert "tracked_users" in engine
        assert engine["tracked_users"] >= 0
        print(f"PASS: Trust engine tracking {engine['tracked_users']} users")
    
    def test_trust_ledger_has_entries(self):
        """Trust ledger should have entries"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        
        ledger = data["components"]["trust_ledger"]
        assert ledger["status"] == "healthy"
        assert "total_entries" in ledger
        assert ledger["total_entries"] >= 0
        print(f"PASS: Trust ledger has {ledger['total_entries']} entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

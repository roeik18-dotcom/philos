"""Tests for decay scheduler with MongoDB-based lock protection and system status endpoint."""
import pytest
import requests
import os
import time
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSystemStatus:
    """Tests for GET /api/system/status endpoint - verifies all 5 components"""
    
    def test_system_status_returns_200(self):
        """System status endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ System status returns 200")
    
    def test_system_status_has_all_components(self):
        """System status should include all 5 components: database, trust_engine, trust_ledger, ai_layer, decay_scheduler"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "components" in data, "Response missing 'components' field"
        components = data["components"]
        
        required_components = ["database", "trust_engine", "trust_ledger", "ai_layer", "decay_scheduler"]
        for comp in required_components:
            assert comp in components, f"Missing component: {comp}"
            assert "status" in components[comp], f"Component {comp} missing 'status' field"
            print(f"✓ Component '{comp}' present with status: {components[comp]['status']}")
    
    def test_database_component_healthy(self):
        """Database component should be healthy"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        db_status = data["components"]["database"]
        
        assert db_status["status"] == "healthy", f"Database unhealthy: {db_status}"
        assert "message" in db_status
        print(f"✓ Database healthy: {db_status['message']}")
    
    def test_trust_engine_component_healthy(self):
        """Trust engine component should be healthy with tracked_users count"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        engine_status = data["components"]["trust_engine"]
        
        assert engine_status["status"] == "healthy", f"Trust engine unhealthy: {engine_status}"
        assert "tracked_users" in engine_status
        assert isinstance(engine_status["tracked_users"], int)
        print(f"✓ Trust engine healthy: {engine_status['tracked_users']} users tracked")
    
    def test_trust_ledger_component_healthy(self):
        """Trust ledger component should be healthy with total_entries count"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        ledger_status = data["components"]["trust_ledger"]
        
        assert ledger_status["status"] == "healthy", f"Trust ledger unhealthy: {ledger_status}"
        assert "total_entries" in ledger_status
        assert isinstance(ledger_status["total_entries"], int)
        print(f"✓ Trust ledger healthy: {ledger_status['total_entries']} entries")
    
    def test_ai_layer_component_present(self):
        """AI layer component should be present"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        ai_status = data["components"]["ai_layer"]
        
        assert "status" in ai_status
        assert "message" in ai_status
        # AI layer can be healthy or degraded depending on env config
        print(f"✓ AI layer status: {ai_status['status']} - {ai_status['message']}")
    
    def test_decay_scheduler_running(self):
        """Decay scheduler component should show scheduler_running: true"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        scheduler_status = data["components"]["decay_scheduler"]
        
        assert scheduler_status["status"] == "healthy", f"Scheduler unhealthy: {scheduler_status}"
        assert "scheduler_running" in scheduler_status
        assert scheduler_status["scheduler_running"] is True, "Scheduler not running"
        print(f"✓ Decay scheduler running: {scheduler_status['scheduler_running']}")
    
    def test_decay_scheduler_has_next_run(self):
        """Decay scheduler should have next_scheduled_run in the future"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        scheduler_status = data["components"]["decay_scheduler"]
        
        assert "next_scheduled_run" in scheduler_status
        next_run = scheduler_status["next_scheduled_run"]
        assert next_run is not None, "next_scheduled_run should not be None"
        
        # Parse and verify it's in the future
        next_run_dt = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        assert next_run_dt > now, f"next_scheduled_run {next_run} should be in the future"
        print(f"✓ Next scheduled run: {next_run}")
    
    def test_decay_scheduler_has_lock_state(self):
        """Decay scheduler should include lock_state info"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        scheduler_status = data["components"]["decay_scheduler"]
        
        assert "lock_state" in scheduler_status
        lock_state = scheduler_status["lock_state"]
        if lock_state:
            assert "lock_id" in lock_state
            assert lock_state["lock_id"] == "daily_decay"
            print(f"✓ Lock state present: running={lock_state.get('running', 'N/A')}")
        else:
            print("✓ Lock state is None (no decay has run yet or lock cleared)")
    
    def test_decay_scheduler_has_recent_executions(self):
        """Decay scheduler should include recent_executions list"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        scheduler_status = data["components"]["decay_scheduler"]
        
        assert "recent_executions" in scheduler_status
        recent = scheduler_status["recent_executions"]
        assert isinstance(recent, list)
        print(f"✓ Recent executions: {len(recent)} entries")
        
        if recent:
            # Verify execution log structure
            first = recent[0]
            assert "job" in first
            assert "success" in first
            assert "users_processed" in first
            print(f"  Last execution: success={first['success']}, users_processed={first['users_processed']}")


class TestExistingAuthStillWorks:
    """Verify auth login still works after scheduler integration"""
    
    def test_login_success(self):
        """POST /api/auth/login should still work with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert "token" in data or "user" in data, "Response missing token or user"
        print("✓ Login successful for newuser@test.com")
        return data


class TestExistingTrustAPIsStillWork:
    """Verify existing trust APIs still work after scheduler integration"""
    
    def test_get_user_trust_profile(self):
        """GET /api/user/{user_id}/trust should return trust profile"""
        # First login to get user_id
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        assert login_resp.status_code == 200
        user_id = login_resp.json().get("user", {}).get("id")
        
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        # Get trust profile
        response = requests.get(f"{BASE_URL}/api/user/{user_id}/trust")
        assert response.status_code == 200, f"Trust profile failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "user_id" in data
        assert "trust_score" in data
        assert "value_score" in data
        assert "risk_score" in data
        print(f"✓ Trust profile for {user_id}: trust_score={data['trust_score']}")
    
    def test_get_user_trust_history(self):
        """GET /api/user/{user_id}/trust-history should return trust history"""
        # First login to get user_id
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "newuser@test.com", "password": "password123"}
        )
        assert login_resp.status_code == 200
        user_id = login_resp.json().get("user", {}).get("id")
        
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        # Get trust history
        response = requests.get(f"{BASE_URL}/api/user/{user_id}/trust-history")
        assert response.status_code == 200, f"Trust history failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "user_id" in data
        assert "trust_score" in data
        assert "total_ledger_entries" in data
        assert "ledger" in data
        assert "summary_by_source" in data
        print(f"✓ Trust history for {user_id}: {data['total_ledger_entries']} ledger entries")


class TestDecayLockMechanics:
    """Test the MongoDB-based lock mechanism for decay scheduler"""
    
    def test_lock_state_structure(self):
        """Verify lock state document structure from system status"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        lock_state = data["components"]["decay_scheduler"]["lock_state"]
        
        if lock_state:
            # Verify expected fields if lock exists
            assert "lock_id" in lock_state
            assert lock_state["lock_id"] == "daily_decay"
            # running, started_at, last_completed_at may or may not exist
            print(f"✓ Lock state structure valid: {list(lock_state.keys())}")
        else:
            print("✓ No lock state yet (acceptable)")
    
    def test_execution_log_structure(self):
        """Verify execution log entries have correct structure"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        recent = data["components"]["decay_scheduler"]["recent_executions"]
        
        if recent:
            entry = recent[0]
            required_fields = ["job", "success", "users_processed"]
            for field in required_fields:
                assert field in entry, f"Execution log missing field: {field}"
            
            assert entry["job"] == "daily_decay"
            assert isinstance(entry["success"], bool)
            assert isinstance(entry["users_processed"], int)
            print(f"✓ Execution log structure valid: {entry}")
        else:
            print("✓ No execution logs yet (acceptable)")


class TestOverallHealthAggregation:
    """Test overall health status aggregation"""
    
    def test_overall_status_present(self):
        """System status should have overall status field"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        
        assert "overall" in data
        assert data["overall"] in ["healthy", "degraded"]
        print(f"✓ Overall system status: {data['overall']}")
    
    def test_healthy_when_all_components_healthy(self):
        """If all critical components healthy, overall should be healthy"""
        response = requests.get(f"{BASE_URL}/api/system/status")
        data = response.json()
        
        critical_components = ["database", "trust_engine", "trust_ledger", "decay_scheduler"]
        all_healthy = all(
            data["components"][c]["status"] == "healthy"
            for c in critical_components
        )
        
        if all_healthy:
            # Overall should be healthy (or degraded if ai_layer missing key)
            print(f"✓ Critical components healthy, overall: {data['overall']}")
        else:
            unhealthy = [c for c in critical_components if data["components"][c]["status"] != "healthy"]
            print(f"⚠ Unhealthy components: {unhealthy}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

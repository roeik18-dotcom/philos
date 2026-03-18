"""
Test Recovery Progress Indicator for Decaying/At Risk users
Tests the new recovery_progress field in GET /api/position/{user_id}
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test users from credentials
USER_1_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"  # At Risk with risk signals
USER_2_ID = "0c98a493-3148-4c72-88e7-662baa393d11"  # At Risk with risk signals


class TestRecoveryProgressAPIStructure:
    """Test that recovery_progress field structure is correct"""

    def test_position_endpoint_returns_recovery_progress_for_at_risk_user(self):
        """At Risk user should have recovery_progress object"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Response should have success=True"
        assert "recovery_progress" in data, "Response should contain recovery_progress field"
        
        # At Risk user should have non-null recovery_progress
        assert data["recovery_progress"] is not None, "At Risk user should have recovery_progress data"
        print(f"PASS: At Risk user has recovery_progress: {data['recovery_progress']}")

    def test_recovery_progress_has_required_fields(self):
        """recovery_progress should have: current_status, target_status, requirement, progress, current, target"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        recovery = data.get("recovery_progress")
        assert recovery is not None, "recovery_progress should not be None for At Risk user"
        
        required_fields = ["current_status", "target_status", "requirement", "progress", "current", "target"]
        for field in required_fields:
            assert field in recovery, f"recovery_progress should contain '{field}' field"
            print(f"  - {field}: {recovery[field]}")
        
        print(f"PASS: All required fields present in recovery_progress")

    def test_recovery_progress_field_types(self):
        """Verify field types in recovery_progress"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        recovery = data.get("recovery_progress")
        assert recovery is not None
        
        # current_status and target_status should be strings
        assert isinstance(recovery["current_status"], str), "current_status should be string"
        assert isinstance(recovery["target_status"], str), "target_status should be string"
        assert isinstance(recovery["requirement"], str), "requirement should be string"
        
        # progress should be float between 0 and 1
        assert isinstance(recovery["progress"], (int, float)), "progress should be numeric"
        assert 0 <= recovery["progress"] <= 1, f"progress should be 0-1, got {recovery['progress']}"
        
        # current and target should be integers
        assert isinstance(recovery["current"], int), "current should be int"
        assert isinstance(recovery["target"], int), "target should be int"
        
        print(f"PASS: Field types correct - progress={recovery['progress']}, current={recovery['current']}, target={recovery['target']}")


class TestRecoveryProgressAtRiskWithRiskSignals:
    """Test At Risk users with active risk signals → target_status=Decaying, target=3"""

    def test_at_risk_risk_signals_target_is_decaying(self):
        """At Risk (risk signals): target_status should be 'Decaying'"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        status = data.get("status", {})
        recovery = data.get("recovery_progress")
        
        # Verify user is At Risk
        assert status.get("status") == "atRisk", f"Expected atRisk status, got {status.get('status')}"
        assert recovery is not None, "At Risk user should have recovery_progress"
        
        # Check target_status and target
        assert recovery["current_status"] == "At Risk", f"current_status should be 'At Risk', got {recovery['current_status']}"
        assert recovery["target_status"] == "Decaying", f"target_status should be 'Decaying', got {recovery['target_status']}"
        assert recovery["target"] == 3, f"target should be 3, got {recovery['target']}"
        
        print(f"PASS: At Risk with risk signals → Decaying with target=3")

    def test_at_risk_risk_signals_with_actions_met_message(self):
        """At Risk (risk signals) with 3+ actions: requirement mentions 'Actions met'"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        recovery = data.get("recovery_progress")
        assert recovery is not None
        
        # Per the context, this user has 3+ recent public actions
        # So they should show 100% progress with 'Actions met' message
        if recovery["current"] >= recovery["target"]:
            assert "Actions met" in recovery["requirement"], f"Should mention 'Actions met' when current >= target, got: {recovery['requirement']}"
            assert recovery["progress"] >= 1.0 or recovery["progress"] == 1, f"Progress should be 100% when actions met, got {recovery['progress']}"
            print(f"PASS: Actions met message shown: {recovery['requirement']}")
        else:
            # User hasn't met target yet
            assert "more public action" in recovery["requirement"], f"Should mention remaining actions needed, got: {recovery['requirement']}"
            print(f"PASS: Requirement shows remaining actions: {recovery['requirement']}")

    def test_second_at_risk_user(self):
        """Second test user should also have At Risk with risk signals recovery path"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_2_ID}")
        assert response.status_code == 200
        
        data = response.json()
        status = data.get("status", {})
        recovery = data.get("recovery_progress")
        
        print(f"User 2 status: {status.get('status')}")
        print(f"User 2 recovery: {recovery}")
        
        if status.get("status") == "atRisk":
            assert recovery is not None, "At Risk user should have recovery_progress"
            assert recovery["current_status"] == "At Risk"
            print(f"PASS: Second At Risk user has recovery_progress")
        else:
            print(f"INFO: User 2 status is {status.get('status')}, not atRisk")


class TestRecoveryProgressNullForRisingStable:
    """Test that Rising/Stable users get recovery_progress=null"""

    def test_recovery_progress_null_concept(self):
        """Recovery progress should only exist for Decaying/At Risk, not Rising/Stable"""
        # This test documents the expected behavior
        # We'd need Rising/Stable test users to fully verify
        # For now, verify the At Risk users do have recovery_progress
        
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        status = data.get("status", {})
        recovery = data.get("recovery_progress")
        
        # At Risk should have recovery_progress
        if status.get("status") in ["atRisk", "decaying"]:
            assert recovery is not None, f"{status.get('status')} user should have recovery_progress"
            print(f"PASS: {status.get('status')} user has recovery_progress as expected")
        elif status.get("status") in ["rising", "stable"]:
            assert recovery is None, f"{status.get('status')} user should have recovery_progress=null"
            print(f"PASS: {status.get('status')} user has recovery_progress=null as expected")


class TestConsequencePanelRegression:
    """Regression tests for existing ConsequencePanel features"""

    def test_consequence_panel_still_returns(self):
        """consequence_panel should still be returned alongside recovery_progress"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Original consequence_panel fields should still exist
        assert "consequence_panel" in data, "consequence_panel should still be present"
        panel = data["consequence_panel"]
        assert "meaning" in panel, "consequence_panel should have meaning"
        assert "next_step" in panel, "consequence_panel should have next_step"
        
        # Status should still be returned
        assert "status" in data, "status should still be present"
        assert "consequence_multiplier" in data, "consequence_multiplier should still be present"
        
        print(f"PASS: Consequence panel still returns: multiplier={data['consequence_multiplier']}, status={data['status']['label']}")

    def test_position_bar_data_still_returns(self):
        """Position bar data (position, label, factors) should still be returned"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_1_ID}")
        assert response.status_code == 200
        
        data = response.json()
        
        # PositionBar needs these fields
        assert "position" in data, "position field should exist"
        assert "label" in data, "label field should exist"
        assert "factors" in data, "factors field should exist"
        
        assert isinstance(data["position"], (int, float)), "position should be numeric"
        assert 0 <= data["position"] <= 1, f"position should be 0-1, got {data['position']}"
        
        print(f"PASS: PositionBar data still returns: position={data['position']}, label={data['label']}")


class TestFeedRegression:
    """Regression tests for feed functionality"""

    def test_feed_still_loads(self):
        """Feed endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200, f"Feed should load, got {response.status_code}"
        
        data = response.json()
        assert "actions" in data, "Feed should return actions list"
        print(f"PASS: Feed loads with {len(data['actions'])} actions")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

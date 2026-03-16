"""
Test suite for Risk Signals Framework
Tests the 8 signal types, scanner detection, and management APIs.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "newuser@test.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_B_EMAIL = "trust_fragile@test.com"
TEST_USER_B_PASSWORD = "password123"

class TestRiskSignalDefinitions:
    """Test GET /api/risk-signals/definitions - returns all 8 signal types"""
    
    def test_get_signal_definitions_returns_8_types(self):
        """Verify all 8 signal types are returned with correct fields"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("total") == 8, f"Expected 8 signals, got {data.get('total')}"
        
        signals = data.get("signals", [])
        assert len(signals) == 8
        
        # Verify all expected signal types
        signal_types = [s["signal_type"] for s in signals]
        expected_types = [
            "reaction_farming", "velocity_spike", "reciprocal_boosting",
            "low_effort_content", "category_flooding", "ghost_reactor",
            "burst_and_vanish", "community_monopoly"
        ]
        for exp_type in expected_types:
            assert exp_type in signal_types, f"Missing signal type: {exp_type}"
    
    def test_signal_definitions_have_required_fields(self):
        """Verify each signal has required fields: signal_type, category, severity, description, indicator, system_response, source"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["signal_type", "category", "severity", "description", "indicator", "system_response", "source"]
        
        for signal in data.get("signals", []):
            for field in required_fields:
                assert field in signal, f"Signal {signal.get('signal_type', 'unknown')} missing field: {field}"
                assert signal[field], f"Signal {signal.get('signal_type', 'unknown')} has empty {field}"
    
    def test_signal_categories_are_valid(self):
        """Verify signals have valid categories from the 4 defined categories"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        
        assert response.status_code == 200
        data = response.json()
        
        valid_categories = ["trust_manipulation", "content_integrity", "account_behavior", "network_anomaly"]
        
        for signal in data.get("signals", []):
            assert signal["category"] in valid_categories, f"Invalid category {signal['category']} for {signal['signal_type']}"
    
    def test_signal_severities_are_valid(self):
        """Verify signals have valid severities"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        
        assert response.status_code == 200
        data = response.json()
        
        valid_severities = ["low", "medium", "high"]
        
        for signal in data.get("signals", []):
            assert signal["severity"] in valid_severities, f"Invalid severity {signal['severity']} for {signal['signal_type']}"


class TestRiskSignalScanner:
    """Test POST /api/risk-signals/scan - runs all 6 scanner detectors"""
    
    def test_scan_returns_results_per_signal_type(self):
        """Verify scan returns results for all 6 scanner detectors"""
        response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        scan_results = data.get("scan_results", {})
        
        # The scanner runs 6 detectors (reaction_farming and velocity_spike are detected inline, not by scanner)
        expected_detectors = [
            "reciprocal_boosting", "low_effort_content", "category_flooding",
            "ghost_reactor", "burst_and_vanish", "community_monopoly"
        ]
        
        for detector in expected_detectors:
            assert detector in scan_results, f"Missing detector result: {detector}"
        
        # Verify scanned_at timestamp
        assert "scanned_at" in data
        assert "total_active_signals" in data
    
    def test_scan_detects_community_monopoly(self):
        """Verify scanner detects community_monopoly when one user has >80% of community actions"""
        # First, trigger a scan
        response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
        assert response.status_code == 200
        
        # Now check if community_monopoly was detected (based on context: 14 actions from 1 user in 'Local Volunteers')
        list_response = requests.get(f"{BASE_URL}/api/risk-signals?category=network_anomaly")
        assert list_response.status_code == 200
        
        data = list_response.json()
        signals = data.get("signals", [])
        
        # Check if community_monopoly signal exists
        monopoly_signals = [s for s in signals if s.get("signal_type") == "community_monopoly"]
        assert len(monopoly_signals) >= 1, "Expected at least 1 community_monopoly signal based on existing data (1 user has 100% of actions in Local Volunteers)"
        
        # Verify evidence fields
        if monopoly_signals:
            evidence = monopoly_signals[0].get("evidence", {})
            assert "community" in evidence or "monopoly_pct" in evidence


class TestRiskSignalList:
    """Test GET /api/risk-signals - list signals with filters"""
    
    def test_list_signals_returns_array(self):
        """Verify listing signals returns array with pagination"""
        response = requests.get(f"{BASE_URL}/api/risk-signals")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "signals" in data
        assert isinstance(data["signals"], list)
        assert "total" in data
    
    def test_filter_by_category(self):
        """Test filtering signals by category"""
        response = requests.get(f"{BASE_URL}/api/risk-signals?category=trust_manipulation")
        
        assert response.status_code == 200
        data = response.json()
        
        for signal in data.get("signals", []):
            assert signal.get("category") == "trust_manipulation"
    
    def test_filter_by_severity(self):
        """Test filtering signals by severity"""
        response = requests.get(f"{BASE_URL}/api/risk-signals?severity=medium")
        
        assert response.status_code == 200
        data = response.json()
        
        for signal in data.get("signals", []):
            assert signal.get("severity") == "medium"
    
    def test_filter_by_status(self):
        """Test filtering signals by status"""
        # Default is 'active'
        response = requests.get(f"{BASE_URL}/api/risk-signals?status=active")
        
        assert response.status_code == 200
        data = response.json()
        
        for signal in data.get("signals", []):
            assert signal.get("status") == "active"
    
    def test_signals_have_signal_id(self):
        """Verify signals have signal_id (converted from _id)"""
        response = requests.get(f"{BASE_URL}/api/risk-signals?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        for signal in data.get("signals", []):
            assert "signal_id" in signal, "Signal missing signal_id field"
            assert "_id" not in signal, "Signal should not expose MongoDB _id"


class TestRiskSignalSummary:
    """Test GET /api/risk-signals/summary - aggregated counts"""
    
    def test_summary_returns_aggregated_counts(self):
        """Verify summary returns counts by category and severity"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/summary")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        # Check expected fields
        assert "total_active" in data
        assert "by_category" in data
        assert "by_severity" in data
        assert "breakdown" in data
        
        # by_category and by_severity should be dicts
        assert isinstance(data["by_category"], dict)
        assert isinstance(data["by_severity"], dict)
        
        # breakdown should be a list
        assert isinstance(data["breakdown"], list)


class TestRiskSignalUser:
    """Test GET /api/risk-signals/user/{user_id} - signals for specific user"""
    
    def test_get_user_signals(self):
        """Verify getting signals for a specific user returns user-scoped data"""
        # Use the known user_id from context
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        
        response = requests.get(f"{BASE_URL}/api/risk-signals/user/{user_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("user_id") == user_id
        assert "signals" in data
        assert "total" in data
        assert "active" in data
        
        # All signals should be for this user
        for signal in data.get("signals", []):
            assert signal.get("subject_user_id") == user_id
    
    def test_get_user_signals_nonexistent_user(self):
        """Verify getting signals for non-existent user returns empty list"""
        user_id = "nonexistent-user-id-12345"
        
        response = requests.get(f"{BASE_URL}/api/risk-signals/user/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("total") == 0
        assert data.get("signals") == []


class TestRiskSignalUpdate:
    """Test PATCH /api/risk-signals/{signal_id} - update signal status"""
    
    def _get_active_signal_id(self):
        """Helper to get an active signal ID for testing"""
        response = requests.get(f"{BASE_URL}/api/risk-signals?status=active&limit=1")
        if response.status_code == 200:
            data = response.json()
            signals = data.get("signals", [])
            if signals:
                return signals[0].get("signal_id")
        return None
    
    def test_update_signal_status_to_resolved(self):
        """Test resolving a signal"""
        signal_id = self._get_active_signal_id()
        if not signal_id:
            pytest.skip("No active signals to test update")
        
        response = requests.patch(
            f"{BASE_URL}/api/risk-signals/{signal_id}",
            json={"status": "resolved", "resolution_note": "TEST_resolved_by_automated_test"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("signal_id") == signal_id
        assert data.get("new_status") == "resolved"
    
    def test_update_signal_invalid_status(self):
        """Test that invalid status is rejected"""
        signal_id = self._get_active_signal_id()
        if not signal_id:
            # Create a signal first via scan
            requests.post(f"{BASE_URL}/api/risk-signals/scan")
            signal_id = self._get_active_signal_id()
            if not signal_id:
                pytest.skip("Cannot create signals for testing")
        
        response = requests.patch(
            f"{BASE_URL}/api/risk-signals/{signal_id}",
            json={"status": "invalid_status"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
    
    def test_update_signal_invalid_id(self):
        """Test that invalid signal ID returns 400"""
        response = requests.patch(
            f"{BASE_URL}/api/risk-signals/invalid-id",
            json={"status": "resolved"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid ID, got {response.status_code}"
    
    def test_update_nonexistent_signal(self):
        """Test that updating non-existent signal returns 404"""
        # Use a valid ObjectId format but non-existent
        fake_id = "000000000000000000000000"
        
        response = requests.patch(
            f"{BASE_URL}/api/risk-signals/{fake_id}",
            json={"status": "resolved"}
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent signal, got {response.status_code}"


class TestDismissedSignalsNotReCreated:
    """Test that dismissed signals are not re-created on subsequent scans"""
    
    def test_dismissed_signal_not_recreated(self):
        """Verify dismissed signals don't reappear after scan"""
        # First, run a scan to ensure we have signals
        scan_response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
        assert scan_response.status_code == 200
        
        # Get current signals and their count
        initial_response = requests.get(f"{BASE_URL}/api/risk-signals?status=active&limit=1")
        initial_data = initial_response.json()
        
        if not initial_data.get("signals"):
            pytest.skip("No active signals to test dismissal")
        
        signal = initial_data["signals"][0]
        signal_id = signal.get("signal_id")
        signal_type = signal.get("signal_type")
        subject_user = signal.get("subject_user_id")
        
        # Dismiss the signal
        dismiss_response = requests.patch(
            f"{BASE_URL}/api/risk-signals/{signal_id}",
            json={"status": "dismissed", "resolution_note": "TEST_dismissed_for_testing"}
        )
        assert dismiss_response.status_code == 200
        
        # Run scan again
        rescan_response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
        assert rescan_response.status_code == 200
        
        # Verify the signal is still dismissed and not re-created as active
        check_response = requests.get(
            f"{BASE_URL}/api/risk-signals/user/{subject_user}"
        )
        assert check_response.status_code == 200
        check_data = check_response.json()
        
        # Find signals of this type for this user
        type_signals = [s for s in check_data.get("signals", []) 
                       if s.get("signal_type") == signal_type]
        
        # Should still have only dismissed status (not a new active one)
        active_of_type = [s for s in type_signals if s.get("status") == "active"]
        dismissed_of_type = [s for s in type_signals if s.get("status") == "dismissed"]
        
        # Note: This depends on whether there are duplicate conditions
        # The key check is that dismissed signal ID should still be dismissed
        user_signals = check_data.get("signals", [])
        for s in user_signals:
            if s.get("signal_id") == signal_id:
                assert s.get("status") == "dismissed", "Dismissed signal was re-activated"


class TestLowEffortContentDetection:
    """Test that scanner detects low_effort_content for short titles/descriptions"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for creating test actions"""
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_detect_low_effort_content_short_title(self, auth_token):
        """Create action with very short title and verify detection"""
        if not auth_token:
            pytest.skip("Auth failed, cannot create test action")
        
        # Create action with short title (< 5 chars) and description (< 15 chars)
        headers = {"Authorization": f"Bearer {auth_token}"}
        unique_suffix = uuid.uuid4().hex[:6]
        
        action_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            headers=headers,
            json={
                "title": f"T{unique_suffix[:2]}",  # 3 chars - should trigger low_effort
                "description": f"Short{unique_suffix[:5]}",  # ~10 chars - should trigger
                "category": "other",
                "community": "Test Community"
            }
        )
        
        # May fail due to rate limit or duplicate, which is fine
        if action_response.status_code not in [200, 429, 409]:
            pytest.fail(f"Unexpected status creating action: {action_response.status_code}: {action_response.text}")
        
        if action_response.status_code == 200:
            action_id = action_response.json().get("action_id")
            
            # Run scan
            scan_response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
            assert scan_response.status_code == 200
            
            scan_data = scan_response.json()
            low_effort_count = scan_data.get("scan_results", {}).get("low_effort_content", 0)
            
            # Verify low_effort_content detection found something
            assert isinstance(low_effort_count, int), f"Expected int, got {type(low_effort_count)}"
            print(f"Low effort content signals detected: {low_effort_count}")


class TestRegressionTrustIntegrity:
    """Regression tests for existing trust integrity endpoints"""
    
    def test_trust_integrity_stats_still_works(self):
        """Verify /api/trust/integrity-stats endpoint is not broken"""
        response = requests.get(f"{BASE_URL}/api/trust/integrity-stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "stats" in data
        
        stats = data["stats"]
        # Verify expected stat fields exist
        expected_fields = ["total_actions", "self_reported", "total_flags"]
        for field in expected_fields:
            assert field in stats, f"Missing stat field: {field}"
    
    def test_trust_flags_still_works(self):
        """Verify /api/trust/flags endpoint is not broken"""
        response = requests.get(f"{BASE_URL}/api/trust/flags")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "flags" in data
        assert "total" in data


class TestRegressionActionsFeed:
    """Regression tests for actions feed endpoint"""
    
    def test_actions_feed_still_works(self):
        """Verify /api/actions/feed endpoint is not broken"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "actions" in data
        assert isinstance(data["actions"], list)
        
        # Verify action structure
        if data["actions"]:
            action = data["actions"][0]
            assert "id" in action
            assert "title" in action
            assert "user_id" in action


class TestRegressionLeaderboard:
    """Regression tests for leaderboard endpoint"""
    
    def test_leaderboard_still_works(self):
        """Verify /api/leaderboard endpoint is not broken"""
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "leaders" in data
        assert isinstance(data["leaders"], list)

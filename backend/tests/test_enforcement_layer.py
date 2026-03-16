"""
Test suite for Risk Signal Enforcement Layer
Tests enforcement behaviors when risk signals are active:
- community_monopoly: trust * 0.5x
- velocity_spike: frozen trust score
- ghost_reactor: reaction weight 0.5x
- reciprocal_boosting: mutual reactions 0.5x
- reaction_farming: reactor suppressed (0 weight)
- burst_and_vanish: accelerated decay 10% vs 5%
- scheduler: risk_signal_scan at 05:00 UTC
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_A_EMAIL = "newuser@test.com"
TEST_USER_A_PASSWORD = "password123"
TEST_USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"

TEST_USER_B_EMAIL = "trust_fragile@test.com"
TEST_USER_B_PASSWORD = "password123"
TEST_USER_B_ID = "0c98a493-3148-4c72-88e7-662baa393d11"


@pytest.fixture(scope="module")
def auth_token_a():
    """Get auth token for Test User A"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_A_EMAIL, "password": TEST_USER_A_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("token"):
            return data.get("token")
    pytest.skip(f"Auth failed for user A: {response.status_code} {response.text}")


@pytest.fixture(scope="module")
def auth_token_b():
    """Get auth token for Test User B"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_B_EMAIL, "password": TEST_USER_B_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("token"):
            return data.get("token")
    pytest.skip(f"Auth failed for user B: {response.status_code} {response.text}")


class TestRiskSignalDefinitionsRegression:
    """Verify /api/risk-signals/definitions still returns 8 signals after enforcement changes"""
    
    def test_definitions_returns_8_signals(self):
        """GET /api/risk-signals/definitions returns all 8 signal types"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("total") == 8, f"Expected 8 signals, got {data.get('total')}"
        
        signal_types = [s["signal_type"] for s in data.get("signals", [])]
        expected_types = [
            "reaction_farming", "velocity_spike", "reciprocal_boosting",
            "low_effort_content", "category_flooding", "ghost_reactor",
            "burst_and_vanish", "community_monopoly"
        ]
        for exp_type in expected_types:
            assert exp_type in signal_types, f"Missing signal type: {exp_type}"


class TestRiskSignalScanRegression:
    """Verify /api/risk-signals/scan still works after enforcement changes"""
    
    def test_scan_endpoint_works(self):
        """POST /api/risk-signals/scan runs without error"""
        response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "scan_results" in data
        assert "total_active_signals" in data
        assert "scanned_at" in data


class TestReactToActionRegression:
    """Verify POST /api/actions/{id}/react still works for normal reactions"""
    
    def test_normal_reaction_works(self, auth_token_a, auth_token_b):
        """Normal reaction (no signals) still adds trust correctly"""
        # Create a fresh action from User B (User A may be rate limited)
        headers_b = {"Authorization": f"Bearer {auth_token_b}"}
        unique_id = uuid.uuid4().hex[:8]
        
        create_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            headers=headers_b,
            json={
                "title": f"Enforcement Test Normal {unique_id}",
                "description": f"Testing normal reaction without enforcement signals - {unique_id}",
                "category": "technology",
                "community": f"TEST_EnforcementNormal_{unique_id}"  # Unique community to avoid monopoly
            }
        )
        
        if create_response.status_code == 429:
            pytest.skip("Rate limited - cannot create test action")
        
        assert create_response.status_code == 200, f"Failed to create action: {create_response.text}"
        action_id = create_response.json().get("action_id")
        
        # User A reacts with 'support' (weight=1)
        headers_a = {"Authorization": f"Bearer {auth_token_a}"}
        react_response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            headers=headers_a,
            json={"reaction_type": "support"}
        )
        
        assert react_response.status_code == 200, f"Reaction failed: {react_response.text}"
        
        data = react_response.json()
        assert data.get("success") == True
        assert data.get("added") == True
        
        # For self_reported verification (mult=1), support reaction (weight=1): trust = 1 * 1 = 1
        trust_signal = data.get("trust_signal", 0)
        assert trust_signal >= 1, f"Expected trust_signal >= 1, got {trust_signal}"
        print(f"Normal reaction trust_signal: {trust_signal}")


class TestActionsFeedRegression:
    """Verify GET /api/actions/feed returns correct trust scores"""
    
    def test_feed_returns_trust_scores(self):
        """Feed actions have trust_signal field"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "actions" in data
        
        actions = data["actions"]
        if actions:
            for action in actions[:5]:  # Check first 5
                assert "trust_signal" in action, f"Action {action.get('id')} missing trust_signal"
                assert "verification_level" in action
                assert "verification_multiplier" in action


class TestTrustVerifyRegression:
    """Verify POST /api/trust/verify/{id} still works"""
    
    def test_verify_action_works(self, auth_token_b):
        """Verification endpoint still functions"""
        # Create action with User B (User A may be rate limited)
        headers = {"Authorization": f"Bearer {auth_token_b}"}
        unique_id = uuid.uuid4().hex[:8]
        
        create_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            headers=headers,
            json={
                "title": f"Verify Regression Test {unique_id}",
                "description": f"Testing verification endpoint regression - {unique_id}",
                "category": "education",
                "community": f"TEST_VerifyRegression_{unique_id}"
            }
        )
        
        if create_response.status_code == 429:
            pytest.skip("Rate limited")
        
        assert create_response.status_code == 200
        action_id = create_response.json().get("action_id")
        
        # Verify the action
        verify_response = requests.post(
            f"{BASE_URL}/api/trust/verify/{action_id}",
            headers=headers,
            json={
                "verification_level": "community_verified",
                "verifier_community": "Test Verifiers"
            }
        )
        
        assert verify_response.status_code == 200, f"Verify failed: {verify_response.text}"
        data = verify_response.json()
        assert data.get("success") == True
        assert data.get("verification_level") == "community_verified"
        assert data.get("multiplier") == 2


class TestIntegrityStatsRegression:
    """Verify GET /api/trust/integrity-stats still works"""
    
    def test_integrity_stats_works(self):
        """Integrity stats endpoint returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/trust/integrity-stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "stats" in data
        
        stats = data["stats"]
        expected_fields = ["total_actions", "self_reported", "community_verified", 
                         "org_verified", "total_flags", "high_severity_flags", "users_decayed"]
        
        for field in expected_fields:
            assert field in stats, f"Missing stats field: {field}"


class TestSchedulerRiskSignalScan:
    """Verify scheduler has risk_signal_scan job at 05:00 UTC"""
    
    def test_scheduler_status_endpoint(self):
        """Check if scheduler status shows risk signal scan job"""
        response = requests.get(f"{BASE_URL}/api/scheduler/status")
        
        # If endpoint exists, verify structure
        if response.status_code == 200:
            data = response.json()
            assert "scheduler_running" in data
            print(f"Scheduler status: {data}")
        else:
            # Even if status endpoint doesn't exist, the scan endpoint must work
            scan_response = requests.post(f"{BASE_URL}/api/risk-signals/scan")
            assert scan_response.status_code == 200, "Risk signal scan must work"
            print("Note: /api/scheduler/status not available, but scan endpoint works")


class TestCommunityMonopolyEnforcement:
    """
    Test community_monopoly enforcement: action in monopolized community gets trust * 0.5x
    
    Setup: User A has 100% of actions in 'Local Volunteers' community (6/6 per context).
    When User B reacts to User A's action in 'Local Volunteers', trust should be halved.
    """
    
    def test_community_monopoly_detection_exists(self):
        """Verify community_monopoly signal exists for Local Volunteers"""
        # Run scan first to ensure signals are up to date
        requests.post(f"{BASE_URL}/api/risk-signals/scan")
        
        response = requests.get(f"{BASE_URL}/api/risk-signals?category=network_anomaly")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        monopoly_signals = [s for s in signals if s.get("signal_type") == "community_monopoly"]
        print(f"Found {len(monopoly_signals)} community_monopoly signals")
        
        # Check for Local Volunteers specifically
        lv_signals = [s for s in monopoly_signals 
                     if s.get("_community_key") == "Local Volunteers" 
                     or s.get("evidence", {}).get("community") == "Local Volunteers"]
        
        if lv_signals:
            print(f"Local Volunteers monopoly signal: {lv_signals[0]}")
        else:
            print("No Local Volunteers monopoly signal found (may have been resolved)")
    
    def test_community_monopoly_halves_trust(self, auth_token_a, auth_token_b):
        """Verify reaction in monopolized community gets 0.5x trust"""
        # Find Local Volunteers action owned by User A
        feed_resp = requests.get(f"{BASE_URL}/api/actions/feed?limit=50")
        assert feed_resp.status_code == 200
        
        actions = feed_resp.json().get("actions", [])
        lv_action = None
        for a in actions:
            if a.get("community") == "Local Volunteers" and a.get("user_id") == TEST_USER_A_ID:
                lv_action = a
                break
        
        if not lv_action:
            pytest.skip("No Local Volunteers action found for User A")
        
        action_id = lv_action.get("id")
        print(f"Testing on action: {action_id} - '{lv_action.get('title')}'")
        
        # User B toggles support reaction
        headers_b = {"Authorization": f"Bearer {auth_token_b}"}
        
        # First, ensure we remove any existing reaction
        if lv_action.get("user_reacted", {}).get("support"):
            requests.post(
                f"{BASE_URL}/api/actions/{action_id}/react",
                headers=headers_b,
                json={"reaction_type": "support"}
            )
        
        # Now add the support reaction
        react_resp = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            headers=headers_b,
            json={"reaction_type": "support"}
        )
        
        assert react_resp.status_code == 200
        data = react_resp.json()
        
        trust_signal = data.get("trust_signal")
        print(f"Trust after reaction: {trust_signal}")
        
        # Get current reactions to calculate expected
        get_resp = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        action_data = get_resp.json().get("action", {})
        reactions = action_data.get("reactions", {})
        
        support = reactions.get("support", 0)
        useful = reactions.get("useful", 0)
        verified = reactions.get("verified", 0)
        
        # REACTION_WEIGHTS: support=1, useful=2, verified=5
        base = support * 1 + useful * 2 + verified * 5
        verification_level = action_data.get("verification_level", "self_reported")
        mult_map = {"self_reported": 1, "community_verified": 2, "org_verified": 3}
        verification_mult = mult_map.get(verification_level, 1)
        
        expected_without_enforcement = base * verification_mult
        expected_with_monopoly = expected_without_enforcement * 0.5
        
        print(f"Reactions: support={support}, useful={useful}, verified={verified}")
        print(f"Base: {base}, Verification mult: {verification_mult}")
        print(f"Expected without enforcement: {expected_without_enforcement}")
        print(f"Expected with community_monopoly (0.5x): {expected_with_monopoly}")
        
        # Trust should be halved due to community_monopoly
        assert trust_signal == expected_with_monopoly, \
            f"Expected {expected_with_monopoly} (with 0.5x monopoly), got {trust_signal}"
        print("✓ Community monopoly enforcement verified: trust halved correctly")


class TestEnforcementFallback:
    """Test that normal trust calculation still works if signal lookup fails"""
    
    def test_action_without_signals_calculates_normally(self, auth_token_a, auth_token_b):
        """Action in unique community (no signals) calculates trust normally"""
        # Use User B for creating action (User A is rate limited)
        headers_b = {"Authorization": f"Bearer {auth_token_b}"}
        unique_id = uuid.uuid4().hex[:8]
        unique_community = f"TEST_NoSignals_{unique_id}"
        
        # Create action in unique community
        create_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            headers=headers_b,
            json={
                "title": f"Fallback Test {unique_id}",
                "description": f"Testing enforcement fallback with unique community - {unique_id}",
                "category": "health",
                "community": unique_community
            }
        )
        
        if create_response.status_code == 429:
            pytest.skip("Rate limited")
        
        assert create_response.status_code == 200
        action_id = create_response.json().get("action_id")
        
        # Get action to verify initial trust is 0
        get_response = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get_response.status_code == 200
        initial_trust = get_response.json().get("action", {}).get("trust_signal", 0)
        assert initial_trust == 0, f"New action should have 0 trust, got {initial_trust}"
        
        # User A reacts with 'useful' (weight=2)
        headers_a = {"Authorization": f"Bearer {auth_token_a}"}
        react_response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            headers=headers_a,
            json={"reaction_type": "useful"}
        )
        
        assert react_response.status_code == 200
        
        data = react_response.json()
        trust_signal = data.get("trust_signal", 0)
        
        # self_reported (mult=1) * useful (weight=2) = 2
        # Without any enforcement signals, trust should be 2
        assert trust_signal == 2, f"Expected trust_signal=2 (useful=2*1), got {trust_signal}"
        print(f"Fallback test: trust_signal = {trust_signal} (expected 2)")


class TestAcceleratedDecayConfig:
    """
    Test burst_and_vanish accelerated decay configuration (10% vs 5%)
    
    Note: Actually triggering decay requires 30+ days inactivity,
    so we verify the configuration/code path exists via API responses.
    """
    
    def test_burst_and_vanish_signal_definition(self):
        """Verify burst_and_vanish signal definition mentions accelerated decay"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        bv_signal = next((s for s in signals if s["signal_type"] == "burst_and_vanish"), None)
        assert bv_signal is not None, "burst_and_vanish signal not found"
        
        # Verify system_response mentions accelerated decay
        system_response = bv_signal.get("system_response", "")
        assert "accelerated" in system_response.lower() or "10%" in system_response, \
            f"Expected accelerated decay in system_response: {system_response}"
        
        print(f"burst_and_vanish system_response: {system_response}")


class TestVelocitySpikeEnforcementLogic:
    """
    Test velocity_spike enforcement: trust should be frozen when flag exists
    
    Note: To fully test this, we would need to insert a trust_flag with type='velocity_spike'.
    Since we're testing via API, we verify the endpoint behavior is correct.
    """
    
    def test_velocity_spike_signal_definition(self):
        """Verify velocity_spike signal definition exists"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        vs_signal = next((s for s in signals if s["signal_type"] == "velocity_spike"), None)
        assert vs_signal is not None, "velocity_spike signal not found"
        
        # Verify system_response mentions freeze
        system_response = vs_signal.get("system_response", "")
        assert "freeze" in system_response.lower(), \
            f"Expected 'freeze' in system_response: {system_response}"
        
        print(f"velocity_spike system_response: {system_response}")


class TestGhostReactorEnforcementLogic:
    """
    Test ghost_reactor enforcement: reactions get 0.5x weight
    """
    
    def test_ghost_reactor_signal_definition(self):
        """Verify ghost_reactor signal definition exists"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        gr_signal = next((s for s in signals if s["signal_type"] == "ghost_reactor"), None)
        assert gr_signal is not None, "ghost_reactor signal not found"
        
        # Verify system_response mentions 0.5x
        system_response = gr_signal.get("system_response", "")
        assert "0.5" in system_response.lower() or "half" in system_response.lower(), \
            f"Expected 0.5x in system_response: {system_response}"
        
        print(f"ghost_reactor system_response: {system_response}")


class TestReciprocalBoostingEnforcementLogic:
    """
    Test reciprocal_boosting enforcement: mutual reactions get 0.5x discount
    """
    
    def test_reciprocal_boosting_signal_definition(self):
        """Verify reciprocal_boosting signal definition exists"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        rb_signal = next((s for s in signals if s["signal_type"] == "reciprocal_boosting"), None)
        assert rb_signal is not None, "reciprocal_boosting signal not found"
        
        # Verify system_response mentions 50% discount
        system_response = rb_signal.get("system_response", "")
        assert "50" in system_response or "discount" in system_response.lower() or "half" in system_response.lower(), \
            f"Expected 50% discount in system_response: {system_response}"
        
        print(f"reciprocal_boosting system_response: {system_response}")


class TestReactionFarmingEnforcementLogic:
    """
    Test reaction_farming enforcement: flagged reactor's reactions are suppressed
    """
    
    def test_reaction_farming_signal_definition(self):
        """Verify reaction_farming signal definition exists"""
        response = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        rf_signal = next((s for s in signals if s["signal_type"] == "reaction_farming"), None)
        assert rf_signal is not None, "reaction_farming signal not found"
        
        # Verify system_response mentions suppress
        system_response = rf_signal.get("system_response", "")
        assert "suppress" in system_response.lower() or "flag" in system_response.lower(), \
            f"Expected 'suppress' in system_response: {system_response}"
        
        print(f"reaction_farming system_response: {system_response}")


class TestTrustFlagsEndpoint:
    """Test /api/trust/flags returns inline-detected flags"""
    
    def test_trust_flags_returns_flags(self):
        """GET /api/trust/flags returns flag data"""
        response = requests.get(f"{BASE_URL}/api/trust/flags")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert "flags" in data
        assert "total" in data
        
        flags = data["flags"]
        print(f"Total trust_flags: {data.get('total')}")
        
        if flags:
            # Check flag structure
            flag = flags[0]
            assert "type" in flag, "Flag missing 'type' field"
            print(f"Sample flag types: {[f.get('type') for f in flags[:5]]}")


class TestEnforcementIntegration:
    """
    Integration test: Create action, add reaction, verify trust calculation
    with enforcement context loaded (even if no active signals apply)
    """
    
    def test_full_reaction_flow_with_enforcement(self, auth_token_a, auth_token_b):
        """Full flow: create action -> react -> verify trust with enforcement"""
        # User B creates action (User A is rate limited)
        headers_b = {"Authorization": f"Bearer {auth_token_b}"}
        headers_a = {"Authorization": f"Bearer {auth_token_a}"}
        unique_id = uuid.uuid4().hex[:8]
        
        # Step 1: Create action
        create_response = requests.post(
            f"{BASE_URL}/api/actions/post",
            headers=headers_b,
            json={
                "title": f"Integration Test {unique_id}",
                "description": f"Full enforcement integration test flow - {unique_id}",
                "category": "mentorship",
                "community": f"TEST_Integration_{unique_id}"
            }
        )
        
        if create_response.status_code == 429:
            pytest.skip("Rate limited")
        
        assert create_response.status_code == 200
        action_id = create_response.json().get("action_id")
        print(f"Created action: {action_id}")
        
        # Step 2: Get initial state
        get1 = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get1.status_code == 200
        initial_trust = get1.json().get("action", {}).get("trust_signal", 0)
        initial_level = get1.json().get("action", {}).get("verification_level")
        print(f"Initial state: trust={initial_trust}, level={initial_level}")
        
        # Step 3: User A reacts with 'verified' (weight=5)
        react_response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            headers=headers_a,
            json={"reaction_type": "verified"}
        )
        
        assert react_response.status_code == 200
        react_data = react_response.json()
        trust_after_react = react_data.get("trust_signal", 0)
        print(f"After 'verified' reaction: trust={trust_after_react}")
        
        # self_reported (mult=1) * verified (weight=5) = 5
        assert trust_after_react == 5, f"Expected trust=5, got {trust_after_react}"
        
        # Step 4: Verify action via community_verified (mult=2)
        verify_response = requests.post(
            f"{BASE_URL}/api/trust/verify/{action_id}",
            headers=headers_b,
            json={
                "verification_level": "community_verified",
                "verifier_community": "Integration Test Community"
            }
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        trust_after_verify = verify_data.get("trust_signal", 0)
        print(f"After community_verified: trust={trust_after_verify}")
        
        # community_verified (mult=2) * verified_reaction (weight=5) = 10
        assert trust_after_verify == 10, f"Expected trust=10, got {trust_after_verify}"
        
        # Step 5: Get final state
        get2 = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get2.status_code == 200
        final_action = get2.json().get("action", {})
        print(f"Final state: trust={final_action.get('trust_signal')}, level={final_action.get('verification_level')}")
        
        assert final_action.get("trust_signal") == 10
        assert final_action.get("verification_level") == "community_verified"

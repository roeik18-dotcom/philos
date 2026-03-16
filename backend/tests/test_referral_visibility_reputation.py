"""
Test Referral Visibility & Reputation Impact
Tests the new referral enrichment (status, display_name, trust_score, action_count)
and referral bonus (+2 trust per active referral)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test user A with 4 referrals (1 active, 3 pending)
TEST_USER_A_EMAIL = "newuser@test.com"
TEST_USER_A_PASSWORD = "password123"
TEST_USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"

# Test user B
TEST_USER_B_EMAIL = "trust_fragile@test.com"
TEST_USER_B_PASSWORD = "password123"


class TestReferralEndpointEnrichment:
    """Tests for GET /api/referrals/{user_id} enriched data"""

    def test_referrals_endpoint_returns_200(self):
        """GET /api/referrals/{user_id} should return 200"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True, "Response should have success=True"
        print(f"PASS: GET /api/referrals/{TEST_USER_A_ID} returns 200")

    def test_referrals_response_structure(self):
        """Response should contain referrals list with expected fields"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level fields
        assert "referrals" in data, "Response should have 'referrals' list"
        assert "total" in data, "Response should have 'total' count"
        assert "active_count" in data, "Response should have 'active_count'"
        assert "pending_count" in data, "Response should have 'pending_count'"
        assert "referral_trust_bonus" in data, "Response should have 'referral_trust_bonus'"
        
        print(f"PASS: Response has correct top-level structure: total={data['total']}, active={data['active_count']}, pending={data['pending_count']}, bonus={data['referral_trust_bonus']}")

    def test_referral_item_enrichment_fields(self):
        """Each referral item should have status, display_name, trust_score, action_count"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        referrals = data.get("referrals", [])
        if len(referrals) == 0:
            pytest.skip("No referrals found for test user")
        
        for i, ref in enumerate(referrals):
            assert "status" in ref, f"Referral {i} should have 'status'"
            assert "display_name" in ref, f"Referral {i} should have 'display_name'"
            assert "trust_score" in ref, f"Referral {i} should have 'trust_score'"
            assert "action_count" in ref, f"Referral {i} should have 'action_count'"
            assert "invited_user_id" in ref, f"Referral {i} should have 'invited_user_id'"
            assert ref["status"] in ["active", "pending"], f"Status should be 'active' or 'pending', got {ref['status']}"
            print(f"  Referral {i}: {ref['display_name']} - status={ref['status']}, actions={ref['action_count']}, trust={ref['trust_score']}")
        
        print(f"PASS: All {len(referrals)} referrals have enriched fields")

    def test_active_status_has_actions(self):
        """Active referrals should have action_count > 0"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        referrals = data.get("referrals", [])
        active_refs = [r for r in referrals if r.get("status") == "active"]
        pending_refs = [r for r in referrals if r.get("status") == "pending"]
        
        for ref in active_refs:
            assert ref["action_count"] > 0, f"Active referral {ref['display_name']} should have action_count > 0"
        
        for ref in pending_refs:
            assert ref["action_count"] == 0, f"Pending referral {ref['display_name']} should have action_count == 0"
        
        print(f"PASS: Active referrals ({len(active_refs)}) have actions, pending ({len(pending_refs)}) have 0 actions")

    def test_referral_trust_bonus_calculation(self):
        """referral_trust_bonus should equal active_count * 2"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        active_count = data.get("active_count", 0)
        bonus = data.get("referral_trust_bonus", 0)
        expected_bonus = active_count * 2
        
        assert bonus == expected_bonus, f"Expected bonus {expected_bonus} (active_count * 2), got {bonus}"
        print(f"PASS: referral_trust_bonus={bonus} equals active_count({active_count}) * 2")

    def test_counts_match_referrals_list(self):
        """active_count + pending_count should equal total and match list length"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        total = data.get("total", 0)
        active = data.get("active_count", 0)
        pending = data.get("pending_count", 0)
        referrals = data.get("referrals", [])
        
        assert total == len(referrals), f"Total ({total}) should match referrals list length ({len(referrals)})"
        assert active + pending == total, f"active_count ({active}) + pending_count ({pending}) should equal total ({total})"
        
        # Verify counts match actual statuses
        actual_active = sum(1 for r in referrals if r.get("status") == "active")
        actual_pending = sum(1 for r in referrals if r.get("status") == "pending")
        
        assert active == actual_active, f"active_count ({active}) should match actual active referrals ({actual_active})"
        assert pending == actual_pending, f"pending_count ({pending}) should match actual pending referrals ({actual_pending})"
        
        print(f"PASS: Counts verified - total={total}, active={active}, pending={pending}")


class TestTrustEndpointReferralBonus:
    """Tests for GET /api/trust/{user_id} referral bonus integration"""

    def test_trust_endpoint_returns_200(self):
        """GET /api/trust/{user_id} should return 200"""
        response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True, "Response should have success=True"
        print(f"PASS: GET /api/trust/{TEST_USER_A_ID} returns 200")

    def test_trust_response_has_referral_bonus(self):
        """Trust response should include referral_bonus field"""
        response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_bonus" in data, "Response should have 'referral_bonus' field"
        assert "trust_score" in data, "Response should have 'trust_score' field"
        
        print(f"PASS: Trust response includes referral_bonus={data['referral_bonus']}, trust_score={data['trust_score']}")

    def test_trust_score_includes_referral_bonus(self):
        """trust_score should include referral_bonus"""
        response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        trust_score = data.get("trust_score", 0)
        referral_bonus = data.get("referral_bonus", 0)
        action_count = data.get("action_count", 0)
        
        # Referral bonus should be included in total trust_score
        # trust_score >= referral_bonus (since action_trust + referral_bonus)
        if referral_bonus > 0:
            assert trust_score >= referral_bonus, f"trust_score ({trust_score}) should be >= referral_bonus ({referral_bonus})"
        
        print(f"PASS: trust_score={trust_score} includes referral_bonus={referral_bonus}, action_count={action_count}")

    def test_referral_bonus_matches_referrals_endpoint(self):
        """referral_bonus in /api/trust should match referral_trust_bonus in /api/referrals"""
        trust_response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A_ID}")
        referral_response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        
        assert trust_response.status_code == 200
        assert referral_response.status_code == 200
        
        trust_data = trust_response.json()
        referral_data = referral_response.json()
        
        trust_bonus = trust_data.get("referral_bonus", 0)
        referral_bonus = referral_data.get("referral_trust_bonus", 0)
        
        assert trust_bonus == referral_bonus, f"Trust referral_bonus ({trust_bonus}) should match referrals referral_trust_bonus ({referral_bonus})"
        print(f"PASS: Both endpoints return consistent bonus value: {trust_bonus}")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""

    def test_actions_feed_works(self):
        """GET /api/actions/feed should still work"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True
        print(f"PASS: GET /api/actions/feed returns 200 with {len(data.get('actions', []))} actions")

    def test_login_works(self):
        """POST /api/auth/login should still work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_A_EMAIL,
            "password": TEST_USER_A_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True, "Login should succeed"
        assert data.get("token") is not None, "Should return token"
        print(f"PASS: Login works for {TEST_USER_A_EMAIL}")

    def test_react_endpoint_works(self):
        """POST /api/actions/{id}/react should still work (authenticated)"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_B_EMAIL,
            "password": TEST_USER_B_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json().get("token")
        
        # Get an action to react to
        feed_response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert feed_response.status_code == 200
        actions = feed_response.json().get("actions", [])
        if not actions:
            pytest.skip("No actions in feed to test react")
        
        action_id = actions[0].get("id")
        
        # React to it
        headers = {"Authorization": f"Bearer {token}"}
        react_response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "support"},
            headers=headers
        )
        
        # Should work (200 or maybe 400 if already reacted)
        assert react_response.status_code in [200, 400], f"Expected 200/400, got {react_response.status_code}"
        print(f"PASS: React endpoint works (status {react_response.status_code})")


class TestUserWithNoReferrals:
    """Test behavior for users with no referrals"""

    def test_empty_referrals_response(self):
        """User with no referrals should get empty list with zeros"""
        # Use user B who might not have referrals
        response = requests.get(f"{BASE_URL}/api/referrals/nonexistent-user-123")
        assert response.status_code == 200, f"Should return 200 even for no referrals"
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("total", -1) == 0, "Total should be 0"
        assert data.get("active_count", -1) == 0, "active_count should be 0"
        assert data.get("pending_count", -1) == 0, "pending_count should be 0"
        assert data.get("referral_trust_bonus", -1) == 0, "referral_trust_bonus should be 0"
        assert data.get("referrals", None) == [], "referrals should be empty list"
        
        print("PASS: Empty referrals response has correct zero values")

    def test_trust_with_no_referral_bonus(self):
        """User with no referrals should have referral_bonus=0"""
        response = requests.get(f"{BASE_URL}/api/trust/nonexistent-user-456")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("referral_bonus", -1) == 0, "User with no referrals should have referral_bonus=0"
        print("PASS: User with no referrals has referral_bonus=0")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

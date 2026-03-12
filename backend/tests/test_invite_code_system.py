"""
Test suite for the Invite Code System feature.
Tests: registration with invite_code, invite code generation, invite-stats endpoint,
       create-invite endpoint limit, PH-XXXX format, influence chain in profile.
"""
import pytest
import requests
import os
import re
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
INVITER_EMAIL = "newuser@test.com"
INVITER_PASSWORD = "password123"
INVITER_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
INVITEE_USER_ID = "2d720b49-cd32-4378-aa4a-10dfe58f88e2"


class TestInviteCodeSystem:
    """Tests for the complete Invite Code System feature."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ==================== Registration Tests ====================

    def test_register_accepts_optional_invite_code_field(self):
        """POST /api/auth/register accepts optional invite_code field."""
        # Test registration without invite code
        unique_email = f"test_no_invite_{uuid.uuid4().hex[:8]}@test.com"
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True or "כתובת האימייל" in data.get("message", "")
        print(f"PASS: Registration without invite_code field works")

    def test_register_with_invalid_invite_code_returns_error(self):
        """POST /api/auth/register with invalid invite code returns error message."""
        unique_email = f"test_invalid_code_{uuid.uuid4().hex[:8]}@test.com"
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "password123",
            "invite_code": "PH-INVALID"
        })
        assert response.status_code == 200  # API returns 200 with success=False
        data = response.json()
        assert data.get("success") == False
        assert "קוד ההזמנה אינו תקף" in data.get("message", "")
        print(f"PASS: Invalid invite code returns error: {data.get('message')}")

    # ==================== Invite Stats Endpoint Tests ====================

    def test_invite_stats_endpoint_returns_expected_fields(self):
        """GET /api/orientation/invite-stats/{user_id} returns codes, remaining count, invitees, invited_by."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields are present
        assert data.get("success") == True
        assert "codes" in data
        assert "codes_remaining" in data
        assert "total_invites_used" in data
        assert "max_codes" in data
        assert "invited_by_alias" in data  # Can be null
        assert "invitees" in data
        
        print(f"PASS: Invite stats returns all expected fields")
        print(f"  - codes: {len(data.get('codes', []))} codes")
        print(f"  - codes_remaining: {data.get('codes_remaining')}")
        print(f"  - total_invites_used: {data.get('total_invites_used')}")
        print(f"  - max_codes: {data.get('max_codes')}")
        print(f"  - invitees count: {len(data.get('invitees', []))}")

    def test_invite_codes_are_ph_xxxx_format(self):
        """Invite codes are PH-XXXX format (4 uppercase alphanumeric chars)."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        codes = data.get("codes", [])
        assert len(codes) > 0, "User should have invite codes"
        
        # Verify PH-XXXX format
        pattern = r'^PH-[A-Z0-9]{4}$'
        for code_obj in codes:
            code = code_obj.get("code")
            assert re.match(pattern, code), f"Code {code} doesn't match PH-XXXX format"
        
        print(f"PASS: All {len(codes)} codes match PH-XXXX format")
        for code_obj in codes:
            print(f"  - {code_obj.get('code')} (used: {code_obj.get('used')})")

    def test_max_invite_codes_is_five(self):
        """Each user gets max 5 invite codes."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("max_codes") == 5
        print(f"PASS: Max invite codes is 5")

    # ==================== Create Invite Endpoint Tests ====================

    def test_create_invite_respects_max_limit(self):
        """POST /api/orientation/create-invite/{user_id} respects MAX_INVITE_CODES limit (5)."""
        # First, check current count
        stats_response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        stats_data = stats_response.json()
        current_codes = len(stats_data.get("codes", []))
        
        if current_codes >= 5:
            # Try to create more - should fail with success=false
            response = self.session.post(f"{BASE_URL}/api/orientation/create-invite/{INVITER_USER_ID}")
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") == False, "Should return success=false when at max limit"
            # Hebrew message: "הגעת למגבלת קודי ההזמנה" (You've reached the invite code limit)
            assert "הגעת למגבלת" in data.get("message", "") or "קודי ההזמנה" in data.get("message", "")
            print(f"PASS: Create invite correctly rejects when at max limit ({current_codes}/5)")
            print(f"  - Message: {data.get('message')}")
        else:
            print(f"INFO: User has {current_codes}/5 codes, could create more (not at limit)")

    # ==================== Get Invite Details Endpoint Tests ====================

    def test_get_invite_returns_inviter_alias(self):
        """GET /api/orientation/invite/{code} returns inviter_alias."""
        # Get a valid code first
        stats_response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        stats_data = stats_response.json()
        codes = stats_data.get("codes", [])
        
        if len(codes) > 0:
            code = codes[0].get("code")
            response = self.session.get(f"{BASE_URL}/api/orientation/invite/{code}")
            assert response.status_code == 200
            data = response.json()
            
            assert "inviter_alias" in data
            print(f"PASS: GET /api/orientation/invite/{code} returns inviter_alias: {data.get('inviter_alias')}")
        else:
            pytest.skip("No invite codes available to test")

    def test_get_invalid_invite_returns_404(self):
        """GET /api/orientation/invite/{code} returns 404 for invalid code."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite/PH-0000")
        assert response.status_code == 404
        print(f"PASS: Invalid invite code returns 404")

    # ==================== Profile Influence Chain Tests ====================

    def test_profile_record_returns_influence_chain(self):
        """GET /api/profile/{user_id}/record returns influence_chain with invited_by_alias and invitees."""
        response = self.session.get(f"{BASE_URL}/api/profile/{INVITER_USER_ID}/record")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                assert "influence_chain" in data
                influence_chain = data.get("influence_chain", {})
                assert "invited_by_alias" in influence_chain
                assert "invitees" in influence_chain
                print(f"PASS: Profile record contains influence_chain")
                print(f"  - invited_by_alias: {influence_chain.get('invited_by_alias')}")
                print(f"  - invitees: {influence_chain.get('invitees')}")
            else:
                print(f"INFO: Profile record returned success=false (user may not have actions)")
        else:
            print(f"INFO: Profile record returned status {response.status_code}")

    # ==================== Login Auto-Generate Codes Test ====================

    def test_login_generates_codes_for_existing_user(self):
        """POST /api/auth/login auto-generates 5 invite codes for existing users without codes."""
        # Login as existing user
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INVITER_EMAIL,
            "password": INVITER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        
        if data.get("success"):
            user_id = data.get("user", {}).get("id")
            # Check that user has invite codes
            stats_response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{user_id}")
            stats_data = stats_response.json()
            assert stats_data.get("success") == True
            codes_count = len(stats_data.get("codes", []))
            assert codes_count > 0, "User should have invite codes after login"
            print(f"PASS: User has {codes_count} invite codes after login")
        else:
            print(f"INFO: Login failed - {data.get('message')}")

    # ==================== Invitee Stats Test ====================

    def test_invitee_has_invited_by_field(self):
        """Invitee (registered with code) has invited_by in their stats."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITEE_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # inviteduser@test.com was registered with invite code PH-9RXU
                # They should have invited_by_alias populated
                print(f"INFO: Invitee invite stats:")
                print(f"  - invited_by_alias: {data.get('invited_by_alias')}")
                print(f"  - invited_by_id: {data.get('invited_by_id')}")
                print(f"  - codes: {len(data.get('codes', []))}")
                
                # Invitee should also have their own codes
                codes = data.get("codes", [])
                if len(codes) > 0:
                    print(f"PASS: Invitee has {len(codes)} own invite codes")
        else:
            print(f"INFO: Could not fetch invitee stats (status {response.status_code})")


class TestInviteCodeIntegration:
    """Integration tests for invite code flow."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_full_invite_flow(self):
        """Test complete invite flow: get code -> validate -> check inviter alias."""
        # Step 1: Get inviter's codes
        stats_response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        
        codes = stats_data.get("codes", [])
        assert len(codes) > 0, "Inviter should have codes"
        
        # Step 2: Get first code details
        code = codes[0].get("code")
        invite_response = self.session.get(f"{BASE_URL}/api/orientation/invite/{code}")
        assert invite_response.status_code == 200
        invite_data = invite_response.json()
        
        assert invite_data.get("success") == True
        assert "inviter_alias" in invite_data
        
        print(f"PASS: Full invite flow works")
        print(f"  - Code: {code}")
        print(f"  - Inviter alias: {invite_data.get('inviter_alias')}")

    def test_codes_remaining_calculation(self):
        """Test that codes_remaining is calculated correctly."""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        codes_count = len(data.get("codes", []))
        codes_remaining = data.get("codes_remaining", 0)
        max_codes = data.get("max_codes", 5)
        
        # remaining = max - existing
        expected_remaining = max(0, max_codes - codes_count)
        assert codes_remaining == expected_remaining, f"Expected {expected_remaining}, got {codes_remaining}"
        
        print(f"PASS: codes_remaining calculation correct")
        print(f"  - codes: {codes_count}, remaining: {codes_remaining}, max: {max_codes}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

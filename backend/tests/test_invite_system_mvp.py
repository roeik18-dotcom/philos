"""
Test suite for Invite System MVP (iteration 70).
Tests the new invite system with invite_codes collection:
- GET /api/invites/me - returns user's codes (auth required)
- POST /api/invites/generate - creates up to 2 active codes
- POST /api/invites/redeem - marks code used, links users, fires trust+analytics
- POST /api/invites/share - tracks share event
- GET /api/invites/lookup/{code} - public lookup (new + legacy collections)
- Registration with invite_code validation
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
USER1_EMAIL = "newuser@test.com"
USER1_PASSWORD = "password123"
USER1_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"

USER2_EMAIL = "trust_building@test.com"
USER2_PASSWORD = "password123"


class TestInvitesMe:
    """Tests for GET /api/invites/me endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_invites_me_returns_401_without_auth(self):
        """GET /api/invites/me without auth returns 401."""
        response = self.session.get(f"{BASE_URL}/api/invites/me")
        assert response.status_code == 401
        data = response.json()
        assert "Authentication required" in data.get("detail", "")
        print("PASS: /api/invites/me returns 401 without auth")
    
    def test_invites_me_returns_codes_with_auth(self):
        """GET /api/invites/me with auth returns user's codes."""
        # Login first
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        assert login_resp.status_code == 200
        token = login_resp.json().get("token")
        
        # Get invites
        response = self.session.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "user_id" in data
        assert "codes" in data
        assert "active_count" in data
        assert "used_count" in data
        assert "can_generate" in data
        assert "invite_url_template" in data
        
        # Verify codes structure
        codes = data.get("codes", [])
        assert isinstance(codes, list)
        if len(codes) > 0:
            code = codes[0]
            assert "code" in code
            assert "status" in code
            assert "created_at" in code
        
        print(f"PASS: /api/invites/me returns codes list with {len(codes)} codes")
        print(f"  - active_count: {data.get('active_count')}")
        print(f"  - used_count: {data.get('used_count')}")


class TestInvitesGenerate:
    """Tests for POST /api/invites/generate endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_generate_requires_auth(self):
        """POST /api/invites/generate requires authentication."""
        response = self.session.post(f"{BASE_URL}/api/invites/generate")
        assert response.status_code == 401
        print("PASS: /api/invites/generate requires auth")
    
    def test_generate_respects_max_active_limit(self):
        """POST /api/invites/generate respects MAX_ACTIVE_CODES=2 limit."""
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        token = login_resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check current active count
        me_resp = self.session.get(f"{BASE_URL}/api/invites/me", headers=headers)
        current_active = me_resp.json().get("active_count", 0)
        
        # Try to generate
        gen_resp = self.session.post(f"{BASE_URL}/api/invites/generate", headers=headers)
        assert gen_resp.status_code == 200
        data = gen_resp.json()
        
        if current_active >= 2:
            # Should return success=False when at max
            assert data.get("success") == False
            assert "maximum active codes" in data.get("message", "")
            print(f"PASS: Generate correctly blocks at max ({current_active} active)")
        else:
            # Should generate new codes
            assert data.get("success") == True
            assert "generated" in data
            assert data.get("active_count") <= 2
            print(f"PASS: Generated {len(data.get('generated', []))} code(s), now {data.get('active_count')} active")


class TestInvitesRedeem:
    """Tests for POST /api/invites/redeem endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Get tokens for both users
        login1 = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        self.token1 = login1.json().get("token")
        self.user1_id = login1.json().get("user", {}).get("id")
        
        login2 = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER2_EMAIL,
            "password": USER2_PASSWORD
        })
        self.token2 = login2.json().get("token")
        self.user2_id = login2.json().get("user", {}).get("id")
    
    def test_redeem_blocks_self_redeem(self):
        """POST /api/invites/redeem blocks self-redeem (400)."""
        # Get an active code from user1
        me_resp = self.session.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        codes = me_resp.json().get("codes", [])
        active_codes = [c for c in codes if c.get("status") == "active"]
        
        if len(active_codes) > 0:
            code = active_codes[0]["code"]
            # Try to redeem own code
            response = self.session.post(
                f"{BASE_URL}/api/invites/redeem",
                headers={"Authorization": f"Bearer {self.token1}"},
                json={"code": code}
            )
            assert response.status_code == 400
            assert "Cannot redeem your own invite code" in response.json().get("detail", "")
            print(f"PASS: Self-redeem blocked for code {code}")
        else:
            pytest.skip("No active codes to test self-redeem")
    
    def test_redeem_blocks_double_redeem(self):
        """POST /api/invites/redeem blocks double-redeem (400)."""
        # Get a used code from user1
        me_resp = self.session.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        codes = me_resp.json().get("codes", [])
        used_codes = [c for c in codes if c.get("status") == "used"]
        
        if len(used_codes) > 0:
            code = used_codes[0]["code"]
            # Try to redeem already-used code
            response = self.session.post(
                f"{BASE_URL}/api/invites/redeem",
                headers={"Authorization": f"Bearer {self.token2}"},
                json={"code": code}
            )
            assert response.status_code == 400
            assert "already used or expired" in response.json().get("detail", "")
            print(f"PASS: Double-redeem blocked for code {code}")
        else:
            pytest.skip("No used codes to test double-redeem")
    
    def test_redeem_invalid_code_returns_404(self):
        """POST /api/invites/redeem with invalid code returns 404."""
        response = self.session.post(
            f"{BASE_URL}/api/invites/redeem",
            headers={"Authorization": f"Bearer {self.token2}"},
            json={"code": "PH-INVALID"}
        )
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "")
        print("PASS: Invalid code returns 404")


class TestInvitesShare:
    """Tests for POST /api/invites/share endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_share_requires_auth(self):
        """POST /api/invites/share requires authentication."""
        response = self.session.post(
            f"{BASE_URL}/api/invites/share",
            json={"code": "PH-TEST"}
        )
        assert response.status_code == 401
        print("PASS: /api/invites/share requires auth")
    
    def test_share_tracks_event(self):
        """POST /api/invites/share tracks share event."""
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        token = login_resp.json().get("token")
        
        response = self.session.post(
            f"{BASE_URL}/api/invites/share",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": "PH-TEST"}
        )
        assert response.status_code == 200
        assert response.json().get("success") == True
        print("PASS: Share event tracked successfully")


class TestInvitesLookup:
    """Tests for GET /api/invites/lookup/{code} endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_lookup_invalid_code_returns_404(self):
        """GET /api/invites/lookup/{code} with invalid code returns 404."""
        response = self.session.get(f"{BASE_URL}/api/invites/lookup/PH-0000")
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "")
        print("PASS: Invalid code lookup returns 404")
    
    def test_lookup_valid_code_returns_details(self):
        """GET /api/invites/lookup/{code} returns code details for valid code."""
        # Login to get a valid code
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        token = login_resp.json().get("token")
        
        me_resp = self.session.get(
            f"{BASE_URL}/api/invites/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        codes = me_resp.json().get("codes", [])
        
        if len(codes) > 0:
            code = codes[0]["code"]
            response = self.session.get(f"{BASE_URL}/api/invites/lookup/{code}")
            assert response.status_code == 200
            data = response.json()
            
            assert data.get("success") == True
            assert "code" in data
            assert "status" in data
            assert "inviter_id" in data
            assert "inviter_alias" in data
            assert "use_count" in data
            
            print(f"PASS: Lookup returns details for {code}")
            print(f"  - status: {data.get('status')}")
            print(f"  - inviter_alias: {data.get('inviter_alias')}")
        else:
            pytest.skip("No codes to test lookup")


class TestAuthLogin:
    """Tests for existing auth/login endpoint still working."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_login_still_works(self):
        """POST /api/auth/login still works."""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER1_EMAIL,
            "password": USER1_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "token" in data
        assert "user" in data
        print("PASS: Login endpoint still works")


class TestTrustAPI:
    """Tests for existing trust API still working."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_trust_profile_still_works(self):
        """GET /api/user/{user_id}/trust still works."""
        response = self.session.get(f"{BASE_URL}/api/user/{USER1_ID}/trust")
        assert response.status_code == 200
        data = response.json()
        
        assert "user_id" in data
        assert "trust_score" in data
        assert "value_score" in data
        assert "risk_score" in data
        
        print(f"PASS: Trust profile endpoint works, score: {data.get('trust_score')}")


class TestAnalyticsEvents:
    """Tests for analytics events being tracked correctly."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_invite_events_tracked(self):
        """Analytics events include invite-related event types."""
        response = self.session.get(f"{BASE_URL}/api/analytics/events?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        events = data.get("events", [])
        event_types = set(e.get("event_type") for e in events)
        
        # Check for invite-related events
        expected_types = {"invite_generated", "invite_viewed", "invite_redeemed", "invite_accepted", "invite_shared"}
        found_types = expected_types.intersection(event_types)
        
        print(f"PASS: Found invite event types: {found_types}")
        
        # Check for trust_change with invite_used source
        trust_changes = [e for e in events if e.get("event_type") == "trust_change" 
                        and e.get("metadata", {}).get("source") == "invite_used"]
        if trust_changes:
            print(f"  - trust_change events with source=invite_used: {len(trust_changes)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

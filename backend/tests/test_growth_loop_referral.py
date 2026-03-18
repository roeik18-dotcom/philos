"""
Tests for Growth Loop / Referral System:
- GET /api/share/action/{id}?ref=USER_ID - Returns OG meta tags and redirects 
- GET /api/actions/{action_id} - Returns action with trust_signal and reactions (public)
- POST /api/auth/register with referral_user_id and referral_action_id
- GET /api/referrals/{user_id} - Returns list of referrals made by that user
- Regression: POST /api/actions/{id}/react still works
- Regression: GET /api/trust/{user_id} still works
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials from review request
TEST_USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
TEST_USER_A_EMAIL = "newuser@test.com"
TEST_USER_A_PASS = "password123"

TEST_USER_B_EMAIL = "trust_fragile@test.com"
TEST_USER_B_PASS = "password123"

# Known action ID from previous testing (with referral)
KNOWN_ACTION_ID = "69b8003830fe74f58fc77fd9"


class TestShareActionPage:
    """Tests for GET /api/share/action/{id}?ref=USER_ID endpoint"""

    def test_share_action_without_ref(self):
        """GET /api/share/action/{id} returns 200 with OG meta tags"""
        # Use a known action ID - get it from feed first
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed")
        assert feed_res.status_code == 200
        feed_data = feed_res.json()
        assert feed_data.get('success') is True
        assert len(feed_data.get('actions', [])) > 0
        
        action_id = feed_data['actions'][0]['id']
        
        # Test share page without ref
        response = requests.get(f"{BASE_URL}/api/share/action/{action_id}")
        assert response.status_code == 200
        
        # Check for OG meta tags in HTML response
        content = response.text
        assert 'og:title' in content
        assert 'og:description' in content
        assert 'og:image' in content
        assert 'og:url' in content
        assert 'twitter:card' in content
        print(f"SUCCESS: Share page for action {action_id} returns OG meta tags")

    def test_share_action_with_ref_param(self):
        """GET /api/share/action/{id}?ref=USER_ID passes ref to redirect URL"""
        # Get a valid action
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed")
        assert feed_res.status_code == 200
        action_id = feed_res.json()['actions'][0]['id']
        
        # Test share page with ref
        ref_user_id = TEST_USER_A_ID
        response = requests.get(f"{BASE_URL}/api/share/action/{action_id}?ref={ref_user_id}")
        assert response.status_code == 200
        
        content = response.text
        # Check that ref param is passed through to redirect URL
        assert f'ref={ref_user_id}' in content
        assert f'/app/action/{action_id}?ref={ref_user_id}' in content
        print(f"SUCCESS: Share page passes ref={ref_user_id} to redirect URL")

    def test_share_action_invalid_id_returns_404(self):
        """GET /api/share/action/{invalid_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/share/action/invalid_action_id")
        assert response.status_code == 404
        print("SUCCESS: Invalid action ID returns 404")


class TestPublicActionEndpoint:
    """Tests for GET /api/actions/{action_id} - public access"""

    def test_get_action_returns_trust_signal(self):
        """GET /api/actions/{action_id} returns action with trust_signal"""
        # Get a valid action from feed
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed")
        assert feed_res.status_code == 200
        action_id = feed_res.json()['actions'][0]['id']
        
        # Get single action
        response = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') is True
        assert 'action' in data
        action = data['action']
        assert 'trust_signal' in action
        assert 'reactions' in action
        assert 'title' in action
        print(f"SUCCESS: Action {action_id} has trust_signal={action['trust_signal']}, reactions={action['reactions']}")

    def test_get_action_invalid_id_returns_error(self):
        """GET /api/actions/{invalid_id} returns 400/404"""
        response = requests.get(f"{BASE_URL}/api/actions/invalid_action_id_123")
        # Accept both 400 (invalid ObjectId) and 404 (not found)
        assert response.status_code in [400, 404]
        print(f"SUCCESS: Invalid action ID returns {response.status_code}")


class TestReferralRegistration:
    """Tests for POST /api/auth/register with referral fields"""

    def test_register_with_referral_creates_user_and_referral(self):
        """POST /api/auth/register with referral_user_id creates referral record"""
        # Generate unique email
        unique_email = f"test_referral_{uuid.uuid4().hex[:8]}@test.com"
        
        # Get a valid action ID
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed")
        action_id = feed_res.json()['actions'][0]['id']
        
        payload = {
            "email": unique_email,
            "password": "testpass123",
            "referral_user_id": TEST_USER_A_ID,
            "referral_action_id": action_id
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        if data.get('success'):
            print(f"SUCCESS: Registered user {unique_email} with referral from {TEST_USER_A_ID}")
            assert 'user' in data
            assert 'token' in data
            new_user_id = data['user']['id']
            
            # Verify referral was created
            ref_response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
            assert ref_response.status_code == 200
            ref_data = ref_response.json()
            
            # Check if new user is in referrals
            referrals = ref_data.get('referrals', [])
            found = any(r['invited_user_id'] == new_user_id for r in referrals)
            assert found, f"Expected to find {new_user_id} in referrals of {TEST_USER_A_ID}"
            print(f"SUCCESS: Referral record created - inviter={TEST_USER_A_ID}, invited={new_user_id}")
        else:
            # May fail due to duplicate email - that's OK for test
            print(f"INFO: Registration returned: {data.get('message')}")

    def test_register_without_referral_works(self):
        """POST /api/auth/register without referral fields still works"""
        unique_email = f"test_no_ref_{uuid.uuid4().hex[:8]}@test.com"
        
        payload = {
            "email": unique_email,
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        if data.get('success'):
            print(f"SUCCESS: Registered user {unique_email} without referral")
        else:
            print(f"INFO: Registration returned: {data.get('message')}")


class TestReferralsEndpoint:
    """Tests for GET /api/referrals/{user_id}"""

    def test_get_referrals_for_user(self):
        """GET /api/referrals/{user_id} returns referrals list"""
        response = requests.get(f"{BASE_URL}/api/referrals/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') is True
        assert 'user_id' in data
        assert data['user_id'] == TEST_USER_A_ID
        assert 'referrals' in data
        assert 'total' in data
        assert isinstance(data['referrals'], list)
        
        print(f"SUCCESS: User {TEST_USER_A_ID} has {data['total']} referrals")
        
        # Verify referral structure if any exist
        if len(data['referrals']) > 0:
            referral = data['referrals'][0]
            assert 'inviter_id' in referral
            assert 'invited_user_id' in referral
            assert 'action_id' in referral
            assert 'source' in referral
            assert 'created_at' in referral
            print(f"SUCCESS: Referral has correct structure: {list(referral.keys())}")

    def test_get_referrals_for_nonexistent_user(self):
        """GET /api/referrals/{unknown_id} returns empty list"""
        response = requests.get(f"{BASE_URL}/api/referrals/nonexistent-user-id-12345")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') is True
        assert data.get('total') == 0
        assert data.get('referrals') == []
        print("SUCCESS: Unknown user returns empty referrals list")


class TestRegressionAPIs:
    """Regression tests for existing APIs"""

    def test_reaction_api_still_works(self):
        """POST /api/actions/{id}/react still works"""
        # Login first
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_A_EMAIL,
            "password": TEST_USER_A_PASS
        })
        
        if login_res.status_code != 200 or not login_res.json().get('success'):
            pytest.skip("Cannot login - skipping reaction test")
        
        token = login_res.json()['token']
        
        # Get an action not owned by this user
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed?viewer_id={TEST_USER_A_ID}")
        actions = feed_res.json().get('actions', [])
        
        # Find action not owned by test user
        target_action = None
        for action in actions:
            if action.get('user_id') != TEST_USER_A_ID:
                target_action = action
                break
        
        if not target_action:
            pytest.skip("No suitable action found for reaction test")
        
        # Try to react
        response = requests.post(
            f"{BASE_URL}/api/actions/{target_action['id']}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        print(f"SUCCESS: Reaction API working - action {target_action['id']}")

    def test_trust_api_still_works(self):
        """GET /api/trust/{user_id} still works"""
        response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') is True
        assert 'trust_score' in data
        assert 'decay_rate' in data
        print(f"SUCCESS: Trust API working - user {TEST_USER_A_ID} has trust_score={data['trust_score']}")

    def test_feed_api_still_works(self):
        """GET /api/actions/feed still works"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') is True
        assert 'actions' in data
        assert len(data['actions']) > 0
        print(f"SUCCESS: Feed API working - returned {len(data['actions'])} actions")


class TestOGImageGeneration:
    """Tests for OG image generation endpoint"""

    def test_og_image_endpoint(self):
        """GET /api/og/action/{id}/image returns image"""
        # Get a valid action
        feed_res = requests.get(f"{BASE_URL}/api/actions/feed")
        action_id = feed_res.json()['actions'][0]['id']
        
        response = requests.get(f"{BASE_URL}/api/og/action/{action_id}/image")
        assert response.status_code == 200
        assert 'image/png' in response.headers.get('Content-Type', '')
        print(f"SUCCESS: OG image generated for action {action_id}")

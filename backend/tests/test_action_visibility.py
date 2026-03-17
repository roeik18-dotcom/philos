"""
Tests for Action Visibility System (3-step post wizard)
- POST /api/actions/post with visibility='private' / 'public'
- GET /api/actions/feed with visibility filter
- Regression tests for trust, referrals, risk-signals
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
USER_A_EMAIL = "newuser@test.com"
USER_A_PASSWORD = "password123"
USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"

USER_B_EMAIL = "trust_fragile@test.com"
USER_B_PASSWORD = "password123"


class TestActionVisibilityBackend:
    """Test visibility field in POST and GET /api/actions/"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login user A
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_A_EMAIL,
            "password": USER_A_PASSWORD
        })
        if login_res.status_code == 200:
            data = login_res.json()
            self.token = data.get("token")
            self.user_id = data.get("user", {}).get("id", USER_A_ID)
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip(f"Login failed: {login_res.status_code}")
    
    # ═══ POST /api/actions/post with visibility ═══
    
    def test_post_action_with_visibility_private(self):
        """POST /api/actions/post with visibility='private' creates action with visibility field"""
        unique_title = f"TEST_Private Action {uuid.uuid4().hex[:8]}"
        payload = {
            "title": unique_title,
            "description": "This is a private reflection for testing",
            "category": "community",
            "visibility": "private"
        }
        res = self.session.post(f"{BASE_URL}/api/actions/post", json=payload)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert "action_id" in data
        
        # Verify action was created with correct visibility by fetching it
        action_id = data["action_id"]
        get_res = self.session.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get_res.status_code == 200
        action_data = get_res.json()
        assert action_data.get("success") is True
        assert action_data["action"]["visibility"] == "private"
        print(f"PASS: Created private action {action_id}")
    
    def test_post_action_with_visibility_public(self):
        """POST /api/actions/post with visibility='public' creates action with visibility field"""
        unique_title = f"TEST_Public Action {uuid.uuid4().hex[:8]}"
        payload = {
            "title": unique_title,
            "description": "This is a public action for testing",
            "category": "education",
            "visibility": "public"
        }
        res = self.session.post(f"{BASE_URL}/api/actions/post", json=payload)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert "action_id" in data
        
        # Verify visibility
        action_id = data["action_id"]
        get_res = self.session.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get_res.status_code == 200
        action_data = get_res.json()
        assert action_data["action"]["visibility"] == "public"
        print(f"PASS: Created public action {action_id}")
    
    def test_post_action_default_visibility(self):
        """POST /api/actions/post without visibility defaults to 'public'"""
        unique_title = f"TEST_Default Visibility {uuid.uuid4().hex[:8]}"
        payload = {
            "title": unique_title,
            "description": "Testing default visibility",
            "category": "health"
        }
        res = self.session.post(f"{BASE_URL}/api/actions/post", json=payload)
        assert res.status_code == 200
        data = res.json()
        action_id = data["action_id"]
        
        # Verify default visibility is public
        get_res = self.session.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get_res.status_code == 200
        action_data = get_res.json()
        assert action_data["action"]["visibility"] == "public", "Default visibility should be 'public'"
        print(f"PASS: Default visibility is 'public'")
    
    # ═══ GET /api/actions/feed with visibility filter ═══
    
    def test_feed_returns_visibility_field(self):
        """GET /api/actions/feed returns visibility field on each action"""
        res = self.session.get(f"{BASE_URL}/api/actions/feed?viewer_id={self.user_id}")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        assert "actions" in data
        
        # Check at least some actions have visibility field
        if len(data["actions"]) > 0:
            for action in data["actions"][:5]:  # Check first 5
                assert "visibility" in action, f"Action {action.get('id')} missing visibility field"
                assert action["visibility"] in ("public", "private"), f"Invalid visibility: {action['visibility']}"
            print(f"PASS: Feed returns visibility field on {len(data['actions'])} actions")
        else:
            print("WARN: No actions in feed to verify visibility")
    
    def test_feed_without_viewer_excludes_private(self):
        """GET /api/actions/feed with no viewer_id excludes private actions"""
        # Get feed without viewer_id
        res = self.session.get(f"{BASE_URL}/api/actions/feed")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        
        # Verify no private actions in response
        for action in data["actions"]:
            visibility = action.get("visibility", "public")
            assert visibility != "private", f"Private action {action['id']} should not appear without viewer_id"
        print(f"PASS: Feed without viewer_id excludes private actions ({len(data['actions'])} public)")
    
    def test_feed_with_viewer_shows_own_private(self):
        """GET /api/actions/feed with viewer_id shows public + viewer's own private"""
        res = self.session.get(f"{BASE_URL}/api/actions/feed?viewer_id={self.user_id}")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        
        # Look for private actions - they should belong to the viewer
        private_actions = [a for a in data["actions"] if a.get("visibility") == "private"]
        for pa in private_actions:
            assert pa["user_id"] == self.user_id, f"Private action {pa['id']} belongs to another user"
        
        print(f"PASS: Feed with viewer_id shows {len(private_actions)} own private, {len(data['actions']) - len(private_actions)} public")
    
    def test_feed_visibility_filter_public_only(self):
        """GET /api/actions/feed?visibility=public shows only public actions"""
        res = self.session.get(f"{BASE_URL}/api/actions/feed?visibility=public")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        
        # All should be public
        for action in data["actions"]:
            vis = action.get("visibility", "public")
            assert vis != "private", f"Private action {action['id']} should not appear in public filter"
        print(f"PASS: visibility=public filter returns {len(data['actions'])} public actions")
    
    def test_feed_visibility_filter_private_only(self):
        """GET /api/actions/feed?visibility=private&viewer_id=X shows only viewer's private"""
        res = self.session.get(f"{BASE_URL}/api/actions/feed?visibility=private&viewer_id={self.user_id}")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        
        # All should be private AND belong to viewer
        for action in data["actions"]:
            assert action.get("visibility") == "private", f"Action {action['id']} should be private"
            assert action["user_id"] == self.user_id, f"Action {action['id']} should belong to viewer"
        print(f"PASS: visibility=private filter returns {len(data['actions'])} viewer's private actions")
    

class TestRegressionAPIs:
    """Regression tests for existing APIs"""
    
    def test_trust_endpoint(self):
        """REGRESSION: GET /api/trust/{user_id} still works"""
        res = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("success") is True
        assert "trust_score" in data or "score" in data or "trust" in data
        print(f"PASS: GET /api/trust/{USER_A_ID} returns data")
    
    def test_referrals_endpoint(self):
        """REGRESSION: GET /api/referrals/{user_id} still works"""
        res = requests.get(f"{BASE_URL}/api/referrals/{USER_A_ID}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("success") is True
        print(f"PASS: GET /api/referrals/{USER_A_ID} returns data")
    
    def test_risk_signals_definitions(self):
        """REGRESSION: GET /api/risk-signals/definitions returns 8 signals"""
        res = requests.get(f"{BASE_URL}/api/risk-signals/definitions")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("success") is True
        signals = data.get("signals", [])
        assert len(signals) == 8, f"Expected 8 signals, got {len(signals)}"
        print(f"PASS: Risk signals definitions returns {len(signals)} signals")


class TestActionEndpoints:
    """Test individual action endpoints"""
    
    def test_get_action_by_id(self):
        """GET /api/actions/{id} returns single action with visibility"""
        # First get feed to find an action ID
        res = requests.get(f"{BASE_URL}/api/actions/feed?limit=1")
        assert res.status_code == 200
        data = res.json()
        if len(data.get("actions", [])) == 0:
            pytest.skip("No actions available")
        
        action_id = data["actions"][0]["id"]
        
        # Fetch single action
        get_res = requests.get(f"{BASE_URL}/api/actions/{action_id}")
        assert get_res.status_code == 200
        action_data = get_res.json()
        assert action_data.get("success") is True
        assert "visibility" in action_data["action"]
        print(f"PASS: GET /api/actions/{action_id} returns action with visibility")

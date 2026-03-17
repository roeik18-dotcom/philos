"""
Daily Orientation Layer API Tests
Tests the GET /api/orientation/{user_id} endpoint and its decision rules.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test users from main agent
USER_A_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"  # Contributing, pos=0.545
USER_A_EMAIL = "newuser@test.com"
USER_A_PASSWORD = "password123"

USER_B_ID = "0c98a493-3148-4c72-88e7-662baa393d11"  # Emerging, pos=0.225, low reactors
USER_B_EMAIL = "trust_fragile@test.com"
USER_B_PASSWORD = "password123"


class TestOrientationAPI:
    """Tests for GET /api/orientation/{user_id} endpoint"""
    
    def test_orientation_endpoint_exists(self):
        """Test that orientation endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_orientation_response_structure(self):
        """Test orientation returns required fields: message, action_type, cta, context"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required top-level fields
        assert data.get("success") == True, "Expected success=True"
        assert "message" in data, "Missing 'message' field"
        assert "action_type" in data, "Missing 'action_type' field"
        assert "cta" in data, "Missing 'cta' field"
        assert "context" in data, "Missing 'context' field"
        
        # Message should be a non-empty string
        assert isinstance(data["message"], str), "message should be a string"
        assert len(data["message"]) > 0, "message should not be empty"
        
        # action_type should be one of the valid types
        valid_action_types = ["post", "visibility", "re_engage", "react", "share", "verify"]
        assert data["action_type"] in valid_action_types, f"Invalid action_type: {data['action_type']}"
        
        # CTA should be a non-empty string
        assert isinstance(data["cta"], str), "cta should be a string"
        assert len(data["cta"]) > 0, "cta should not be empty"
        
    def test_orientation_context_structure(self):
        """Test orientation context contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        context = data.get("context", {})
        
        # Context should have position info
        assert "position" in context, "Missing 'position' in context"
        assert "label" in context, "Missing 'label' in context"
        assert "public_actions" in context, "Missing 'public_actions' in context"
        assert "private_actions" in context, "Missing 'private_actions' in context"
        assert "days_inactive" in context, "Missing 'days_inactive' in context"
        assert "unique_reactors" in context, "Missing 'unique_reactors' in context"
        assert "active_referrals" in context, "Missing 'active_referrals' in context"
        
        # Position should be between 0 and 1
        assert 0 <= context["position"] <= 1, f"Position {context['position']} out of range [0,1]"
        
        # Label should be valid
        valid_labels = ["Self", "Emerging", "Contributing", "Connected", "Network"]
        assert context["label"] in valid_labels, f"Invalid label: {context['label']}"
        
    def test_user_a_contributing_orientation(self):
        """Test User A (Contributing, pos=0.545) gets 'engage with more people' guidance"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        context = data.get("context", {})
        
        # User A should be Contributing
        assert context["label"] == "Contributing", f"Expected 'Contributing', got '{context['label']}'"
        
        # For Contributing users with referrals or reactors, action_type should be 'react'
        # Based on decision rules: Contributing + has referrals → "engage more" (react)
        # or Contributing + no referrals → "share to invite" (share)
        assert data["action_type"] in ["react", "share"], f"Expected 'react' or 'share', got '{data['action_type']}'"
        
        # CTA should be appropriate
        assert data["cta"] in ["View Feed", "Go to Feed", "Create Action"], f"Unexpected CTA: {data['cta']}"
        
    def test_user_b_emerging_low_reactors(self):
        """Test User B (Emerging, low reactors) gets 'Engage with others' guidance"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_B_ID}")
        assert response.status_code == 200
        data = response.json()
        context = data.get("context", {})
        
        # User B should be Emerging with low reactors
        # Decision rule: Emerging + low reactors → "Engage with others' actions" (react)
        print(f"User B context: position={context.get('position')}, label={context.get('label')}, reactors={context.get('unique_reactors')}")
        print(f"User B message: {data['message']}")
        print(f"User B action_type: {data['action_type']}")
        
        # If label is Emerging, check the decision logic
        if context["label"] == "Emerging":
            if context.get("unique_reactors", 0) < 3:
                assert data["action_type"] == "react", f"Expected 'react' for Emerging with low reactors, got '{data['action_type']}'"
                assert "View Feed" in data["cta"], f"Expected CTA with 'View Feed', got '{data['cta']}'"
            else:
                assert data["action_type"] == "post", f"Expected 'post' for Emerging with enough reactors, got '{data['action_type']}'"

    def test_nonexistent_user_returns_post_first(self):
        """Test user with no actions gets 'Post your first action' guidance"""
        # Use a random UUID that won't have any actions
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/orientation/{fake_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # New user should get "post first action" message
        assert data["action_type"] == "post", f"Expected 'post' for new user, got '{data['action_type']}'"
        assert "first" in data["message"].lower() or "begin" in data["message"].lower(), \
            f"Expected message about first action, got '{data['message']}'"
        assert data["cta"] == "Create Action", f"Expected 'Create Action' CTA, got '{data['cta']}'"
        
        # Context should show 0 actions
        context = data.get("context", {})
        assert context.get("public_actions") == 0, f"Expected 0 public_actions, got {context.get('public_actions')}"
        
    def test_orientation_action_type_values(self):
        """Test that action_type is one of the documented types"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        valid_types = ["post", "visibility", "re_engage", "react", "share", "verify"]
        assert data["action_type"] in valid_types, \
            f"action_type '{data['action_type']}' not in valid types: {valid_types}"


class TestRegressionAPIs:
    """Regression tests for existing APIs"""
    
    def test_position_api_still_works(self):
        """REGRESSION: GET /api/position/{user_id} still works"""
        response = requests.get(f"{BASE_URL}/api/position/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "position" in data
        assert "label" in data
        
    def test_trust_api_still_works(self):
        """REGRESSION: GET /api/trust/{user_id} still works"""
        response = requests.get(f"{BASE_URL}/api/trust/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "trust_score" in data
        
    def test_feed_api_still_works(self):
        """REGRESSION: GET /api/actions/feed still works"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "actions" in data
        
    def test_auth_login_works(self):
        """REGRESSION: POST /api/auth/login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": USER_A_EMAIL, "password": USER_A_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("success") == True


class TestOrientationDecisionRules:
    """Tests for specific decision rule scenarios"""
    
    def test_cta_mapping_for_post_types(self):
        """Test that post/visibility/re_engage action types map to Create Action CTA"""
        # This tests the frontend mapping logic expectation
        # If action_type is post, visibility, or re_engage -> CTA should navigate to post
        response = requests.get(f"{BASE_URL}/api/orientation/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 200
        data = response.json()
        
        if data["action_type"] in ["post", "visibility", "re_engage"]:
            # CTA should indicate creating an action
            assert "Action" in data["cta"] or "Post" in data["cta"], \
                f"For {data['action_type']}, expected CTA about action/post, got '{data['cta']}'"
                
    def test_cta_mapping_for_feed_types(self):
        """Test that react/share/verify action types map to View Feed CTA"""
        response = requests.get(f"{BASE_URL}/api/orientation/{USER_A_ID}")
        assert response.status_code == 200
        data = response.json()
        
        if data["action_type"] in ["react", "share", "verify"]:
            # CTA should indicate viewing feed
            assert "Feed" in data["cta"], \
                f"For {data['action_type']}, expected CTA with 'Feed', got '{data['cta']}'"

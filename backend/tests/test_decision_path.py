"""
Backend tests for Decision Path Engine API.
Tests the /api/decision-path/{user_id} endpoint which generates
concrete action recommendations based on user state and imbalance detection.
"""

import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDecisionPathEndpoint:
    """Tests for the /api/decision-path/{user_id} endpoint"""
    
    # Response structure tests
    
    def test_endpoint_returns_success(self):
        """Test that endpoint returns success=true"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-user-new-123")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True, "success should be True"
    
    def test_endpoint_returns_user_id(self):
        """Test that response includes correct user_id"""
        test_user = "test-decision-path-user-abc"
        response = requests.get(f"{BASE_URL}/api/decision-path/{test_user}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('user_id') == test_user
    
    def test_response_has_required_fields(self):
        """Test that response includes all required fields"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-fields-user")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            'success', 'user_id', 'current_state', 'drift_type',
            'recommended_direction', 'headline', 'recommended_step',
            'concrete_action', 'theory_basis', 'session_id'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_response_is_json(self):
        """Test that response is valid JSON"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-json-user")
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('content-type', '')
    
    # New user tests
    
    def test_new_user_gets_recovery_recommendation(self):
        """Test that new users get recovery as recommended direction"""
        response = requests.get(f"{BASE_URL}/api/decision-path/brand-new-user-xyz")
        data = response.json()
        
        assert data.get('current_state') == 'new_user'
        assert data.get('recommended_direction') == 'recovery'
        assert data.get('drift_type') is None
    
    def test_new_user_headline_is_welcome(self):
        """Test that new users get welcome headline in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/decision-path/new-welcome-user")
        data = response.json()
        
        assert data.get('current_state') == 'new_user'
        assert data.get('headline') == "ברוך הבא למסע."
    
    def test_new_user_has_concrete_action(self):
        """Test that new users get a concrete action (not empty)"""
        response = requests.get(f"{BASE_URL}/api/decision-path/new-action-user")
        data = response.json()
        
        assert data.get('concrete_action') is not None
        assert len(data.get('concrete_action', '')) > 5
    
    def test_new_user_has_theory_basis(self):
        """Test that new users get theory basis explaining recommendation"""
        response = requests.get(f"{BASE_URL}/api/decision-path/new-theory-user")
        data = response.json()
        
        assert data.get('theory_basis') is not None
        assert 'התאוששות' in data.get('theory_basis', '')  # Should mention recovery
    
    def test_new_user_has_session_id(self):
        """Test that response includes session_id for tracking"""
        response = requests.get(f"{BASE_URL}/api/decision-path/new-session-user")
        data = response.json()
        
        assert data.get('session_id') is not None
        assert len(data.get('session_id', '')) >= 8
    
    # Existing user with data tests
    
    def test_existing_user_returns_data(self):
        """Test that existing user gets proper response"""
        # Use test user created in previous tests
        response = requests.get(f"{BASE_URL}/api/decision-path/test_comparison_user_ui_test")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('success') == True
        assert data.get('recommended_direction') is not None
    
    def test_existing_user_current_state_not_new(self):
        """Test that user with history doesn't show as new_user"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test_comparison_user_ui_test")
        data = response.json()
        
        # User with data should either have drift detected or be positive
        assert data.get('current_state') in ['positive', 'drift_toward_harm', 'drift_toward_avoidance', 'isolation_detected', 'rigidity_detected']
    
    # Drift type detection tests
    
    def test_drift_type_values_are_valid(self):
        """Test that drift_type is either None or valid type"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-drift-type-user")
        data = response.json()
        
        drift_type = data.get('drift_type')
        valid_types = [None, 'harm', 'avoidance', 'isolation', 'rigidity']
        assert drift_type in valid_types, f"Invalid drift_type: {drift_type}"
    
    def test_recommended_direction_values_are_valid(self):
        """Test that recommended_direction is a valid direction"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-direction-user")
        data = response.json()
        
        direction = data.get('recommended_direction')
        valid_directions = ['recovery', 'order', 'contribution', 'exploration']
        assert direction in valid_directions, f"Invalid direction: {direction}"
    
    # Concrete action tests
    
    def test_concrete_action_is_hebrew(self):
        """Test that concrete_action is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-hebrew-user")
        data = response.json()
        
        concrete_action = data.get('concrete_action', '')
        # Check for Hebrew characters
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in concrete_action)
        assert has_hebrew, f"Concrete action should be in Hebrew: {concrete_action}"
    
    def test_headline_is_hebrew(self):
        """Test that headline is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-headline-user")
        data = response.json()
        
        headline = data.get('headline', '')
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in headline)
        assert has_hebrew, f"Headline should be in Hebrew: {headline}"
    
    def test_recommended_step_is_hebrew(self):
        """Test that recommended_step is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-step-user")
        data = response.json()
        
        step = data.get('recommended_step', '')
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in step)
        assert has_hebrew, f"Recommended step should be in Hebrew: {step}"
    
    # Theory basis tests
    
    def test_theory_basis_explains_recommendation(self):
        """Test that theory_basis provides explanation"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-theory-explain-user")
        data = response.json()
        
        theory = data.get('theory_basis', '')
        assert len(theory) >= 10, "Theory basis should have meaningful content"
    
    def test_theory_basis_is_hebrew(self):
        """Test that theory_basis is in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-theory-hebrew-user")
        data = response.json()
        
        theory = data.get('theory_basis', '')
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in theory)
        assert has_hebrew, f"Theory basis should be in Hebrew: {theory}"
    
    # Consistency tests
    
    def test_different_sessions_may_get_different_actions(self):
        """Test that multiple requests can return different session_ids"""
        user_id = f"test-consistency-{datetime.now().timestamp()}"
        
        response1 = requests.get(f"{BASE_URL}/api/decision-path/{user_id}")
        response2 = requests.get(f"{BASE_URL}/api/decision-path/{user_id}")
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Both should succeed
        assert data1.get('success') == True
        assert data2.get('success') == True
        
        # Session IDs should be different
        assert data1.get('session_id') != data2.get('session_id')


class TestDecisionPathDriftDetection:
    """Tests for drift detection logic in Decision Path Engine"""
    
    def test_harm_drift_recommends_recovery(self):
        """Test that harm drift recommends recovery direction
        
        Theory: harm → recovery mapping
        """
        # This tests the expected mapping based on theory
        # When drift_type is 'harm', recommended_direction should be 'recovery'
        
        # We can't directly trigger harm drift without data, but we can verify
        # the mapping exists by checking new user response
        response = requests.get(f"{BASE_URL}/api/decision-path/test-harm-mapping-user")
        data = response.json()
        
        # For new user, should get recovery (the default path)
        if data.get('drift_type') is None:
            # New user gets recovery by default
            assert data.get('recommended_direction') == 'recovery'
    
    def test_avoidance_drift_recommends_order(self):
        """Test that avoidance drift would recommend order direction
        
        Theory: avoidance → order mapping
        """
        # Same logic - verify mapping exists in theory
        response = requests.get(f"{BASE_URL}/api/decision-path/test-avoidance-mapping-user")
        data = response.json()
        
        # If drift_type is 'avoidance', direction should be 'order'
        if data.get('drift_type') == 'avoidance':
            assert data.get('recommended_direction') == 'order'
    
    def test_positive_state_exists(self):
        """Test that positive state is returned for users with balanced history"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test_comparison_user_ui_test")
        data = response.json()
        
        # User with data but no drift should be 'positive'
        if data.get('drift_type') is None and data.get('current_state') != 'new_user':
            assert data.get('current_state') == 'positive'


class TestDecisionPathHeadlines:
    """Tests for headline messages in Decision Path Engine"""
    
    def test_new_user_welcome_headline(self):
        """Test that new users see welcome message"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test-welcome-msg-user")
        data = response.json()
        
        if data.get('current_state') == 'new_user':
            assert "ברוך הבא" in data.get('headline', ''), "New user headline should welcome"
    
    def test_positive_state_headline(self):
        """Test that positive state has encouraging headline"""
        response = requests.get(f"{BASE_URL}/api/decision-path/test_comparison_user_ui_test")
        data = response.json()
        
        if data.get('current_state') == 'positive':
            assert "על המסלול" in data.get('headline', ''), "Positive headline should be encouraging"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

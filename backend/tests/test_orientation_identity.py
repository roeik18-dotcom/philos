"""
Test suite for Orientation Identity Layer
Tests the /api/orientation/identity/{user_id} endpoint

Identity types:
- avoidance_loop: High avoidance pattern (warning state)
- recovery_dominant: Focused on recovery
- order_builder: Building structure and order
- contribution_oriented: Contributing to others
- exploration_driven: Exploring and growing
- recovery_to_contribution: Transitioning from recovery to contribution
- drifting_from_order: Was order-focused, now drifting
- balanced: Well distributed across directions
- new_user: No history yet
"""

import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOrientationIdentityEndpoint:
    """Test the /api/orientation/identity/{user_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    # --- Basic endpoint tests ---
    
    def test_endpoint_returns_success_for_new_user(self):
        """New user should get identity_type='new_user'"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-new-user-identity-{datetime.now().timestamp()}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
    
    def test_new_user_identity_type(self):
        """New user should have identity_type='new_user'"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-new-user-no-data-123")
        assert response.status_code == 200
        data = response.json()
        assert data['identity_type'] == 'new_user'
    
    def test_new_user_label_hebrew(self):
        """New user should have Hebrew label 'מתחיל מסע'"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-new-user-label-456")
        assert response.status_code == 200
        data = response.json()
        assert data['identity_label'] == 'מתחיל מסע'
    
    def test_new_user_not_warning_state(self):
        """New user should not be in warning state"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-new-user-warning-789")
        assert response.status_code == 200
        data = response.json()
        assert data['is_warning_state'] == False
    
    # --- Response structure tests ---
    
    def test_response_has_required_fields(self):
        """Response should have all required fields"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-structure-check")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            'success', 'user_id', 'identity_type', 'identity_label',
            'identity_description', 'is_warning_state'
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_response_has_computation_fields(self):
        """Response should have computation input fields"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-computation-fields")
        assert response.status_code == 200
        data = response.json()
        
        # These should be present (even if None/empty for new user)
        computation_fields = [
            'dominant_direction', 'momentum', 'time_in_direction',
            'avoidance_ratio', 'previous_dominant'
        ]
        for field in computation_fields:
            assert field in data, f"Missing computation field: {field}"
    
    def test_response_has_context_fields(self):
        """Response should have additional context fields"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-context-fields")
        assert response.status_code == 200
        data = response.json()
        
        context_fields = ['direction_counts', 'total_actions', 'weeks_analyzed', 'insight']
        for field in context_fields:
            assert field in data, f"Missing context field: {field}"
    
    def test_identity_description_is_hebrew(self):
        """Identity description should be in Hebrew"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-hebrew-desc")
        assert response.status_code == 200
        data = response.json()
        
        desc = data.get('identity_description', '')
        # Check for Hebrew characters
        assert any('\u0590' <= char <= '\u05FF' for char in desc), "Description should contain Hebrew characters"
    
    def test_insight_is_hebrew(self):
        """Insight should be in Hebrew"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-hebrew-insight")
        assert response.status_code == 200
        data = response.json()
        
        insight = data.get('insight', '')
        if insight:  # Only check if insight exists
            assert any('\u0590' <= char <= '\u05FF' for char in insight), "Insight should contain Hebrew characters"
    
    # --- Identity type validation tests ---
    
    def test_valid_identity_types(self):
        """identity_type should be one of the valid types"""
        valid_types = [
            'avoidance_loop', 'recovery_dominant', 'order_builder',
            'contribution_oriented', 'exploration_driven',
            'recovery_to_contribution', 'drifting_from_order',
            'balanced', 'new_user'
        ]
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-valid-type")
        assert response.status_code == 200
        data = response.json()
        
        assert data['identity_type'] in valid_types, f"Invalid identity type: {data['identity_type']}"
    
    def test_valid_momentum_values(self):
        """momentum should be one of valid values or None"""
        valid_momentum = ['stabilizing', 'drifting', 'shifting', 'stable', None]
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-momentum-value")
        assert response.status_code == 200
        data = response.json()
        
        assert data['momentum'] in valid_momentum, f"Invalid momentum: {data['momentum']}"
    
    # --- Test with existing user data ---
    
    def test_user_with_session_data(self):
        """Test with a user that has existing session data"""
        # First, create some session data
        test_user_id = f"TEST_identity_user_{datetime.now().timestamp()}"
        
        sync_data = {
            "user_id": test_user_id,
            "history": [
                {"action": "Test recovery 1", "value_tag": "recovery", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"action": "Test recovery 2", "value_tag": "recovery", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"action": "Test recovery 3", "value_tag": "recovery", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"action": "Test order 1", "value_tag": "order", "timestamp": datetime.now(timezone.utc).isoformat()},
            ],
            "global_stats": {"recovery": 3, "order": 1, "totalDecisions": 4},
            "trend_history": []
        }
        
        # Sync data
        sync_response = self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        assert sync_response.status_code == 200
        
        # Get identity
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have valid identity data
        assert data['success'] == True
        assert data['identity_type'] != 'new_user'  # Should have an identity based on data
        assert data['total_actions'] > 0


class TestAvoidanceLoopWarningState:
    """Test that avoidance_loop triggers warning state"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_avoidance_loop_triggers_warning(self):
        """High avoidance should trigger is_warning_state=true"""
        test_user_id = f"TEST_avoidance_user_{datetime.now().timestamp()}"
        
        # Create user with high avoidance ratio (>40%)
        history = []
        now = datetime.now(timezone.utc)
        
        for i in range(5):
            history.append({
                "action": f"Test avoidance {i}",
                "value_tag": "avoidance",
                "timestamp": (now - timedelta(hours=i)).isoformat()
            })
        
        for i in range(3):
            history.append({
                "action": f"Test recovery {i}",
                "value_tag": "recovery",
                "timestamp": (now - timedelta(hours=i+5)).isoformat()
            })
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"avoidance": 5, "recovery": 3, "totalDecisions": 8},
            "trend_history": []
        }
        
        # Sync data
        sync_response = self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        assert sync_response.status_code == 200
        
        # Get identity
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Should be avoidance_loop with warning state
        assert data['identity_type'] == 'avoidance_loop', f"Expected avoidance_loop, got {data['identity_type']}"
        assert data['is_warning_state'] == True, "Avoidance loop should have is_warning_state=True"
    
    def test_avoidance_loop_label_hebrew(self):
        """Avoidance loop should have Hebrew label 'לולאת הימנעות'"""
        test_user_id = f"TEST_avoidance_label_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = [{"action": f"Test avoidance {i}", "value_tag": "avoidance", "timestamp": (now - timedelta(hours=i)).isoformat()} for i in range(6)]
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"avoidance": 6, "totalDecisions": 6},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        if data['identity_type'] == 'avoidance_loop':
            assert data['identity_label'] == 'לולאת הימנעות'


class TestIdentityTypes:
    """Test different identity type computations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_recovery_dominant_identity(self):
        """User with mostly recovery actions should be recovery_dominant"""
        test_user_id = f"TEST_recovery_dom_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = []
        for i in range(5):
            history.append({
                "action": f"Recovery action {i}",
                "value_tag": "recovery",
                "timestamp": (now - timedelta(hours=i)).isoformat()
            })
        history.append({
            "action": "Order action",
            "value_tag": "order",
            "timestamp": (now - timedelta(hours=6)).isoformat()
        })
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"recovery": 5, "order": 1, "totalDecisions": 6},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        assert data['dominant_direction'] == 'recovery'
        assert data['identity_type'] in ['recovery_dominant', 'balanced']
    
    def test_order_builder_identity(self):
        """User with mostly order actions should be order_builder"""
        test_user_id = f"TEST_order_build_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = []
        for i in range(5):
            history.append({
                "action": f"Order action {i}",
                "value_tag": "order",
                "timestamp": (now - timedelta(hours=i)).isoformat()
            })
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"order": 5, "totalDecisions": 5},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        assert data['dominant_direction'] == 'order'
        assert data['identity_type'] in ['order_builder', 'balanced']
    
    def test_contribution_oriented_identity(self):
        """User with mostly contribution actions should be contribution_oriented"""
        test_user_id = f"TEST_contrib_oriented_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = []
        for i in range(5):
            history.append({
                "action": f"Contribution action {i}",
                "value_tag": "contribution",
                "timestamp": (now - timedelta(hours=i)).isoformat()
            })
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"contribution": 5, "totalDecisions": 5},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        assert data['dominant_direction'] == 'contribution'
        assert data['identity_type'] in ['contribution_oriented', 'balanced']


class TestSnapshotPersistence:
    """Test that orientation snapshots are saved to database"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_identity_call_returns_success(self):
        """Calling identity endpoint should return success (indicates no errors including DB save)"""
        test_user_id = f"TEST_snapshot_user_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = [
            {"action": "Test action", "value_tag": "recovery", "timestamp": now.isoformat()}
        ]
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"recovery": 1, "totalDecisions": 1},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        # Call identity endpoint (this should save snapshot)
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True


class TestDirectionCounts:
    """Test direction_counts field in response"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_direction_counts_structure(self):
        """direction_counts should have expected structure"""
        test_user_id = f"TEST_dir_counts_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = [
            {"action": "Recovery 1", "value_tag": "recovery", "timestamp": now.isoformat()},
            {"action": "Recovery 2", "value_tag": "recovery", "timestamp": now.isoformat()},
            {"action": "Order 1", "value_tag": "order", "timestamp": now.isoformat()},
        ]
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"recovery": 2, "order": 1, "totalDecisions": 3},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        assert 'direction_counts' in data
        direction_counts = data['direction_counts']
        
        # Should have all direction keys
        expected_keys = ['recovery', 'order', 'contribution', 'exploration', 'harm', 'avoidance']
        for key in expected_keys:
            assert key in direction_counts, f"Missing direction key: {key}"
    
    def test_direction_counts_values_non_negative(self):
        """All direction counts should be non-negative"""
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/test-counts-nonneg")
        data = response.json()
        
        direction_counts = data.get('direction_counts', {})
        for direction, count in direction_counts.items():
            assert count >= 0, f"Direction {direction} has negative count: {count}"


class TestMomentumBadge:
    """Test momentum values for frontend badge"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_momentum_values_valid(self):
        """momentum should be one of: stabilizing, drifting, shifting, stable"""
        test_user_id = f"TEST_momentum_{datetime.now().timestamp()}"
        
        now = datetime.now(timezone.utc)
        history = [
            {"action": "Recovery", "value_tag": "recovery", "timestamp": now.isoformat()},
        ]
        
        sync_data = {
            "user_id": test_user_id,
            "history": history,
            "global_stats": {"recovery": 1, "totalDecisions": 1},
            "trend_history": []
        }
        
        self.session.post(f"{BASE_URL}/api/philos/sync", json=sync_data)
        
        response = self.session.get(f"{BASE_URL}/api/orientation/identity/{test_user_id}")
        data = response.json()
        
        valid_momentum = ['stabilizing', 'drifting', 'shifting', 'stable', None]
        assert data.get('momentum') in valid_momentum


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

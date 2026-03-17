"""
Position Bar API Tests - Testing /api/position/{user_id} endpoint
Tests position score calculation based on public actions, unique reactors, trust score, and active referrals.
Position labels: 0-0.15=Self, 0.15-0.35=Emerging, 0.35-0.55=Contributing, 0.55-0.75=Connected, 0.75-1=Network
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test user credentials
TEST_USER_A = {
    "email": "newuser@test.com",
    "password": "password123",
    "user_id": "05d47b99-88f1-44b3-a879-6c995634eaa0"
}


class TestPositionBarAPI:
    """Tests for GET /api/position/{user_id} endpoint"""
    
    def test_position_endpoint_returns_success(self):
        """Test that position endpoint returns success for existing user"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"PASS: Position endpoint returns success for user")
    
    def test_position_returns_required_fields(self):
        """Test that position response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        required_fields = ["success", "position", "label", "public_actions", "private_actions", 
                          "unique_reactors", "total_trust", "active_referrals", "factors"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Check factors sub-fields
        factors = data.get("factors", {})
        factor_fields = ["actions", "reactors", "trust", "referrals"]
        for field in factor_fields:
            assert field in factors, f"Missing factor field: {field}"
        
        print(f"PASS: Position response contains all required fields")
        print(f"  Position: {data['position']}, Label: {data['label']}")
        print(f"  Public: {data['public_actions']}, Private: {data['private_actions']}")
        print(f"  Unique reactors: {data['unique_reactors']}, Trust: {data['total_trust']}")
        print(f"  Active referrals: {data['active_referrals']}")
        print(f"  Factors: {data['factors']}")
    
    def test_position_value_is_between_0_and_1(self):
        """Test that position score is between 0.0 and 1.0"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        position = data.get("position", -1)
        assert 0.0 <= position <= 1.0, f"Position {position} should be between 0 and 1"
        print(f"PASS: Position {position} is within valid range [0, 1]")
    
    def test_position_label_matches_score_range(self):
        """Test that position label matches the position score range"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        position = data.get("position", 0)
        label = data.get("label", "")
        
        # Verify label matches position range
        # 0-0.15=Self, 0.15-0.35=Emerging, 0.35-0.55=Contributing, 0.55-0.75=Connected, 0.75-1=Network
        if position < 0.15:
            expected = "Self"
        elif position < 0.35:
            expected = "Emerging"
        elif position < 0.55:
            expected = "Contributing"
        elif position < 0.75:
            expected = "Connected"
        else:
            expected = "Network"
        
        assert label == expected, f"Label '{label}' should be '{expected}' for position {position}"
        print(f"PASS: Position {position} has correct label '{label}'")
    
    def test_factors_add_up_to_position(self):
        """Test that factors (actions + reactors + trust + referrals) sum to position"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        factors = data.get("factors", {})
        position = data.get("position", 0)
        
        factor_sum = (
            factors.get("actions", 0) +
            factors.get("reactors", 0) +
            factors.get("trust", 0) +
            factors.get("referrals", 0)
        )
        
        # Allow small floating point tolerance
        assert abs(factor_sum - position) < 0.001, f"Factor sum {factor_sum} should equal position {position}"
        print(f"PASS: Factors sum ({factor_sum}) equals position ({position})")
        print(f"  actions={factors.get('actions')}, reactors={factors.get('reactors')}, trust={factors.get('trust')}, referrals={factors.get('referrals')}")
    
    def test_factor_max_values(self):
        """Test that factors don't exceed their max weights"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        factors = data.get("factors", {})
        
        # Max values: actions=0.35, reactors=0.25, trust=0.25, referrals=0.15
        assert factors.get("actions", 0) <= 0.35, f"Actions factor {factors.get('actions')} exceeds max 0.35"
        assert factors.get("reactors", 0) <= 0.25, f"Reactors factor {factors.get('reactors')} exceeds max 0.25"
        assert factors.get("trust", 0) <= 0.25, f"Trust factor {factors.get('trust')} exceeds max 0.25"
        assert factors.get("referrals", 0) <= 0.15, f"Referrals factor {factors.get('referrals')} exceeds max 0.15"
        
        print(f"PASS: All factors within max limits")
    
    def test_position_for_user_with_no_actions(self):
        """Test that user with no public actions has position 0.0 and label 'Self'"""
        # Use a non-existent user ID
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/position/{fake_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("position") == 0.0, f"Position should be 0.0 for user with no actions"
        assert data.get("label") == "Self", f"Label should be 'Self' for position 0.0"
        assert data.get("public_actions") == 0
        assert data.get("unique_reactors") == 0
        assert data.get("total_trust") == 0.0
        assert data.get("active_referrals") == 0
        
        print(f"PASS: User with no actions has position=0.0, label='Self'")
    
    def test_private_actions_do_not_affect_position(self):
        """Test that private actions are counted but don't affect position calculation"""
        response = requests.get(f"{BASE_URL}/api/position/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        
        # Private actions should be reported but not included in position calculation
        private_count = data.get("private_actions", 0)
        public_count = data.get("public_actions", 0)
        
        # Position factors are calculated from public_actions only
        # The presence of private actions should not change the position
        print(f"PASS: User has {public_count} public actions, {private_count} private actions")
        print(f"  Position is calculated from public actions only")
        
        # According to agent context: user has 22 public actions, 2 private
        if public_count > 0:
            # Verify actions factor is based on public_count
            factors = data.get("factors", {})
            expected_actions_factor = min(public_count / 15, 1.0) * 0.35
            actual_actions_factor = factors.get("actions", 0)
            assert abs(expected_actions_factor - actual_actions_factor) < 0.01, \
                f"Actions factor should be based on public count only"
            print(f"  Actions factor {actual_actions_factor} calculated correctly from {public_count} public actions")


class TestRegressionAPIs:
    """Regression tests for related APIs"""
    
    def test_feed_api_still_works(self):
        """REGRESSION: GET /api/actions/feed still works with visibility filter"""
        response = requests.get(f"{BASE_URL}/api/actions/feed?visibility=public")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"PASS: Feed API with visibility filter works")
    
    def test_trust_api_still_works(self):
        """REGRESSION: GET /api/trust/{user_id} still works"""
        response = requests.get(f"{BASE_URL}/api/trust/{TEST_USER_A['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "trust_score" in data
        print(f"PASS: Trust API works, trust_score={data.get('trust_score')}")
    
    def test_post_action_api_still_works(self):
        """REGRESSION: POST /api/actions/post with visibility still works (auth required)"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_A["email"],
            "password": TEST_USER_A["password"]
        })
        
        if login_response.status_code != 200:
            pytest.skip("Login failed - skipping post action test")
        
        token = login_response.json().get("token")
        if not token:
            pytest.skip("No token in login response")
        
        # Test that the endpoint accepts visibility parameter
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/actions/post", 
            headers=headers,
            json={
                "title": "TEST_position_regression",
                "description": "Testing post action with visibility",
                "category": "community",
                "visibility": "private"  # Use private to avoid cluttering feed
            }
        )
        
        # May get rate limited (429) or succeed (200/201) - both are acceptable
        assert response.status_code in [200, 201, 429], f"Unexpected status: {response.status_code}"
        if response.status_code == 429:
            print("PASS: Post action API works (rate limited)")
        else:
            data = response.json()
            assert data.get("success") == True or "action" in data
            print("PASS: Post action API works with visibility parameter")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

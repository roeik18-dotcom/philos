"""
Backend API tests for Reactions System
Testing: React endpoint, user_reacted flags in feed, trust_signal calculation, profile trust_score aggregation
Trust weights: Support=1, Useful=2, Verified=5
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-status.preview.emergentagent.com')


class TestReactionSystem:
    """Reaction endpoint tests - POST /api/actions/{id}/react"""
    
    @pytest.fixture
    def auth_token_and_user(self):
        """Get auth token and user ID from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        data = response.json()
        return {"token": data["token"], "user_id": data["user"]["id"]}
    
    @pytest.fixture
    def action_id(self):
        """Get first action ID from feed"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        data = response.json()
        if data["actions"]:
            return data["actions"][0]["id"]
        return None
    
    def test_react_requires_auth(self, action_id):
        """Test that reacting requires authentication"""
        if not action_id:
            pytest.skip("No actions in feed")
        response = requests.post(f"{BASE_URL}/api/actions/{action_id}/react", json={
            "reaction_type": "support"
        })
        # Should return 401 without auth
        assert response.status_code == 401
        print(f"PASS: React endpoint requires auth (401)")
    
    def test_react_invalid_type(self, auth_token_and_user, action_id):
        """Test that invalid reaction type returns 400"""
        if not action_id:
            pytest.skip("No actions in feed")
        response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "invalid_type"},
            headers={"Authorization": f"Bearer {auth_token_and_user['token']}"}
        )
        assert response.status_code == 400
        print(f"PASS: Invalid reaction type returns 400")
    
    def test_react_support_toggle(self, auth_token_and_user, action_id):
        """Test toggling support reaction on and off"""
        if not action_id:
            pytest.skip("No actions in feed")
        token = auth_token_and_user['token']
        
        # First reaction - should add
        response1 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("success") == True
        assert "trust_signal" in data1
        first_trust = data1["trust_signal"]
        print(f"First react: trust_signal={first_trust}, added={data1.get('added')}")
        
        # Second reaction - should toggle off
        response2 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("success") == True
        second_trust = data2["trust_signal"]
        print(f"Second react (toggle): trust_signal={second_trust}, added={data2.get('added')}")
        
        # Trust should differ by 1 (support weight)
        assert abs(first_trust - second_trust) == 1
        print(f"PASS: Support reaction toggles correctly, trust_signal changes by weight 1")
    
    def test_react_useful_weight(self, auth_token_and_user, action_id):
        """Test useful reaction has weight of 2"""
        if not action_id:
            pytest.skip("No actions in feed")
        token = auth_token_and_user['token']
        
        # Add useful reaction
        response1 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "useful"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        first_trust = data1["trust_signal"]
        
        # Toggle off
        response2 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "useful"},
            headers={"Authorization": f"Bearer {token}"}
        )
        data2 = response2.json()
        second_trust = data2["trust_signal"]
        
        # Useful weight = 2
        assert abs(first_trust - second_trust) == 2
        print(f"PASS: Useful reaction weight is 2 (trust_signal change: {abs(first_trust - second_trust)})")
    
    def test_react_verified_weight(self, auth_token_and_user, action_id):
        """Test verified reaction has weight of 5"""
        if not action_id:
            pytest.skip("No actions in feed")
        token = auth_token_and_user['token']
        
        # Add verified reaction
        response1 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "verified"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        first_trust = data1["trust_signal"]
        
        # Toggle off
        response2 = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "verified"},
            headers={"Authorization": f"Bearer {token}"}
        )
        data2 = response2.json()
        second_trust = data2["trust_signal"]
        
        # Verified weight = 5
        assert abs(first_trust - second_trust) == 5
        print(f"PASS: Verified reaction weight is 5 (trust_signal change: {abs(first_trust - second_trust)})")


class TestFeedUserReacted:
    """Test feed endpoint returns user_reacted flags with viewer_id"""
    
    @pytest.fixture
    def user_data(self):
        """Get user ID and token from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        data = response.json()
        return {"token": data["token"], "user_id": data["user"]["id"]}
    
    def test_feed_without_viewer_id(self):
        """Test feed without viewer_id returns user_reacted as all false"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200
        data = response.json()
        
        if data["actions"]:
            action = data["actions"][0]
            assert "user_reacted" in action
            # Without viewer_id, all should be False
            assert action["user_reacted"]["support"] == False
            assert action["user_reacted"]["useful"] == False
            assert action["user_reacted"]["verified"] == False
        print(f"PASS: Feed without viewer_id returns user_reacted all False")
    
    def test_feed_with_viewer_id(self, user_data):
        """Test feed with viewer_id returns correct user_reacted flags"""
        user_id = user_data["user_id"]
        
        response = requests.get(f"{BASE_URL}/api/actions/feed?viewer_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        
        if data["actions"]:
            action = data["actions"][0]
            assert "user_reacted" in action
            assert "support" in action["user_reacted"]
            assert "useful" in action["user_reacted"]
            assert "verified" in action["user_reacted"]
            # Values should be boolean
            assert isinstance(action["user_reacted"]["support"], bool)
            assert isinstance(action["user_reacted"]["useful"], bool)
            assert isinstance(action["user_reacted"]["verified"], bool)
        print(f"PASS: Feed with viewer_id returns user_reacted flags correctly")
    
    def test_feed_action_has_reactions(self):
        """Test feed actions have reactions counts"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        data = response.json()
        
        if data["actions"]:
            action = data["actions"][0]
            assert "reactions" in action
            assert "support" in action["reactions"]
            assert "useful" in action["reactions"]
            assert "verified" in action["reactions"]
            # Values should be numbers
            assert isinstance(action["reactions"]["support"], int)
            assert isinstance(action["reactions"]["useful"], int)
            assert isinstance(action["reactions"]["verified"], int)
        print(f"PASS: Feed actions have reactions counts structure")
    
    def test_feed_action_has_trust_signal(self):
        """Test feed actions have trust_signal field"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        data = response.json()
        
        if data["actions"]:
            action = data["actions"][0]
            assert "trust_signal" in action
            assert isinstance(action["trust_signal"], (int, float))
        print(f"PASS: Feed actions have trust_signal field")


class TestProfileTrustScore:
    """Test profile endpoint returns trust_score aggregated from actions"""
    
    @pytest.fixture
    def user_id(self):
        """Get user ID from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        return response.json()["user"]["id"]
    
    def test_profile_has_trust_score(self, user_id):
        """Test profile returns trust_score field"""
        response = requests.get(f"{BASE_URL}/api/impact/profile/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        profile = data["profile"]
        assert "trust_score" in profile
        assert isinstance(profile["trust_score"], (int, float))
        print(f"PASS: Profile has trust_score field: {profile['trust_score']}")
    
    def test_profile_trust_score_value(self, user_id):
        """Test profile trust_score is a reasonable value"""
        response = requests.get(f"{BASE_URL}/api/impact/profile/{user_id}")
        data = response.json()
        profile = data["profile"]
        
        # Trust score should be >= 0
        assert profile["trust_score"] >= 0
        print(f"PASS: Profile trust_score is valid: {profile['trust_score']}")


class TestReactAndVerifyFlow:
    """E2E test: React to action and verify counts + trust_signal update"""
    
    def test_react_and_verify_count_update(self):
        """Test full flow: react, verify count updated, verify trust_signal"""
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        token = login_data["token"]
        user_id = login_data["user"]["id"]
        
        # Get first action
        feed_response = requests.get(f"{BASE_URL}/api/actions/feed?viewer_id={user_id}")
        assert feed_response.status_code == 200
        actions = feed_response.json()["actions"]
        if not actions:
            pytest.skip("No actions in feed")
        
        action = actions[0]
        action_id = action["id"]
        initial_support = action["reactions"]["support"]
        initial_trust = action["trust_signal"]
        initial_user_reacted = action["user_reacted"]["support"]
        
        print(f"Initial state: support={initial_support}, trust={initial_trust}, user_reacted={initial_user_reacted}")
        
        # React with support
        react_response = requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert react_response.status_code == 200
        react_data = react_response.json()
        
        # Verify the feed reflects the change
        feed_response2 = requests.get(f"{BASE_URL}/api/actions/feed?viewer_id={user_id}")
        updated_actions = feed_response2.json()["actions"]
        updated_action = next((a for a in updated_actions if a["id"] == action_id), None)
        
        if updated_action:
            new_support = updated_action["reactions"]["support"]
            new_trust = updated_action["trust_signal"]
            new_user_reacted = updated_action["user_reacted"]["support"]
            
            print(f"After react: support={new_support}, trust={new_trust}, user_reacted={new_user_reacted}")
            
            # If user was not reacted before, count should increase
            # If user was reacted before, count should decrease (toggle)
            if initial_user_reacted:
                # Was toggled off
                assert new_support == initial_support - 1
                assert new_trust == initial_trust - 1
            else:
                # Was toggled on
                assert new_support == initial_support + 1
                assert new_trust == initial_trust + 1
            
            # User reacted should be toggled
            assert new_user_reacted != initial_user_reacted
        
        print(f"PASS: React and verify flow works correctly")
        
        # Toggle back to restore original state
        requests.post(
            f"{BASE_URL}/api/actions/{action_id}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {token}"}
        )


class TestInvalidActionReact:
    """Test reacting to invalid action IDs"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        return response.json()["token"]
    
    def test_react_to_invalid_action_id(self, auth_token):
        """Test reacting to invalid action ID returns 404 or 400"""
        response = requests.post(
            f"{BASE_URL}/api/actions/invalid_id_12345/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 400 (invalid ObjectId) or 404 (not found)
        assert response.status_code in [400, 404]
        print(f"PASS: Invalid action ID returns {response.status_code}")
    
    def test_react_to_nonexistent_action(self, auth_token):
        """Test reacting to valid ObjectId format but nonexistent action"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format
        response = requests.post(
            f"{BASE_URL}/api/actions/{fake_id}/react",
            json={"reaction_type": "support"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print(f"PASS: Nonexistent action returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Test Decision Replay Feature APIs
- POST /api/memory/replay - Save replay metadata
- GET /api/memory/replays/{user_id} - Get replay history
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestDecisionReplayAPIs:
    """Test Decision Replay backend endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Generate unique test user ID for each test"""
        self.test_user_id = f"TEST_replay_user_{uuid.uuid4().hex[:8]}"
    
    def test_health_check(self):
        """Test that the API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"API not accessible: {response.status_code}"
        print("✓ API health check passed")
    
    def test_save_replay_metadata(self):
        """Test POST /api/memory/replay - Save replay metadata"""
        replay_data = {
            "user_id": self.test_user_id,
            "replay_of_decision_id": f"dec_{uuid.uuid4().hex[:12]}",
            "original_value_tag": "recovery",
            "alternative_path_id": 1,
            "alternative_path_type": "contribution",
            "predicted_metrics": {
                "orderDrift": 5,
                "collectiveDrift": 15,
                "harmPressure": -15,
                "recoveryStability": 10,
                "predictedOrder": 10,
                "predictedCollective": 20,
                "predictedBalance": 70,
                "balanceDiff": 5
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/replay",
            json=replay_data
        )
        
        assert response.status_code == 200, f"Save replay failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Response should indicate success: {data}"
        assert "id" in data, "Response should contain replay ID"
        assert "timestamp" in data, "Response should contain timestamp"
        
        print(f"✓ Save replay metadata passed - ID: {data['id']}")
        return data["id"]
    
    def test_save_multiple_replays(self):
        """Test saving multiple replay records for same user"""
        replays_created = []
        
        for i in range(3):
            path_types = ["contribution", "order", "recovery"]
            original_tags = ["harm", "avoidance", "recovery"]
            
            replay_data = {
                "user_id": self.test_user_id,
                "replay_of_decision_id": f"dec_{uuid.uuid4().hex[:12]}",
                "original_value_tag": original_tags[i],
                "alternative_path_id": i + 1,
                "alternative_path_type": path_types[i],
                "predicted_metrics": {
                    "orderDrift": 5 * (i + 1),
                    "collectiveDrift": 10 * (i + 1),
                    "harmPressure": -10,
                    "recoveryStability": 15,
                    "predictedOrder": 20,
                    "predictedCollective": 25,
                    "predictedBalance": 55,
                    "balanceDiff": 10
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/memory/replay",
                json=replay_data
            )
            
            assert response.status_code == 200, f"Save replay {i+1} failed: {response.text}"
            data = response.json()
            assert data.get("success") == True
            replays_created.append(data["id"])
        
        print(f"✓ Created {len(replays_created)} replay records")
        return replays_created
    
    def test_get_replay_history(self):
        """Test GET /api/memory/replays/{user_id} - Get replay history"""
        # First create some replays
        self.test_save_multiple_replays()
        
        # Then fetch replay history
        response = requests.get(
            f"{BASE_URL}/api/memory/replays/{self.test_user_id}"
        )
        
        assert response.status_code == 200, f"Get replay history failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "replays" in data, "Response should contain replays array"
        assert "total_replays" in data, "Response should contain total_replays count"
        assert "pattern_counts" in data, "Response should contain pattern_counts"
        
        # Verify replays are returned
        replays = data["replays"]
        assert len(replays) >= 3, f"Expected at least 3 replays, got {len(replays)}"
        
        # Verify replay structure
        first_replay = replays[0]
        assert "user_id" in first_replay, "Replay should have user_id"
        assert "replay_of_decision_id" in first_replay, "Replay should have decision_id"
        assert "original_value_tag" in first_replay, "Replay should have original_value_tag"
        assert "alternative_path_type" in first_replay, "Replay should have alternative_path_type"
        assert "predicted_metrics" in first_replay, "Replay should have predicted_metrics"
        
        # Verify pattern_counts aggregation
        pattern_counts = data["pattern_counts"]
        assert isinstance(pattern_counts, dict), "pattern_counts should be a dict"
        
        print(f"✓ Get replay history passed - {len(replays)} replays, patterns: {pattern_counts}")
    
    def test_get_replay_history_empty_user(self):
        """Test GET /api/memory/replays/{user_id} for user with no replays"""
        new_user_id = f"TEST_empty_user_{uuid.uuid4().hex[:8]}"
        
        response = requests.get(
            f"{BASE_URL}/api/memory/replays/{new_user_id}"
        )
        
        assert response.status_code == 200, f"Get empty history failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("replays") == [], "Empty user should have empty replays"
        assert data.get("total_replays") == 0, "Empty user should have 0 total replays"
        
        print("✓ Get empty replay history passed")
    
    def test_save_replay_with_timestamp(self):
        """Test saving replay with custom timestamp"""
        custom_timestamp = "2025-01-15T10:30:00.000Z"
        
        replay_data = {
            "user_id": self.test_user_id,
            "replay_of_decision_id": f"dec_{uuid.uuid4().hex[:12]}",
            "original_value_tag": "harm",
            "alternative_path_id": 2,
            "alternative_path_type": "recovery",
            "predicted_metrics": {
                "orderDrift": -5,
                "collectiveDrift": 0,
                "harmPressure": -20,
                "recoveryStability": 20
            },
            "timestamp": custom_timestamp
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/replay",
            json=replay_data
        )
        
        assert response.status_code == 200, f"Save replay with timestamp failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Save replay with custom timestamp passed")
    
    def test_replay_limit_parameter(self):
        """Test GET /api/memory/replays/{user_id} with limit parameter"""
        # First ensure we have some replays
        self.test_save_multiple_replays()
        
        # Test with limit=1
        response = requests.get(
            f"{BASE_URL}/api/memory/replays/{self.test_user_id}?limit=1"
        )
        
        assert response.status_code == 200, f"Get with limit failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        # Note: total_replays reflects how many were returned, not total in DB
        
        print("✓ Replay limit parameter test passed")


class TestAuthAPIs:
    """Test authentication endpoints used before decision replay"""
    
    def test_login_api(self):
        """Test POST /api/auth/login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "newuser@test.com",
                "password": "password123"
            }
        )
        
        # Either success (200) or user doesn't exist yet
        assert response.status_code == 200, f"Login endpoint failed: {response.status_code}"
        
        data = response.json()
        # If user exists, should have success=True, else success=False with message
        if data.get("success"):
            assert "user" in data, "Successful login should return user"
            assert "token" in data, "Successful login should return token"
            print(f"✓ Login passed for existing user: {data['user']['email']}")
        else:
            assert "message" in data, "Failed login should have message"
            print(f"✓ Login endpoint works - User doesn't exist: {data['message']}")
    
    def test_register_api(self):
        """Test POST /api/auth/register"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "password123"
            }
        )
        
        assert response.status_code == 200, f"Register failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Registration should succeed: {data}"
        assert "user" in data, "Registration should return user"
        assert "token" in data, "Registration should return token"
        assert data["user"]["email"] == unique_email, "Email should match"
        
        print(f"✓ Registration passed for: {unique_email}")


class TestDecisionAPI:
    """Test decision saving API (prerequisite for replay)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_user_id = f"TEST_decision_user_{uuid.uuid4().hex[:8]}"
    
    def test_save_decision(self):
        """Test POST /api/memory/decision - needed before replay"""
        decision_data = {
            "user_id": self.test_user_id,
            "action": "לקחת הפסקה קצרה",
            "decision": "Allowed",
            "chaos_order": 10,
            "ego_collective": 15,
            "balance_score": 75,
            "value_tag": "recovery"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/decision",
            json=decision_data
        )
        
        assert response.status_code == 200, f"Save decision failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Decision save should succeed"
        assert "id" in data, "Response should contain decision ID"
        
        print(f"✓ Save decision passed - ID: {data['id']}")
        return data["id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

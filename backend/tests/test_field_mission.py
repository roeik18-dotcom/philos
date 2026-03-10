"""
Tests for Field Mission System (Daily Community Challenge)
Tests the mission-today endpoint and mission_contributed in daily-answer endpoint
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMissionToday:
    """Tests for GET /api/orientation/mission-today endpoint"""
    
    def test_mission_today_returns_success(self):
        """Test mission-today endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"PASS: mission-today returns success=True")
    
    def test_mission_today_returns_direction(self):
        """Test mission-today returns direction field"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "direction" in data
        assert data["direction"] in ["contribution", "recovery", "order", "exploration"]
        print(f"PASS: mission-today returns direction='{data['direction']}'")
    
    def test_mission_today_returns_mission_he(self):
        """Test mission-today returns Hebrew mission title"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "mission_he" in data
        assert isinstance(data["mission_he"], str)
        assert len(data["mission_he"]) > 0
        print(f"PASS: mission-today returns mission_he='{data['mission_he']}'")
    
    def test_mission_today_returns_description_he(self):
        """Test mission-today returns Hebrew description"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "description_he" in data
        assert isinstance(data["description_he"], str)
        assert len(data["description_he"]) > 0
        print(f"PASS: mission-today returns description_he='{data['description_he']}'")
    
    def test_mission_today_returns_participants(self):
        """Test mission-today returns participants count"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data
        assert isinstance(data["participants"], int)
        assert data["participants"] >= 0
        print(f"PASS: mission-today returns participants={data['participants']}")
    
    def test_mission_today_returns_target(self):
        """Test mission-today returns target count"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "target" in data
        assert isinstance(data["target"], int)
        assert data["target"] > 0
        print(f"PASS: mission-today returns target={data['target']}")
    
    def test_mission_today_returns_progress_percent(self):
        """Test mission-today returns progress percentage"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        assert "progress_percent" in data
        assert isinstance(data["progress_percent"], (int, float))
        assert 0 <= data["progress_percent"] <= 100
        print(f"PASS: mission-today returns progress_percent={data['progress_percent']}")


class TestDailyAnswerMissionContributed:
    """Tests for mission_contributed in POST /api/orientation/daily-answer/{user_id}"""
    
    def test_daily_answer_returns_mission_contributed(self):
        """Test daily-answer returns mission_contributed field"""
        # Use fresh user ID for each test
        test_user_id = f"TEST_mission_{uuid.uuid4().hex[:8]}"
        
        # First get the daily question to get the question_id
        question_res = requests.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert question_res.status_code == 200
        q_data = question_res.json()
        
        if q_data.get("already_answered_today"):
            print(f"SKIP: User already answered today, cannot test mission_contributed")
            return
        
        question_id = q_data.get("question_id")
        assert question_id is not None
        
        # Submit the answer
        answer_res = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{test_user_id}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert answer_res.status_code == 200
        answer_data = answer_res.json()
        
        assert "mission_contributed" in answer_data
        assert isinstance(answer_data["mission_contributed"], bool)
        print(f"PASS: daily-answer returns mission_contributed={answer_data['mission_contributed']}")
        print(f"  - User direction: {q_data.get('suggested_direction')}")
    
    def test_mission_contributed_true_when_direction_matches(self):
        """Test mission_contributed is True when user's direction matches mission direction"""
        # Get today's mission direction
        mission_res = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert mission_res.status_code == 200
        mission_data = mission_res.json()
        mission_direction = mission_data.get("direction")
        print(f"INFO: Today's mission direction is '{mission_direction}'")
        
        # Generate a fresh user
        test_user_id = f"TEST_mission_match_{uuid.uuid4().hex[:8]}"
        
        # Get daily question for this user
        question_res = requests.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert question_res.status_code == 200
        q_data = question_res.json()
        
        user_direction = q_data.get("suggested_direction")
        question_id = q_data.get("question_id")
        print(f"INFO: User suggested direction is '{user_direction}'")
        
        if q_data.get("already_answered_today"):
            print(f"SKIP: User already answered today")
            return
        
        # Submit the answer
        answer_res = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{test_user_id}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert answer_res.status_code == 200
        answer_data = answer_res.json()
        
        # Check if mission_contributed matches direction match expectation
        if user_direction == mission_direction:
            assert answer_data["mission_contributed"] == True
            print(f"PASS: mission_contributed=True when directions match ({user_direction}=={mission_direction})")
        else:
            assert answer_data["mission_contributed"] == False
            print(f"PASS: mission_contributed=False when directions differ ({user_direction}!={mission_direction})")


class TestMissionParticipantsIncrement:
    """Tests for mission participants increment when direction matches"""
    
    def test_participants_increment_on_match(self):
        """Test that participants count increases when user contributes to mission"""
        # Get current mission state
        before_res = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert before_res.status_code == 200
        before_data = before_res.json()
        before_participants = before_data.get("participants", 0)
        mission_direction = before_data.get("direction")
        print(f"INFO: Before - participants={before_participants}, direction={mission_direction}")
        
        # Create a fresh user and submit answer
        test_user_id = f"TEST_participants_{uuid.uuid4().hex[:8]}"
        
        # Get daily question
        question_res = requests.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert question_res.status_code == 200
        q_data = question_res.json()
        
        user_direction = q_data.get("suggested_direction")
        question_id = q_data.get("question_id")
        
        if q_data.get("already_answered_today"):
            print(f"SKIP: User already answered today")
            return
        
        # Submit answer
        answer_res = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{test_user_id}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert answer_res.status_code == 200
        answer_data = answer_res.json()
        
        # Get mission state after
        after_res = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert after_res.status_code == 200
        after_data = after_res.json()
        after_participants = after_data.get("participants", 0)
        print(f"INFO: After - participants={after_participants}")
        
        # Verify increment happened if direction matched
        if user_direction == mission_direction:
            assert after_participants == before_participants + 1
            print(f"PASS: Participants incremented from {before_participants} to {after_participants} (direction match)")
        else:
            # May or may not increment depending on concurrent users
            print(f"INFO: User direction ({user_direction}) != mission direction ({mission_direction}), no increment expected")
            print(f"PASS: Participants count is {after_participants}")


class TestMissionResponseStructure:
    """Test complete response structure of mission-today"""
    
    def test_complete_response_structure(self):
        """Test all required fields are present in mission-today response"""
        response = requests.get(f"{BASE_URL}/api/orientation/mission-today")
        assert response.status_code == 200
        data = response.json()
        
        # All required fields
        required_fields = ["success", "direction", "mission_he", "description_he", "participants", "target", "progress_percent"]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"PASS: All required fields present: {required_fields}")
        print(f"Response: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

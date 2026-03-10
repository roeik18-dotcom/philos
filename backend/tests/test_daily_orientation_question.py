"""
Backend tests for Daily Orientation Question feature
Tests:
- GET /api/orientation/daily-question/{user_id} - returns question_he and suggested_direction
- Question generation based on identity type
- POST /api/orientation/daily-answer/{user_id} - records action to history
- Saves daily question to daily_questions collection
- Prevents duplicate questions same day (already_answered_today)
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDailyQuestionEndpoint:
    """Tests for GET /api/orientation/daily-question/{user_id}"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a unique test user ID for each test"""
        self.test_user_id = f"test-daily-q-{uuid.uuid4()}"
    
    def test_endpoint_returns_success(self):
        """Test daily question endpoint returns success for new user"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        print(f"PASS: Endpoint returns success=True")
    
    def test_response_has_required_fields(self):
        """Test response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        required_fields = ['success', 'user_id', 'identity', 'question_he', 
                          'suggested_direction', 'question_id', 'already_answered_today']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print(f"PASS: All required fields present: {required_fields}")
    
    def test_question_he_is_hebrew(self):
        """Test that question_he contains Hebrew text"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        question = data.get('question_he', '')
        assert question, "question_he should not be empty"
        # Check for Hebrew characters (Unicode range 0x0590-0x05FF)
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in question)
        assert has_hebrew, f"question_he should contain Hebrew: {question}"
        print(f"PASS: Question is in Hebrew: {question}")
    
    def test_suggested_direction_valid(self):
        """Test that suggested_direction is a valid direction"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        valid_directions = ['recovery', 'order', 'contribution', 'exploration', 'harm', 'avoidance']
        suggested = data.get('suggested_direction')
        assert suggested in valid_directions, f"Invalid direction: {suggested}"
        print(f"PASS: Suggested direction is valid: {suggested}")
    
    def test_question_id_is_generated(self):
        """Test that question_id is generated"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        question_id = data.get('question_id')
        assert question_id, "question_id should be generated"
        assert len(question_id) > 0, "question_id should not be empty"
        print(f"PASS: Question ID generated: {question_id}")
    
    def test_new_user_not_already_answered(self):
        """Test that new user has already_answered_today=False"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        assert data.get('already_answered_today') is False
        print(f"PASS: New user has already_answered_today=False")
    
    def test_identity_is_returned(self):
        """Test that identity is returned (new_user for new users)"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data = response.json()
        
        # For a new user, identity should be 'new_user'
        assert data.get('identity') == 'new_user', f"Expected new_user, got: {data.get('identity')}"
        print(f"PASS: Identity returned for new user: {data.get('identity')}")


class TestDailyQuestionPersistence:
    """Tests for saving daily question to database"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a unique test user ID"""
        self.test_user_id = f"test-persist-{uuid.uuid4()}"
    
    def test_same_question_returned_same_day(self):
        """Test that same question is returned when called multiple times same day"""
        # First call
        response1 = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data1 = response1.json()
        question_id1 = data1.get('question_id')
        question_he1 = data1.get('question_he')
        
        # Second call - should return same question
        response2 = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data2 = response2.json()
        question_id2 = data2.get('question_id')
        question_he2 = data2.get('question_he')
        
        assert question_id1 == question_id2, "Same question_id should be returned same day"
        assert question_he1 == question_he2, "Same question_he should be returned same day"
        print(f"PASS: Same question returned: {question_id1}")


class TestDailyAnswerEndpoint:
    """Tests for POST /api/orientation/daily-answer/{user_id}"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a unique test user ID and get a question"""
        self.test_user_id = f"test-answer-{uuid.uuid4()}"
        # First get a question
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        self.question_data = response.json()
    
    def test_answer_endpoint_returns_success(self):
        """Test answer endpoint returns success"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{self.test_user_id}",
            json={
                "question_id": self.question_data.get('question_id'),
                "action_taken": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        print(f"PASS: Answer endpoint returns success")
    
    def test_answer_records_action(self):
        """Test that answering records action_taken"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{self.test_user_id}",
            json={
                "question_id": self.question_data.get('question_id'),
                "action_taken": True
            }
        )
        data = response.json()
        assert data.get('action_recorded') is True
        print(f"PASS: Action recorded: {data.get('action_recorded')}")
    
    def test_answer_returns_direction(self):
        """Test that answer returns the direction"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{self.test_user_id}",
            json={
                "question_id": self.question_data.get('question_id'),
                "action_taken": True
            }
        )
        data = response.json()
        
        valid_directions = ['recovery', 'order', 'contribution', 'exploration', 'harm', 'avoidance']
        assert data.get('direction') in valid_directions
        print(f"PASS: Direction returned: {data.get('direction')}")
    
    def test_invalid_question_id_returns_404(self):
        """Test that invalid question_id returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{self.test_user_id}",
            json={
                "question_id": "invalid-id-12345",
                "action_taken": True
            }
        )
        assert response.status_code == 404
        print(f"PASS: Invalid question_id returns 404")


class TestAlreadyAnsweredToday:
    """Tests for already_answered_today flag"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a unique test user ID"""
        self.test_user_id = f"test-answered-{uuid.uuid4()}"
    
    def test_already_answered_after_submit(self):
        """Test that already_answered_today is True after submitting answer"""
        # Get question
        response1 = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data1 = response1.json()
        question_id = data1.get('question_id')
        
        # Initial state should be False
        assert data1.get('already_answered_today') is False
        
        # Submit answer
        response2 = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{self.test_user_id}",
            json={
                "question_id": question_id,
                "action_taken": True
            }
        )
        assert response2.status_code == 200
        
        # Get question again - should show already_answered_today=True
        response3 = requests.get(f"{BASE_URL}/api/orientation/daily-question/{self.test_user_id}")
        data3 = response3.json()
        
        assert data3.get('already_answered_today') is True, \
            f"Expected already_answered_today=True, got: {data3.get('already_answered_today')}"
        print(f"PASS: already_answered_today is True after submit")


class TestIdentityBasedQuestions:
    """Tests for question generation based on identity type"""
    
    def test_new_user_gets_recovery_direction(self):
        """Test that new user gets recovery as suggested_direction"""
        user_id = f"test-new-{uuid.uuid4()}"
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        data = response.json()
        
        # New user should get recovery direction
        assert data.get('suggested_direction') == 'recovery', \
            f"Expected recovery for new user, got: {data.get('suggested_direction')}"
        print(f"PASS: New user gets recovery direction")
    
    def test_new_user_question_content(self):
        """Test that new user gets appropriate question"""
        user_id = f"test-new-content-{uuid.uuid4()}"
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        data = response.json()
        
        # Question should be from new_user questions
        new_user_questions = [
            "מה הדבר הראשון שתעשה היום לטובת עצמך?",
            "איך תרצה להתחיל את המסע שלך?",
            "מה יגרום לך להרגיש טוב היום?"
        ]
        
        question = data.get('question_he', '')
        assert question in new_user_questions, f"Question not from new_user set: {question}"
        print(f"PASS: New user gets appropriate question: {question}")


class TestDailyQuestionUserIdValidation:
    """Tests for user_id handling"""
    
    def test_user_id_returned_in_response(self):
        """Test that user_id is returned in response"""
        user_id = f"test-uid-{uuid.uuid4()}"
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        data = response.json()
        
        assert data.get('user_id') == user_id
        print(f"PASS: user_id returned correctly")


# Run pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Test suite for Philos Orientation 5 new features:
1. Streak display in DailyOrientationQuestion
2. Personal Impact on Field after answering daily question
3. Orientation Share Card modal
4. Weekly Orientation Insight section
5. Orientation Index Page (global distribution)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_USER_ID = f"TEST_user_{uuid.uuid4().hex[:8]}"


class TestDailyQuestion:
    """Feature 1 & 2: Daily Question with Streak and Impact"""
    
    def test_daily_question_endpoint_returns_success(self):
        """GET /api/orientation/daily-question/{user_id} returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Daily question endpoint returns success")
    
    def test_daily_question_returns_streak_fields(self):
        """Verify streak and longest_streak are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert 'streak' in data, "streak field missing"
        assert 'longest_streak' in data, "longest_streak field missing"
        assert isinstance(data['streak'], int), "streak should be integer"
        assert isinstance(data['longest_streak'], int), "longest_streak should be integer"
        print(f"PASS: Streak={data['streak']}, Longest={data['longest_streak']}")
    
    def test_daily_question_returns_question_data(self):
        """Verify question_he, suggested_direction, question_id are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        data = response.json()
        
        assert 'question_he' in data and data['question_he'], "question_he missing"
        assert 'suggested_direction' in data, "suggested_direction missing"
        assert 'question_id' in data and data['question_id'], "question_id missing"
        assert 'identity' in data, "identity missing"
        print(f"PASS: Question: {data['question_he'][:30]}...")
    
    def test_daily_answer_returns_impact_message(self):
        """POST /api/orientation/daily-answer/{user_id} returns impact_message and impact_percent"""
        # First get a question
        question_resp = requests.get(f"{BASE_URL}/api/orientation/daily-question/{TEST_USER_ID}")
        question_data = question_resp.json()
        question_id = question_data.get('question_id')
        
        # Submit answer
        answer_response = requests.post(
            f"{BASE_URL}/api/orientation/daily-answer/{TEST_USER_ID}",
            json={"question_id": question_id, "action_taken": True}
        )
        assert answer_response.status_code == 200
        data = answer_response.json()
        
        assert data.get('success') == True
        assert 'impact_percent' in data, "impact_percent missing in response"
        assert 'impact_message' in data, "impact_message missing in response"
        
        if data.get('impact_message'):
            print(f"PASS: Impact message: {data['impact_message']}")
        else:
            print(f"PASS: Impact fields present (message may be None for first action)")


class TestWeeklyInsight:
    """Feature 4: Weekly Orientation Insight"""
    
    def test_weekly_insight_endpoint_returns_success(self):
        """GET /api/orientation/weekly-insight/{user_id} returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-insight/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Weekly insight endpoint returns success")
    
    def test_weekly_insight_returns_distribution(self):
        """Verify distribution and distribution_percent are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-insight/{TEST_USER_ID}")
        data = response.json()
        
        assert 'distribution' in data, "distribution missing"
        assert 'distribution_percent' in data, "distribution_percent missing"
        
        # Check all 4 directions present
        expected_directions = ['contribution', 'recovery', 'order', 'exploration']
        for d in expected_directions:
            assert d in data['distribution'], f"{d} missing in distribution"
            assert d in data['distribution_percent'], f"{d} missing in distribution_percent"
        print(f"PASS: Distribution: {data['distribution']}")
    
    def test_weekly_insight_returns_insight_text(self):
        """Verify insight_he (Hebrew insight text) is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-insight/{TEST_USER_ID}")
        data = response.json()
        
        assert 'insight_he' in data, "insight_he missing"
        assert data['insight_he'] is not None, "insight_he should not be None"
        assert 'trend' in data, "trend missing"
        print(f"PASS: Insight: {data['insight_he']}")
    
    def test_weekly_insight_returns_total_actions(self):
        """Verify total_actions and dominant_direction are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-insight/{TEST_USER_ID}")
        data = response.json()
        
        assert 'total_actions' in data, "total_actions missing"
        assert isinstance(data['total_actions'], int), "total_actions should be integer"
        # dominant_direction can be null if no actions
        assert 'dominant_direction' in data, "dominant_direction field missing"
        print(f"PASS: Total actions: {data['total_actions']}")


class TestShareCard:
    """Feature 3: Orientation Share Card"""
    
    def test_share_card_endpoint_returns_success(self):
        """GET /api/orientation/share/{user_id} returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/share/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Share card endpoint returns success")
    
    def test_share_card_returns_orientation(self):
        """Verify orientation label is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/share/{TEST_USER_ID}")
        data = response.json()
        
        assert 'orientation' in data, "orientation missing"
        assert data['orientation'] is not None, "orientation should not be None"
        # Should be Hebrew label
        valid_orientations = ['התאוששות', 'סדר', 'תרומה', 'חקירה', 'איזון']
        assert data['orientation'] in valid_orientations, f"Invalid orientation: {data['orientation']}"
        print(f"PASS: Orientation: {data['orientation']}")
    
    def test_share_card_returns_streak(self):
        """Verify streak is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/share/{TEST_USER_ID}")
        data = response.json()
        
        assert 'streak' in data, "streak missing"
        assert isinstance(data['streak'], int), "streak should be integer"
        print(f"PASS: Streak: {data['streak']}")
    
    def test_share_card_returns_compass_position(self):
        """Verify compass_position with x,y coordinates is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/share/{TEST_USER_ID}")
        data = response.json()
        
        assert 'compass_position' in data, "compass_position missing"
        assert 'x' in data['compass_position'], "compass_position.x missing"
        assert 'y' in data['compass_position'], "compass_position.y missing"
        print(f"PASS: Compass position: ({data['compass_position']['x']}, {data['compass_position']['y']})")
    
    def test_share_card_returns_message(self):
        """Verify message_he is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/share/{TEST_USER_ID}")
        data = response.json()
        
        assert 'message_he' in data, "message_he missing"
        assert data['message_he'] is not None, "message_he should not be None"
        print(f"PASS: Message: {data['message_he']}")


class TestOrientationIndex:
    """Feature 5: Orientation Index Page (global distribution)"""
    
    def test_orientation_index_endpoint_returns_success(self):
        """GET /api/orientation/index returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print("PASS: Orientation index endpoint returns success")
    
    def test_orientation_index_returns_distribution(self):
        """Verify distribution with 4 directions is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        data = response.json()
        
        assert 'distribution' in data, "distribution missing"
        
        expected_directions = ['contribution', 'recovery', 'order', 'exploration']
        for d in expected_directions:
            assert d in data['distribution'], f"{d} missing in distribution"
        
        # Verify percentages sum to ~100 or all 0 or all 25
        total = sum(data['distribution'].values())
        assert 95 <= total <= 105 or total == 0 or total == 100, f"Distribution should sum to ~100, got {total}"
        print(f"PASS: Distribution: {data['distribution']}")
    
    def test_orientation_index_returns_user_counts(self):
        """Verify total_users and total_actions_today are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        data = response.json()
        
        assert 'total_users' in data, "total_users missing"
        assert 'total_actions_today' in data, "total_actions_today missing"
        assert isinstance(data['total_users'], int), "total_users should be integer"
        assert isinstance(data['total_actions_today'], int), "total_actions_today should be integer"
        print(f"PASS: Users: {data['total_users']}, Actions today: {data['total_actions_today']}")
    
    def test_orientation_index_returns_headline(self):
        """Verify headline_he (Hebrew headline) is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        data = response.json()
        
        assert 'headline_he' in data, "headline_he missing"
        assert data['headline_he'] is not None, "headline_he should not be None"
        print(f"PASS: Headline: {data['headline_he']}")
    
    def test_orientation_index_returns_dominant_direction(self):
        """Verify dominant_direction is returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        data = response.json()
        
        assert 'dominant_direction' in data, "dominant_direction field missing"
        # Can be null if no data
        if data['dominant_direction']:
            valid_directions = ['contribution', 'recovery', 'order', 'exploration']
            assert data['dominant_direction'] in valid_directions, f"Invalid dominant: {data['dominant_direction']}"
        print(f"PASS: Dominant direction: {data['dominant_direction']}")
    
    def test_orientation_index_returns_direction_change(self):
        """Verify direction_change and yesterday_dominant are returned"""
        response = requests.get(f"{BASE_URL}/api/orientation/index")
        data = response.json()
        
        assert 'direction_change' in data, "direction_change field missing"
        assert 'yesterday_dominant' in data, "yesterday_dominant field missing"
        print(f"PASS: Direction change: {data['direction_change']}, Yesterday: {data['yesterday_dominant']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

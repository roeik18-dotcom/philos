"""
Test: Base-influenced daily questions & base_reflection_he feature
Iteration 52 - Testing base→question influence and base reflection in day summary

Key features:
1. Daily question is influenced by chosen base (body/heart/head)
2. Day summary includes base_reflection_he comparing base vs actual department
"""
import pytest
import requests
import os
from datetime import datetime
import time
from pymongo import MongoClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-mvp.preview.emergentagent.com')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Expected question banks per base
BODY_QUESTIONS = [
    "עשה פעולה פיזית קטנה שמסדרת משהו סביבך.",
    "הזז את הגוף היום — אפילו הליכה קצרה.",
    "סדר פינה אחת בסביבה שלך.",
    "עשה משהו מעשי שדחית."
]

HEART_QUESTIONS = [
    "שלח מילה טובה למישהו שלא ציפה לזה.",
    "הקשב למישהו היום — באמת הקשב.",
    "עשה משהו קטן עבור מישהו קרוב.",
    "תן לעצמך רגע של חמלה היום."
]

HEAD_QUESTIONS = [
    "מצא דבר אחד חדש שלא שמת לב אליו קודם.",
    "ארגן רעיון אחד שמסתובב לך בראש.",
    "למד משהו קטן שלא ידעת.",
    "קבל החלטה אחת שדחית."
]


@pytest.fixture(scope="module")
def mongo_client():
    """Direct MongoDB connection for test setup/teardown"""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    yield db
    client.close()


@pytest.fixture(scope="module")
def test_user_id():
    """Use test user from previous iterations"""
    return "05d47b99-88f1-44b3-a879-6c995634eaa0"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def get_today_date():
    """Get today's date in ISO format"""
    return datetime.utcnow().strftime('%Y-%m-%d')


class TestBaseInfluencedQuestions:
    """Test that chosen base influences the daily question"""

    def test_set_body_base_and_verify_question(self, api_client, mongo_client, test_user_id):
        """Body base → physical/practical questions"""
        today = get_today_date()
        
        # Clear today's question and base
        mongo_client.daily_questions.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_bases.delete_many({"user_id": test_user_id, "date": today})
        
        # Set body base
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "body"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        # Fetch daily question - should be body-influenced
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        question = data.get("question_he", "")
        suggested_direction = data.get("suggested_direction", "")
        
        # Verify question is from body questions bank
        assert question in BODY_QUESTIONS, f"Body base should generate body question, got: {question}"
        # Body questions suggest 'order' direction
        assert suggested_direction == "order", f"Body base should suggest 'order', got: {suggested_direction}"
        print(f"✓ Body base generated question: {question}")

    def test_set_heart_base_and_verify_question(self, api_client, mongo_client, test_user_id):
        """Heart base → relational/emotional questions"""
        today = get_today_date()
        
        # Clear today's question and base
        mongo_client.daily_questions.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_bases.delete_many({"user_id": test_user_id, "date": today})
        
        # Set heart base
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "heart"}
        )
        assert response.status_code == 200
        
        # Fetch daily question - should be heart-influenced
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        question = data.get("question_he", "")
        suggested_direction = data.get("suggested_direction", "")
        
        # Verify question is from heart questions bank
        assert question in HEART_QUESTIONS, f"Heart base should generate heart question, got: {question}"
        # Heart questions suggest 'contribution' direction
        assert suggested_direction == "contribution", f"Heart base should suggest 'contribution', got: {suggested_direction}"
        print(f"✓ Heart base generated question: {question}")

    def test_set_head_base_and_verify_question(self, api_client, mongo_client, test_user_id):
        """Head base → thinking/exploring questions"""
        today = get_today_date()
        
        # Clear today's question and base
        mongo_client.daily_questions.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_bases.delete_many({"user_id": test_user_id, "date": today})
        
        # Set head base
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "head"}
        )
        assert response.status_code == 200
        
        # Fetch daily question - should be head-influenced
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        question = data.get("question_he", "")
        suggested_direction = data.get("suggested_direction", "")
        
        # Verify question is from head questions bank
        assert question in HEAD_QUESTIONS, f"Head base should generate head question, got: {question}"
        # Head questions suggest 'exploration' direction
        assert suggested_direction == "exploration", f"Head base should suggest 'exploration', got: {suggested_direction}"
        print(f"✓ Head base generated question: {question}")

    def test_questions_are_simple_one_sentence_actionable(self, api_client, mongo_client, test_user_id):
        """All questions should be simple, one-sentence, actionable (no theory)"""
        all_questions = BODY_QUESTIONS + HEART_QUESTIONS + HEAD_QUESTIONS
        
        for q in all_questions:
            # Should be one sentence (ends with .)
            assert q.endswith('.'), f"Question should end with period: {q}"
            # Should not have multiple sentences
            sentence_count = q.count('.') + q.count('?') + q.count('!')
            assert sentence_count <= 2, f"Question should be simple one-sentence: {q}"
            # Should not contain theory words
            theory_words = ['כי', 'משום', 'לכן', 'הסיבה', 'תיאוריה', 'פילוסופיה']
            for tw in theory_words:
                assert tw not in q, f"Question should not contain theory word '{tw}': {q}"
        
        print(f"✓ All {len(all_questions)} questions are simple, one-sentence, actionable")


class TestBaseReflectionInDaySummary:
    """Test base_reflection_he field in day summary"""

    def test_day_summary_returns_base_reflection_field(self, api_client, test_user_id):
        """Day summary should include base_reflection_he field"""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        # Field should exist (even if empty)
        assert "base_reflection_he" in data, "base_reflection_he field missing from day summary"
        print(f"✓ base_reflection_he field present: '{data.get('base_reflection_he', '')}'")

    def test_reflection_empty_when_no_actions(self, api_client, mongo_client, test_user_id):
        """base_reflection_he should be empty when no actions today (nothing to reflect on)"""
        today = get_today_date()
        
        # Clear today's actions
        mongo_client.daily_answers.delete_many({"user_id": test_user_id, "date": today})
        
        # Set a base
        api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "heart"}
        )
        
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # When total_actions = 0, reflection should be empty
        if data.get("total_actions", 0) == 0:
            assert data.get("base_reflection_he") == "", "Reflection should be empty when no actions"
            print("✓ base_reflection_he correctly empty when no actions")
        else:
            print(f"Note: User has {data.get('total_actions')} actions today, reflection may not be empty")

    def test_reflection_shows_alignment_when_base_matches_dept(self, api_client, mongo_client, test_user_id):
        """base_reflection_he shows alignment when base matches most_used_dept"""
        today = get_today_date()
        
        # Clear and set heart base
        mongo_client.daily_bases.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_answers.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_questions.delete_many({"user_id": test_user_id, "date": today})
        
        # Set heart base
        api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "heart"}
        )
        
        # Get a question
        q_response = api_client.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        q_data = q_response.json()
        question_id = q_data.get("question_id")
        
        # Submit action with contribution direction (maps to heart department)
        if question_id:
            answer_response = api_client.post(
                f"{BASE_URL}/api/orientation/daily-answer/{test_user_id}",
                json={
                    "question_id": question_id,
                    "action_taken": True,
                    "response_text": "Test action - contribution"
                }
            )
        
        # Fetch day summary
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        reflection = data.get("base_reflection_he", "")
        chosen_base = data.get("chosen_base")
        most_used_dept = data.get("most_used_dept")
        
        print(f"Chosen base: {chosen_base}, Most used dept: {most_used_dept}")
        print(f"base_reflection_he: {reflection}")
        
        # If base matches most_used_dept and there are actions, reflection should show alignment
        if chosen_base and most_used_dept and data.get("total_actions", 0) > 0:
            if chosen_base == most_used_dept:
                assert "תאמו את הבחירה" in reflection, f"Should show alignment message, got: {reflection}"
                print("✓ Reflection shows alignment when base matches most_used_dept")
            else:
                assert "אך רוב הפעולות" in reflection, f"Should show misalignment message, got: {reflection}"
                print("✓ Reflection shows misalignment when base differs from most_used_dept")


class TestFullFlow:
    """Test the complete flow: base → question → action → reflection"""

    def test_full_flow_body_base(self, api_client, mongo_client, test_user_id):
        """Full flow: select body base → get physical question → check reflection"""
        today = get_today_date()
        
        # 1. Clear existing data
        mongo_client.daily_bases.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_questions.delete_many({"user_id": test_user_id, "date": today})
        mongo_client.daily_answers.delete_many({"user_id": test_user_id, "date": today})
        
        # 2. Select body base
        base_response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "body"}
        )
        assert base_response.status_code == 200
        assert base_response.json().get("success") is True
        print("✓ Step 1: Body base selected")
        
        # 3. Get daily question (should be body-influenced)
        question_response = api_client.get(f"{BASE_URL}/api/orientation/daily-question/{test_user_id}")
        assert question_response.status_code == 200
        q_data = question_response.json()
        
        question = q_data.get("question_he", "")
        assert question in BODY_QUESTIONS, f"Expected body question, got: {question}"
        assert q_data.get("suggested_direction") == "order"
        print(f"✓ Step 2: Got body question: {question}")
        
        # 4. Submit an answer
        question_id = q_data.get("question_id")
        answer_response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-answer/{test_user_id}",
            json={
                "question_id": question_id,
                "action_taken": True,
                "response_text": "Cleaned up my desk - physical action"
            }
        )
        assert answer_response.status_code == 200
        print("✓ Step 3: Action submitted")
        
        # 5. Check day summary includes base_reflection_he
        summary_response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        
        assert "base_reflection_he" in summary_data
        reflection = summary_data.get("base_reflection_he", "")
        print(f"✓ Step 4: Day summary includes base_reflection_he: {reflection}")
        
        # Verify base is in summary
        assert summary_data.get("chosen_base") == "body"
        print("✓ Full flow completed successfully")


class TestExistingFeaturesRegression:
    """Ensure existing base selection and gating features still work"""

    def test_base_selection_returns_allocations(self, api_client, test_user_id):
        """Base selection should return Hebrew allocations"""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert "bases" in data
        
        for base_key in ['heart', 'head', 'body']:
            assert base_key in data["bases"]
            base_data = data["bases"][base_key]
            assert "name_he" in base_data
            assert "allocations_he" in base_data
            assert len(base_data["allocations_he"]) == 4
        
        print("✓ Base selection returns all allocations correctly")

    def test_invalid_base_rejected(self, api_client, test_user_id):
        """Invalid base values should be rejected"""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "invalid_base"}
        )
        assert response.status_code == 400, "Invalid base should return 400"
        print("✓ Invalid base correctly rejected")

    def test_day_summary_has_dept_allocation(self, api_client, test_user_id):
        """Day summary should have department allocation percentages"""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "dept_allocation" in data
        dept_alloc = data["dept_allocation"]
        assert "heart" in dept_alloc
        assert "head" in dept_alloc
        assert "body" in dept_alloc
        print(f"✓ Dept allocation: {dept_alloc}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

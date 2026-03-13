"""
Test English Translation - Verify all API responses are in English (no Hebrew)
Tests the Hebrew-to-English translation of the Philos Orientation application.
"""
import pytest
import requests
import re
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Hebrew character unicode range detector
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')

def contains_hebrew(text):
    """Check if text contains Hebrew characters."""
    if not text:
        return False
    return bool(HEBREW_PATTERN.search(str(text)))

def find_hebrew_in_response(data, path=""):
    """Recursively search for Hebrew text in API response."""
    hebrew_found = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            hebrew_found.extend(find_hebrew_in_response(value, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            hebrew_found.extend(find_hebrew_in_response(item, current_path))
    elif isinstance(data, str) and contains_hebrew(data):
        hebrew_found.append({"path": path, "text": data[:100]})
    return hebrew_found


class TestAuthEnglishMessages:
    """Test that authentication endpoints return English messages."""
    
    def test_register_duplicate_email_english(self):
        """Test duplicate email registration returns English error."""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        data = response.json()
        # Should return English message for duplicate email
        assert response.status_code == 200
        if not data.get('success'):
            message = data.get('message', '')
            assert not contains_hebrew(message), f"Hebrew found in error message: {message}"
            # Check message is in English
            assert any(word in message.lower() for word in ['email', 'already', 'registered', 'exists']), f"Expected English error, got: {message}"
            print(f"PASS: Duplicate email error in English: {message}")
    
    def test_login_success_message_english(self):
        """Test successful login returns English message."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        data = response.json()
        assert response.status_code == 200
        message = data.get('message', '')
        assert not contains_hebrew(message), f"Hebrew found in success message: {message}"
        if data.get('success'):
            assert any(word in message.lower() for word in ['success', 'logged', 'welcome']), f"Expected English success message, got: {message}"
            print(f"PASS: Login success message in English: {message}")
    
    def test_login_error_message_english(self):
        """Test login failure returns English error message."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "wrongpassword"
        })
        data = response.json()
        message = data.get('message', '')
        assert not contains_hebrew(message), f"Hebrew found in error message: {message}"
        if not data.get('success'):
            assert any(word in message.lower() for word in ['invalid', 'password', 'email', 'incorrect', 'wrong']), f"Expected English error, got: {message}"
            print(f"PASS: Login error message in English: {message}")
    
    def test_logout_message_english(self):
        """Test logout returns English message."""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        message = data.get('message', '')
        assert not contains_hebrew(message), f"Hebrew found in logout message: {message}"
        print(f"PASS: Logout message in English: {message}")


class TestOnboardingEnglish:
    """Test onboarding endpoints return English messages."""
    
    def test_onboarding_first_action_english(self):
        """Test first action message is in English."""
        test_user_id = f"TEST_{uuid.uuid4()}"
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json={
            "user_id": test_user_id,
            "direction": "contribution"
        })
        assert response.status_code == 200
        data = response.json()
        message = data.get('message', '')
        assert not contains_hebrew(message), f"Hebrew found in onboarding message: {message}"
        assert any(word in message.lower() for word in ['action', 'sent', 'field', 'first', 'complete']), f"Expected English message, got: {message}"
        print(f"PASS: Onboarding message in English: {message}")


class TestDecisionPathEnglish:
    """Test decision-path endpoint returns English text."""
    
    def test_decision_path_english_headlines(self):
        """Test decision path returns English headlines and steps."""
        # Login to get a user_id
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_resp.json().get('user', {}).get('id')
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        response = requests.get(f"{BASE_URL}/api/decision-path/{user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check all text fields for Hebrew
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in decision-path: {hebrew_found}"
        
        # Verify specific fields are in English
        headline = data.get('headline', '')
        recommended_step = data.get('recommended_step', '')
        concrete_action = data.get('concrete_action', '')
        theory_basis = data.get('theory_basis', '')
        
        assert not contains_hebrew(headline), f"Hebrew in headline: {headline}"
        assert not contains_hebrew(recommended_step), f"Hebrew in recommended_step: {recommended_step}"
        assert not contains_hebrew(concrete_action), f"Hebrew in concrete_action: {concrete_action}"
        assert not contains_hebrew(theory_basis), f"Hebrew in theory_basis: {theory_basis}"
        
        print(f"PASS: Decision path in English - headline: {headline[:50]}")


class TestIdentityEnglish:
    """Test identity endpoint returns English labels and descriptions."""
    
    def test_identity_english_labels(self):
        """Test orientation identity returns English text."""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_resp.json().get('user', {}).get('id')
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        response = requests.get(f"{BASE_URL}/api/orientation/identity/{user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check all text fields for Hebrew
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in identity: {hebrew_found}"
        
        # Verify specific fields
        identity_label = data.get('identity_label', '')
        identity_description = data.get('identity_description', '')
        insight = data.get('insight', '')
        
        assert not contains_hebrew(identity_label), f"Hebrew in identity_label: {identity_label}"
        assert not contains_hebrew(identity_description), f"Hebrew in identity_description: {identity_description}"
        assert not contains_hebrew(insight), f"Hebrew in insight: {insight}"
        
        print(f"PASS: Identity in English - label: {identity_label}")


class TestFieldTodayEnglish:
    """Test field-today endpoint returns English insight."""
    
    def test_field_today_insight_english(self):
        """Test field today returns English insight text."""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        
        # Check for Hebrew in response
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in field-today: {hebrew_found}"
        
        insight = data.get('insight', '')
        assert not contains_hebrew(insight), f"Hebrew in insight: {insight}"
        
        # Verify insight contains English words
        if insight:
            assert any(word in insight.lower() for word in ['field', 'today', 'toward', 'balanced', 'recovery', 'order', 'contribution', 'exploration']), f"Expected English insight, got: {insight}"
        
        print(f"PASS: Field today insight in English: {insight}")


class TestWeeklyInsightEnglish:
    """Test weekly insight endpoint returns English text."""
    
    def test_weekly_insight_english(self):
        """Test weekly insight returns English insight text."""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_resp.json().get('user', {}).get('id')
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        response = requests.get(f"{BASE_URL}/api/orientation/weekly-insight/{user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check for Hebrew in response
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in weekly-insight: {hebrew_found}"
        
        insight_he = data.get('insight_he', '')  # Note: field name may still be _he but content should be English
        assert not contains_hebrew(insight_he), f"Hebrew in insight_he: {insight_he}"
        
        print(f"PASS: Weekly insight in English: {insight_he}")


class TestComparisonEnglish:
    """Test comparison endpoint returns English insight."""
    
    def test_comparison_insight_english(self):
        """Test user comparison returns English insight."""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_resp.json().get('user', {}).get('id')
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        response = requests.get(f"{BASE_URL}/api/orientation/compare/{user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check for Hebrew in response
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in comparison: {hebrew_found}"
        
        comparison_insight = data.get('comparison_insight', '')
        assert not contains_hebrew(comparison_insight), f"Hebrew in comparison_insight: {comparison_insight}"
        
        print(f"PASS: Comparison insight in English: {comparison_insight}")


class TestFeedbackEnglish:
    """Test feedback endpoint returns English message."""
    
    def test_feedback_success_message_english(self):
        """Test feedback submission returns English message."""
        response = requests.post(f"{BASE_URL}/api/feedback", json={
            "user_id": "test_user",
            "text": "Test feedback",
            "type": "general"
        })
        assert response.status_code == 200
        data = response.json()
        message = data.get('message', '')
        assert not contains_hebrew(message), f"Hebrew in feedback message: {message}"
        assert any(word in message.lower() for word in ['thank', 'feedback', 'received']), f"Expected English message, got: {message}"
        print(f"PASS: Feedback message in English: {message}")


class TestOrientationFieldEnglish:
    """Test orientation field endpoint returns English text."""
    
    def test_orientation_field_insights_english(self):
        """Test orientation field returns English insights."""
        response = requests.get(f"{BASE_URL}/api/orientation/field")
        assert response.status_code == 200
        data = response.json()
        
        # Check for Hebrew in response
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in orientation field: {hebrew_found}"
        
        field_insight = data.get('field_insight', '')
        momentum_insight = data.get('momentum_insight', '')
        
        assert not contains_hebrew(field_insight), f"Hebrew in field_insight: {field_insight}"
        assert not contains_hebrew(momentum_insight), f"Hebrew in momentum_insight: {momentum_insight}"
        
        print(f"PASS: Orientation field insights in English")


class TestDailyQuestionEnglish:
    """Test daily question endpoint returns English question."""
    
    def test_daily_question_english(self):
        """Test daily question returns English text."""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "newuser@test.com",
            "password": "password123"
        })
        user_id = login_resp.json().get('user', {}).get('id')
        if not user_id:
            pytest.skip("Could not get user_id from login")
        
        response = requests.get(f"{BASE_URL}/api/orientation/daily-question/{user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check for Hebrew in response
        hebrew_found = find_hebrew_in_response(data)
        assert len(hebrew_found) == 0, f"Hebrew found in daily question: {hebrew_found}"
        
        question_he = data.get('question_he', '')  # Field name may still be _he but content should be English
        assert not contains_hebrew(question_he), f"Hebrew in question_he: {question_he}"
        
        print(f"PASS: Daily question in English: {question_he}")


class TestNoHebrewInResponses:
    """Comprehensive test to verify no Hebrew unicode appears in any API response."""
    
    def test_no_hebrew_unicode_in_auth_responses(self):
        """Verify no Hebrew characters in auth endpoints."""
        endpoints_to_test = [
            ("POST", "/api/auth/logout", None),
        ]
        
        for method, endpoint, payload in endpoints_to_test:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=payload) if payload else requests.post(f"{BASE_URL}{endpoint}")
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            data = response.json()
            hebrew_found = find_hebrew_in_response(data)
            assert len(hebrew_found) == 0, f"Hebrew found in {endpoint}: {hebrew_found}"
        
        print("PASS: No Hebrew in auth responses")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

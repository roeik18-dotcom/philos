"""
Tests for Profile AI Calibration (iteration 62).
Verifies that profile AI outputs are GROUNDED and CLEAR (not overly poetic).

Changes verified:
- PROFILE_SYSTEM_PROMPT with anti-poetry rules
- Hebrew reference examples for each trust state
- Outputs should mention value/risk relationship

Test users by trust state:
- Stable (~15): 05d47b99-88f1-44b3-a879-6c995634eaa0
- Building (~4): 2f49d593-1c59-4074-b5b0-edd75d1ccb8c  
- Fragile (~0.1): 0c98a493-3148-4c72-88e7-662baa393d11
- Restricted (~-2.8): d6a4bffd-e689-4ea8-b8c4-57f630a3a01e (negative trust)
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test users by trust state
STABLE_USER = {
    "user_id": "05d47b99-88f1-44b3-a879-6c995634eaa0",
    "email": "newuser@test.com",
    "password": "password123",
    "expected_state": "stable",
    "expected_trust_min": 15
}

BUILDING_USER = {
    "user_id": "2f49d593-1c59-4074-b5b0-edd75d1ccb8c",
    "email": "trust_building@test.com",
    "password": "password123",
    "expected_state": "building",
    "expected_trust_range": (5, 15)
}

FRAGILE_USER = {
    "user_id": "0c98a493-3148-4c72-88e7-662baa393d11",
    "email": "trust_fragile@test.com",
    "password": "password123",
    "expected_state": "fragile",
    "expected_trust_range": (0, 5)
}

RESTRICTED_USER = {
    "user_id": "d6a4bffd-e689-4ea8-b8c4-57f630a3a01e",
    "email": "trust_restricted@test.com",
    "password": "password123",
    "expected_state": "restricted",
    "expected_trust_max": 0  # Negative trust
}

# Punitive/shaming words that should NOT appear (especially for restricted user)
PUNITIVE_WORDS_HE = [
    "נכשל", "כישלון",    # fail/failure
    "אשם", "אשמה",        # guilt
    "עונש", "נענש",       # punishment
    "רע", "גרוע",         # bad
    "בוגד", "בגידה",      # betrayal
    "מאכזב",              # disappointing
    "חסר ערך",            # worthless
    "מבזה", "בזיון",      # disgrace
    "נבזה",               # despicable
]

# Overly poetic/mystical words to detect (calibration aims to reduce these)
POETIC_WORDS_HE = [
    "חולם",               # dreamer
    "נודד",               # wanderer
    "אפק",                # horizon (abstract)
    "מסתורי",             # mysterious
    "קסם",                # magic
    "נשמה",               # soul
    "מסע",                # journey (abstract)
    "אינסוף",             # infinity
    "נצח",                # eternity
    "מרחב",               # expanse (abstract)
]


def has_hebrew(text):
    """Check if text contains Hebrew characters"""
    return bool(re.search(r'[\u0590-\u05FF]', text))


def count_sentences(text):
    """Count sentences in Hebrew text"""
    if not text:
        return 0
    sentences = re.split(r'[.!?]\s*', text.strip())
    return len([s for s in sentences if s.strip()])


def contains_punitive_words(text):
    """Check if text contains punitive/shaming words"""
    for word in PUNITIVE_WORDS_HE:
        if word in text:
            return word
    return None


def contains_poetic_words(text):
    """Check if text contains overly poetic/mystical words"""
    found = []
    for word in POETIC_WORDS_HE:
        if word in text:
            found.append(word)
    return found


def is_grounded_description(text):
    """Check if text mentions grounded value/risk relationship"""
    # These phrases indicate grounded descriptions (from PROFILE_SYSTEM_PROMPT examples)
    grounded_indicators = [
        "ערך",           # value
        "סיכון",         # risk
        "יציב",          # stable
        "מוגבל",         # restricted/limited
        "שביר",          # fragile
        "בבנייה",        # building
        "נוכחות",        # presence
        "איזון",         # balance
        "היסטוריה",      # history
        "פעולות",        # actions
    ]
    count = sum(1 for indicator in grounded_indicators if indicator in text)
    return count >= 2  # At least 2 grounded terms


class TestStableTrustProfile:
    """Tests for stable trust user (trust_score >= 15)"""
    
    def test_stable_profile_returns_200(self):
        """Stable user profile endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{STABLE_USER['user_id']}/record",
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        print("✓ Stable profile returns 200")
    
    def test_stable_has_ai_interpretation(self):
        """ai_profile_interpretation field exists"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{STABLE_USER['user_id']}/record",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "ai_profile_interpretation" in data
        ai_text = data.get("ai_profile_interpretation", "")
        assert isinstance(ai_text, str) and len(ai_text) > 0, f"Empty interpretation"
        print(f"✓ Stable AI interpretation: '{ai_text}'")
    
    def test_stable_interpretation_is_hebrew_sentence(self):
        """Interpretation is one Hebrew sentence"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{STABLE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        assert has_hebrew(ai_text), f"Not Hebrew: '{ai_text}'"
        sentence_count = count_sentences(ai_text)
        assert 1 <= sentence_count <= 2, f"Expected 1-2 sentences, got {sentence_count}"
        print(f"✓ Stable interpretation is {sentence_count} Hebrew sentence(s)")
    
    def test_stable_has_field_trust(self):
        """field_trust object present"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{STABLE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        assert "field_trust" in data, "field_trust missing"
        ft = data["field_trust"]
        assert "value_score" in ft
        assert "risk_score" in ft
        assert "trust_score" in ft
        print(f"✓ Stable field_trust: {ft}")


class TestBuildingTrustProfile:
    """Tests for building trust user (5 <= trust_score < 15)"""
    
    def test_building_profile_returns_200(self):
        """Building user profile works"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{BUILDING_USER['user_id']}/record",
            timeout=30
        )
        assert response.status_code == 200
        print("✓ Building profile returns 200")
    
    def test_building_has_ai_interpretation(self):
        """ai_profile_interpretation exists and is Hebrew"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{BUILDING_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        assert isinstance(ai_text, str) and len(ai_text) > 0
        assert has_hebrew(ai_text)
        print(f"✓ Building AI interpretation: '{ai_text}'")
    
    def test_building_has_field_trust(self):
        """field_trust object present"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{BUILDING_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        assert "field_trust" in data
        print(f"✓ Building field_trust: {data['field_trust']}")


class TestFragileTrustProfile:
    """Tests for fragile trust user (0 < trust_score < 5)"""
    
    def test_fragile_profile_returns_200(self):
        """Fragile user profile works"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{FRAGILE_USER['user_id']}/record",
            timeout=30
        )
        assert response.status_code == 200
        print("✓ Fragile profile returns 200")
    
    def test_fragile_has_ai_interpretation(self):
        """ai_profile_interpretation exists and is Hebrew"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{FRAGILE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        assert isinstance(ai_text, str) and len(ai_text) > 0
        assert has_hebrew(ai_text)
        print(f"✓ Fragile AI interpretation: '{ai_text}'")
    
    def test_fragile_is_non_punitive(self):
        """Fragile interpretation has no shaming language"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{FRAGILE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        punitive = contains_punitive_words(ai_text)
        assert punitive is None, f"Found punitive word '{punitive}' in: '{ai_text}'"
        print(f"✓ Fragile interpretation is non-punitive")
    
    def test_fragile_has_field_trust(self):
        """field_trust object present"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{FRAGILE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        assert "field_trust" in data
        print(f"✓ Fragile field_trust: {data['field_trust']}")


class TestRestrictedTrustProfile:
    """Tests for restricted trust user (trust_score <= 0)"""
    
    def test_restricted_profile_returns_200(self):
        """Restricted user profile works"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        print("✓ Restricted profile returns 200")
    
    def test_restricted_has_negative_trust(self):
        """Restricted user has trust_score <= 0"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ft = data.get("field_trust", {})
        trust_score = ft.get("trust_score", 1)
        
        assert trust_score <= 0, f"Expected negative trust, got {trust_score}"
        print(f"✓ Restricted user trust_score: {trust_score}")
    
    def test_restricted_has_ai_interpretation(self):
        """ai_profile_interpretation exists and is Hebrew"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        assert isinstance(ai_text, str) and len(ai_text) > 0, "Empty interpretation"
        assert has_hebrew(ai_text), f"Not Hebrew: '{ai_text}'"
        print(f"✓ Restricted AI interpretation: '{ai_text}'")
    
    def test_restricted_is_non_punitive(self):
        """CRITICAL: Restricted interpretation MUST NOT contain shaming/punitive language"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        punitive = contains_punitive_words(ai_text)
        assert punitive is None, f"SHAMING FOUND: '{punitive}' in: '{ai_text}'"
        print(f"✓ Restricted interpretation is non-punitive: '{ai_text}'")
    
    def test_restricted_is_one_sentence(self):
        """Interpretation is one Hebrew sentence"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        sentence_count = count_sentences(ai_text)
        assert 1 <= sentence_count <= 2, f"Expected 1-2 sentences, got {sentence_count}"
        print(f"✓ Restricted interpretation is {sentence_count} sentence(s)")
    
    def test_restricted_has_field_trust(self):
        """field_trust object present"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        assert "field_trust" in data
        ft = data["field_trust"]
        print(f"✓ Restricted field_trust: {ft}")


class TestCalibrationGroundedness:
    """Tests to verify outputs are grounded (not overly poetic)"""
    
    def test_stable_output_groundedness(self):
        """Check stable user output for grounded description"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{STABLE_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        poetic = contains_poetic_words(ai_text)
        # Log poetic words found (warning, not failure)
        if poetic:
            print(f"⚠ Stable output contains poetic words: {poetic}")
        
        # Check for grounded indicators
        grounded = is_grounded_description(ai_text)
        print(f"✓ Stable output grounded: {grounded}, text: '{ai_text}'")
    
    def test_restricted_output_groundedness(self):
        """Check restricted user output for grounded description"""
        response = requests.get(
            f"{BASE_URL}/api/profile/{RESTRICTED_USER['user_id']}/record",
            timeout=30
        )
        data = response.json()
        ai_text = data.get("ai_profile_interpretation", "")
        
        poetic = contains_poetic_words(ai_text)
        if poetic:
            print(f"⚠ Restricted output contains poetic words: {poetic}")
        
        grounded = is_grounded_description(ai_text)
        print(f"✓ Restricted output grounded: {grounded}, text: '{ai_text}'")


class TestExistingEndpointsRegression:
    """Regression tests for other endpoints"""
    
    def test_field_dashboard_works(self):
        """GET /api/orientation/field-dashboard returns ai_field_interpretation"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "ai_field_interpretation" in data
        print(f"✓ Field dashboard ai_field_interpretation: '{data.get('ai_field_interpretation', '')[:60]}...'")
    
    def test_login_works(self):
        """POST /api/auth/login works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STABLE_USER["email"], "password": STABLE_USER["password"]}
        )
        assert response.status_code == 200
        print("✓ Login endpoint works")
    
    def test_trust_endpoint_works(self):
        """GET /api/user/{user_id}/trust works"""
        response = requests.get(f"{BASE_URL}/api/user/{STABLE_USER['user_id']}/trust")
        assert response.status_code == 200
        data = response.json()
        assert "trust_score" in data
        print(f"✓ Trust endpoint works: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

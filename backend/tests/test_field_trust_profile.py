"""
Tests for Field Trust integration on Profile page (iteration 60).
Verifies that GET /api/profile/{user_id}/record includes field_trust data
and that it matches the user's trust profile from GET /api/user/{user_id}/trust.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"


class TestProfileFieldTrust:
    """Tests for field_trust in profile record response"""
    
    def test_profile_record_includes_field_trust(self):
        """GET /api/profile/{user_id}/record includes field_trust object"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, f"Response not successful: {data}"
        assert "field_trust" in data, "field_trust object missing from profile response"
        
        field_trust = data["field_trust"]
        assert "value_score" in field_trust, "value_score missing from field_trust"
        assert "risk_score" in field_trust, "risk_score missing from field_trust"
        assert "trust_score" in field_trust, "trust_score missing from field_trust"
        
        print(f"✓ field_trust found: value={field_trust['value_score']}, risk={field_trust['risk_score']}, trust={field_trust['trust_score']}")
    
    def test_field_trust_values_are_numeric(self):
        """Field trust scores are numeric values"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        field_trust = data.get("field_trust", {})
        
        assert isinstance(field_trust.get("value_score"), (int, float)), "value_score must be numeric"
        assert isinstance(field_trust.get("risk_score"), (int, float)), "risk_score must be numeric"
        assert isinstance(field_trust.get("trust_score"), (int, float)), "trust_score must be numeric"
        
        print(f"✓ All field_trust scores are numeric")
    
    def test_field_trust_matches_trust_endpoint(self):
        """field_trust values match GET /api/user/{user_id}/trust response"""
        # Get profile data
        profile_response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        profile_trust = profile_data.get("field_trust", {})
        
        # Get trust endpoint data
        trust_response = requests.get(f"{BASE_URL}/api/user/{TEST_USER_ID}/trust")
        assert trust_response.status_code == 200
        trust_data = trust_response.json()
        
        # Compare values (rounded to 1 decimal)
        profile_value = round(profile_trust.get("value_score", 0), 1)
        profile_risk = round(profile_trust.get("risk_score", 0), 1)
        profile_trust_score = round(profile_trust.get("trust_score", 0), 1)
        
        trust_value = round(trust_data.get("value_score", 0), 1)
        trust_risk = round(trust_data.get("risk_score", 0), 1)
        trust_trust_score = round(trust_data.get("trust_score", 0), 1)
        
        # Allow small variance due to concurrent test execution adding value/risk
        assert abs(profile_value - trust_value) <= 1.0, f"value_score mismatch: profile={profile_value}, trust={trust_value}"
        assert abs(profile_risk - trust_risk) <= 1.0, f"risk_score mismatch: profile={profile_risk}, trust={trust_risk}"
        assert abs(profile_trust_score - trust_trust_score) <= 2.0, f"trust_score mismatch: profile={profile_trust_score}, trust={trust_trust_score}"
        
        print(f"✓ field_trust matches trust endpoint: value={profile_value}, risk={profile_risk}, trust={profile_trust_score}")
    
    def test_trust_score_calculation_correct(self):
        """trust_score = value_score - risk_score"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        field_trust = data.get("field_trust", {})
        value_score = field_trust.get("value_score", 0)
        risk_score = field_trust.get("risk_score", 0)
        trust_score = field_trust.get("trust_score", 0)
        
        expected_trust = round(value_score - risk_score, 1)
        actual_trust = round(trust_score, 1)
        
        assert abs(actual_trust - expected_trust) < 0.2, f"trust_score calculation wrong: {trust_score} != {value_score} - {risk_score}"
        print(f"✓ Trust calculation verified: {actual_trust} ≈ {value_score} - {risk_score}")


class TestExistingProfileElements:
    """Regression tests to ensure existing profile elements still work"""
    
    def test_profile_identity_present(self):
        """Profile includes identity section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "identity" in data
        identity = data["identity"]
        assert "alias" in identity
        assert "country" in identity
        assert "dominant_direction" in identity
        print(f"✓ Identity present: alias={identity.get('alias')}")
    
    def test_profile_value_growth_present(self):
        """Profile includes value_growth section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "value_growth" in data
        vg = data["value_growth"]
        assert "total_actions" in vg
        assert "impact_score" in vg
        assert "streak" in vg
        print(f"✓ Value growth present: actions={vg.get('total_actions')}, streak={vg.get('streak')}")
    
    def test_profile_direction_distribution_present(self):
        """Profile includes direction_distribution section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "direction_distribution" in data
        dd = data["direction_distribution"]
        assert "contribution" in dd or "recovery" in dd or "order" in dd or "exploration" in dd
        print(f"✓ Direction distribution present: {dd}")
    
    def test_profile_opposition_axes_present(self):
        """Profile includes opposition_axes section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "opposition_axes" in data
        axes = data["opposition_axes"]
        assert "chaos_order" in axes
        assert "ego_collective" in axes
        assert "exploration_stability" in axes
        print(f"✓ Opposition axes present: {axes}")
    
    def test_profile_influence_chain_present(self):
        """Profile includes influence_chain section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "influence_chain" in data
        ic = data["influence_chain"]
        assert "total_invited" in ic
        print(f"✓ Influence chain present: invited={ic.get('total_invited')}")
    
    def test_profile_action_record_present(self):
        """Profile includes action_record section"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "action_record" in data
        ar = data["action_record"]
        assert isinstance(ar, list)
        print(f"✓ Action record present: {len(ar)} actions")
    
    def test_profile_ai_interpretation_present(self):
        """Profile includes ai_profile_interpretation"""
        response = requests.get(f"{BASE_URL}/api/profile/{TEST_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_profile_interpretation" in data
        ai_text = data["ai_profile_interpretation"]
        # Check for Hebrew characters
        if ai_text:
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in ai_text)
            print(f"✓ AI interpretation present (Hebrew={has_hebrew}): '{ai_text[:60]}...'")
        else:
            print("✓ AI interpretation field present (empty)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

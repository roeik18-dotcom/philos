"""
Test cases for the redesigned Public Profile Page (Human Action Record)
Testing iteration 55 - Dark theme profile with field_contribution and share features
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
MAIN_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
INVITEE_USER_ID = "2d720b49-cd32-4378-aa4a-10dfe58f88e2"


class TestProfileRecordEndpoint:
    """Test the /api/profile/{user_id}/record endpoint"""
    
    def test_profile_record_returns_success(self):
        """Test profile record endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        print("✓ Profile record returns success")

    def test_profile_record_identity_section(self):
        """Test identity section contains required fields"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        identity = data.get("identity", {})
        assert "alias" in identity, "Missing alias in identity"
        assert "country" in identity, "Missing country in identity"
        assert "member_since" in identity, "Missing member_since in identity"
        assert "dominant_direction" in identity, "Missing dominant_direction in identity"
        assert "dominant_direction_he" in identity, "Missing dominant_direction_he in identity"
        assert "niche_label_he" in identity or identity.get("niche") is None, "Niche field structure issue"
        
        print(f"✓ Identity section valid: alias={identity.get('alias')}, country={identity.get('country')}")

    def test_profile_record_direction_badge(self):
        """Test dominant direction badge data is present"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        identity = data.get("identity", {})
        # Direction badge should show if there's a dominant direction
        if identity.get("dominant_direction"):
            assert identity.get("dominant_direction_he"), "Missing Hebrew direction label"
            print(f"✓ Direction badge: {identity.get('dominant_direction_he')}")
        else:
            print("✓ No dominant direction yet (user may have few actions)")

    def test_profile_record_invited_by_field(self):
        """Test invitee profile shows invited_by_alias"""
        response = requests.get(f"{BASE_URL}/api/profile/{INVITEE_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        identity = data.get("identity", {})
        # Invitee should have invited_by_alias
        invited_by = identity.get("invited_by_alias")
        assert invited_by is not None, "Invitee should have invited_by_alias"
        print(f"✓ Invited by alias present: {invited_by}")

    def test_profile_record_value_growth_stats(self):
        """Test value growth stats (impact, actions, streak)"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        value_growth = data.get("value_growth", {})
        assert "impact_score" in value_growth, "Missing impact_score"
        assert "total_actions" in value_growth, "Missing total_actions"
        assert "streak" in value_growth, "Missing streak"
        
        # Data type validation
        assert isinstance(value_growth["total_actions"], int), "total_actions should be int"
        assert isinstance(value_growth["streak"], int), "streak should be int"
        
        print(f"✓ Value growth stats: impact={value_growth.get('impact_score')}, actions={value_growth.get('total_actions')}, streak={value_growth.get('streak')}")

    def test_profile_record_field_contribution_present(self):
        """Test field_contribution object exists with required fields"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        field_contribution = data.get("field_contribution")
        assert field_contribution is not None, "Missing field_contribution object"
        assert "total_actions" in field_contribution, "Missing total_actions in field_contribution"
        assert "days_active" in field_contribution, "Missing days_active in field_contribution"
        assert "field_percentage" in field_contribution, "Missing field_percentage in field_contribution"
        
        # field_percentage should be a number
        field_pct = field_contribution["field_percentage"]
        assert isinstance(field_pct, (int, float)), f"field_percentage should be number, got {type(field_pct)}"
        
        print(f"✓ Field contribution: actions={field_contribution.get('total_actions')}, days={field_contribution.get('days_active')}, pct={field_pct}%")

    def test_profile_record_direction_distribution(self):
        """Test direction distribution bar data"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        dir_dist = data.get("direction_distribution", {})
        expected_dirs = ['contribution', 'recovery', 'order', 'exploration']
        for d in expected_dirs:
            assert d in dir_dist, f"Missing {d} in direction_distribution"
            assert isinstance(dir_dist[d], int), f"{d} should be int"
        
        print(f"✓ Direction distribution: {dir_dist}")

    def test_profile_record_opposition_axes(self):
        """Test opposition axes data (3 tension arcs)"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        axes = data.get("opposition_axes", {})
        expected_axes = ['chaos_order', 'ego_collective', 'exploration_stability']
        for axis in expected_axes:
            assert axis in axes, f"Missing {axis} in opposition_axes"
            val = axes[axis]
            assert 0 <= val <= 100, f"{axis} value {val} out of range [0,100]"
        
        print(f"✓ Opposition axes: chaos_order={axes['chaos_order']}, ego_collective={axes['ego_collective']}, exploration_stability={axes['exploration_stability']}")

    def test_profile_record_influence_chain(self):
        """Test influence chain section (invited_by, invitees, active, credits)"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        chain = data.get("influence_chain", {})
        # Required fields
        assert "invitees" in chain, "Missing invitees in influence_chain"
        assert "active_invitees" in chain, "Missing active_invitees in influence_chain"
        assert "invite_credits" in chain, "Missing invite_credits in influence_chain"
        assert "total_invited" in chain, "Missing total_invited in influence_chain"
        
        # Data type checks
        assert isinstance(chain["invitees"], list), "invitees should be list"
        assert isinstance(chain["active_invitees"], int), "active_invitees should be int"
        assert isinstance(chain["invite_credits"], int), "invite_credits should be int"
        
        print(f"✓ Influence chain: invitees={len(chain['invitees'])}, active={chain['active_invitees']}, credits={chain['invite_credits']}")

    def test_profile_record_action_record(self):
        """Test action record (expandable action cards with meanings)"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        action_record = data.get("action_record", [])
        assert isinstance(action_record, list), "action_record should be list"
        
        if len(action_record) > 0:
            action = action_record[0]
            assert "direction" in action, "Action missing direction"
            assert "direction_he" in action, "Action missing direction_he"
            assert "action_he" in action, "Action missing action_he"
            assert "impact" in action, "Action missing impact"
            assert "meanings" in action, "Action missing meanings"
            
            meanings = action.get("meanings", {})
            assert "personal_he" in meanings, "Meanings missing personal_he"
            assert "social_he" in meanings, "Meanings missing social_he"
            assert "value_he" in meanings, "Meanings missing value_he"
            assert "system_he" in meanings, "Meanings missing system_he"
            
            print(f"✓ Action record has {len(action_record)} actions with meanings")
        else:
            print("✓ Action record is empty (user has no actions)")

    def test_profile_record_user_without_inviter(self):
        """Test profile for main user (may or may not have inviter)"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        identity = data.get("identity", {})
        # Main user may or may not have invited_by_alias - just check it renders
        invited_by = identity.get("invited_by_alias")
        print(f"✓ Main user invited_by_alias: {invited_by}")

    def test_profile_record_nonexistent_user(self):
        """Test profile for nonexistent user should return something (empty profile or 404)"""
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/profile/{fake_user_id}/record")
        # Endpoint may return success with empty data or 404
        assert response.status_code in [200, 404], f"Unexpected status {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            # Should still have success=True with minimal data
            assert data.get("success") is True
            print("✓ Nonexistent user returns empty profile")
        else:
            print("✓ Nonexistent user returns 404")


class TestProfileShareData:
    """Test that the share card has all required data"""
    
    def test_share_card_has_stats_data(self):
        """Test that impact, actions, streak, field_contribution% are present for share card"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        # Stats for share card
        value_growth = data.get("value_growth", {})
        field_contrib = data.get("field_contribution", {})
        
        assert value_growth.get("impact_score") is not None, "Missing impact for share"
        assert value_growth.get("total_actions") is not None, "Missing actions for share"
        assert value_growth.get("streak") is not None, "Missing streak for share"
        assert field_contrib.get("field_percentage") is not None, "Missing field_percentage for share"
        
        print(f"✓ Share card stats available: impact={value_growth['impact_score']}, actions={value_growth['total_actions']}, streak={value_growth['streak']}, field%={field_contrib['field_percentage']}")

    def test_share_card_has_axes_data(self):
        """Test that axes data is present for share card"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        axes = data.get("opposition_axes", {})
        assert len(axes) == 3, "Should have 3 opposition axes"
        print(f"✓ Share card axes available: {list(axes.keys())}")

    def test_share_card_has_influence_data(self):
        """Test that influence chain data is present for share card"""
        response = requests.get(f"{BASE_URL}/api/profile/{MAIN_USER_ID}/record")
        assert response.status_code == 200
        data = response.json()
        
        chain = data.get("influence_chain", {})
        assert "total_invited" in chain, "Missing total_invited for share"
        assert "active_invitees" in chain, "Missing active_invitees for share"
        assert "invite_credits" in chain, "Missing invite_credits for share"
        
        print(f"✓ Share card influence data available: invited={chain['total_invited']}, active={chain['active_invitees']}, credits={chain['invite_credits']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

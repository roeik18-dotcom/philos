"""
Test Suite: Consequence Transparency Panel Backend Tests
Tests the /api/position/{user_id} endpoint for the new consequence_panel field
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://philos-status.preview.emergentagent.com')


class TestConsequencePanelAPI:
    """Tests for GET /api/position/{user_id} consequence_panel field"""

    # Test users with known states
    AT_RISK_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"  # Has active risk signals
    AT_RISK_USER_2_ID = "0c98a493-3148-4c72-88e7-662baa393d11"  # Has active risk signals
    RISING_USER_ID = "ff309373-cbc9-4a3e-a7f2-153609bda629"  # Rising status

    def test_position_endpoint_returns_consequence_panel(self):
        """Verify consequence_panel object is returned"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "consequence_panel" in data
        assert isinstance(data["consequence_panel"], dict)
        print(f"PASS: consequence_panel object exists in response")

    def test_consequence_panel_has_meaning_field(self):
        """Verify consequence_panel contains meaning field"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        panel = data["consequence_panel"]
        assert "meaning" in panel
        assert isinstance(panel["meaning"], str)
        assert len(panel["meaning"]) > 0
        print(f"PASS: meaning field exists: '{panel['meaning']}'")

    def test_consequence_panel_has_next_step_field(self):
        """Verify consequence_panel contains next_step field"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        panel = data["consequence_panel"]
        assert "next_step" in panel
        assert isinstance(panel["next_step"], str)
        assert len(panel["next_step"]) > 0
        print(f"PASS: next_step field exists: '{panel['next_step']}'")

    def test_at_risk_with_risk_signals_meaning(self):
        """Verify atRisk status with risk signals mentions 'reduced visibility'"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"]["status"] == "atRisk"
        panel = data["consequence_panel"]
        
        # atRisk due to risk signals should mention "reduced visibility"
        assert "reduced visibility" in panel["meaning"].lower()
        assert "risk signals" in panel["meaning"].lower()
        print(f"PASS: atRisk (risk signals) meaning mentions 'reduced visibility': '{panel['meaning']}'")

    def test_at_risk_with_risk_signals_next_step(self):
        """Verify atRisk next_step provides actionable guidance"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"]["status"] == "atRisk"
        panel = data["consequence_panel"]
        
        # next_step should mention posting authentic actions or resolving
        assert "post" in panel["next_step"].lower() or "action" in panel["next_step"].lower()
        print(f"PASS: atRisk next_step is actionable: '{panel['next_step']}'")

    def test_rising_status_meaning_mentions_visibility_boost(self):
        """Verify rising status mentions 'visibility boost'"""
        response = requests.get(f"{BASE_URL}/api/position/{self.RISING_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        
        # This user should be rising status
        if data["status"]["status"] == "rising":
            panel = data["consequence_panel"]
            assert "boost" in panel["meaning"].lower() or "visibility" in panel["meaning"].lower()
            print(f"PASS: rising status meaning mentions boost: '{panel['meaning']}'")
        else:
            # Status may change over time - check that panel still works
            panel = data["consequence_panel"]
            assert "meaning" in panel
            assert "next_step" in panel
            print(f"INFO: User status is {data['status']['status']}, panel still valid")

    def test_consequence_multiplier_alignment(self):
        """Verify consequence_multiplier aligns with status"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        status = data["status"]["status"]
        multiplier = data["consequence_multiplier"]
        
        # At Risk users should have 0.70 multiplier
        if status == "atRisk":
            assert multiplier == 0.7
            print(f"PASS: atRisk multiplier is 0.70")
        elif status == "rising":
            assert multiplier == 1.15
            print(f"PASS: rising multiplier is 1.15")
        elif status == "stable":
            assert multiplier == 1.0
            print(f"PASS: stable multiplier is 1.0")
        elif status == "decaying":
            assert multiplier == 0.85
            print(f"PASS: decaying multiplier is 0.85")

    def test_at_risk_user_2_consequence_panel(self):
        """Verify second at-risk user has correct consequence_panel"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_2_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["status"]["status"] == "atRisk"
        
        panel = data["consequence_panel"]
        assert "meaning" in panel
        assert "next_step" in panel
        assert "reduced visibility" in panel["meaning"].lower()
        print(f"PASS: User 2 atRisk consequence_panel valid")

    def test_at_risk_inactivity_meaning_differs_from_risk_signals(self):
        """Verify atRisk due to inactivity has different meaning than risk signals"""
        # Get a user with no activity (test user)
        response = requests.get(f"{BASE_URL}/api/position/test-user-stable-001")
        assert response.status_code == 200

        data = response.json()
        
        # If atRisk due to inactivity, meaning should mention "inactivity"
        if data["status"]["status"] == "atRisk" and "inactivity" in data["status"].get("reason", "").lower():
            panel = data["consequence_panel"]
            assert "inactivity" in panel["meaning"].lower() or "inactive" in panel["meaning"].lower()
            print(f"PASS: atRisk (inactivity) meaning correctly mentions inactivity: '{panel['meaning']}'")
        else:
            print(f"INFO: User status is {data['status']['status']}, reason: {data['status'].get('reason', 'N/A')}")

    def test_multiplier_format_in_api_response(self):
        """Verify multiplier is returned as a decimal number (for Nx formatting)"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        multiplier = data["consequence_multiplier"]
        
        # Should be a number
        assert isinstance(multiplier, (int, float))
        # Should be a reasonable multiplier value (0.5 to 1.5 range)
        assert 0.5 <= multiplier <= 1.5
        # At Risk should be 0.70
        assert multiplier == 0.7
        print(f"PASS: Multiplier format valid: {multiplier}")

    def test_consequence_panel_structure_complete(self):
        """Verify consequence_panel has exactly the expected structure"""
        response = requests.get(f"{BASE_URL}/api/position/{self.AT_RISK_USER_ID}")
        assert response.status_code == 200

        data = response.json()
        panel = data["consequence_panel"]
        
        # Should have exactly two keys
        expected_keys = {"meaning", "next_step"}
        actual_keys = set(panel.keys())
        assert actual_keys == expected_keys, f"Expected {expected_keys}, got {actual_keys}"
        print(f"PASS: consequence_panel has correct structure: {actual_keys}")


class TestConsequencePanelStatusVariations:
    """Tests for consequence_panel message variations based on status"""

    def test_status_meta_in_response(self):
        """Verify status object includes icon, label, color"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200

        data = response.json()
        status = data["status"]
        
        assert "status" in status
        assert "icon" in status
        assert "label" in status
        assert "color" in status
        print(f"PASS: status object has all required fields")

    def test_at_risk_status_color_is_red(self):
        """Verify atRisk status has red color (#dc2626)"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"]["status"] == "atRisk"
        assert data["status"]["color"] == "#dc2626"
        print(f"PASS: atRisk color is correct: {data['status']['color']}")

    def test_at_risk_status_icon_is_warning(self):
        """Verify atRisk status has warning icon"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"]["status"] == "atRisk"
        assert data["status"]["icon"] == "warning"
        print(f"PASS: atRisk icon is warning")

    def test_rising_multiplier_greater_than_1(self):
        """Verify rising status has multiplier > 1.0"""
        user_id = "ff309373-cbc9-4a3e-a7f2-153609bda629"
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200

        data = response.json()
        
        if data["status"]["status"] == "rising":
            assert data["consequence_multiplier"] > 1.0
            assert data["consequence_multiplier"] == 1.15
            print(f"PASS: rising multiplier is > 1.0: {data['consequence_multiplier']}")
        else:
            print(f"INFO: User status changed to {data['status']['status']}")

    def test_consequence_panel_returns_for_new_user(self):
        """Verify consequence_panel works for users with zero activity"""
        response = requests.get(f"{BASE_URL}/api/position/test-user-new-001")
        assert response.status_code == 200

        data = response.json()
        assert "consequence_panel" in data
        assert "meaning" in data["consequence_panel"]
        assert "next_step" in data["consequence_panel"]
        print(f"PASS: consequence_panel works for new users")


class TestRegressionFromIteration95:
    """Regression tests to ensure previous features still work"""

    def test_feed_loads_with_rank_score(self):
        """Verify feed still returns rank_score from iteration 95"""
        response = requests.get(f"{BASE_URL}/api/actions/feed")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "actions" in data
        
        if len(data["actions"]) > 0:
            first_action = data["actions"][0]
            assert "rank_score" in first_action
            print(f"PASS: Feed returns rank_score: {first_action.get('rank_score')}")
        else:
            print("INFO: No actions in feed to verify")

    def test_position_returns_all_expected_fields(self):
        """Verify position endpoint returns all expected fields"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/position/{user_id}")
        assert response.status_code == 200

        data = response.json()
        
        # Fields from previous iterations
        expected_fields = [
            "success", "position", "label", "public_actions", "private_actions",
            "unique_reactors", "total_trust", "active_referrals", "factors",
            "status", "consequence_multiplier", "consequence_panel"
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"PASS: All expected fields present in position response")

    def test_orientation_endpoint_works(self):
        """Verify orientation endpoint still works from iteration 95"""
        user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
        response = requests.get(f"{BASE_URL}/api/orientation/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "consequence_multiplier" in data
        print(f"PASS: Orientation endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

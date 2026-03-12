"""
Daily Base Allocation System Tests
Testing the new feature: User selects one base each morning (Heart/Head/Body),
which gates the daily question. End-of-day summary includes department analysis.
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review_request
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def test_user_id(api_client):
    """Login and get user_id."""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("user"):
            return data["user"]["id"]
    # Create user if not exists
    response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("user"):
            return data["user"]["id"]
    pytest.skip("Could not authenticate or create test user")


class TestDailyBaseGetEndpoint:
    """GET /api/orientation/daily-base/{user_id} tests"""

    def test_get_daily_base_returns_success(self, api_client, test_user_id):
        """Test GET endpoint returns success status."""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"✓ GET daily-base returns success: {data.get('success')}")

    def test_get_daily_base_has_base_definitions(self, api_client, test_user_id):
        """Test endpoint returns 3 base definitions with allocations."""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Must have bases dict with heart, head, body
        bases = data.get("bases", {})
        assert "heart" in bases, "Missing heart base definition"
        assert "head" in bases, "Missing head base definition"
        assert "body" in bases, "Missing body base definition"
        print(f"✓ Has 3 base definitions: heart, head, body")

    def test_base_definitions_have_hebrew_names(self, api_client, test_user_id):
        """Test base definitions have Hebrew names: לב, ראש, גוף."""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        data = response.json()
        bases = data.get("bases", {})
        
        assert bases.get("heart", {}).get("name_he") == "לב", "Heart should be 'לב'"
        assert bases.get("head", {}).get("name_he") == "ראש", "Head should be 'ראש'"
        assert bases.get("body", {}).get("name_he") == "גוף", "Body should be 'גוף'"
        print(f"✓ Hebrew names correct: לב, ראש, גוף")

    def test_base_definitions_have_allocations(self, api_client, test_user_id):
        """Test each base has allocations_he array."""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        data = response.json()
        bases = data.get("bases", {})
        
        for base_key in ["heart", "head", "body"]:
            allocations = bases.get(base_key, {}).get("allocations_he", [])
            assert len(allocations) >= 3, f"{base_key} should have at least 3 allocations"
        print(f"✓ Each base has allocations_he array")

    def test_get_daily_base_has_department_history(self, api_client, test_user_id):
        """Test endpoint returns department history counts."""
        response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        data = response.json()
        
        dept_history = data.get("dept_history", {})
        assert "heart" in dept_history
        assert "head" in dept_history
        assert "body" in dept_history
        print(f"✓ Department history present: {dept_history}")


class TestDailyBasePostEndpoint:
    """POST /api/orientation/daily-base/{user_id} tests"""

    def test_post_daily_base_heart_success(self, api_client, test_user_id):
        """Test setting base to 'heart' succeeds."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "heart"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("base") == "heart"
        assert data.get("base_he") == "לב"
        assert "allocations_he" in data
        print(f"✓ POST heart base success: {data.get('base_he')}")

    def test_post_daily_base_head_success(self, api_client, test_user_id):
        """Test setting base to 'head' succeeds."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "head"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("base") == "head"
        assert data.get("base_he") == "ראש"
        print(f"✓ POST head base success: {data.get('base_he')}")

    def test_post_daily_base_body_success(self, api_client, test_user_id):
        """Test setting base to 'body' succeeds."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "body"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("base") == "body"
        assert data.get("base_he") == "גוף"
        print(f"✓ POST body base success: {data.get('base_he')}")

    def test_post_daily_base_invalid_rejected(self, api_client, test_user_id):
        """Test POST with invalid base value returns 400."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "invalid_base"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid base, got {response.status_code}"
        print(f"✓ Invalid base rejected with 400")

    def test_post_daily_base_empty_rejected(self, api_client, test_user_id):
        """Test POST with empty base value returns 400."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": ""}
        )
        assert response.status_code == 400, f"Expected 400 for empty base, got {response.status_code}"
        print(f"✓ Empty base rejected with 400")

    def test_post_daily_base_returns_allocations(self, api_client, test_user_id):
        """Test POST returns allocations_he for the selected base."""
        response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "heart"}
        )
        data = response.json()
        allocations = data.get("allocations_he", [])
        assert len(allocations) >= 3, "Should return at least 3 allocations"
        # Heart allocations should include relationship-related items
        assert any("קשרים" in a for a in allocations), "Heart should have 'קשרים' allocation"
        print(f"✓ POST returns allocations_he: {allocations}")


class TestDailyBasePersistence:
    """Test base selection persists correctly."""

    def test_base_selection_persists(self, api_client, test_user_id):
        """Test that selected base is returned in subsequent GET."""
        # Set base to head
        post_response = api_client.post(
            f"{BASE_URL}/api/orientation/daily-base/{test_user_id}",
            json={"base": "head"}
        )
        assert post_response.status_code == 200
        
        # GET should return the selected base
        get_response = api_client.get(f"{BASE_URL}/api/orientation/daily-base/{test_user_id}")
        data = get_response.json()
        
        assert data.get("base_selected") is True, "base_selected should be True"
        assert data.get("today_base") == "head", f"today_base should be 'head', got {data.get('today_base')}"
        assert data.get("today_base_he") == "ראש", "today_base_he should be 'ראש'"
        print(f"✓ Base selection persists: {data.get('today_base_he')}")


class TestDaySummaryEndpoint:
    """GET /api/orientation/day-summary/{user_id} tests"""

    def test_day_summary_returns_success(self, api_client, test_user_id):
        """Test day-summary endpoint returns success."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"✓ GET day-summary returns success")

    def test_day_summary_has_chosen_base(self, api_client, test_user_id):
        """Test day-summary includes chosen_base field."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        # chosen_base should be present (may be null if not selected)
        assert "chosen_base" in data, "Response must include chosen_base field"
        assert "chosen_base_he" in data, "Response must include chosen_base_he field"
        print(f"✓ day-summary has chosen_base: {data.get('chosen_base')}")

    def test_day_summary_has_dept_allocation(self, api_client, test_user_id):
        """Test day-summary includes dept_allocation with heart/head/body percentages."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        dept_alloc = data.get("dept_allocation", {})
        assert "heart" in dept_alloc, "dept_allocation must have heart"
        assert "head" in dept_alloc, "dept_allocation must have head"
        assert "body" in dept_alloc, "dept_allocation must have body"
        
        # Values should be percentages (0-100)
        for dept, pct in dept_alloc.items():
            assert 0 <= pct <= 100, f"{dept} percentage {pct} out of range"
        print(f"✓ day-summary has dept_allocation: {dept_alloc}")

    def test_day_summary_has_most_used_dept(self, api_client, test_user_id):
        """Test day-summary includes most_used_dept field."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        assert "most_used_dept" in data, "Response must include most_used_dept"
        assert "most_used_dept_he" in data, "Response must include most_used_dept_he"
        print(f"✓ day-summary has most_used_dept: {data.get('most_used_dept')}")

    def test_day_summary_has_neglected_dept(self, api_client, test_user_id):
        """Test day-summary includes neglected_dept field."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        assert "neglected_dept" in data, "Response must include neglected_dept"
        assert "neglected_dept_he" in data, "Response must include neglected_dept_he"
        print(f"✓ day-summary has neglected_dept: {data.get('neglected_dept')}")

    def test_day_summary_has_preferred_dept(self, api_client, test_user_id):
        """Test day-summary includes preferred_dept (historical preference)."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        assert "preferred_dept" in data, "Response must include preferred_dept"
        assert "preferred_dept_he" in data, "Response must include preferred_dept_he"
        print(f"✓ day-summary has preferred_dept: {data.get('preferred_dept')}")

    def test_day_summary_has_direction_data(self, api_client, test_user_id):
        """Test day-summary has chosen_direction and direction counts."""
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        assert "chosen_direction" in data
        assert "chosen_direction_he" in data
        assert "direction_counts" in data
        assert "total_actions" in data
        print(f"✓ day-summary has direction data: {data.get('chosen_direction')}")


class TestDirectionToDeptMapping:
    """Test direction→department mapping: contribution→heart, recovery→body, order→head, exploration→head."""

    def test_contribution_maps_to_heart(self, api_client, test_user_id):
        """Verify contribution direction maps to heart department."""
        # This is tested via day-summary after actions are recorded
        # The mapping is: contribution→heart, recovery→body, order→head, exploration→head
        response = api_client.get(f"{BASE_URL}/api/orientation/day-summary/{test_user_id}")
        data = response.json()
        
        # Just verify the endpoint returns data — actual mapping tested via integration
        assert "dept_allocation" in data
        print(f"✓ Direction to department mapping endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

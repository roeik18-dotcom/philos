"""
Test Core Theory Integration Phase - 4 new features:
1. Daily Opening Section (GET /api/orientation/daily-opening/{user_id})
2. End of Day Summary (GET /api/orientation/day-summary/{user_id})
3. Globe Activity (GET /api/orientation/globe-activity)
4. Directions (GET /api/orientation/directions)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDailyOpeningEndpoint:
    """Tests for GET /api/orientation/daily-opening/{user_id}"""

    def test_daily_opening_returns_200(self):
        """Test endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        assert response.status_code == 200
        print("✓ Daily opening returns 200")

    def test_daily_opening_has_success_true(self):
        """Test response has success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert data.get("success") is True
        print("✓ Daily opening has success=true")

    def test_daily_opening_has_compass_state(self):
        """Test response has compass_state with 4 directions"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        compass_state = data.get("compass_state")
        assert compass_state is not None
        assert "contribution" in compass_state
        assert "recovery" in compass_state
        assert "order" in compass_state
        assert "exploration" in compass_state
        print("✓ Daily opening has compass_state with 4 directions")

    def test_daily_opening_has_dominant_force(self):
        """Test response has dominant_force field"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert "dominant_force" in data
        assert "dominant_force_he" in data
        print(f"✓ Daily opening has dominant_force: {data['dominant_force']}")

    def test_daily_opening_has_suggested_direction(self):
        """Test response has suggested_direction"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert "suggested_direction" in data
        assert data["suggested_direction"] in ["contribution", "recovery", "order", "exploration"]
        assert "suggested_direction_he" in data
        print(f"✓ Daily opening has suggested_direction: {data['suggested_direction']}")

    def test_daily_opening_has_greeting_he(self):
        """Test response has Hebrew greeting"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        assert "greeting_he" in data
        assert data["greeting_he"] in ["בוקר טוב", "צהריים טובים", "ערב טוב"]
        print(f"✓ Daily opening has greeting_he: {data['greeting_he']}")

    def test_daily_opening_has_theory(self):
        """Test response has theory object with explanation"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test-user-123")
        data = response.json()
        theory = data.get("theory")
        assert theory is not None
        assert "explanation_he" in theory
        assert "label_he" in theory
        print("✓ Daily opening has theory object")


class TestDaySummaryEndpoint:
    """Tests for GET /api/orientation/day-summary/{user_id}"""

    def test_day_summary_returns_200(self):
        """Test endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        assert response.status_code == 200
        print("✓ Day summary returns 200")

    def test_day_summary_has_success_true(self):
        """Test response has success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert data.get("success") is True
        print("✓ Day summary has success=true")

    def test_day_summary_has_direction_counts(self):
        """Test response has direction_counts with 4 directions"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        direction_counts = data.get("direction_counts")
        assert direction_counts is not None
        assert "contribution" in direction_counts
        assert "recovery" in direction_counts
        assert "order" in direction_counts
        assert "exploration" in direction_counts
        print("✓ Day summary has direction_counts")

    def test_day_summary_has_streak(self):
        """Test response has streak field"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert "streak" in data
        assert isinstance(data["streak"], int)
        print(f"✓ Day summary has streak: {data['streak']}")

    def test_day_summary_has_impact_on_field(self):
        """Test response has impact_on_field percentage"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert "impact_on_field" in data
        print(f"✓ Day summary has impact_on_field: {data['impact_on_field']}")

    def test_day_summary_has_global_field_effect(self):
        """Test response has global_field_effect distribution"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        field_effect = data.get("global_field_effect")
        assert field_effect is not None
        assert "contribution" in field_effect
        assert "recovery" in field_effect
        assert "order" in field_effect
        assert "exploration" in field_effect
        print("✓ Day summary has global_field_effect")

    def test_day_summary_has_reflection_he(self):
        """Test response has Hebrew reflection text"""
        response = requests.get(f"{BASE_URL}/api/orientation/day-summary/test-user-123")
        data = response.json()
        assert "reflection_he" in data
        assert isinstance(data["reflection_he"], str)
        assert len(data["reflection_he"]) > 0
        print(f"✓ Day summary has reflection_he")


class TestGlobeActivityEndpoint:
    """Tests for GET /api/orientation/globe-activity"""

    def test_globe_activity_returns_200(self):
        """Test endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        print("✓ Globe activity returns 200")

    def test_globe_activity_has_success_true(self):
        """Test response has success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert data.get("success") is True
        print("✓ Globe activity has success=true")

    def test_globe_activity_has_points_array(self):
        """Test response has points array"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        points = data.get("points")
        assert points is not None
        assert isinstance(points, list)
        print(f"✓ Globe activity has points array with {len(points)} points")

    def test_globe_activity_points_have_lat_lng(self):
        """Test points have lat/lng coordinates"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        points = data.get("points", [])
        if len(points) > 0:
            point = points[0]
            assert "lat" in point
            assert "lng" in point
            assert isinstance(point["lat"], (int, float))
            assert isinstance(point["lng"], (int, float))
            print("✓ Globe activity points have lat/lng")
        else:
            print("⚠ No points to verify (may be empty due to time window)")

    def test_globe_activity_points_have_direction_and_color(self):
        """Test points have direction and color"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        points = data.get("points", [])
        if len(points) > 0:
            point = points[0]
            assert "direction" in point
            assert point["direction"] in ["contribution", "recovery", "order", "exploration"]
            assert "color" in point
            print(f"✓ Globe activity points have direction: {point['direction']}, color: {point['color']}")
        else:
            print("⚠ No points to verify")

    def test_globe_activity_has_total_points(self):
        """Test response has total_points count"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        assert "total_points" in data
        assert isinstance(data["total_points"], int)
        print(f"✓ Globe activity has total_points: {data['total_points']}")

    def test_globe_activity_has_color_map(self):
        """Test response has color_map with direction colors"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        data = response.json()
        color_map = data.get("color_map")
        assert color_map is not None
        assert "contribution" in color_map
        assert "recovery" in color_map
        assert "order" in color_map
        assert "exploration" in color_map
        print("✓ Globe activity has color_map")


class TestDirectionsEndpoint:
    """Tests for GET /api/orientation/directions"""

    def test_directions_returns_200(self):
        """Test endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        assert response.status_code == 200
        print("✓ Directions returns 200")

    def test_directions_has_success_true(self):
        """Test response has success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        assert data.get("success") is True
        print("✓ Directions has success=true")

    def test_directions_has_4_directions(self):
        """Test response has 4 direction objects"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        directions = data.get("directions")
        assert directions is not None
        assert "contribution" in directions
        assert "recovery" in directions
        assert "order" in directions
        assert "exploration" in directions
        print("✓ Directions has 4 directions")

    def test_direction_contribution_has_all_fields(self):
        """Test contribution direction has all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        contribution = data.get("directions", {}).get("contribution")
        assert contribution is not None
        assert "label_he" in contribution
        assert "symbol" in contribution
        assert "symbolic_meaning_he" in contribution
        assert "behavior_example_he" in contribution
        assert "field_effect_he" in contribution
        print(f"✓ Contribution has all fields: label_he={contribution['label_he']}")

    def test_direction_recovery_has_all_fields(self):
        """Test recovery direction has all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        recovery = data.get("directions", {}).get("recovery")
        assert recovery is not None
        assert "label_he" in recovery
        assert "symbol" in recovery
        assert "symbolic_meaning_he" in recovery
        assert "behavior_example_he" in recovery
        assert "field_effect_he" in recovery
        print(f"✓ Recovery has all fields: label_he={recovery['label_he']}")

    def test_direction_order_has_all_fields(self):
        """Test order direction has all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        order = data.get("directions", {}).get("order")
        assert order is not None
        assert "label_he" in order
        assert "symbol" in order
        assert "symbolic_meaning_he" in order
        assert "behavior_example_he" in order
        assert "field_effect_he" in order
        print(f"✓ Order has all fields: label_he={order['label_he']}")

    def test_direction_exploration_has_all_fields(self):
        """Test exploration direction has all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        data = response.json()
        exploration = data.get("directions", {}).get("exploration")
        assert exploration is not None
        assert "label_he" in exploration
        assert "symbol" in exploration
        assert "symbolic_meaning_he" in exploration
        assert "behavior_example_he" in exploration
        assert "field_effect_he" in exploration
        print(f"✓ Exploration has all fields: label_he={exploration['label_he']}")

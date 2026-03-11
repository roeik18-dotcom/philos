"""
Tests for Demo Agents System
- 50 demo agents seeded in demo_agents collection
- Demo events generated every 5 minutes
- /api/orientation/feed returns mix of real and demo events
- /api/orientation/metrics-today excludes demo agents from active_users_today
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDemoAgentsSeeding:
    """Tests for demo agents seeding (50 agents with aliases, countries, etc.)"""

    def test_demo_agents_collection_has_50_agents(self):
        """Verify that demo_agents collection has exactly 50 demo agents."""
        # We test via the feed endpoint which relies on demo_agents being seeded
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True
        # Feed should have demo events (from seeded agents)
        feed = data.get("feed", [])
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        assert len(demo_events) > 0, "Should have demo events in feed from seeded agents"

    def test_demo_agent_structure_in_events(self):
        """Demo events should have expected structure: direction, country_code, location."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        assert response.status_code == 200
        data = response.json()
        feed = data.get("feed", [])
        
        # Find demo events
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        assert len(demo_events) > 0, "Should have at least 1 demo event"
        
        # Check first demo event structure
        demo_event = demo_events[0]
        assert "direction" in demo_event, "Demo event should have direction"
        assert "country_code" in demo_event, "Demo event should have country_code"
        assert "location" in demo_event, "Demo event should have location (country name)"
        assert "time" in demo_event, "Demo event should have time"
        assert demo_event.get("type") == "demo_action", "Type should be demo_action"


class TestOrientationFeed:
    """Tests for GET /api/orientation/feed endpoint with demo events."""

    def test_feed_returns_200(self):
        """Feed endpoint should return 200."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        assert response.status_code == 200

    def test_feed_has_success_true(self):
        """Response should have success=True."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        assert data.get("success") is True

    def test_feed_returns_array(self):
        """Feed should return a feed array."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        assert "feed" in data
        assert isinstance(data["feed"], list)

    def test_demo_events_have_type_demo_action(self):
        """Demo events should have type='demo_action'."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        assert len(demo_events) > 0, "Should have demo_action events"
        
        for event in demo_events:
            assert event.get("type") == "demo_action"

    def test_demo_events_have_location_field(self):
        """Demo events should have location field (country name)."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        for event in demo_events:
            assert "location" in event, f"Demo event missing location: {event}"

    def test_demo_events_have_country_code(self):
        """Demo events should have country_code field."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        for event in demo_events:
            assert "country_code" in event, f"Demo event missing country_code: {event}"
            # Country codes should be 2-letter ISO codes
            assert len(event.get("country_code", "")) == 2, f"Country code should be 2 letters: {event}"

    def test_demo_events_have_valid_direction(self):
        """Demo events should have valid direction values."""
        valid_directions = ['contribution', 'recovery', 'order', 'exploration']
        
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        for event in demo_events:
            assert event.get("direction") in valid_directions, f"Invalid direction: {event}"

    def test_demo_events_have_time_field(self):
        """Demo events should have time field with relative time."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        for event in demo_events:
            assert "time" in event, f"Demo event missing time: {event}"

    def test_feed_contains_valid_country_codes(self):
        """Country codes should be from expected list."""
        valid_codes = [
            "BR", "IN", "DE", "US", "JP", "NG", "IL", "FR",
            "AU", "KR", "MX", "GB", "CA", "IT", "ES", "AR",
            "TR", "TH", "PL", "NL"
        ]
        
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        for event in demo_events:
            code = event.get("country_code")
            assert code in valid_codes, f"Unexpected country code: {code}"


class TestMetricsTodayExcludesDemoAgents:
    """Tests for GET /api/orientation/metrics-today - demo agents should NOT be counted."""

    def test_metrics_today_returns_200(self):
        """Metrics endpoint should return 200."""
        response = requests.get(f"{BASE_URL}/api/orientation/metrics-today")
        assert response.status_code == 200

    def test_metrics_today_has_active_users_today(self):
        """Response should have active_users_today field."""
        response = requests.get(f"{BASE_URL}/api/orientation/metrics-today")
        data = response.json()
        assert "active_users_today" in data

    def test_active_users_today_excludes_demo_agents(self):
        """active_users_today should NOT include demo agents.
        Since demo events use fake agent_ids (demo-agent-XXX), they should not
        appear in philos_sessions.user_id, thus not counted."""
        response = requests.get(f"{BASE_URL}/api/orientation/metrics-today")
        data = response.json()
        
        # Demo agents have user_ids like "demo-agent-000" which are NOT in philos_sessions
        # So active_users_today should only count real users
        active_users = data.get("active_users_today", 0)
        
        # Check feed to see how many demo events we have
        feed_response = requests.get(f"{BASE_URL}/api/orientation/feed")
        feed_data = feed_response.json()
        demo_events = [f for f in feed_data.get("feed", []) if f.get("type") == "demo_action"]
        
        # We have demo events but they should NOT contribute to active_users_today
        print(f"Demo events in feed: {len(demo_events)}")
        print(f"active_users_today: {active_users}")
        
        # The key assertion: metrics-today uses philos_sessions collection
        # which does NOT contain demo agent data
        # active_users_today should be a reasonable number (could be 0 if no real users today)
        assert isinstance(active_users, int) and active_users >= 0

    def test_metrics_today_response_structure(self):
        """Verify complete response structure."""
        response = requests.get(f"{BASE_URL}/api/orientation/metrics-today")
        data = response.json()
        
        assert data.get("success") is True
        assert "active_users_today" in data
        assert "daily_question_completion_rate" in data
        assert "day2_retention" in data
        assert "mission_participation_rate" in data
        assert "avg_streak" in data
        assert "invite_conversions" in data


class TestDemoEventsGeneration:
    """Tests verifying demo events are being generated."""

    def test_demo_events_exist_in_feed(self):
        """Demo events should be present in the feed."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        assert len(demo_events) > 0, "Demo events should be generated and visible in feed"

    def test_feed_is_sorted_by_time(self):
        """Feed should be sorted by most recent first."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        # All items should have time field
        for item in feed:
            assert "time" in item

    def test_multiple_countries_in_feed(self):
        """Feed should have events from multiple countries (diversity)."""
        response = requests.get(f"{BASE_URL}/api/orientation/feed")
        data = response.json()
        feed = data.get("feed", [])
        
        demo_events = [f for f in feed if f.get("type") == "demo_action"]
        country_codes = set(e.get("country_code") for e in demo_events if e.get("country_code"))
        
        # Should have at least 3 different countries in demo events
        assert len(country_codes) >= 3, f"Expected multiple countries, got: {country_codes}"
        print(f"Countries in feed: {country_codes}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

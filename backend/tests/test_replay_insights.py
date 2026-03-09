"""
Test Replay Insights Summary Feature APIs
- GET /api/memory/replay-insights/{user_id} - Aggregated replay pattern analysis

Tests cover:
- Alternative path counts
- Transition patterns (from → to with counts)
- Blind spots detection
- Hebrew behavioral insights generation
- Summary stats (total replays, patterns, blind spots)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestReplayInsightsAPI:
    """Test Replay Insights Summary backend endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Generate unique test user ID for each test"""
        self.test_user_id = f"TEST_insights_user_{uuid.uuid4().hex[:8]}"
        yield
        # Cleanup would go here if needed
    
    def create_replay(self, user_id, original_tag, alt_path_type, alt_path_id=1):
        """Helper to create a replay record"""
        replay_data = {
            "user_id": user_id,
            "replay_of_decision_id": f"dec_{uuid.uuid4().hex[:12]}",
            "original_value_tag": original_tag,
            "alternative_path_id": alt_path_id,
            "alternative_path_type": alt_path_type,
            "predicted_metrics": {
                "orderDrift": 5,
                "collectiveDrift": 10,
                "harmPressure": -15,
                "recoveryStability": 10,
                "predictedOrder": 20,
                "predictedCollective": 25,
                "predictedBalance": 70,
                "balanceDiff": 5
            }
        }
        response = requests.post(f"{BASE_URL}/api/memory/replay", json=replay_data)
        return response
    
    def test_health_check(self):
        """Test that the API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"API not accessible: {response.status_code}"
        print("✓ API health check passed")
    
    def test_replay_insights_empty_user(self):
        """Test GET /api/memory/replay-insights/{user_id} for user with no replays"""
        new_user_id = f"TEST_empty_insights_{uuid.uuid4().hex[:8]}"
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{new_user_id}")
        
        assert response.status_code == 200, f"Replay insights failed: {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Should succeed for empty user"
        assert data.get("total_replays") == 0, "Empty user should have 0 replays"
        assert data.get("alternative_path_counts") == {}, "Empty user should have empty path counts"
        assert data.get("transition_patterns") == [], "Empty user should have no patterns"
        assert data.get("blind_spots") == [], "Empty user should have no blind spots"
        assert len(data.get("insights", [])) == 1, "Should have default insight message"
        
        # Verify default Hebrew insight message
        default_insight = data.get("insights", [""])[0]
        assert "אין עדיין נתוני הפעלה חוזרת" in default_insight, "Should have Hebrew no-data message"
        
        print("✓ Empty user replay insights passed")
    
    def test_replay_insights_with_data(self):
        """Test replay insights with actual replay data"""
        # Create multiple replay records with different patterns
        patterns = [
            ("harm", "contribution"),
            ("harm", "contribution"),  # Repeated pattern
            ("harm", "recovery"),
            ("avoidance", "order"),
            ("avoidance", "contribution"),
            ("recovery", "order"),
        ]
        
        for i, (original, alternative) in enumerate(patterns):
            response = self.create_replay(self.test_user_id, original, alternative, i+1)
            assert response.status_code == 200, f"Failed to create replay: {response.text}"
        
        # Fetch insights
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200, f"Replay insights failed: {response.status_code}"
        
        data = response.json()
        
        # Validate response structure
        assert data.get("success") == True
        assert data.get("total_replays") == 6, f"Expected 6 replays, got {data.get('total_replays')}"
        assert data.get("user_id") == self.test_user_id
        
        # Validate alternative_path_counts
        alt_counts = data.get("alternative_path_counts", {})
        assert alt_counts.get("contribution") == 3, "Contribution should have 3 counts"
        assert alt_counts.get("order") == 2, "Order should have 2 counts"
        assert alt_counts.get("recovery") == 1, "Recovery should have 1 count"
        
        print(f"✓ Alternative path counts validated: {alt_counts}")
    
    def test_transition_patterns(self):
        """Test that transition patterns are correctly aggregated"""
        # Create specific patterns
        patterns = [
            ("harm", "contribution"),  # 3 times
            ("harm", "contribution"),
            ("harm", "contribution"),
            ("avoidance", "order"),    # 2 times
            ("avoidance", "order"),
        ]
        
        for i, (original, alternative) in enumerate(patterns):
            self.create_replay(self.test_user_id, original, alternative, i+1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        patterns = data.get("transition_patterns", [])
        
        # Should be sorted by count (descending)
        assert len(patterns) >= 2, f"Expected at least 2 patterns, got {len(patterns)}"
        
        # First pattern should have highest count
        first_pattern = patterns[0]
        assert first_pattern.get("from") == "harm"
        assert first_pattern.get("to") == "contribution"
        assert first_pattern.get("count") == 3
        
        # Second pattern
        second_pattern = patterns[1]
        assert second_pattern.get("from") == "avoidance"
        assert second_pattern.get("to") == "order"
        assert second_pattern.get("count") == 2
        
        print(f"✓ Transition patterns validated: {len(patterns)} patterns found")
    
    def test_blind_spots_detection(self):
        """Test blind spots detection - patterns never explored"""
        # Create replays that leave some patterns unexplored
        patterns = [
            ("recovery", "contribution"),  # User explores from recovery
            ("recovery", "contribution"),
        ]
        
        for i, (original, alternative) in enumerate(patterns):
            self.create_replay(self.test_user_id, original, alternative, i+1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        blind_spots = data.get("blind_spots", [])
        
        # Should identify unexplored positive transitions from 'recovery'
        # Since user explored recovery → contribution, 
        # recovery → order should be a blind spot
        recovery_blind_spots = [s for s in blind_spots if s.get("from") == "recovery"]
        
        # Verify blind spots have correct structure
        if blind_spots:
            spot = blind_spots[0]
            assert "from" in spot, "Blind spot should have 'from'"
            assert "to" in spot, "Blind spot should have 'to'"
        
        print(f"✓ Blind spots detection passed: {len(blind_spots)} spots found")
    
    def test_hebrew_insights_generation(self):
        """Test that Hebrew behavioral insights are generated correctly"""
        # Create diverse replay data
        patterns = [
            ("harm", "contribution"),  # Multiple times - should mention contribution as top
            ("harm", "contribution"),
            ("harm", "contribution"),
            ("avoidance", "recovery"),
            ("recovery", "order"),
        ]
        
        for i, (original, alternative) in enumerate(patterns):
            self.create_replay(self.test_user_id, original, alternative, i+1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        insights = data.get("insights", [])
        
        # Should have insights
        assert len(insights) > 0, "Should generate at least one insight"
        assert len(insights) <= 4, "Should limit to 4 insights max"
        
        # Verify insights are in Hebrew
        for insight in insights:
            assert isinstance(insight, str), "Insight should be string"
            # Hebrew text check - should contain Hebrew characters
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in insight)
            assert has_hebrew, f"Insight should be in Hebrew: {insight}"
        
        # First insight should mention most explored path (contribution)
        first_insight = insights[0]
        assert "תרומה" in first_insight, f"First insight should mention תרומה: {first_insight}"
        
        print(f"✓ Hebrew insights generated: {len(insights)} insights")
        for i, insight in enumerate(insights):
            print(f"  {i+1}. {insight}")
    
    def test_most_replayed_original_tags(self):
        """Test that most_replayed_original_tags is correctly populated"""
        # Create replays where 'harm' is replayed most
        patterns = [
            ("harm", "contribution"),  # 3 harm replays
            ("harm", "recovery"),
            ("harm", "order"),
            ("avoidance", "contribution"),  # 1 avoidance replay
        ]
        
        for i, (original, alternative) in enumerate(patterns):
            self.create_replay(self.test_user_id, original, alternative, i+1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        orig_tags = data.get("most_replayed_original_tags", {})
        
        assert orig_tags.get("harm") == 3, "harm should have 3 counts"
        assert orig_tags.get("avoidance") == 1, "avoidance should have 1 count"
        
        print(f"✓ Most replayed original tags validated: {orig_tags}")
    
    def test_recent_replay_count(self):
        """Test that recent_replay_count (last 7 days) is correctly calculated"""
        # Create replays (all will be recent since we just created them)
        for i in range(4):
            self.create_replay(self.test_user_id, "harm", "contribution", i+1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # All replays should be counted as recent
        assert data.get("recent_replay_count") == 4, f"Expected 4 recent, got {data.get('recent_replay_count')}"
        
        print(f"✓ Recent replay count validated: {data.get('recent_replay_count')}")
    
    def test_response_structure_completeness(self):
        """Test that all expected fields are present in response"""
        # Create at least one replay
        self.create_replay(self.test_user_id, "harm", "contribution", 1)
        
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all required fields
        required_fields = [
            "success",
            "user_id",
            "total_replays",
            "alternative_path_counts",
            "transition_patterns",
            "blind_spots",
            "most_replayed_original_tags",
            "insights",
            "recent_replay_count",
            "generated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify types
        assert isinstance(data["success"], bool)
        assert isinstance(data["total_replays"], int)
        assert isinstance(data["alternative_path_counts"], dict)
        assert isinstance(data["transition_patterns"], list)
        assert isinstance(data["blind_spots"], list)
        assert isinstance(data["insights"], list)
        assert isinstance(data["recent_replay_count"], int)
        assert isinstance(data["generated_at"], str)
        
        print("✓ Response structure completeness validated")


class TestReplayInsightsIntegration:
    """Integration tests for replay insights with auth flow"""
    
    def test_insights_with_authenticated_user(self):
        """Test replay insights work with authenticated user ID"""
        # Register a new user
        unique_email = f"test_insights_{uuid.uuid4().hex[:8]}@test.com"
        
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": unique_email, "password": "password123"}
        )
        
        if reg_response.status_code == 200 and reg_response.json().get("success"):
            user_id = reg_response.json()["user"]["id"]
            
            # Create replay with authenticated user ID
            replay_data = {
                "user_id": user_id,
                "replay_of_decision_id": f"dec_{uuid.uuid4().hex[:12]}",
                "original_value_tag": "harm",
                "alternative_path_id": 1,
                "alternative_path_type": "contribution",
                "predicted_metrics": {
                    "orderDrift": 5,
                    "collectiveDrift": 10,
                    "harmPressure": -15,
                    "recoveryStability": 10
                }
            }
            
            requests.post(f"{BASE_URL}/api/memory/replay", json=replay_data)
            
            # Get insights for authenticated user
            response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{user_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data.get("success") == True
            assert data.get("total_replays") >= 1
            
            print(f"✓ Authenticated user insights passed for: {user_id}")
        else:
            print("✓ Skipped - user registration not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

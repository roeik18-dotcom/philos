"""
Test suite for Replay Insights API integration with Weekly Behavioral Report
Tests the /api/memory/replay-insights/{user_id} endpoint
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestReplayInsightsAPI:
    """Tests for the replay insights endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.test_user_id = f"test-replay-{str(uuid.uuid4())[:8]}"
        self.existing_user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"  # test user with data
    
    def test_replay_insights_endpoint_exists(self):
        """Test that the replay insights endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/test-user")
        # Should return 200 with empty data for non-existent user
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get('success') is True
        print("PASS: Replay insights endpoint exists and returns success")
    
    def test_replay_insights_returns_correct_structure(self):
        """Test that replay insights returns the correct response structure"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields in response
        required_fields = [
            'success', 'user_id', 'total_replays', 'alternative_path_counts',
            'transition_patterns', 'blind_spots', 'most_replayed_original_tags',
            'insights', 'recent_replay_count', 'generated_at'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify data types
        assert isinstance(data['success'], bool)
        assert isinstance(data['user_id'], str)
        assert isinstance(data['total_replays'], int)
        assert isinstance(data['alternative_path_counts'], dict)
        assert isinstance(data['transition_patterns'], list)
        assert isinstance(data['blind_spots'], list)
        assert isinstance(data['insights'], list)
        
        print("PASS: Replay insights returns correct structure")
    
    def test_replay_insights_with_existing_user(self):
        """Test replay insights with a user that has replay data"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.existing_user_id}")
        assert response.status_code == 200
        data = response.json()
        
        # This user should have replay data from previous tests
        assert data['success'] is True
        assert data['user_id'] == self.existing_user_id
        
        # Should have some replays
        if data['total_replays'] > 0:
            # Verify alternative_path_counts has all value types
            alt_counts = data['alternative_path_counts']
            expected_value_types = ['contribution', 'recovery', 'order', 'harm', 'avoidance']
            for vtype in expected_value_types:
                assert vtype in alt_counts, f"Missing value type: {vtype}"
            
            # Verify insights are in Hebrew
            if data['insights']:
                # Hebrew characters are in Unicode range 0x0590-0x05FF
                first_insight = data['insights'][0]
                has_hebrew = any('\u0590' <= c <= '\u05FF' for c in first_insight)
                assert has_hebrew, f"Insight should contain Hebrew text: {first_insight}"
            
            print(f"PASS: User has {data['total_replays']} replays with Hebrew insights")
        else:
            print("PASS: Empty replay data returned correctly for user")
    
    def test_alternative_path_counts_format(self):
        """Test that alternative_path_counts contains all value types"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.existing_user_id}")
        data = response.json()
        
        alt_counts = data['alternative_path_counts']
        
        # All value types should be present
        expected_types = ['contribution', 'recovery', 'order', 'harm', 'avoidance']
        for vtype in expected_types:
            assert vtype in alt_counts, f"Missing alternative path type: {vtype}"
            assert isinstance(alt_counts[vtype], int), f"{vtype} should be an integer"
        
        print("PASS: Alternative path counts format is correct")
    
    def test_transition_patterns_format(self):
        """Test that transition_patterns have correct format"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.existing_user_id}")
        data = response.json()
        
        if data['transition_patterns']:
            for pattern in data['transition_patterns']:
                assert 'from' in pattern, "Pattern missing 'from' field"
                assert 'to' in pattern, "Pattern missing 'to' field"
                assert 'count' in pattern, "Pattern missing 'count' field"
                assert isinstance(pattern['count'], int)
        
        print("PASS: Transition patterns format is correct")
    
    def test_blind_spots_format(self):
        """Test that blind_spots have correct format"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.existing_user_id}")
        data = response.json()
        
        if data['blind_spots']:
            for spot in data['blind_spots']:
                assert 'from' in spot, "Blind spot missing 'from' field"
                assert 'to' in spot, "Blind spot missing 'to' field"
        
        print("PASS: Blind spots format is correct")
    
    def test_recent_replay_count(self):
        """Test that recent_replay_count is returned"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.existing_user_id}")
        data = response.json()
        
        assert 'recent_replay_count' in data
        assert isinstance(data['recent_replay_count'], int)
        assert data['recent_replay_count'] >= 0
        
        # Recent count should be <= total replays
        assert data['recent_replay_count'] <= data['total_replays']
        
        print(f"PASS: Recent replay count: {data['recent_replay_count']} / {data['total_replays']} total")


class TestCreateReplayData:
    """Tests for creating replay metadata"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.test_user_id = f"test-create-replay-{str(uuid.uuid4())[:8]}"
    
    def test_create_replay_metadata(self):
        """Test creating a new replay record"""
        payload = {
            "user_id": self.test_user_id,
            "replay_of_decision_id": f"decision-{str(uuid.uuid4())[:8]}",
            "original_value_tag": "harm",
            "alternative_path_id": 1,
            "alternative_path_type": "recovery",
            "predicted_metrics": {
                "order_drift": 5,
                "collective_drift": 3,
                "harm_pressure": -2,
                "recovery_stability": 8
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/memory/replay", json=payload)
        assert response.status_code == 200, f"Failed to create replay: {response.text}"
        
        data = response.json()
        assert data.get('success') is True
        assert 'id' in data
        assert 'timestamp' in data
        
        print("PASS: Successfully created replay metadata")
    
    def test_verify_created_replay_appears_in_insights(self):
        """Create replay and verify it appears in insights"""
        # Create multiple replays
        for i in range(3):
            payload = {
                "user_id": self.test_user_id,
                "replay_of_decision_id": f"decision-{str(uuid.uuid4())[:8]}",
                "original_value_tag": "avoidance" if i % 2 == 0 else "harm",
                "alternative_path_id": i + 1,
                "alternative_path_type": "contribution" if i == 0 else "recovery",
                "predicted_metrics": {
                    "order_drift": 5 + i,
                    "collective_drift": 3 + i,
                    "harm_pressure": -2 - i,
                    "recovery_stability": 8 + i
                }
            }
            requests.post(f"{BASE_URL}/api/memory/replay", json=payload)
        
        # Now get insights
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        data = response.json()
        
        assert data['total_replays'] >= 3, f"Expected at least 3 replays, got {data['total_replays']}"
        
        # Check that alternative paths were counted
        alt_counts = data['alternative_path_counts']
        total_counted = sum(alt_counts.values())
        assert total_counted >= 3, f"Expected at least 3 in alternative_path_counts, got {total_counted}"
        
        print(f"PASS: Created replays appear in insights with total_replays={data['total_replays']}")


class TestWeeklyReportIntegration:
    """Tests for Weekly Behavioral Report integration with replay insights"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.test_user_id = "05d47b99-88f1-44b3-a879-6c995634eaa0"
    
    def test_replay_insights_for_weekly_report(self):
        """Test that replay insights provide data needed for weekly report integration"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        data = response.json()
        
        # Weekly report needs these fields
        assert 'total_replays' in data  # For replayCount display
        assert 'recent_replay_count' in data  # For "X replays this week"
        assert 'alternative_path_counts' in data  # For most explored stat
        assert 'transition_patterns' in data  # For missed positive/avoided risky
        assert 'insights' in data  # For Hebrew insight texts
        
        # Verify we can determine most explored alternative
        alt_counts = data['alternative_path_counts']
        if any(v > 0 for v in alt_counts.values()):
            most_explored = max(alt_counts.items(), key=lambda x: x[1])
            assert most_explored[0] in ['contribution', 'recovery', 'order', 'harm', 'avoidance']
            print(f"PASS: Most explored alternative: {most_explored[0]} ({most_explored[1]} times)")
        else:
            print("PASS: No alternatives explored yet")
    
    def test_gap_analysis_data_available(self):
        """Test that data for gap analysis is available"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        data = response.json()
        
        # Gap analysis in frontend compares actual choices vs replay preferences
        # This needs alternative_path_counts to compare with actual value distribution
        assert 'alternative_path_counts' in data
        
        # The frontend also needs most_replayed_original_tags for context
        assert 'most_replayed_original_tags' in data
        
        orig_tags = data['most_replayed_original_tags']
        expected_types = ['contribution', 'recovery', 'order', 'harm', 'avoidance']
        for vtype in expected_types:
            assert vtype in orig_tags
        
        print("PASS: Gap analysis data structure is correct")
    
    def test_hebrew_insights_generated(self):
        """Test that Hebrew insights are generated for replay patterns"""
        response = requests.get(f"{BASE_URL}/api/memory/replay-insights/{self.test_user_id}")
        data = response.json()
        
        insights = data.get('insights', [])
        
        if data['total_replays'] > 0 and insights:
            # Check for Hebrew characters in insights
            for insight in insights:
                has_hebrew = any('\u0590' <= c <= '\u05FF' for c in insight)
                assert has_hebrew, f"Insight should contain Hebrew: {insight}"
            
            print(f"PASS: {len(insights)} Hebrew insights generated")
            for i, insight in enumerate(insights):
                print(f"  Insight {i+1}: {insight[:60]}...")
        else:
            # Empty insights are fine if no replays
            print("PASS: No insights generated (no replay data)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

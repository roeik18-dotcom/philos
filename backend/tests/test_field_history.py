"""
Test historical momentum tracking for collective field (4 weeks)
Tests /api/orientation/history endpoint
Features: weekly_snapshots, sparkline_data, trend_type, trend_insight
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestFieldHistoryEndpoint:
    """Test /api/orientation/history endpoint returns correct structure"""
    
    def test_history_endpoint_returns_success(self):
        """Test endpoint returns success=true"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        print("PASS: History endpoint returns success=true")
    
    def test_weekly_snapshots_is_array(self):
        """Test weekly_snapshots is an array"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'weekly_snapshots' in data
        assert isinstance(data['weekly_snapshots'], list)
        print(f"PASS: weekly_snapshots is array with {len(data['weekly_snapshots'])} items")
    
    def test_weekly_snapshots_has_4_weeks(self):
        """Test weekly_snapshots has 4 weeks of data"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert len(data['weekly_snapshots']) == 4
        print("PASS: weekly_snapshots has exactly 4 weeks")
    
    def test_weekly_snapshot_structure(self):
        """Test each weekly snapshot has required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        required_fields = ['week_label', 'week_start', 'center_x', 'center_y', 
                          'dominant_direction', 'positive_ratio', 'total_actions']
        
        for i, snapshot in enumerate(data['weekly_snapshots']):
            for field in required_fields:
                assert field in snapshot, f"Week {i} missing field: {field}"
        print(f"PASS: All 4 weekly snapshots have required fields: {required_fields}")
    
    def test_sparkline_data_is_array(self):
        """Test sparkline_data is an array"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'sparkline_data' in data
        assert isinstance(data['sparkline_data'], list)
        print(f"PASS: sparkline_data is array with {len(data['sparkline_data'])} items")
    
    def test_sparkline_data_matches_weeks(self):
        """Test sparkline_data length matches weekly_snapshots"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert len(data['sparkline_data']) == len(data['weekly_snapshots'])
        print("PASS: sparkline_data length matches weekly_snapshots")
    
    def test_sparkline_data_values_are_floats(self):
        """Test sparkline_data contains numeric values"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        for i, val in enumerate(data['sparkline_data']):
            assert isinstance(val, (int, float)), f"sparkline_data[{i}] is not numeric: {val}"
            assert 0 <= val <= 100, f"sparkline_data[{i}] out of range: {val}"
        print("PASS: sparkline_data values are valid floats 0-100")
    
    def test_trend_type_present(self):
        """Test trend_type is present"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'trend_type' in data
        print(f"PASS: trend_type present: '{data['trend_type']}'")
    
    def test_trend_type_valid_values(self):
        """Test trend_type is one of valid values"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        # Valid trend types: stable, stabilizing, drifting, shifting_*
        valid_prefixes = ['stable', 'stabilizing', 'drifting', 'shifting_']
        trend_type = data.get('trend_type')
        
        if trend_type:
            is_valid = any(trend_type.startswith(prefix) for prefix in valid_prefixes)
            assert is_valid, f"Invalid trend_type: {trend_type}"
        print(f"PASS: trend_type '{trend_type}' is valid")
    
    def test_trend_insight_present_and_hebrew(self):
        """Test trend_insight is present and in Hebrew"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'trend_insight' in data
        
        trend_insight = data.get('trend_insight')
        if trend_insight:
            # Check for Hebrew characters (Unicode range for Hebrew)
            has_hebrew = any('\u0590' <= char <= '\u05FF' for char in trend_insight)
            assert has_hebrew, f"trend_insight not in Hebrew: {trend_insight}"
            print(f"PASS: trend_insight in Hebrew: '{trend_insight}'")
        else:
            print("SKIP: trend_insight is None (acceptable when no data)")
    
    def test_weeks_analyzed_present(self):
        """Test weeks_analyzed count is present"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'weeks_analyzed' in data
        assert isinstance(data['weeks_analyzed'], int)
        assert 0 <= data['weeks_analyzed'] <= 4
        print(f"PASS: weeks_analyzed = {data['weeks_analyzed']}")
    
    def test_week_labels_are_hebrew(self):
        """Test week labels are in Hebrew format"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        for snapshot in data['weekly_snapshots']:
            label = snapshot.get('week_label', '')
            # Check for Hebrew
            has_hebrew = any('\u0590' <= char <= '\u05FF' for char in label)
            assert has_hebrew, f"Week label not Hebrew: {label}"
        print("PASS: All week labels are in Hebrew")
    
    def test_positive_ratio_in_valid_range(self):
        """Test positive_ratio values are in 0-100 range"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        for snapshot in data['weekly_snapshots']:
            ratio = snapshot.get('positive_ratio', 0)
            assert 0 <= ratio <= 100, f"positive_ratio out of range: {ratio}"
        print("PASS: All positive_ratio values in valid range")
    
    def test_center_coordinates_in_valid_range(self):
        """Test center coordinates are in 0-100 range"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        for snapshot in data['weekly_snapshots']:
            x = snapshot.get('center_x', 50)
            y = snapshot.get('center_y', 50)
            assert 0 <= x <= 100, f"center_x out of range: {x}"
            assert 0 <= y <= 100, f"center_y out of range: {y}"
        print("PASS: All center coordinates in valid range")
    
    def test_dominant_direction_valid_or_null(self):
        """Test dominant_direction is valid direction or null"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        valid_directions = ['recovery', 'order', 'contribution', 'exploration', None]
        
        for snapshot in data['weekly_snapshots']:
            direction = snapshot.get('dominant_direction')
            assert direction in valid_directions, f"Invalid dominant_direction: {direction}"
        print("PASS: All dominant_direction values are valid")
    
    def test_trend_direction_field_present(self):
        """Test trend_direction field is present"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        assert 'trend_direction' in data
        print(f"PASS: trend_direction present: {data.get('trend_direction')}")


class TestFieldHistoryDataQuality:
    """Test data quality and consistency"""
    
    def test_sparkline_matches_positive_ratios(self):
        """Test sparkline_data matches weekly_snapshots positive_ratio values"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        snapshots = data['weekly_snapshots']
        sparkline = data['sparkline_data']
        
        for i, (snapshot, spark_val) in enumerate(zip(snapshots, sparkline)):
            expected = snapshot['positive_ratio']
            assert spark_val == expected, f"Week {i}: sparkline {spark_val} != positive_ratio {expected}"
        print("PASS: sparkline_data matches weekly positive_ratios")
    
    def test_weeks_ordered_chronologically(self):
        """Test weeks are ordered from oldest to newest"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        dates = [s['week_start'] for s in data['weekly_snapshots']]
        sorted_dates = sorted(dates)
        assert dates == sorted_dates, f"Weeks not in chronological order: {dates}"
        print("PASS: Weeks ordered chronologically")
    
    def test_current_week_labeled_correctly(self):
        """Test current week has correct label"""
        response = requests.get(f"{BASE_URL}/api/orientation/history")
        data = response.json()
        
        # Last week should be current
        current_week = data['weekly_snapshots'][-1]
        # Hebrew for "this week" is "השבוע"
        assert 'השבוע' in current_week['week_label'] or 'שבוע 4' in current_week['week_label'], \
            f"Current week label unexpected: {current_week['week_label']}"
        print(f"PASS: Current week labeled correctly: '{current_week['week_label']}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

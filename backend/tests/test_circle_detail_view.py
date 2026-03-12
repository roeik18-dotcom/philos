"""
Test Circle Detail View feature - Backend API tests
Tests GET /api/orientation/value-circles/{circle_id} and POST /api/orientation/value-circles/leave
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Circle IDs from the app
CIRCLE_IDS = [
    'builders_of_order', 'explorers', 'contributors', 
    'regenerators', 'social_connectors', 'deep_thinkers'
]


class TestCircleDetailGet:
    """Tests for GET /api/orientation/value-circles/{circle_id}"""
    
    def test_circle_detail_returns_success(self):
        """Test that circle detail endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        print(f"PASS: Circle detail returns success for {CIRCLE_IDS[0]}")
    
    def test_circle_detail_has_circle_info(self):
        """Test that response contains circle info with all required fields"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        
        # Check circle object exists and has required fields
        assert 'circle' in data
        circle = data['circle']
        assert 'id' in circle
        assert 'label_he' in circle
        assert 'direction' in circle
        assert 'color' in circle
        assert 'description_he' in circle
        assert 'member_count' in circle
        assert isinstance(circle['member_count'], int)
        print(f"PASS: Circle info has all required fields - {circle['label_he']}")
    
    def test_circle_detail_has_is_member_field(self):
        """Test that response includes is_member boolean"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        
        assert 'is_member' in data
        assert isinstance(data['is_member'], bool)
        print(f"PASS: is_member field present: {data['is_member']}")
    
    def test_circle_detail_with_user_id_param(self):
        """Test that user_id query param works and returns membership status"""
        test_user = f"test_{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}?user_id={test_user}")
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'is_member' in data
        # New user should not be a member
        assert data['is_member'] is False
        print(f"PASS: user_id param works, is_member=False for new user")
    
    def test_circle_detail_has_feed(self):
        """Test that circle detail includes feed array with 8 items"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        
        assert 'feed' in data
        assert isinstance(data['feed'], list)
        assert len(data['feed']) == 8
        
        # Check feed item structure
        feed_item = data['feed'][0]
        assert 'alias' in feed_item
        assert 'action_he' in feed_item
        assert 'direction' in feed_item
        assert 'impact' in feed_item
        print(f"PASS: Feed has 8 items with correct structure")
    
    def test_circle_detail_has_leaderboard(self):
        """Test that circle detail includes leaderboard with 5 leaders"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        
        assert 'leaderboard' in data
        assert isinstance(data['leaderboard'], list)
        assert len(data['leaderboard']) == 5
        
        # Check leader structure
        leader = data['leaderboard'][0]
        assert 'rank' in leader
        assert 'alias' in leader
        assert 'country' in leader
        assert 'impact' in leader
        assert 'actions' in leader
        assert leader['rank'] == 1
        print(f"PASS: Leaderboard has 5 ranked leaders")
    
    def test_circle_detail_has_missions(self):
        """Test that circle detail includes missions array"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{CIRCLE_IDS[0]}")
        assert response.status_code == 200
        data = response.json()
        
        assert 'missions' in data
        assert isinstance(data['missions'], list)
        assert len(data['missions']) >= 1
        
        # Check mission structure
        mission = data['missions'][0]
        assert 'id' in mission
        assert 'title_he' in mission
        assert 'direction' in mission
        assert 'direction_he' in mission
        assert 'description_he' in mission
        assert 'participants' in mission
        assert 'target' in mission
        assert 'status' in mission
        print(f"PASS: Missions array present with {len(data['missions'])} missions")
    
    def test_all_six_circles_accessible(self):
        """Test that all 6 circle detail endpoints work"""
        for circle_id in CIRCLE_IDS:
            response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{circle_id}")
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['circle']['id'] == circle_id
        print(f"PASS: All 6 circles accessible: {', '.join(CIRCLE_IDS)}")
    
    def test_invalid_circle_returns_404(self):
        """Test that invalid circle ID returns 404"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/invalid_circle_xyz")
        assert response.status_code == 404
        print("PASS: Invalid circle returns 404")


class TestCircleLeaveEndpoint:
    """Tests for POST /api/orientation/value-circles/leave"""
    
    def test_leave_circle_success(self):
        """Test leave circle endpoint structure"""
        test_user = f"test_{uuid.uuid4().hex[:8]}"
        
        # First join
        join_response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/join",
            json={"user_id": test_user, "circle_id": CIRCLE_IDS[0]}
        )
        assert join_response.status_code == 200
        
        # Then leave
        leave_response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/leave",
            json={"user_id": test_user, "circle_id": CIRCLE_IDS[0]}
        )
        assert leave_response.status_code == 200
        data = leave_response.json()
        
        assert data['success'] is True
        assert 'message_he' in data
        assert data['was_member'] is True
        print(f"PASS: Leave circle succeeds for joined user")
    
    def test_leave_circle_non_member(self):
        """Test leaving circle when not a member"""
        test_user = f"test_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/leave",
            json={"user_id": test_user, "circle_id": CIRCLE_IDS[0]}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert data['was_member'] is False
        print("PASS: Leave non-member returns was_member=False")
    
    def test_leave_invalid_circle(self):
        """Test leaving invalid circle returns error"""
        response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/leave",
            json={"user_id": "test_user", "circle_id": "invalid_circle"}
        )
        assert response.status_code == 400
        print("PASS: Leave invalid circle returns 400")


class TestJoinLeaveFlow:
    """Test complete Join/Leave flow and membership verification"""
    
    def test_join_verify_leave_verify_flow(self):
        """Full flow: Join -> Verify member -> Leave -> Verify not member"""
        test_user = f"test_flow_{uuid.uuid4().hex[:8]}"
        circle_id = CIRCLE_IDS[1]  # explorers
        
        # 1. Verify not member initially
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{circle_id}?user_id={test_user}")
        assert response.status_code == 200
        assert response.json()['is_member'] is False
        print(f"Step 1: User not member initially ✓")
        
        # 2. Join circle
        join_response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/join",
            json={"user_id": test_user, "circle_id": circle_id}
        )
        assert join_response.status_code == 200
        assert join_response.json()['success'] is True
        print(f"Step 2: Join circle succeeded ✓")
        
        # 3. Verify now member
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{circle_id}?user_id={test_user}")
        assert response.status_code == 200
        assert response.json()['is_member'] is True
        print(f"Step 3: User is now member ✓")
        
        # 4. Leave circle
        leave_response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/leave",
            json={"user_id": test_user, "circle_id": circle_id}
        )
        assert leave_response.status_code == 200
        assert leave_response.json()['was_member'] is True
        print(f"Step 4: Leave circle succeeded ✓")
        
        # 5. Verify no longer member
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/{circle_id}?user_id={test_user}")
        assert response.status_code == 200
        assert response.json()['is_member'] is False
        print(f"Step 5: User no longer member ✓")
        
        print("PASS: Complete Join/Leave flow works correctly")


class TestRegressionExistingEndpoints:
    """Regression tests for existing circle endpoints"""
    
    def test_value_circles_list_still_works(self):
        """Test GET /api/orientation/value-circles still returns 6 circles"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'circles' in data
        assert len(data['circles']) == 6
        print("PASS: Value circles list returns 6 circles")
    
    def test_join_circle_still_works(self):
        """Test POST /api/orientation/value-circles/join still works"""
        test_user = f"test_reg_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/orientation/value-circles/join",
            json={"user_id": test_user, "circle_id": CIRCLE_IDS[0]}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'message_he' in data
        print("PASS: Join circle endpoint still works")
    
    def test_missions_endpoint_still_works(self):
        """Test GET /api/orientation/missions still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'missions' in data
        print("PASS: Missions endpoint still works")
    
    def test_leaders_endpoint_still_works(self):
        """Test GET /api/orientation/leaders still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'global_leaders' in data
        print("PASS: Leaders endpoint still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

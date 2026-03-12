"""
Test suite for Iteration 44 new features:
1. Admin analytics page (GET /api/admin/analytics, GET /api/admin/feedback)
2. Feedback submission (POST /api/feedback)
3. Onboarding first action (POST /api/onboarding/first-action)

Regression tests for: Globe on HomeTab, 6-tab navigation, Community circle detail view
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAnalytics:
    """Test GET /api/admin/analytics endpoint"""
    
    def test_admin_analytics_returns_success(self):
        """Admin analytics endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Admin analytics endpoint returns success=True")
    
    def test_admin_analytics_has_dau_array(self):
        """Admin analytics returns DAU array with 7 days"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        data = response.json()
        assert 'dau' in data
        assert isinstance(data['dau'], list)
        assert len(data['dau']) == 7
        print(f"✓ DAU array has 7 days of data")
    
    def test_admin_analytics_dau_fields(self):
        """DAU entries have required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        data = response.json()
        day_entry = data['dau'][0]
        assert 'date' in day_entry
        assert 'active_users' in day_entry
        assert 'total_actions' in day_entry
        assert 'actions_per_user' in day_entry
        print(f"✓ DAU entry has date={day_entry['date']}, active_users={day_entry['active_users']}, actions_per_user={day_entry['actions_per_user']}")
    
    def test_admin_analytics_has_retention(self):
        """Admin analytics returns retention D1/D7"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        data = response.json()
        assert 'retention' in data
        assert 'd1' in data['retention']
        assert 'd7' in data['retention']
        d1 = data['retention']['d1']
        d7 = data['retention']['d7']
        assert 'cohort_size' in d1
        assert 'returned' in d1
        assert 'rate' in d1
        print(f"✓ Retention D1: cohort={d1['cohort_size']}, returned={d1['returned']}, rate={d1['rate']}%")
        print(f"✓ Retention D7: cohort={d7['cohort_size']}, returned={d7['returned']}, rate={d7['rate']}%")
    
    def test_admin_analytics_has_totals(self):
        """Admin analytics returns totals"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        data = response.json()
        assert 'totals' in data
        totals = data['totals']
        assert 'users' in totals
        assert 'actions' in totals
        assert 'feedback' in totals
        print(f"✓ Totals: users={totals['users']}, actions={totals['actions']}, feedback={totals['feedback']}")
    
    def test_admin_analytics_has_generated_at(self):
        """Admin analytics returns generated_at timestamp"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        data = response.json()
        assert 'generated_at' in data
        assert data['generated_at']  # Not empty
        print(f"✓ Generated at: {data['generated_at']}")


class TestAdminFeedback:
    """Test GET /api/admin/feedback endpoint"""
    
    def test_admin_feedback_returns_success(self):
        """Admin feedback list endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Admin feedback endpoint returns success=True")
    
    def test_admin_feedback_returns_array(self):
        """Admin feedback returns feedback array"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback")
        data = response.json()
        assert 'feedback' in data
        assert isinstance(data['feedback'], list)
        print(f"✓ Feedback array has {len(data['feedback'])} items")
    
    def test_admin_feedback_item_fields(self):
        """Feedback items have required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback")
        data = response.json()
        if data['feedback']:
            item = data['feedback'][0]
            assert 'user_id' in item
            assert 'text' in item
            assert 'type' in item
            assert 'created_at' in item
            print(f"✓ Feedback item has type={item['type']}, text='{item['text'][:30]}...'")
        else:
            print("✓ No feedback items yet (empty array is valid)")


class TestFeedbackSubmission:
    """Test POST /api/feedback endpoint"""
    
    def test_submit_feedback_success(self):
        """Submitting feedback returns success"""
        payload = {
            "user_id": "test_feedback_user_iter44",
            "text": "Test feedback from iteration 44 tests",
            "page": "home",
            "type": "improvement"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'message_he' in data
        print(f"✓ Feedback submitted successfully, message: {data['message_he']}")
    
    def test_submit_feedback_confusion_type(self):
        """Submitting confusion feedback type"""
        payload = {
            "user_id": "test_confusion_user",
            "text": "I'm confused about the directions",
            "page": "home",
            "type": "confusion"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Confusion feedback submitted")
    
    def test_submit_feedback_bug_type(self):
        """Submitting bug feedback type"""
        payload = {
            "user_id": "test_bug_user",
            "text": "Found a bug in the app",
            "page": "community",
            "type": "bug"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Bug feedback submitted")


class TestOnboardingFirstAction:
    """Test POST /api/onboarding/first-action endpoint"""
    
    def test_onboarding_first_action_success(self):
        """Onboarding first action returns success"""
        payload = {
            "user_id": f"test_onboarding_{datetime.now().timestamp()}",
            "direction": "contribution"
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'message_he' in data
        assert data.get('direction') == 'contribution'
        print(f"✓ Onboarding first action: direction=contribution, message={data['message_he']}")
    
    def test_onboarding_direction_recovery(self):
        """Onboarding with recovery direction"""
        payload = {
            "user_id": f"test_onb_recovery_{datetime.now().timestamp()}",
            "direction": "recovery"
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('direction') == 'recovery'
        print(f"✓ Onboarding with recovery direction works")
    
    def test_onboarding_direction_order(self):
        """Onboarding with order direction"""
        payload = {
            "user_id": f"test_onb_order_{datetime.now().timestamp()}",
            "direction": "order"
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('direction') == 'order'
        print(f"✓ Onboarding with order direction works")
    
    def test_onboarding_direction_exploration(self):
        """Onboarding with exploration direction"""
        payload = {
            "user_id": f"test_onb_exploration_{datetime.now().timestamp()}",
            "direction": "exploration"
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/first-action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('direction') == 'exploration'
        print(f"✓ Onboarding with exploration direction works")


class TestRegressionTabNavigation:
    """Regression tests for 6-tab navigation"""
    
    def test_daily_opening_still_works(self):
        """Daily opening endpoint still works (Home tab)"""
        response = requests.get(f"{BASE_URL}/api/orientation/daily-opening/test_user")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Daily opening endpoint works (Home tab regression)")
    
    def test_field_dashboard_still_works(self):
        """Field dashboard endpoint still works (Home tab globe)"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'dominant_direction' in data
        print(f"✓ Field dashboard works: dominant_direction={data['dominant_direction']}")
    
    def test_feed_still_works(self):
        """Feed endpoint still works (Feed tab)"""
        response = requests.get(f"{BASE_URL}/api/orientation/feed/for-you/test_user")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'cards' in data
        print(f"✓ Feed endpoint works: {len(data['cards'])} cards")
    
    def test_value_circles_still_works(self):
        """Value circles endpoint still works (Community tab)"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert len(data.get('circles', [])) == 6
        print(f"✓ Value circles endpoint works: 6 circles")
    
    def test_leaders_still_works(self):
        """Leaders endpoint still works (Community tab)"""
        response = requests.get(f"{BASE_URL}/api/orientation/leaders")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'global_leaders' in data
        print(f"✓ Leaders endpoint works: {len(data['global_leaders'])} leaders")
    
    def test_missions_still_works(self):
        """Missions endpoint still works (Community tab)"""
        response = requests.get(f"{BASE_URL}/api/orientation/missions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'missions' in data
        print(f"✓ Missions endpoint works: {len(data['missions'])} missions")


class TestRegressionCircleDetailView:
    """Regression tests for Circle detail view feature"""
    
    def test_circle_detail_builders_of_order(self):
        """Circle detail for builders_of_order works"""
        response = requests.get(f"{BASE_URL}/api/orientation/value-circles/builders_of_order")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'circle' in data
        assert 'feed' in data
        assert 'leaderboard' in data
        print(f"✓ Circle detail view for builders_of_order works")
    
    def test_join_circle_still_works(self):
        """Join circle endpoint still works"""
        payload = {"user_id": "test_join_regression", "circle_id": "explorers"}
        response = requests.post(f"{BASE_URL}/api/orientation/value-circles/join", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Join circle endpoint works")
    
    def test_leave_circle_still_works(self):
        """Leave circle endpoint still works"""
        payload = {"user_id": "test_join_regression", "circle_id": "explorers"}
        response = requests.post(f"{BASE_URL}/api/orientation/value-circles/leave", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Leave circle endpoint works")


class TestRegressionGlobeEndpoints:
    """Regression tests for Globe/Field data on HomeTab"""
    
    def test_globe_activity_endpoint(self):
        """Globe activity endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/globe-activity")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'points' in data
        print(f"✓ Globe activity endpoint works: {len(data['points'])} points")
    
    def test_field_today_endpoint(self):
        """Field today endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/field-today")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"✓ Field today endpoint works")
    
    def test_directions_endpoint(self):
        """Directions endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/orientation/directions")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'directions' in data
        print(f"✓ Directions endpoint works")

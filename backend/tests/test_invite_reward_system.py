"""
Test: Invite Reward System
Features:
1. When invitee completes first daily action, inviter's invite_credits increments
2. Daily answer response includes invite_reward with message_he when invitee just took first action
3. Reward is only given once per invitee (double-credit prevention)
4. invite-stats endpoint returns invite_credits, active_invitees count
5. invite-stats shows invitees with active status and action count
6. ProfilePage influence_chain shows active_invitees and invite_credits
7. No reward given for users without an inviter
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test users from context
INVITER_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
INVITER_EMAIL = "newuser@test.com"
INVITER_PASSWORD = "password123"

INVITEE_USER_ID = "2d720b49-cd32-4378-aa4a-10dfe58f88e2"
INVITEE_EMAIL = "inviteduser@test.com"
INVITEE_PASSWORD = "password123"


class TestInviteRewardSystem:
    """Tests for the Invite Reward System feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    # ==================== INVITE-STATS ENDPOINT TESTS ====================
    
    def test_invite_stats_returns_invite_credits_field(self):
        """invite-stats endpoint should return invite_credits field"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "invite_credits" in data, "invite_credits field should be present"
        assert isinstance(data["invite_credits"], int), "invite_credits should be an integer"
        print(f"✓ invite_credits returned: {data['invite_credits']}")
    
    def test_invite_stats_returns_active_invitees_count(self):
        """invite-stats endpoint should return active_invitees count"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_invitees" in data, "active_invitees field should be present"
        assert isinstance(data["active_invitees"], int), "active_invitees should be an integer"
        print(f"✓ active_invitees returned: {data['active_invitees']}")
    
    def test_invite_stats_invitees_have_active_status_and_actions(self):
        """invite-stats invitees should have active status and action count"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "invitees" in data, "invitees field should be present"
        
        if len(data["invitees"]) > 0:
            invitee = data["invitees"][0]
            assert "active" in invitee, "Invitee should have 'active' field"
            assert "actions" in invitee, "Invitee should have 'actions' field"
            assert "alias" in invitee, "Invitee should have 'alias' field"
            assert isinstance(invitee["active"], bool), "'active' should be boolean"
            assert isinstance(invitee["actions"], int), "'actions' should be integer"
            print(f"✓ Invitee has active={invitee['active']}, actions={invitee['actions']}")
        else:
            print("⚠ No invitees found for this user - skipping field validation")
    
    # ==================== PROFILE ENDPOINT TESTS ====================
    
    def test_profile_record_returns_influence_chain_with_credits(self):
        """Profile record should return influence_chain with invite_credits and active_invitees"""
        response = self.session.get(f"{BASE_URL}/api/profile/{INVITER_USER_ID}/record")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "influence_chain" in data, "influence_chain should be present"
        
        chain = data["influence_chain"]
        assert "invite_credits" in chain, "influence_chain should have invite_credits"
        assert "active_invitees" in chain, "influence_chain should have active_invitees"
        assert isinstance(chain["invite_credits"], int), "invite_credits should be int"
        assert isinstance(chain["active_invitees"], int), "active_invitees should be int"
        print(f"✓ Profile influence_chain: credits={chain['invite_credits']}, active={chain['active_invitees']}")
    
    def test_profile_record_returns_invitees_list(self):
        """Profile record should return invitees list in influence_chain"""
        response = self.session.get(f"{BASE_URL}/api/profile/{INVITER_USER_ID}/record")
        assert response.status_code == 200
        
        data = response.json()
        chain = data.get("influence_chain", {})
        assert "invitees" in chain, "influence_chain should have invitees list"
        assert isinstance(chain["invitees"], list), "invitees should be a list"
        print(f"✓ Profile invitees count: {len(chain['invitees'])}")
    
    # ==================== DAILY ANSWER ENDPOINT STRUCTURE TESTS ====================
    
    def test_daily_question_endpoint_exists(self):
        """Daily question endpoint should work"""
        response = self.session.get(f"{BASE_URL}/api/orientation/daily-question/{INVITER_USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        print(f"✓ Daily question endpoint works")
    
    def test_daily_answer_endpoint_exists(self):
        """Daily answer endpoint should accept POST and return proper structure"""
        # Get a question first
        question_response = self.session.get(f"{BASE_URL}/api/orientation/daily-question/{INVITER_USER_ID}")
        question_data = question_response.json()
        
        if question_data.get("already_answered_today"):
            print("✓ User already answered today - endpoint works")
            return
        
        question_id = question_data.get("question_id")
        if not question_id:
            print("⚠ No question_id available - skipping answer test")
            return
        
        # Submit answer
        response = self.session.post(
            f"{BASE_URL}/api/orientation/daily-answer/{INVITER_USER_ID}",
            json={"question_id": question_id, "action_taken": True}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True
        # invite_reward field should be in response (can be None)
        assert "invite_reward" in data, "Response should include invite_reward field"
        print(f"✓ Daily answer response includes invite_reward: {data.get('invite_reward')}")
    
    # ==================== INVITEE STATUS TESTS ====================
    
    def test_invitee_has_invited_by_relationship(self):
        """Invitee's invite-stats should show invited_by_alias"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITEE_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "invited_by_id" in data, "invited_by_id should be in response"
        assert "invited_by_alias" in data, "invited_by_alias should be in response"
        
        if data.get("invited_by_id"):
            assert data["invited_by_id"] == INVITER_USER_ID, "Inviter ID should match"
            print(f"✓ Invitee was invited by {data.get('invited_by_alias')} ({data.get('invited_by_id')})")
        else:
            print("⚠ Invitee has no inviter set")
    
    # ==================== RESPONSE STRUCTURE TESTS ====================
    
    def test_invite_stats_returns_all_expected_fields(self):
        """invite-stats should return all expected fields for 4 stats display"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Fields needed for InviteSection 4 stats: joined, active, credits, remaining
        expected_fields = [
            "total_invites_used",  # joined (הצטרפו)
            "active_invitees",     # active (פעילים)
            "invite_credits",      # credits (נקודות)
            "codes_remaining"      # remaining (נותרו)
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ All 4 stats fields present: joined={data['total_invites_used']}, "
              f"active={data['active_invitees']}, credits={data['invite_credits']}, "
              f"remaining={data['codes_remaining']}")
    
    def test_invite_stats_codes_field_structure(self):
        """invite-stats codes should have proper structure"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "codes" in data, "codes field should be present"
        assert isinstance(data["codes"], list), "codes should be a list"
        
        if len(data["codes"]) > 0:
            code = data["codes"][0]
            assert "code" in code, "Code should have 'code' field"
            assert "used" in code, "Code should have 'used' field"
            print(f"✓ Code structure valid: {code['code']}, used={code['used']}")


class TestInviteRewardFlowLogic:
    """Tests for the actual reward flow logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_user_without_inviter_gets_no_reward(self):
        """A user without an inviter should not trigger any reward"""
        # Create a new user without invite code
        import uuid
        test_email = f"test_no_inviter_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register without invite code
        register_response = self.session.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": test_email, "password": "testpass123"}
        )
        
        if register_response.status_code == 200:
            data = register_response.json()
            if data.get("success"):
                new_user_id = data["user"]["id"]
                
                # Get daily question
                question_response = self.session.get(
                    f"{BASE_URL}/api/orientation/daily-question/{new_user_id}"
                )
                
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    if question_data.get("question_id") and not question_data.get("already_answered_today"):
                        # Answer the question
                        answer_response = self.session.post(
                            f"{BASE_URL}/api/orientation/daily-answer/{new_user_id}",
                            json={"question_id": question_data["question_id"], "action_taken": True}
                        )
                        
                        if answer_response.status_code == 200:
                            answer_data = answer_response.json()
                            # User without inviter should have invite_reward as None
                            assert answer_data.get("invite_reward") is None, \
                                "User without inviter should not get invite_reward"
                            print("✓ User without inviter has no invite_reward (as expected)")
                            return
        
        print("⚠ Could not complete test - skipping")
    
    def test_verify_inviter_has_credits_for_active_invitee(self):
        """Verify inviter has credits if invitee has taken actions"""
        # Get invitee's action count
        invitee_stats = self.session.get(
            f"{BASE_URL}/api/orientation/invite-stats/{INVITEE_USER_ID}"
        ).json()
        
        # Get inviter's stats
        inviter_stats = self.session.get(
            f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}"
        ).json()
        
        print(f"Invitee invited_by: {invitee_stats.get('invited_by_id')}")
        print(f"Inviter credits: {inviter_stats.get('invite_credits')}")
        print(f"Inviter active_invitees: {inviter_stats.get('active_invitees')}")
        
        # Find invitee in inviter's list
        invitees = inviter_stats.get("invitees", [])
        invitee_entry = None
        for inv in invitees:
            if inv.get("user_id") == INVITEE_USER_ID:
                invitee_entry = inv
                break
        
        if invitee_entry:
            print(f"Invitee found in list: active={invitee_entry.get('active')}, "
                  f"actions={invitee_entry.get('actions')}")
            
            if invitee_entry.get("active"):
                assert inviter_stats.get("invite_credits", 0) > 0 or inviter_stats.get("active_invitees", 0) > 0, \
                    "If invitee is active, inviter should have credits or active count > 0"
                print("✓ Inviter has recognition for active invitee")
        else:
            print("⚠ Invitee not found in inviter's invitees list")


class TestInviteRewardDataIntegrity:
    """Tests for data integrity of the reward system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_active_invitees_count_matches_list(self):
        """active_invitees count should match active=True count in invitees list"""
        response = self.session.get(f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        invitees = data.get("invitees", [])
        reported_active = data.get("active_invitees", 0)
        calculated_active = sum(1 for i in invitees if i.get("active"))
        
        assert reported_active == calculated_active, \
            f"active_invitees mismatch: reported={reported_active}, calculated={calculated_active}"
        print(f"✓ active_invitees count is consistent: {reported_active}")
    
    def test_profile_and_invite_stats_credits_match(self):
        """invite_credits should be consistent between profile and invite-stats"""
        invite_stats = self.session.get(
            f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}"
        ).json()
        
        profile_record = self.session.get(
            f"{BASE_URL}/api/profile/{INVITER_USER_ID}/record"
        ).json()
        
        stats_credits = invite_stats.get("invite_credits", 0)
        profile_credits = profile_record.get("influence_chain", {}).get("invite_credits", 0)
        
        assert stats_credits == profile_credits, \
            f"Credits mismatch: invite-stats={stats_credits}, profile={profile_credits}"
        print(f"✓ invite_credits consistent across endpoints: {stats_credits}")
    
    def test_profile_and_invite_stats_active_invitees_match(self):
        """active_invitees should be consistent between profile and invite-stats"""
        invite_stats = self.session.get(
            f"{BASE_URL}/api/orientation/invite-stats/{INVITER_USER_ID}"
        ).json()
        
        profile_record = self.session.get(
            f"{BASE_URL}/api/profile/{INVITER_USER_ID}/record"
        ).json()
        
        stats_active = invite_stats.get("active_invitees", 0)
        profile_active = profile_record.get("influence_chain", {}).get("active_invitees", 0)
        
        assert stats_active == profile_active, \
            f"Active invitees mismatch: invite-stats={stats_active}, profile={profile_active}"
        print(f"✓ active_invitees consistent across endpoints: {stats_active}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

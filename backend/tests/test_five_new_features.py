"""
Tests for 5 New Features:
1. Dynamic OG Meta Tags - /api/share/action/{id} returns HTML with OG meta tags
2. OG Image Generation - /api/og/action/{id}/image returns PNG
3. Opportunities System - /api/opportunities with eligibility
4. Community Funds Leaderboard - /api/community-funds
5. Trust Leaderboard + Weekly Report - /api/leaderboard, /api/weekly-report/{user_id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials from the request
TEST_USER_ID = "05d47b99-88f1-44b3-a879-6c995634eaa0"
TEST_EMAIL = "newuser@test.com"
TEST_PASSWORD = "password123"
KNOWN_ACTION_ID = "69b6b246302458e7d6ca4e2b"


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_token(api_client):
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


class TestDynamicOGSharePage:
    """Test 1: Dynamic OG meta tags for social sharing"""
    
    def test_og_share_page_returns_html(self, api_client):
        """GET /api/share/action/{id} should return HTML with OG tags"""
        response = api_client.get(f"{BASE_URL}/api/share/action/{KNOWN_ACTION_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content_type = response.headers.get('content-type', '')
        assert 'text/html' in content_type, f"Expected text/html, got {content_type}"
        
        html = response.text
        # Check for required OG meta tags
        assert 'og:title' in html, "Missing og:title meta tag"
        assert 'og:description' in html, "Missing og:description meta tag"
        assert 'og:image' in html, "Missing og:image meta tag"
        assert 'twitter:card' in html, "Missing twitter:card meta tag"
        print("PASS: OG share page contains all required meta tags")
    
    def test_og_share_page_has_redirect(self, api_client):
        """Share page should redirect real users to SPA"""
        response = api_client.get(f"{BASE_URL}/api/share/action/{KNOWN_ACTION_ID}")
        assert response.status_code == 200
        html = response.text
        assert 'http-equiv="refresh"' in html, "Missing meta refresh redirect"
        assert f'/app/action/{KNOWN_ACTION_ID}' in html, "Missing redirect to SPA URL"
        print("PASS: OG share page has proper redirect to SPA")
    
    def test_og_share_page_invalid_id(self, api_client):
        """Invalid action ID should return 404"""
        response = api_client.get(f"{BASE_URL}/api/share/action/invalid_id_123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid action ID returns 404")


class TestOGImageGeneration:
    """Test 2: OG Image endpoint returns valid PNG"""
    
    def test_og_image_returns_png(self, api_client):
        """GET /api/og/action/{id}/image should return PNG image"""
        response = api_client.get(f"{BASE_URL}/api/og/action/{KNOWN_ACTION_ID}/image")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content_type = response.headers.get('content-type', '')
        assert 'image/png' in content_type, f"Expected image/png, got {content_type}"
        
        # Check PNG signature
        content = response.content
        assert content[:8] == b'\x89PNG\r\n\x1a\n', "Response is not a valid PNG file"
        print(f"PASS: OG image is valid PNG ({len(content)} bytes)")
    
    def test_og_image_has_cache_header(self, api_client):
        """OG image should have cache control header"""
        response = api_client.get(f"{BASE_URL}/api/og/action/{KNOWN_ACTION_ID}/image")
        assert response.status_code == 200
        cache_header = response.headers.get('Cache-Control', '')
        assert 'max-age' in cache_header, "Missing Cache-Control max-age"
        print("PASS: OG image has cache control header")
    
    def test_og_image_invalid_id(self, api_client):
        """Invalid action ID should return 404"""
        response = api_client.get(f"{BASE_URL}/api/og/action/invalid_id_123/image")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid action ID for image returns 404")


class TestOpportunitiesSystem:
    """Test 3: Opportunities API with eligibility check"""
    
    def test_opportunities_list(self, api_client):
        """GET /api/opportunities should return list of opportunities"""
        response = api_client.get(f"{BASE_URL}/api/opportunities")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True, "Response should have success=True"
        assert 'opportunities' in data, "Response should have opportunities array"
        
        opps = data['opportunities']
        assert len(opps) > 0, "Should have at least one opportunity"
        
        # Check structure of first opportunity
        opp = opps[0]
        assert 'id' in opp, "Opportunity should have id"
        assert 'title' in opp, "Opportunity should have title"
        assert 'type' in opp, "Opportunity should have type"
        assert 'description' in opp, "Opportunity should have description"
        assert 'min_trust_score' in opp, "Opportunity should have min_trust_score"
        print(f"PASS: Opportunities list returned {len(opps)} opportunities")
    
    def test_opportunities_type_values(self, api_client):
        """Opportunities should have valid type values"""
        response = api_client.get(f"{BASE_URL}/api/opportunities")
        data = response.json()
        
        valid_types = {'job', 'grant', 'collaboration', 'support'}
        for opp in data['opportunities']:
            assert opp['type'] in valid_types, f"Invalid type: {opp['type']}"
        print("PASS: All opportunities have valid types")
    
    def test_opportunities_with_user_eligibility(self, api_client):
        """GET /api/opportunities?user_id=... should return eligibility status"""
        response = api_client.get(f"{BASE_URL}/api/opportunities?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert 'user_trust_score' in data, "Response should have user_trust_score"
        
        # User has trust_score=8, so min_trust_score=5 should be eligible
        opps = data['opportunities']
        eligible_count = sum(1 for o in opps if o.get('eligible'))
        print(f"PASS: User trust score={data['user_trust_score']}, eligible for {eligible_count} opportunities")
        
        # Check that at least one is eligible (min_trust=5 should be eligible for user with 8)
        assert eligible_count >= 1, "User with trust=8 should be eligible for at least 1 opportunity"


class TestCommunityFunds:
    """Test 4: Community Funds Leaderboard API"""
    
    def test_community_funds_list(self, api_client):
        """GET /api/community-funds should return list of funds"""
        response = api_client.get(f"{BASE_URL}/api/community-funds")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'funds' in data
        
        funds = data['funds']
        assert len(funds) == 5, f"Expected 5 community funds, got {len(funds)}"
        
        # Check structure
        fund = funds[0]
        assert 'community' in fund, "Fund should have community name"
        assert 'total_raised' in fund, "Fund should have total_raised"
        assert 'total_distributed' in fund, "Fund should have total_distributed"
        assert 'current_balance' in fund, "Fund should have current_balance"
        print(f"PASS: Community funds list returned {len(funds)} funds")
    
    def test_community_funds_sorted_by_balance(self, api_client):
        """Funds should be sorted by current_balance descending"""
        response = api_client.get(f"{BASE_URL}/api/community-funds")
        data = response.json()
        funds = data['funds']
        
        balances = [f['current_balance'] for f in funds]
        assert balances == sorted(balances, reverse=True), "Funds should be sorted by balance descending"
        print("PASS: Funds are sorted by balance descending")
    
    def test_community_fund_detail(self, api_client):
        """GET /api/community-funds/{name} should return fund with transactions"""
        community_name = "Tel Aviv Volunteers"
        response = api_client.get(f"{BASE_URL}/api/community-funds/{community_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'fund' in data
        assert 'transactions' in data
        
        txns = data['transactions']
        assert len(txns) > 0, "Fund should have transactions"
        
        # Check transaction structure
        txn = txns[0]
        assert 'amount' in txn, "Transaction should have amount"
        assert 'type' in txn, "Transaction should have type"
        assert 'description' in txn, "Transaction should have description"
        print(f"PASS: Fund detail returned {len(txns)} transactions")
    
    def test_community_fund_balance_calculation(self, api_client):
        """Current balance should equal total_raised - total_distributed"""
        response = api_client.get(f"{BASE_URL}/api/community-funds")
        data = response.json()
        
        for fund in data['funds']:
            expected = fund['total_raised'] - fund['total_distributed']
            actual = fund['current_balance']
            assert actual == expected, f"Balance mismatch for {fund['community']}: {actual} != {expected}"
        print("PASS: All fund balances are calculated correctly")


class TestLeaderboard:
    """Test 5a: Trust Leaderboard API"""
    
    def test_leaderboard_list(self, api_client):
        """GET /api/leaderboard should return ranked list of users"""
        response = api_client.get(f"{BASE_URL}/api/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'leaders' in data
        
        leaders = data['leaders']
        assert len(leaders) > 0, "Should have at least one leader"
        
        # Check structure
        leader = leaders[0]
        assert 'rank' in leader, "Leader should have rank"
        assert 'user_id' in leader, "Leader should have user_id"
        assert 'user_name' in leader, "Leader should have user_name"
        assert 'trust_score' in leader, "Leader should have trust_score"
        assert 'total_actions' in leader, "Leader should have total_actions"
        assert 'categories' in leader, "Leader should have categories"
        print(f"PASS: Leaderboard returned {len(leaders)} leaders")
    
    def test_leaderboard_sorted_by_trust(self, api_client):
        """Leaders should be sorted by trust_score descending"""
        response = api_client.get(f"{BASE_URL}/api/leaderboard")
        data = response.json()
        leaders = data['leaders']
        
        scores = [l['trust_score'] for l in leaders]
        assert scores == sorted(scores, reverse=True), "Leaders should be sorted by trust descending"
        print("PASS: Leaderboard is sorted by trust score")
    
    def test_leaderboard_ranks_are_sequential(self, api_client):
        """Ranks should be sequential starting from 1"""
        response = api_client.get(f"{BASE_URL}/api/leaderboard")
        data = response.json()
        leaders = data['leaders']
        
        for i, leader in enumerate(leaders):
            assert leader['rank'] == i + 1, f"Expected rank {i+1}, got {leader['rank']}"
        print("PASS: Leaderboard ranks are sequential")


class TestWeeklyReport:
    """Test 5b: Weekly Impact Report API"""
    
    def test_weekly_report(self, api_client):
        """GET /api/weekly-report/{user_id} should return weekly summary"""
        response = api_client.get(f"{BASE_URL}/api/weekly-report/{TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'report' in data
        
        report = data['report']
        # Required fields
        assert 'period' in report, "Report should have period"
        assert 'user_id' in report, "Report should have user_id"
        assert 'week_actions' in report, "Report should have week_actions"
        assert 'week_trust_earned' in report, "Report should have week_trust_earned"
        assert 'total_trust_score' in report, "Report should have total_trust_score"
        assert 'rank' in report, "Report should have rank"
        assert 'network_actions_this_week' in report, "Report should have network_actions_this_week"
        assert 'network_active_users' in report, "Report should have network_active_users"
        print(f"PASS: Weekly report returned for period {report['period']}")
    
    def test_weekly_report_network_stats(self, api_client):
        """Weekly report should include network-wide statistics"""
        response = api_client.get(f"{BASE_URL}/api/weekly-report/{TEST_USER_ID}")
        data = response.json()
        report = data['report']
        
        # Network stats should be numbers
        assert isinstance(report['network_actions_this_week'], int), "network_actions_this_week should be int"
        assert isinstance(report['network_active_users'], int), "network_active_users should be int"
        assert isinstance(report['network_trust_this_week'], (int, float)), "network_trust_this_week should be numeric"
        print("PASS: Weekly report has valid network stats")
    
    def test_weekly_report_all_time_stats(self, api_client):
        """Weekly report should include all-time statistics"""
        response = api_client.get(f"{BASE_URL}/api/weekly-report/{TEST_USER_ID}")
        data = response.json()
        report = data['report']
        
        assert 'total_actions' in report, "Should have total_actions"
        assert 'total_users' in report, "Should have total_users"
        
        # Rank should be <= total_users
        if report['rank'] > 0:
            assert report['rank'] <= report['total_users'], "Rank should be <= total_users"
        print(f"PASS: All-time stats: rank #{report['rank']} of {report['total_users']}")


class TestCommunities:
    """Additional test for communities list"""
    
    def test_communities_list(self, api_client):
        """GET /api/communities should return list of communities"""
        response = api_client.get(f"{BASE_URL}/api/communities")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is True
        assert 'communities' in data
        
        communities = data['communities']
        assert len(communities) == 5, f"Expected 5 communities, got {len(communities)}"
        
        # Check structure
        c = communities[0]
        assert 'name' in c, "Community should have name"
        assert 'location' in c, "Community should have location"
        assert 'description' in c, "Community should have description"
        print(f"PASS: Communities list returned {len(communities)} communities")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

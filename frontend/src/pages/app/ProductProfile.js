import { useState, useEffect } from 'react';
import { Loader2, Tag, Award, Activity, Briefcase, Flame } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  education: '#7c3aed',
  environment: '#10b981',
  health: '#f43f5e',
  community: '#00d4ff',
  technology: '#f59e0b',
  mentorship: '#ec4899',
  volunteering: '#8b5cf6',
  other: '#6b7280',
};

export default function ProductProfile({ user }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${API_URL}/api/impact/profile/${user.id}`);
        const data = await res.json();
        if (data.success) setProfile(data.profile);
      } catch (err) {
        console.error('Profile fetch error:', err);
      }
      setLoading(false);
    };
    fetchProfile();
  }, [user]);

  if (loading) {
    return (
      <div className="profile-page" data-testid="product-profile-page">
        <div className="feed-loading">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading profile...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="profile-page" data-testid="product-profile-page">
        <div className="feed-empty"><p>Sign in to view your profile.</p></div>
      </div>
    );
  }

  return (
    <div className="profile-page" data-testid="product-profile-page">
      <div className="profile-header-card" data-testid="profile-header">
        <div className="profile-avatar" data-testid="profile-avatar">
          {(user.name || user.email || '?')[0].toUpperCase()}
        </div>
        <h1 className="profile-name" data-testid="profile-name">{user.name || user.email?.split('@')[0]}</h1>
        <p className="profile-email" data-testid="profile-email">{user.email}</p>
      </div>

      {/* Stats grid */}
      <div className="profile-stats" data-testid="profile-stats">
        <div className="profile-stat-card">
          <Flame className="w-5 h-5" style={{ color: '#f59e0b' }} />
          <div className="profile-stat-value" data-testid="stat-trust-score">{profile?.trust_score || 0}</div>
          <div className="profile-stat-label">Trust Score</div>
        </div>
        <div className="profile-stat-card">
          <Activity className="w-5 h-5" style={{ color: '#00d4ff' }} />
          <div className="profile-stat-value" data-testid="stat-actions">{profile?.total_actions || 0}</div>
          <div className="profile-stat-label">Actions Posted</div>
        </div>
        <div className="profile-stat-card">
          <Award className="w-5 h-5" style={{ color: '#10b981' }} />
          <div className="profile-stat-value" data-testid="stat-impact">{profile?.impact_score || 0}</div>
          <div className="profile-stat-label">Impact Score</div>
        </div>
        <div className="profile-stat-card">
          <Tag className="w-5 h-5" style={{ color: '#7c3aed' }} />
          <div className="profile-stat-value" data-testid="stat-verified">{profile?.verified_count || 0}</div>
          <div className="profile-stat-label">Verified</div>
        </div>
      </div>

      {/* Categories */}
      {profile?.fields?.length > 0 && (
        <div className="profile-section" data-testid="profile-categories">
          <h2 className="profile-section-title">
            <Briefcase className="w-4 h-4" /> Contribution Categories
          </h2>
          <div className="profile-tags">
            {profile.fields.map(cat => (
              <span
                key={cat}
                className="profile-tag"
                style={{ borderColor: (CATEGORY_COLORS[cat] || '#6b7280') + '44', color: CATEGORY_COLORS[cat] || '#6b7280' }}
                data-testid={`category-tag-${cat}`}
              >
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Communities */}
      {profile?.communities?.length > 0 && (
        <div className="profile-section" data-testid="profile-communities">
          <h2 className="profile-section-title">Communities Helped</h2>
          <div className="profile-tags">
            {profile.communities.map(c => (
              <span key={c} className="profile-tag" data-testid={`community-tag-${c}`}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

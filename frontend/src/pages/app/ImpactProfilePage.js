import { useState, useEffect } from 'react';
import { ShieldCheck, Target, Users, Briefcase, TrendingUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 text-center">
      <Icon className="w-4 h-4 mx-auto mb-2" style={{ color }} />
      <div className="text-xl font-bold" style={{ color }}>{value}</div>
      <div className="text-[10px] text-white/30 uppercase tracking-wider mt-1">{label}</div>
    </div>
  );
}

export default function ImpactProfilePage({ user }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    fetch(`${API}/api/impact/profile/${user.id}`)
      .then(r => r.json())
      .then(d => { if (d.success) setProfile(d.profile); })
      .finally(() => setLoading(false));
  }, [user]);

  if (!user) {
    return (
      <div className="max-w-md mx-auto px-4 pt-16 text-center">
        <p className="text-white/40 text-sm">Sign in to view your impact profile.</p>
      </div>
    );
  }

  if (loading) return <div className="text-center pt-16 text-white/30 text-sm">Loading...</div>;

  const p = profile || { impact_score: 0, total_actions: 0, fields: [], communities: [], verified_count: 0 };

  return (
    <div className="max-w-md mx-auto px-4 pb-24" data-testid="impact-profile-page">
      {/* Header */}
      <div className="pt-8 pb-6 text-center">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-white/[0.06] flex items-center justify-center mx-auto mb-3">
          <span className="text-xl font-bold text-white">{user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase()}</span>
        </div>
        <h1 className="text-lg font-semibold">{user.name || user.email?.split('@')[0]}</h1>
        <p className="text-xs text-white/30 mt-1">Impact contributor</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <StatCard icon={TrendingUp} label="Impact Score" value={p.impact_score} color="#00d4ff" />
        <StatCard icon={Target} label="Actions" value={p.total_actions} color="#f59e0b" />
        <StatCard icon={ShieldCheck} label="Verified" value={p.verified_count} color="#10b981" />
        <StatCard icon={Briefcase} label="Opportunities" value={p.opportunities_generated || 0} color="#7c3aed" />
      </div>

      {/* Fields */}
      {p.fields.length > 0 && (
        <div className="mb-6">
          <h2 className="text-[10px] uppercase tracking-wider text-white/30 mb-2">Fields of contribution</h2>
          <div className="flex flex-wrap gap-1.5">
            {p.fields.map(f => (
              <span key={f} className="text-[10px] px-2.5 py-1 rounded-full border border-white/[0.06] text-white/50 capitalize">{f}</span>
            ))}
          </div>
        </div>
      )}

      {/* Communities */}
      {p.communities.length > 0 && (
        <div className="mb-6">
          <h2 className="text-[10px] uppercase tracking-wider text-white/30 mb-2">Communities helped</h2>
          <div className="flex flex-wrap gap-1.5">
            {p.communities.map(c => (
              <span key={c} className="text-[10px] px-2.5 py-1 rounded-full border border-emerald-500/20 text-emerald-400/60 flex items-center gap-1">
                <Users className="w-3 h-3" /> {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Trust loop */}
      <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-4 text-center">
        <p className="text-[10px] uppercase tracking-wider text-white/20 mb-3">Your trust loop</p>
        <div className="flex items-center justify-center gap-2 text-xs text-white/40">
          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400">Action</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400">Reaction</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">Trust</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-400">Opportunity</span>
        </div>
      </div>
    </div>
  );
}

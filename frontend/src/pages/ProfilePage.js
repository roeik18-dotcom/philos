import { useState, useEffect, useRef, useCallback } from 'react';
import { toPng } from 'html-to-image';
import { MapPin, ChevronDown, ChevronUp, Loader2, Flame, Share2, Download, Link2, Check, Copy, Info } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'Contribution', recovery: 'Recovery', order: 'Order', exploration: 'Exploration' };

export default function ProfilePage() {
  const [data, setData] = useState(null);
  const [trustHistory, setTrustHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedAction, setExpandedAction] = useState(null);
  const [showShare, setShowShare] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  const pathParts = window.location.pathname.split('/');
  const userId = pathParts[pathParts.length - 1];
  const profileUrl = `${window.location.origin}/profile/${userId}`;

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/profile/${userId}/record`).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/api/user/${userId}/trust-history?limit=10`).then(r => r.ok ? r.json() : null),
    ]).then(([profile, history]) => {
      if (profile?.success) setData(profile);
      if (history?.user_id) setTrustHistory(history);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [userId]);

  const handleCopyLink = useCallback(() => {
    navigator.clipboard.writeText(profileUrl).catch(() => {
      const input = document.createElement('input');
      input.value = profileUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    });
    setLinkCopied(true);
    setTimeout(() => setLinkCopied(false), 2500);
  }, [profileUrl]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#0a0a12] flex flex-col items-center justify-center gap-3 px-4">
        <p className="text-sm text-gray-500">Record not found</p>
        <a href="/" className="text-xs text-gray-400 hover:text-white transition-colors">Back to Philos</a>
      </div>
    );
  }

  const { identity, action_record, opposition_axes, value_growth, direction_distribution, influence_chain, field_contribution, ai_profile_interpretation, field_trust } = data;
  const dc = dirColors[identity.dominant_direction] || '#6366f1';

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white" data-testid="profile-page">

      {/* ═══ TOP BAR ═══ */}
      <div className="sticky top-0 z-10 bg-[#0a0a12]/90 backdrop-blur-md border-b border-white/[0.04] px-4 py-2.5 flex items-center justify-between">
        <span className="text-[9px] tracking-[0.3em] uppercase text-gray-600 font-medium">Human Action Record</span>
        <a href="/" className="text-[10px] text-gray-500 hover:text-white transition-colors" data-testid="profile-back">Philos</a>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-8 pb-12 space-y-8">

        {/* ═══ HERO — Identity Document ═══ */}
        <section className="text-center" data-testid="profile-identity">
          {/* Dominant direction ambient line */}
          <div className="w-12 h-[2px] mx-auto mb-6 rounded-full" style={{ backgroundColor: dc }} />

          <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-xl font-bold mb-4" style={{ backgroundColor: `${dc}15`, color: dc, border: `1px solid ${dc}25` }}>
            {identity.alias?.charAt(0) || '?'}
          </div>

          <h1 className="text-2xl font-bold text-white mb-1.5">{identity.alias}</h1>

          <div className="flex items-center justify-center gap-2 text-[10px] text-gray-500 mb-3">
            <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{identity.country}</span>
            <span className="text-gray-700">·</span>
            <span>{new Date(identity.member_since).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</span>
          </div>

          {/* Identity markers */}
          <div className="flex items-center justify-center gap-2 flex-wrap mb-4">
            {identity.dominant_direction_he && (
              <span className="px-3 py-1 rounded-full text-[10px] font-medium" style={{ backgroundColor: `${dc}12`, color: dc, border: `1px solid ${dc}20` }} data-testid="profile-direction-badge">
                {identity.dominant_direction_he}
              </span>
            )}
            {identity.niche_label_he && (
              <span className="px-3 py-1 rounded-full text-[10px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20" data-testid="profile-niche-badge">
                {identity.niche_label_he}
              </span>
            )}
          </div>

          {/* Invited by — lineage */}
          {identity.invited_by_alias && (
            <p className="text-[10px] text-gray-600 mb-4" data-testid="profile-invited-by">
              Invited by <span className="text-gray-400">{identity.invited_by_alias}</span>
            </p>
          )}

          {/* AI Profile Interpretation */}
          {ai_profile_interpretation && (
            <p className="text-xs text-gray-500 italic leading-relaxed mb-4 max-w-xs mx-auto" data-testid="ai-profile-interpretation">
              {ai_profile_interpretation}
            </p>
          )}

          {/* Share actions — prominent */}
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setShowShare(true)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-[10px] font-medium transition-all hover:bg-white/10"
              style={{ backgroundColor: `${dc}12`, color: dc, border: `1px solid ${dc}20` }}
              data-testid="profile-share-btn"
            >
              <Share2 className="w-3 h-3" />Share Record
            </button>
            <button
              onClick={handleCopyLink}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-[10px] font-medium bg-white/[0.04] text-gray-400 border border-white/[0.06] transition-all hover:bg-white/[0.08]"
              data-testid="profile-copy-link-btn"
            >
              {linkCopied ? <><Check className="w-3 h-3 text-emerald-400" /><span className="text-emerald-400">Copied</span></> : <><Copy className="w-3 h-3" />Copy Link</>}
            </button>
          </div>
        </section>

        {/* ═══ STATS STRIP — Documentary metrics ═══ */}
        <section className="grid grid-cols-4 gap-px bg-white/[0.04] rounded-2xl overflow-hidden" data-testid="profile-stats-strip">
          <StatCell label="Impact" value={value_growth.impact_score} color={dc} testId="profile-impact" />
          <StatCell label="Actions" value={value_growth.total_actions} color="#9ca3af" testId="profile-actions" />
          <StatCell label="Streak" value={value_growth.streak} suffix=" days" color="#f59e0b" testId="profile-streak" />
          <StatCell label="Field Contribution" value={`${field_contribution?.field_percentage || 0}%`} color="#22c55e" testId="profile-field-contribution" />
        </section>

        {/* ═══ FIELD TRUST — Quiet indicator ═══ */}
        {field_trust && <FieldTrustBlock trust={field_trust} />}

        {/* ═══ TRUST HISTORY — Explainability ═══ */}
        {trustHistory && trustHistory.ledger && trustHistory.ledger.length > 0 && (
          <TrustHistorySection history={trustHistory} />
        )}

        {/* ═══ DIRECTION DISTRIBUTION ═══ */}
        <DirectionBar distribution={direction_distribution} total={value_growth.total_actions} dominantDir={identity.dominant_direction} />

        {/* ═══ OPPOSITION AXES — Tension map ═══ */}
        <OppositionAxes axes={opposition_axes} />

        {/* ═══ INFLUENCE CHAIN ═══ */}
        {influence_chain && (
          <InfluenceSection chain={influence_chain} />
        )}

        {/* ═══ ACTION RECORD — Recent actions ═══ */}
        <ActionRecord actions={action_record} expandedAction={expandedAction} setExpandedAction={setExpandedAction} />

        {/* ═══ FOOTER ═══ */}
        <footer className="text-center pt-4 border-t border-white/[0.04]">
          <p className="text-[9px] text-gray-700 tracking-wide">Philos Orientation · Human Action Record</p>
        </footer>
      </div>

      {/* Share Modal */}
      {showShare && (
        <ShareCardModal
          data={data}
          dominantColor={dc}
          profileUrl={profileUrl}
          onClose={() => setShowShare(false)}
        />
      )}
    </div>
  );
}


function StatCell({ label, value, suffix = '', color, testId }) {
  return (
    <div className="bg-[#0e0e1a] p-3 text-center" data-testid={testId}>
      <p className="text-lg font-bold tabular-nums" style={{ color }}>{value}{suffix}</p>
      <p className="text-[9px] text-gray-600 mt-0.5">{label}</p>
    </div>
  );
}


function FieldTrustBlock({ trust }) {
  const { value_score, risk_score, trust_score } = trust;
  const [showTooltip, setShowTooltip] = useState(false);

  const maxBar = Math.max(value_score, risk_score, 1);
  const valuePct = Math.min((value_score / maxBar) * 100, 100);
  const riskPct = Math.min((risk_score / maxBar) * 100, 100);

  let stateLabel, stateColor;
  if (trust_score <= 0) {
    stateLabel = 'Restricted'; stateColor = '#ef4444';
  } else if (trust_score < 5) {
    stateLabel = 'Fragile'; stateColor = '#f59e0b';
  } else if (trust_score < 15) {
    stateLabel = 'Building'; stateColor = '#3b82f6';
  } else {
    stateLabel = 'Stable'; stateColor = '#22c55e';
  }

  return (
    <section data-testid="field-trust-block">
      <div className="flex items-center gap-1.5 mb-3">
        <p className="text-[10px] text-gray-600">Field Trust</p>
        <button
          onClick={() => setShowTooltip(!showTooltip)}
          className="text-gray-700 hover:text-gray-500 transition-colors"
          data-testid="field-trust-info-btn"
        >
          <Info className="w-3 h-3" />
        </button>
      </div>

      {showTooltip && (
        <p className="text-[9px] text-gray-500 leading-relaxed mb-3 bg-white/[0.02] rounded-lg p-2.5 border border-white/[0.04]" data-testid="field-trust-tooltip">
          Field trust reflects the value accumulated relative to risk patterns over time.
        </p>
      )}

      <div className="rounded-2xl bg-white/[0.02] border border-white/[0.04] p-4 space-y-3.5">
        {/* Value bar */}
        <div data-testid="field-trust-value">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] text-gray-500">Field Value</span>
            <span className="text-[10px] font-medium text-emerald-500 tabular-nums">{value_score}</span>
          </div>
          <div className="h-[3px] rounded-full bg-white/[0.06] overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${valuePct}%`, backgroundColor: '#22c55e' }}
            />
          </div>
        </div>

        {/* Risk bar */}
        <div data-testid="field-trust-risk">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] text-gray-500">Field Risk</span>
            <span className="text-[10px] font-medium text-red-400 tabular-nums">{risk_score}</span>
          </div>
          <div className="h-[3px] rounded-full bg-white/[0.06] overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${riskPct}%`, backgroundColor: '#ef444480' }}
            />
          </div>
        </div>

        {/* Trust state */}
        <div className="pt-2.5 border-t border-white/[0.04] flex items-center justify-between" data-testid="field-trust-state">
          <span className="text-[10px] text-gray-500">Trust Status</span>
          <span
            className="text-[10px] font-medium px-2.5 py-0.5 rounded-full"
            style={{ color: stateColor, backgroundColor: `${stateColor}12`, border: `1px solid ${stateColor}20` }}
            data-testid="field-trust-state-label"
          >
            {stateLabel}
          </span>
        </div>
      </div>
    </section>
  );
}


const SOURCE_LABELS = {
  daily_action: 'Daily Direction Action',
  globe_point: 'Field Point',
  mission_join: 'Mission Join',
  onboarding: 'First Action',
  invite_used: 'Invite Redeemed',
  manual: 'Manual Update',
  decay: 'Daily Decay',
};

const ACTION_LABELS = {
  contribute: 'Contribution',
  help: 'Help',
  create: 'Creation',
  explore: 'Exploration',
  spam: 'Spam',
  manipulation: 'Manipulation',
  aggression: 'Aggression',
  deception: 'Deception',
  disruption: 'Disruption',
  decay: 'Decay',
};

function buildSummaryLine(history) {
  const { summary_by_source, ledger, trust_score, value_score, risk_score } = history;
  if (!summary_by_source || Object.keys(summary_by_source).length === 0) return null;

  // --- Compute trust state ---
  let state;
  if (trust_score <= 0) state = 'restricted';
  else if (trust_score < 5) state = 'fragile';
  else if (trust_score < 15) state = 'building';
  else state = 'stable';

  // --- Aggregate by source: value contribution (positive flows) ---
  const positiveSources = Object.entries(summary_by_source)
    .filter(([k, v]) => k !== 'decay' && v.total_value_delta > 0)
    .sort((a, b) => b[1].total_value_delta - a[1].total_value_delta);

  // --- Risk contribution ---
  const riskSources = Object.entries(summary_by_source)
    .filter(([, v]) => v.total_risk_delta > 0)
    .sort((a, b) => b[1].total_risk_delta - a[1].total_risk_delta);

  const totalPositiveValue = positiveSources.reduce((s, [, v]) => s + v.total_value_delta, 0);
  const totalRisk = riskSources.reduce((s, [, v]) => s + v.total_risk_delta, 0);
  const decayData = summary_by_source.decay;
  const decayValueLoss = decayData ? Math.abs(decayData.total_value_delta) : 0;

  // --- Recentness: analyze last 5 entries ---
  const recent = (ledger || []).slice(0, 5);
  const recentDecayCount = recent.filter(e => e.source_flow === 'decay').length;
  const recentActionCount = recent.filter(e => e.source_flow !== 'decay').length;
  const recentlyDecayDominant = recentDecayCount >= 4;

  // --- Check if value is mainly from shallow sources (onboarding/manual one-offs) ---
  const shallowSources = ['onboarding', 'manual'];
  const shallowValue = positiveSources
    .filter(([k]) => shallowSources.includes(k))
    .reduce((s, [, v]) => s + v.total_value_delta, 0);
  const deepValue = totalPositiveValue - shallowValue;
  const mostlyShallow = totalPositiveValue > 0 && shallowValue > deepValue * 2;

  // --- Build summary ---

  // Case 1: Decay dominates recently
  if (recentlyDecayDominant && recentActionCount <= 1) {
    if (state === 'stable' || state === 'building') {
      return 'Recent trust changes are mainly from natural decay, but the foundation built still holds.';
    }
    return 'Daily decay is affecting trust — new actions will strengthen your standing.';
  }

  // Case 2: Risk materially shapes trust
  if (totalRisk > 0 && totalRisk > totalPositiveValue * 0.3) {
    const topRisk = riskSources[0];
    const topRiskKey = topRisk[0];
    if (state === 'restricted') {
      return 'Accumulated risk exceeds value, and field presence is currently restricted.';
    }
    if (state === 'fragile') {
      return 'Risk patterns are reducing some of the value built — field status is still fragile.';
    }
    const topPos = positiveSources.length > 0 ? positiveSources[0] : null;
    if (topPos && topPos[0] !== topRiskKey) {
      const posLabel = SOURCE_LABELS[topPos[0]] || topPos[0];
      const riskLabel = SOURCE_LABELS[topRiskKey] || topRiskKey;
      return `Value is built mainly from ${posLabel}, but ${riskLabel} reduces some of it.`;
    }
    return 'Accumulated value is partially offset by risk patterns — continued building is needed.';
  }

  // Case 3: Mostly shallow (onboarding/manual)
  if (mostlyShallow && positiveSources.length > 0) {
    if (state === 'building' || state === 'stable') {
      return 'Current value is mainly based on one-time actions — daily actions will strengthen the foundation.';
    }
    return 'Accumulated value is not yet backed by consistent field activity.';
  }

  // Case 4: Clear dominant positive source
  if (positiveSources.length > 0) {
    const top = positiveSources[0];
    const topLabel = SOURCE_LABELS[top[0]] || top[0];
    const topPct = totalPositiveValue > 0 ? Math.round((top[1].total_value_delta / totalPositiveValue) * 100) : 0;

    const decayNote = decayValueLoss > totalPositiveValue * 0.3
      ? ', with natural decay offsetting some of the value'
      : '';

    if (topPct >= 70) {
      return `${topLabel} is the main source of field value${decayNote}.`;
    }

    if (positiveSources.length >= 2) {
      const secondLabel = SOURCE_LABELS[positiveSources[1][0]] || positiveSources[1][0];
      return `Field value is built mainly from ${topLabel} and ${secondLabel}${decayNote}.`;
    }

    return `${topLabel} builds field value${decayNote}.`;
  }

  // Case 5: Only decay, no positive sources
  return 'No actions affecting trust yet — daily decay is running in the background.';
}

function formatTimestamp(ts) {
  try {
    const d = new Date(ts);
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short' }) +
      ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } catch { return ''; }
}

function TrustHistorySection({ history }) {
  const summary = buildSummaryLine(history);

  return (
    <section data-testid="trust-history-section">
      <p className="text-[10px] text-gray-600 mb-2">Field History</p>

      {summary && (
        <p className="text-[9px] text-gray-500 leading-relaxed mb-3 bg-white/[0.02] rounded-lg p-2.5 border border-white/[0.04]" data-testid="trust-history-summary">
          {summary}
        </p>
      )}

      <div className="rounded-2xl bg-white/[0.02] border border-white/[0.04] overflow-hidden divide-y divide-white/[0.04]">
        {history.ledger.map((entry) => {
          const srcLabel = SOURCE_LABELS[entry.source_flow] || entry.source_flow;
          const actLabel = ACTION_LABELS[entry.action_type] || entry.action_type;
          const isDecay = entry.source_flow === 'decay';
          const isRisk = entry.computed_risk_delta > 0 && entry.computed_value_delta === 0;
          const vd = entry.computed_value_delta;
          const rd = entry.computed_risk_delta;

          return (
            <div key={entry.id} className="px-3.5 py-2.5 flex items-center justify-between gap-2" data-testid="trust-history-item">
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-gray-300 truncate" data-testid="trust-history-item-source">{srcLabel}</p>
                <p className="text-[9px] text-gray-600 mt-0.5">{actLabel} · {formatTimestamp(entry.timestamp)}</p>
              </div>
              <div className="flex items-center gap-2.5 shrink-0">
                {vd !== 0 && (
                  <span
                    className="text-[9px] font-medium tabular-nums"
                    style={{ color: vd > 0 ? '#22c55e' : '#ef4444' }}
                    data-testid="trust-history-item-value-delta"
                  >
                    {vd > 0 ? '+' : ''}{vd.toFixed(2)}
                  </span>
                )}
                {rd !== 0 && (
                  <span
                    className="text-[9px] font-medium tabular-nums"
                    style={{ color: rd < 0 ? '#22c55e' : '#ef4444' }}
                    data-testid="trust-history-item-risk-delta"
                  >
                    {isRisk ? '' : ''}{rd > 0 ? '+' : ''}{rd.toFixed(2)}
                  </span>
                )}
                {isDecay && vd === 0 && rd === 0 && (
                  <span className="text-[9px] text-gray-700">—</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}


function DirectionBar({ distribution, total, dominantDir }) {
  if (!total) return null;
  const dirs = ['contribution', 'recovery', 'order', 'exploration'];
  return (
    <section data-testid="profile-direction-bar">
      <p className="text-[10px] text-gray-600 mb-2">Direction Distribution</p>
      <div className="flex h-[3px] rounded-full overflow-hidden bg-white/[0.04] mb-2">
        {dirs.map(d => {
          const pct = ((distribution[d] || 0) / total) * 100;
          return pct > 0 ? <div key={d} style={{ width: `${pct}%`, backgroundColor: dirColors[d] }} className="transition-all" /> : null;
        })}
      </div>
      <div className="flex gap-3">
        {dirs.map(d => {
          const count = distribution[d] || 0;
          const isDom = d === dominantDir;
          return (
            <div key={d} className="flex items-center gap-1" data-testid={`profile-dir-${d}`}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: dirColors[d], opacity: isDom ? 1 : 0.4 }} />
              <span className="text-[9px]" style={{ color: isDom ? dirColors[d] : '#4b5563' }}>
                {dirLabels[d]} {count}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}


function OppositionAxes({ axes }) {
  const axisData = [
    { key: 'chaos_order', left: 'Chaos', right: 'Order', leftC: '#f59e0b', rightC: '#6366f1' },
    { key: 'ego_collective', left: 'Ego', right: 'Collective', leftC: '#ef4444', rightC: '#22c55e' },
    { key: 'exploration_stability', left: 'Exploration', right: 'Stability', leftC: '#f59e0b', rightC: '#3b82f6' }
  ];

  return (
    <section data-testid="profile-opposition-axes">
      <p className="text-[10px] text-gray-600 mb-3">Opposition Axes</p>
      <div className="space-y-4">
        {axisData.map(a => {
          const val = axes[a.key] ?? 50;
          const domC = val > 55 ? a.rightC : val < 45 ? a.leftC : '#6b7280';
          return (
            <div key={a.key} data-testid={`axis-${a.key}`}>
              <div className="flex justify-between text-[10px] mb-1.5">
                <span style={{ color: a.leftC }}>{a.left}</span>
                <span style={{ color: a.rightC }}>{a.right}</span>
              </div>
              <div className="relative h-[3px] rounded-full bg-white/[0.06]">
                <div className="absolute inset-y-0 right-0 rounded-full" style={{ width: `${val}%`, background: `linear-gradient(to left, ${a.rightC}50, ${a.rightC}10)` }} />
                <div className="absolute inset-y-0 left-0 rounded-full" style={{ width: `${100 - val}%`, background: `linear-gradient(to right, ${a.leftC}50, ${a.leftC}10)` }} />
                {/* Position dot */}
                <div className="absolute top-1/2 -translate-y-1/2" style={{ right: `calc(${val}% - 5px)` }}>
                  <div className="w-[10px] h-[10px] rounded-full border-2 border-[#0a0a12]" style={{ backgroundColor: domC, boxShadow: `0 0 6px ${domC}50` }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}


function InfluenceSection({ chain }) {
  const hasData = chain.invited_by_alias || chain.total_invited > 0 || chain.invite_credits > 0;
  if (!hasData) return null;

  return (
    <section data-testid="profile-influence-chain">
      <p className="text-[10px] text-gray-600 mb-3">Influence Chain</p>
      <div className="rounded-2xl bg-white/[0.02] border border-white/[0.04] p-4 space-y-3">
        {chain.invited_by_alias && (
          <div className="flex items-center gap-2.5">
            <span className="w-6 h-6 rounded-lg bg-violet-500/10 flex items-center justify-center text-[10px] font-bold text-violet-400">
              {chain.invited_by_alias.charAt(0)}
            </span>
            <span className="text-xs text-gray-400">Invited by <span className="text-violet-400 font-medium">{chain.invited_by_alias}</span></span>
          </div>
        )}

        {chain.total_invited > 0 && (
          <div className="flex items-center gap-2.5">
            <span className="w-6 h-6 rounded-lg bg-emerald-500/10 flex items-center justify-center text-[10px] font-bold text-emerald-400">
              {chain.total_invited}
            </span>
            <div className="flex-1">
              <span className="text-xs text-gray-400">Brought {chain.total_invited} people to the field</span>
              {chain.invitees && chain.invitees.length > 0 && (
                <p className="text-[10px] text-gray-600 mt-0.5">{chain.invitees.join(', ')}</p>
              )}
            </div>
          </div>
        )}

        {/* Stats row */}
        <div className="flex gap-4 pt-2 border-t border-white/[0.04]">
          {chain.active_invitees > 0 && (
            <span className="text-[10px] text-emerald-500" data-testid="profile-active-invitees">
              {chain.active_invitees} active
            </span>
          )}
          {chain.invite_credits > 0 && (
            <span className="text-[10px] text-amber-500" data-testid="profile-invite-credits">
              {chain.invite_credits} value points
            </span>
          )}
        </div>
      </div>
    </section>
  );
}


function ActionRecord({ actions, expandedAction, setExpandedAction }) {
  if (!actions?.length) {
    return (
      <section className="text-center py-8">
        <p className="text-[10px] text-gray-600">No recorded actions yet</p>
      </section>
    );
  }

  return (
    <section data-testid="profile-action-record">
      <div className="flex items-center justify-between mb-3">
        <p className="text-[10px] text-gray-600">Action Record</p>
        <span className="text-[9px] text-gray-700">{actions.length}</span>
      </div>
      <div className="space-y-2">
        {actions.map((a, i) => {
          const color = dirColors[a.direction] || '#6366f1';
          const isExpanded = expandedAction === i;
          const dateStr = a.date ? new Date(a.date).toLocaleDateString('en-US', { day: 'numeric', month: 'short' }) : '';
          return (
            <div key={i} className="rounded-xl border border-white/[0.04] overflow-hidden bg-white/[0.02] transition-all" data-testid={`action-record-${i}`}>
              <button className="w-full flex items-center gap-2.5 p-3 text-right" onClick={() => setExpandedAction(isExpanded ? null : i)}>
                <div className="w-1 h-8 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-[10px] font-medium" style={{ color }}>{a.direction_he}</span>
                    <span className="text-[9px] text-gray-700">{dateStr}</span>
                  </div>
                  <p className="text-xs text-gray-300 truncate">{a.action_he}</p>
                </div>
                <span className="text-[10px] font-medium flex-shrink-0 text-gray-500">+{a.impact}</span>
                {isExpanded ? <ChevronUp className="w-3 h-3 text-gray-600 flex-shrink-0" /> : <ChevronDown className="w-3 h-3 text-gray-600 flex-shrink-0" />}
              </button>
              {isExpanded && a.meanings && (
                <div className="px-3 pb-3 pt-0 border-t border-white/[0.04]" data-testid={`action-meanings-${i}`}>
                  <p className="text-[9px] text-gray-700 mb-2 mt-2">Interpretation</p>
                  <div className="grid grid-cols-2 gap-1.5">
                    <MeaningCard label="Personal" text={a.meanings.personal_he} color="#6366f1" />
                    <MeaningCard label="Social" text={a.meanings.social_he} color="#22c55e" />
                    <MeaningCard label="Value" text={a.meanings.value_he} color="#f59e0b" />
                    <MeaningCard label="Systemic" text={a.meanings.system_he} color="#3b82f6" />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}


function MeaningCard({ label, text, color }) {
  return (
    <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}08`, border: `1px solid ${color}10` }}>
      <p className="text-[9px] font-medium mb-0.5" style={{ color }}>{label}</p>
      <p className="text-[9px] text-gray-500 leading-relaxed">{text}</p>
    </div>
  );
}


function ShareCardModal({ data, dominantColor, profileUrl, onClose }) {
  const cardRef = useRef(null);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  const { identity, opposition_axes, value_growth, influence_chain, field_contribution } = data;
  const dc = dominantColor;

  const axisData = [
    { key: 'chaos_order', left: 'Chaos', right: 'Order', leftC: '#f59e0b', rightC: '#6366f1' },
    { key: 'ego_collective', left: 'Ego', right: 'Collective', leftC: '#ef4444', rightC: '#22c55e' },
    { key: 'exploration_stability', left: 'Exploration', right: 'Stability', leftC: '#f59e0b', rightC: '#3b82f6' }
  ];

  const handleDownload = useCallback(async () => {
    if (!cardRef.current) return;
    setDownloading(true);
    try {
      const dataUrl = await toPng(cardRef.current, { quality: 0.95, pixelRatio: 2, backgroundColor: '#0a0a12' });
      const link = document.createElement('a');
      link.download = `philos-${identity.alias}.png`;
      link.href = dataUrl;
      link.click();
    } catch (e) {
      console.error('Share card error:', e);
    } finally { setDownloading(false); }
  }, [identity.alias]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(profileUrl).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }, [profileUrl]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={onClose} data-testid="share-modal-overlay">
      <div className="w-full max-w-md" onClick={e => e.stopPropagation()}>

        {/* ═══ SHARE CARD ═══ */}
        <div ref={cardRef} className="rounded-2xl overflow-hidden" style={{ backgroundColor: '#0a0a12' }} data-testid="share-card">
          <div className="p-6" data-testid="share-card-inner">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <span className="text-[8px] tracking-[0.3em] uppercase text-gray-600 font-medium">Human Action Record</span>
              <span className="text-[8px] text-gray-700">Philos</span>
            </div>

            {/* Identity */}
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold" style={{ backgroundColor: `${dc}15`, color: dc, border: `1px solid ${dc}25` }}>
                {identity.alias?.charAt(0)}
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">{identity.alias}</h2>
                <div className="flex items-center gap-2 text-[10px] text-gray-500">
                  <span>{identity.country}</span>
                  {identity.dominant_direction_he && (
                    <><span className="text-gray-700">·</span><span style={{ color: dc }}>{identity.dominant_direction_he}</span></>
                  )}
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-px bg-white/[0.04] rounded-xl overflow-hidden mb-5">
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold" style={{ color: dc }}>{value_growth.impact_score}</p>
                <p className="text-[7px] text-gray-600">Impact</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-white">{value_growth.total_actions}</p>
                <p className="text-[7px] text-gray-600">Actions</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-amber-400">{value_growth.streak}</p>
                <p className="text-[7px] text-gray-600">Streak</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-emerald-400">{field_contribution?.field_percentage || 0}%</p>
                <p className="text-[7px] text-gray-600">Field Contribution</p>
              </div>
            </div>

            {/* Opposition Axes */}
            <div className="space-y-2 mb-5">
              {axisData.map(a => {
                const val = opposition_axes[a.key] ?? 50;
                return (
                  <div key={a.key}>
                    <div className="flex justify-between text-[8px] mb-1">
                      <span style={{ color: a.leftC }}>{a.left}</span>
                      <span style={{ color: a.rightC }}>{a.right}</span>
                    </div>
                    <div className="relative h-[2px] bg-white/[0.06] rounded-full">
                      <div className="absolute inset-y-0 right-0 rounded-full" style={{ width: `${val}%`, background: `linear-gradient(to left, ${a.rightC}50, ${a.rightC}10)` }} />
                      <div className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white" style={{ right: `calc(${val}% - 4px)`, boxShadow: `0 0 4px ${val > 50 ? a.rightC : a.leftC}60` }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Influence */}
            {(influence_chain?.total_invited > 0 || influence_chain?.invite_credits > 0) && (
              <div className="flex items-center gap-4 mb-5 py-2 border-t border-b border-white/[0.04]">
                {influence_chain.total_invited > 0 && (
                  <span className="text-[9px] text-emerald-500">Brought {influence_chain.total_invited} people to the field</span>
                )}
                {influence_chain.active_invitees > 0 && (
                  <span className="text-[9px] text-emerald-400">{influence_chain.active_invitees} active</span>
                )}
                {influence_chain.invite_credits > 0 && (
                  <span className="text-[9px] text-amber-500">{influence_chain.invite_credits} points</span>
                )}
              </div>
            )}

            {/* Footer with URL */}
            <div className="flex items-center justify-between">
              <span className="text-[8px] text-gray-600">{new Date().toLocaleDateString('en-US')}</span>
              <span className="text-[8px] text-gray-700 font-mono" dir="ltr">philos-orientation/profile</span>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 mt-3">
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-white text-gray-900 rounded-xl text-xs font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
            data-testid="share-download-btn"
          >
            {downloading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <><Download className="w-3.5 h-3.5" />Download Image</>}
          </button>
          <button
            onClick={handleCopy}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-white/10 text-white rounded-xl text-xs font-medium hover:bg-white/20 transition-colors"
            data-testid="share-copy-link-btn"
          >
            {copied ? <><Check className="w-3.5 h-3.5 text-emerald-400" /><span className="text-emerald-400">Copied</span></> : <><Link2 className="w-3.5 h-3.5" />Copy Link</>}
          </button>
        </div>

        <p className="text-center text-[10px] text-gray-600 mt-2 cursor-pointer" onClick={onClose}>Click outside to close</p>
      </div>
    </div>
  );
}

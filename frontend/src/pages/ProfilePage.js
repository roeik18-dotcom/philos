import { useState, useEffect, useRef, useCallback } from 'react';
import { toPng } from 'html-to-image';
import { MapPin, ChevronDown, ChevronUp, Loader2, Flame, Share2, Download, Link2, Check, Copy } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };

export default function ProfilePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedAction, setExpandedAction] = useState(null);
  const [showShare, setShowShare] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  const pathParts = window.location.pathname.split('/');
  const userId = pathParts[pathParts.length - 1];
  const profileUrl = `${window.location.origin}/profile/${userId}`;

  useEffect(() => {
    fetch(`${API_URL}/api/profile/${userId}/record`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
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
        <p className="text-sm text-gray-500">רשומה לא נמצאה</p>
        <a href="/" className="text-xs text-gray-400 hover:text-white transition-colors">חזרה ל-Philos</a>
      </div>
    );
  }

  const { identity, action_record, opposition_axes, value_growth, direction_distribution, influence_chain, field_contribution, ai_profile_interpretation } = data;
  const dc = dirColors[identity.dominant_direction] || '#6366f1';

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white" dir="rtl" data-testid="profile-page">

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
            <span>{new Date(identity.member_since).toLocaleDateString('he-IL', { month: 'short', year: 'numeric' })}</span>
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
              הוזמן על ידי <span className="text-gray-400">{identity.invited_by_alias}</span>
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
              <Share2 className="w-3 h-3" />שתף רשומה
            </button>
            <button
              onClick={handleCopyLink}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-[10px] font-medium bg-white/[0.04] text-gray-400 border border-white/[0.06] transition-all hover:bg-white/[0.08]"
              data-testid="profile-copy-link-btn"
            >
              {linkCopied ? <><Check className="w-3 h-3 text-emerald-400" /><span className="text-emerald-400">הועתק</span></> : <><Copy className="w-3 h-3" />העתק קישור</>}
            </button>
          </div>
        </section>

        {/* ═══ STATS STRIP — Documentary metrics ═══ */}
        <section className="grid grid-cols-4 gap-px bg-white/[0.04] rounded-2xl overflow-hidden" data-testid="profile-stats-strip">
          <StatCell label="השפעה" value={value_growth.impact_score} color={dc} testId="profile-impact" />
          <StatCell label="פעולות" value={value_growth.total_actions} color="#9ca3af" testId="profile-actions" />
          <StatCell label="רצף" value={value_growth.streak} suffix=" ימים" color="#f59e0b" testId="profile-streak" />
          <StatCell label="תרומה לשדה" value={`${field_contribution?.field_percentage || 0}%`} color="#22c55e" testId="profile-field-contribution" />
        </section>

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


function DirectionBar({ distribution, total, dominantDir }) {
  if (!total) return null;
  const dirs = ['contribution', 'recovery', 'order', 'exploration'];
  return (
    <section data-testid="profile-direction-bar">
      <p className="text-[10px] text-gray-600 mb-2">התפלגות כיוונים</p>
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
    { key: 'chaos_order', left: 'כאוס', right: 'סדר', leftC: '#f59e0b', rightC: '#6366f1' },
    { key: 'ego_collective', left: 'אגו', right: 'קולקטיב', leftC: '#ef4444', rightC: '#22c55e' },
    { key: 'exploration_stability', left: 'חקירה', right: 'יציבות', leftC: '#f59e0b', rightC: '#3b82f6' }
  ];

  return (
    <section data-testid="profile-opposition-axes">
      <p className="text-[10px] text-gray-600 mb-3">ציר הניגודים</p>
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
      <p className="text-[10px] text-gray-600 mb-3">שרשרת השפעה</p>
      <div className="rounded-2xl bg-white/[0.02] border border-white/[0.04] p-4 space-y-3">
        {chain.invited_by_alias && (
          <div className="flex items-center gap-2.5">
            <span className="w-6 h-6 rounded-lg bg-violet-500/10 flex items-center justify-center text-[10px] font-bold text-violet-400">
              {chain.invited_by_alias.charAt(0)}
            </span>
            <span className="text-xs text-gray-400">הוזמן על ידי <span className="text-violet-400 font-medium">{chain.invited_by_alias}</span></span>
          </div>
        )}

        {chain.total_invited > 0 && (
          <div className="flex items-center gap-2.5">
            <span className="w-6 h-6 rounded-lg bg-emerald-500/10 flex items-center justify-center text-[10px] font-bold text-emerald-400">
              {chain.total_invited}
            </span>
            <div className="flex-1">
              <span className="text-xs text-gray-400">הביא לשדה {chain.total_invited} אנשים</span>
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
              {chain.active_invitees} פעילים
            </span>
          )}
          {chain.invite_credits > 0 && (
            <span className="text-[10px] text-amber-500" data-testid="profile-invite-credits">
              {chain.invite_credits} נקודות ערך
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
        <p className="text-[10px] text-gray-600">אין פעולות מתועדות עדיין</p>
      </section>
    );
  }

  return (
    <section data-testid="profile-action-record">
      <div className="flex items-center justify-between mb-3">
        <p className="text-[10px] text-gray-600">רשומת פעולות</p>
        <span className="text-[9px] text-gray-700">{actions.length}</span>
      </div>
      <div className="space-y-2">
        {actions.map((a, i) => {
          const color = dirColors[a.direction] || '#6366f1';
          const isExpanded = expandedAction === i;
          const dateStr = a.date ? new Date(a.date).toLocaleDateString('he-IL', { day: 'numeric', month: 'short' }) : '';
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
                  <p className="text-[9px] text-gray-700 mb-2 mt-2">פרשנות</p>
                  <div className="grid grid-cols-2 gap-1.5">
                    <MeaningCard label="אישי" text={a.meanings.personal_he} color="#6366f1" />
                    <MeaningCard label="חברתי" text={a.meanings.social_he} color="#22c55e" />
                    <MeaningCard label="ערכי" text={a.meanings.value_he} color="#f59e0b" />
                    <MeaningCard label="מערכתי" text={a.meanings.system_he} color="#3b82f6" />
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
    { key: 'chaos_order', left: 'כאוס', right: 'סדר', leftC: '#f59e0b', rightC: '#6366f1' },
    { key: 'ego_collective', left: 'אגו', right: 'קולקטיב', leftC: '#ef4444', rightC: '#22c55e' },
    { key: 'exploration_stability', left: 'חקירה', right: 'יציבות', leftC: '#f59e0b', rightC: '#3b82f6' }
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
          <div className="p-6" dir="rtl">
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
                <p className="text-[7px] text-gray-600">השפעה</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-white">{value_growth.total_actions}</p>
                <p className="text-[7px] text-gray-600">פעולות</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-amber-400">{value_growth.streak}</p>
                <p className="text-[7px] text-gray-600">רצף</p>
              </div>
              <div className="bg-[#0e0e1a] p-2.5 text-center">
                <p className="text-base font-bold text-emerald-400">{field_contribution?.field_percentage || 0}%</p>
                <p className="text-[7px] text-gray-600">תרומה לשדה</p>
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
                  <span className="text-[9px] text-emerald-500">הביא {influence_chain.total_invited} אנשים לשדה</span>
                )}
                {influence_chain.active_invitees > 0 && (
                  <span className="text-[9px] text-emerald-400">{influence_chain.active_invitees} פעילים</span>
                )}
                {influence_chain.invite_credits > 0 && (
                  <span className="text-[9px] text-amber-500">{influence_chain.invite_credits} נקודות</span>
                )}
              </div>
            )}

            {/* Footer with URL */}
            <div className="flex items-center justify-between">
              <span className="text-[8px] text-gray-600">{new Date().toLocaleDateString('he-IL')}</span>
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
            {downloading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <><Download className="w-3.5 h-3.5" />הורד תמונה</>}
          </button>
          <button
            onClick={handleCopy}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-white/10 text-white rounded-xl text-xs font-medium hover:bg-white/20 transition-colors"
            data-testid="share-copy-link-btn"
          >
            {copied ? <><Check className="w-3.5 h-3.5 text-emerald-400" /><span className="text-emerald-400">הועתק</span></> : <><Link2 className="w-3.5 h-3.5" />העתק קישור</>}
          </button>
        </div>

        <p className="text-center text-[10px] text-gray-600 mt-2 cursor-pointer" onClick={onClose}>לחץ בחוץ לסגירה</p>
      </div>
    </div>
  );
}

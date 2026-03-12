import { useState, useEffect, useRef, useCallback } from 'react';
import { toPng } from 'html-to-image';
import { Compass, MapPin, Shield, Zap, Target, Award, ArrowRight, ChevronDown, ChevronUp, Loader2, Flame, Share2, Download, Link2, Check } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };

export default function ProfilePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedAction, setExpandedAction] = useState(null);
  const [showShare, setShowShare] = useState(false);

  const pathParts = window.location.pathname.split('/');
  const userId = pathParts[pathParts.length - 1];

  useEffect(() => {
    fetch(`${API_URL}/api/profile/${userId}/record`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf9f6] flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#faf9f6] flex flex-col items-center justify-center gap-3 px-4">
        <p className="text-sm text-gray-400">Record not found</p>
        <a href="/" className="text-xs text-indigo-500 hover:underline">Back to Philos</a>
      </div>
    );
  }

  const { identity, action_record, opposition_axes, value_growth, direction_distribution, influence_chain } = data;
  const dominantColor = dirColors[identity.dominant_direction] || '#6366f1';

  return (
    <div className="min-h-screen bg-[#faf9f6]" dir="rtl" data-testid="profile-page">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-[#faf9f6]/90 backdrop-blur-sm border-b border-gray-100 px-4 py-2.5 flex items-center justify-between">
        <span className="text-[10px] tracking-widest text-gray-300 uppercase font-medium">Human Action Record</span>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowShare(true)}
            className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600 transition-colors"
            data-testid="profile-share-btn"
          >
            <Share2 className="w-3 h-3" />שתף
          </button>
          <a href="/" className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600" data-testid="profile-back">
            <ArrowRight className="w-3 h-3" />Philos
          </a>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        <IdentityHeader identity={identity} dominantColor={dominantColor} />
        <OppositionAxes axes={opposition_axes} />
        <ValueGrowth growth={value_growth} dominantColor={dominantColor} />
        <DirectionBar distribution={direction_distribution} total={value_growth.total_actions} />
        {influence_chain && (influence_chain.invited_by_alias || (influence_chain.invitees && influence_chain.invitees.length > 0)) && (
          <InfluenceChain chain={influence_chain} />
        )}
        <ActionRecord actions={action_record} expandedAction={expandedAction} setExpandedAction={setExpandedAction} />
      </div>

      {/* Share Modal */}
      {showShare && (
        <ShareCardModal
          data={data}
          dominantColor={dominantColor}
          profileUrl={`${window.location.origin}/profile/${userId}`}
          onClose={() => setShowShare(false)}
        />
      )}
    </div>
  );
}


function IdentityHeader({ identity, dominantColor }) {
  const initial = identity.alias?.charAt(0) || '?';
  return (
    <section className="text-center" data-testid="profile-identity">
      <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-white text-xl font-bold mb-3 shadow-lg" style={{ backgroundColor: dominantColor }}>
        {initial}
      </div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">{identity.alias}</h1>
      <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mb-2">
        <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{identity.country}</span>
        <span className="text-gray-200">|</span>
        <span>חבר מ-{new Date(identity.member_since).toLocaleDateString('he-IL', { month: 'short', year: 'numeric' })}</span>
      </div>
      <div className="flex items-center justify-center gap-2 flex-wrap">
        {identity.dominant_direction_he && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold" style={{ backgroundColor: `${dominantColor}12`, color: dominantColor }} data-testid="profile-direction-badge">
            {identity.dominant_direction_he}
          </span>
        )}
        {identity.niche_label_he && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-purple-50 text-purple-600" data-testid="profile-niche-badge">
            {identity.niche_label_he}
          </span>
        )}
      </div>
      {identity.invited_by_alias && (
        <p className="text-[10px] text-gray-400 mt-2" data-testid="profile-invited-by">
          הוזמן על ידי <span className="font-medium text-violet-500">{identity.invited_by_alias}</span>
        </p>
      )}
    </section>
  );
}


function OppositionAxes({ axes }) {
  const axisData = [
    { key: 'chaos_order', leftLabel: 'כאוס', rightLabel: 'סדר', leftColor: '#f59e0b', rightColor: '#6366f1' },
    { key: 'ego_collective', leftLabel: 'אגו', rightLabel: 'קולקטיב', leftColor: '#ef4444', rightColor: '#22c55e' },
    { key: 'exploration_stability', leftLabel: 'חקירה', rightLabel: 'יציבות', leftColor: '#f59e0b', rightColor: '#3b82f6' }
  ];

  return (
    <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="profile-opposition-axes">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">ציר הניגודים</h2>
      </div>
      <div className="space-y-4">
        {axisData.map(axis => {
          const value = axes[axis.key] ?? 50;
          return (
            <div key={axis.key} data-testid={`axis-${axis.key}`}>
              <div className="flex justify-between text-[10px] mb-1.5">
                <span className="font-semibold" style={{ color: axis.leftColor }}>{axis.leftLabel}</span>
                <span className="font-semibold" style={{ color: axis.rightColor }}>{axis.rightLabel}</span>
              </div>
              <div className="relative h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="absolute top-0 h-full rounded-full transition-all duration-500" style={{ right: 0, width: `${value}%`, background: `linear-gradient(to left, ${axis.rightColor}, ${axis.rightColor}40)` }} />
                <div className="absolute top-0 w-3.5 h-3.5 -mt-[2px] rounded-full bg-white border-2 shadow-sm transition-all duration-500" style={{ right: `calc(${value}% - 7px)`, borderColor: value > 50 ? axis.rightColor : axis.leftColor }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}


function ValueGrowth({ growth, dominantColor }) {
  return (
    <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="profile-value-growth">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">צמיחת ערך</h2>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold" style={{ color: dominantColor }}>{growth.impact_score}</p>
          <p className="text-[9px] text-gray-400">השפעה</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold text-gray-800">Lv.{growth.level}</p>
          <p className="text-[9px] text-gray-400">דרגה</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold text-gray-800">{growth.circle_memberships}</p>
          <p className="text-[9px] text-gray-400">מעגלים</p>
        </div>
      </div>
      <div className="space-y-2.5">
        <ProgressRow label="התקדמות דרגה" value={growth.level_progress} color={dominantColor} />
        {growth.niche_progress > 0 && <ProgressRow label="התקדמות נישה" value={growth.niche_progress} color="#a855f7" />}
      </div>
      <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-50">
        {growth.streak > 0 && (
          <span className="flex items-center gap-1 text-[10px] text-orange-500 font-medium" data-testid="profile-streak">
            <Flame className="w-3 h-3" />{growth.streak} ימים רצף
          </span>
        )}
        {growth.badges?.length > 0 && (
          <span className="flex items-center gap-1 text-[10px] text-amber-500 font-medium">
            <Award className="w-3 h-3" />{growth.badges.length} תגים
          </span>
        )}
        <span className="flex items-center gap-1 text-[10px] text-gray-400">
          <Zap className="w-3 h-3" />{growth.total_actions} פעולות
        </span>
      </div>
    </section>
  );
}


function DirectionBar({ distribution, total }) {
  if (!total) return null;
  const dirs = ['contribution', 'recovery', 'order', 'exploration'];
  return (
    <section data-testid="profile-direction-bar">
      <div className="flex h-2 rounded-full overflow-hidden">
        {dirs.map(d => {
          const pct = (distribution[d] || 0) / total * 100;
          return pct > 0 ? <div key={d} style={{ width: `${pct}%`, backgroundColor: dirColors[d] }} className="transition-all" /> : null;
        })}
      </div>
      <div className="flex justify-between mt-1.5">
        {dirs.map(d => (
          <span key={d} className="text-[9px] flex items-center gap-0.5" style={{ color: dirColors[d] }}>
            <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ backgroundColor: dirColors[d] }} />
            {dirLabels[d]} {distribution[d] || 0}
          </span>
        ))}
      </div>
    </section>
  );
}


function ActionRecord({ actions, expandedAction, setExpandedAction }) {
  if (!actions?.length) {
    return (
      <section className="text-center py-8">
        <p className="text-sm text-gray-400">אין פעולות מתועדות עדיין</p>
      </section>
    );
  }

  return (
    <section data-testid="profile-action-record">
      <div className="flex items-center gap-2 mb-3">
        <Compass className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">רשומת פעולות</h2>
        <span className="text-[10px] text-gray-300 mr-auto">{actions.length} פעולות</span>
      </div>
      <div className="space-y-2">
        {actions.map((a, i) => {
          const color = dirColors[a.direction] || '#6366f1';
          const isExpanded = expandedAction === i;
          const dateStr = a.date ? new Date(a.date).toLocaleDateString('he-IL', { day: 'numeric', month: 'short' }) : '';
          return (
            <div key={i} className="bg-white rounded-xl border border-gray-100 overflow-hidden transition-all shadow-sm" data-testid={`action-record-${i}`}>
              <button className="w-full flex items-center gap-2.5 p-3 text-right" onClick={() => setExpandedAction(isExpanded ? null : i)}>
                <div className="w-1 h-8 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-[10px] font-semibold" style={{ color }}>{a.direction_he}</span>
                    <span className="text-[9px] text-gray-300">{dateStr}</span>
                  </div>
                  <p className="text-xs text-gray-700 truncate">{a.action_he}</p>
                </div>
                <span className="text-xs font-bold flex-shrink-0" style={{ color }}>+{a.impact}</span>
                {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" /> : <ChevronDown className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" />}
              </button>
              {isExpanded && (
                <div className="px-3 pb-3 pt-0 border-t border-gray-50" data-testid={`action-meanings-${i}`}>
                  <p className="text-[9px] text-gray-300 mb-2 mt-2">פרשנות רב-ממדית</p>
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
    <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}06`, border: `1px solid ${color}15` }}>
      <p className="text-[9px] font-semibold mb-0.5" style={{ color }}>{label}</p>
      <p className="text-[9px] text-gray-600 leading-relaxed">{text}</p>
    </div>
  );
}


function ProgressRow({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-[10px] mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="font-semibold" style={{ color }}>{value}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}


function ShareCardModal({ data, dominantColor, profileUrl, onClose }) {
  const cardRef = useRef(null);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  const { identity, opposition_axes, value_growth, action_record } = data;
  const highlightAction = action_record?.[0] || null;

  const axisData = [
    { key: 'chaos_order', left: 'כאוס', right: 'סדר', leftC: '#f59e0b', rightC: '#6366f1' },
    { key: 'ego_collective', left: 'אגו', right: 'קולקטיב', leftC: '#ef4444', rightC: '#22c55e' },
    { key: 'exploration_stability', left: 'חקירה', right: 'יציבות', leftC: '#f59e0b', rightC: '#3b82f6' }
  ];

  const handleDownload = useCallback(async () => {
    if (!cardRef.current) return;
    setDownloading(true);
    try {
      const dataUrl = await toPng(cardRef.current, { quality: 0.95, pixelRatio: 2, backgroundColor: '#1a1a2e' });
      const link = document.createElement('a');
      link.download = `philos-record-${identity.alias}.png`;
      link.href = dataUrl;
      link.click();
    } catch (e) {
      console.error('Share card generation failed:', e);
    } finally {
      setDownloading(false);
    }
  }, [identity.alias]);

  const handleCopyLink = useCallback(() => {
    navigator.clipboard.writeText(profileUrl).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {});
  }, [profileUrl]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={onClose} data-testid="share-modal-overlay">
      <div className="w-full max-w-md" onClick={e => e.stopPropagation()}>
        {/* The share card — captured by html-to-image */}
        <div ref={cardRef} className="rounded-2xl overflow-hidden" style={{ backgroundColor: '#1a1a2e' }} data-testid="share-card">
          {/* Card content */}
          <div className="p-6" dir="rtl">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <span className="text-[9px] tracking-[0.25em] uppercase text-gray-500 font-medium">Human Action Record</span>
              <span className="text-[8px] text-gray-600">Philos Orientation</span>
            </div>

            {/* Identity */}
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white text-lg font-bold" style={{ backgroundColor: dominantColor }}>
                {identity.alias?.charAt(0)}
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">{identity.alias}</h2>
                <div className="flex items-center gap-2 text-[10px] text-gray-400">
                  <span>{identity.country}</span>
                  {identity.dominant_direction_he && (
                    <>
                      <span className="text-gray-600">·</span>
                      <span style={{ color: dominantColor }}>{identity.dominant_direction_he}</span>
                    </>
                  )}
                  {identity.niche_label_he && (
                    <>
                      <span className="text-gray-600">·</span>
                      <span className="text-purple-400">{identity.niche_label_he}</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-700/50 mb-5" />

            {/* Stats row */}
            <div className="grid grid-cols-3 gap-3 mb-5">
              <div className="text-center">
                <p className="text-xl font-bold text-white">{value_growth.impact_score}</p>
                <p className="text-[8px] text-gray-500 mt-0.5">השפעה</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-white">Lv.{value_growth.level}</p>
                <p className="text-[8px] text-gray-500 mt-0.5">דרגה</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-white">{value_growth.total_actions}</p>
                <p className="text-[8px] text-gray-500 mt-0.5">פעולות</p>
              </div>
            </div>

            {/* Opposition Axes */}
            <div className="space-y-2.5 mb-5">
              {axisData.map(a => {
                const val = opposition_axes[a.key] ?? 50;
                return (
                  <div key={a.key}>
                    <div className="flex justify-between text-[8px] mb-1">
                      <span style={{ color: a.leftC }}>{a.left}</span>
                      <span style={{ color: a.rightC }}>{a.right}</span>
                    </div>
                    <div className="relative h-1.5 bg-gray-700/50 rounded-full">
                      <div className="absolute top-0 h-full rounded-full" style={{ right: 0, width: `${val}%`, background: `linear-gradient(to left, ${a.rightC}, ${a.rightC}40)` }} />
                      <div className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white shadow-lg" style={{ right: `calc(${val}% - 5px)` }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Highlighted action */}
            {highlightAction && (
              <div className="rounded-xl p-3 mb-4" style={{ backgroundColor: `${dirColors[highlightAction.direction] || dominantColor}10` }}>
                <div className="flex items-center gap-1.5 mb-1">
                  <div className="w-1 h-4 rounded-full" style={{ backgroundColor: dirColors[highlightAction.direction] || dominantColor }} />
                  <span className="text-[9px] font-semibold" style={{ color: dirColors[highlightAction.direction] || dominantColor }}>{highlightAction.direction_he}</span>
                  <span className="text-[8px] text-gray-500 mr-auto">+{highlightAction.impact}</span>
                </div>
                <p className="text-[10px] text-gray-300">{highlightAction.action_he}</p>
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-700/30">
              <span className="text-[8px] text-gray-600">philos-orientation.com</span>
              <span className="text-[8px] text-gray-600">{new Date().toLocaleDateString('he-IL')}</span>
            </div>
          </div>
        </div>

        {/* Action buttons (not captured in image) */}
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
            onClick={handleCopyLink}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-white/10 text-white rounded-xl text-xs font-medium hover:bg-white/20 transition-colors"
            data-testid="share-copy-link-btn"
          >
            {copied ? <><Check className="w-3.5 h-3.5 text-green-400" /><span className="text-green-400">הועתק!</span></> : <><Link2 className="w-3.5 h-3.5" />העתק קישור</>}
          </button>
        </div>

        {/* Close hint */}
        <p className="text-center text-[10px] text-gray-500 mt-2 cursor-pointer" onClick={onClose}>לחץ בחוץ לסגירה</p>
      </div>
    </div>
  );
}


function InfluenceChain({ chain }) {
  if (!chain) return null;
  return (
    <section className="bg-white rounded-2xl p-4 border border-gray-100" data-testid="profile-influence-chain">
      <p className="text-[10px] text-gray-400 mb-2.5">שרשרת השפעה</p>
      <div className="space-y-2">
        {chain.invited_by_alias && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span className="w-5 h-5 rounded-full bg-violet-100 flex items-center justify-center text-[9px] font-bold text-violet-600">
              {chain.invited_by_alias.charAt(0)}
            </span>
            <span><span className="font-medium text-violet-600">{chain.invited_by_alias}</span> הזמין אותך</span>
          </div>
        )}
        {chain.invitees && chain.invitees.length > 0 && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-[9px] font-bold text-emerald-600">
              {chain.total_invited || chain.invitees.length}
            </span>
            <span>הבאת לשדה: <span className="font-medium text-emerald-600">{chain.invitees.join(', ')}</span></span>
          </div>
        )}
        {(chain.active_invitees > 0 || chain.invite_credits > 0) && (
          <div className="flex gap-3 mt-1">
            {chain.active_invitees > 0 && (
              <span className="text-[10px] text-emerald-600" data-testid="profile-active-invitees">
                {chain.active_invitees} פעילים
              </span>
            )}
            {chain.invite_credits > 0 && (
              <span className="text-[10px] text-amber-600" data-testid="profile-invite-credits">
                {chain.invite_credits} נקודות ערך
              </span>
            )}
          </div>
        )}
      </div>
    </section>
  );
}


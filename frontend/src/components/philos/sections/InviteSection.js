import { useState, useEffect, useCallback } from 'react';
import { UserPlus, Copy, Check, Link2, ChevronDown, ChevronUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InviteSection({ userId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);
  const [showCodes, setShowCodes] = useState(false);
  const [creating, setCreating] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const fetchStats = useCallback(async () => {
    if (!effectiveUserId) return;
    try {
      const res = await fetch(`${API_URL}/api/orientation/invite-stats/${effectiveUserId}`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) setStats(json);
      }
    } catch (e) {}
  }, [effectiveUserId]);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  const handleCopy = async (code) => {
    const url = `${window.location.origin}/invite/${code}`;
    try {
      await navigator.clipboard.writeText(url);
    } catch {
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    }
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleCreate = async () => {
    if (!effectiveUserId || creating) return;
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/api/orientation/create-invite/${effectiveUserId}`, { method: 'POST' });
      if (res.ok) {
        const json = await res.json();
        if (json.success) fetchStats();
      }
    } catch (e) {}
    finally { setCreating(false); }
  };

  if (!stats) return null;

  const unusedCodes = (stats.codes || []).filter(c => !c.used);
  const usedCodes = (stats.codes || []).filter(c => c.used);

  return (
    <section className="philos-section bg-white border-border animate-section" dir="rtl" data-testid="invite-section">
      {/* Header + stats row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
            <UserPlus className="w-4 h-4 text-violet-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">הזמן לשדה</span>
            <p className="text-[10px] text-gray-400">צור שרשרת השפעה אנושית</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-center" data-testid="invite-used-count">
            <p className="text-sm font-bold text-violet-600">{stats.total_invites_used}</p>
            <p className="text-[9px] text-gray-400">הצטרפו</p>
          </div>
          <div className="text-center" data-testid="invite-remaining-count">
            <p className="text-sm font-bold text-gray-600">{stats.codes_remaining + unusedCodes.length}</p>
            <p className="text-[9px] text-gray-400">נותרו</p>
          </div>
        </div>
      </div>

      {/* Influence chain — who invited you */}
      {stats.invited_by_alias && (
        <div className="flex items-center gap-1.5 mb-3 px-2 py-1.5 bg-violet-50 rounded-xl" data-testid="invite-invited-by">
          <Link2 className="w-3 h-3 text-violet-400" />
          <span className="text-[10px] text-violet-600">הוזמנת על ידי <span className="font-semibold">{stats.invited_by_alias}</span></span>
        </div>
      )}

      {/* Invitees — who you brought */}
      {stats.invitees && stats.invitees.length > 0 && (
        <div className="flex items-center gap-1.5 mb-3 px-2 py-1.5 bg-emerald-50 rounded-xl" data-testid="invite-invitees">
          <span className="text-[10px] text-emerald-600">
            הבאת לשדה: {stats.invitees.map(i => i.alias).join(', ')}
          </span>
        </div>
      )}

      {/* Quick copy — first unused code */}
      {unusedCodes.length > 0 && (
        <div className="flex items-center gap-2 mb-2">
          <div className="flex-1 flex items-center gap-2 bg-gray-50 rounded-xl p-2 border border-gray-100">
            <span className="text-xs font-mono text-gray-600 flex-1" dir="ltr" data-testid="invite-code-display">{unusedCodes[0].code}</span>
            <button
              onClick={() => handleCopy(unusedCodes[0].code)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all flex items-center gap-1 ${
                copiedCode === unusedCodes[0].code ? 'bg-green-100 text-green-700' : 'bg-violet-100 text-violet-700 hover:bg-violet-200'
              }`}
              data-testid="invite-copy-btn"
            >
              {copiedCode === unusedCodes[0].code ? <><Check className="w-2.5 h-2.5" /><span>הועתק</span></> : <><Copy className="w-2.5 h-2.5" /><span>העתק קישור</span></>}
            </button>
          </div>
        </div>
      )}

      {/* Toggle all codes */}
      {stats.codes && stats.codes.length > 1 && (
        <button
          onClick={() => setShowCodes(!showCodes)}
          className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600 transition-colors mb-2"
          data-testid="invite-toggle-codes"
        >
          {showCodes ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          {showCodes ? 'הסתר קודים' : `הצג את כל הקודים (${stats.codes.length})`}
        </button>
      )}

      {showCodes && (
        <div className="space-y-1.5 mb-2 animate-fadeIn">
          {stats.codes.map((c) => (
            <div key={c.code} className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg text-[10px] ${c.used ? 'bg-emerald-50 border border-emerald-100' : 'bg-gray-50 border border-gray-100'}`}>
              <span className="font-mono text-gray-600" dir="ltr">{c.code}</span>
              {c.used ? (
                <span className="text-emerald-600 font-medium">נוצל</span>
              ) : (
                <button
                  onClick={() => handleCopy(c.code)}
                  className="text-violet-600 hover:text-violet-700 font-medium"
                >
                  {copiedCode === c.code ? 'הועתק' : 'העתק'}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create new code if under limit */}
      {stats.codes_remaining > 0 && unusedCodes.length === 0 && (
        <button
          onClick={handleCreate}
          disabled={creating}
          className="w-full py-2.5 px-4 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl text-xs font-medium transition-all flex items-center justify-center gap-2 active:scale-[0.97]"
          data-testid="invite-create-btn"
        >
          {creating ? '...' : <><UserPlus className="w-3.5 h-3.5" /><span>צור קוד הזמנה</span></>}
        </button>
      )}
    </section>
  );
}

import { useState, useEffect, useCallback } from 'react';
import { UserPlus, Copy, Check, Link2, Loader2, RefreshCw } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InviteSection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedCode, setCopiedCode] = useState(null);
  const [generating, setGenerating] = useState(false);

  const token = localStorage.getItem('philos_auth_token');

  const fetchInvites = useCallback(async () => {
    if (!token) { setLoading(false); return; }
    try {
      const res = await fetch(`${API_URL}/api/invites/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success) setData(json);
      }
    } catch (e) {
      console.log('Could not fetch invites:', e);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchInvites(); }, [fetchInvites]);

  const handleCopy = async (code) => {
    const url = `${window.location.origin}/join?invite=${code}`;
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
    // Track share event
    fetch(`${API_URL}/api/invites/share`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ code }),
    }).catch(() => {});
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleGenerate = async () => {
    if (generating) return;
    setGenerating(true);
    try {
      const res = await fetch(`${API_URL}/api/invites/generate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) fetchInvites();
    } catch (e) {
      console.log('Could not generate invite:', e);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <section className="rounded-2xl border border-gray-100 bg-white p-4 animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3" />
        <div className="h-10 bg-gray-200 rounded w-full" />
      </section>
    );
  }

  if (!token) {
    return (
      <section className="rounded-2xl border border-dashed border-gray-200 p-4 text-center" data-testid="invite-section-auth-gate">
        <UserPlus className="w-5 h-5 text-gray-300 mx-auto mb-2" />
        <p className="text-xs text-gray-400">Sign In to get invite codes</p>
      </section>
    );
  }

  if (!data) return null;

  const activeCodes = data.codes.filter(c => c.status === 'active');
  const usedCodes = data.codes.filter(c => c.status === 'used');

  return (
    <section className="rounded-2xl border border-gray-100 bg-white p-4" data-testid="invite-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
            <UserPlus className="w-4 h-4 text-violet-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">Invite to Field</span>
            <p className="text-[10px] text-gray-400">Share a link and invite someone to join</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-center" data-testid="invite-active-count">
            <p className="text-sm font-bold text-violet-600">{data.active_count}</p>
            <p className="text-[9px] text-gray-400">active</p>
          </div>
          <div className="text-center" data-testid="invite-used-count">
            <p className="text-sm font-bold text-emerald-600">{data.used_count}</p>
            <p className="text-[9px] text-gray-400">Redeemed</p>
          </div>
        </div>
      </div>

      {/* Active codes */}
      {activeCodes.length > 0 ? (
        <div className="space-y-2 mb-3">
          {activeCodes.map(c => (
            <div key={c.code} className="flex items-center gap-2 bg-gray-50 rounded-xl p-2.5 border border-gray-100">
              <Link2 className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
              <span className="text-xs font-mono text-gray-600 flex-1" dir="ltr" data-testid="invite-code-display">{c.code}</span>
              <button
                onClick={() => handleCopy(c.code)}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all flex items-center gap-1 ${
                  copiedCode === c.code
                    ? 'bg-green-100 text-green-700'
                    : 'bg-violet-100 text-violet-700 hover:bg-violet-200'
                }`}
                data-testid={`invite-copy-btn-${c.code}`}
              >
                {copiedCode === c.code
                  ? <><Check className="w-2.5 h-2.5" /><span>Copied</span></>
                  : <><Copy className="w-2.5 h-2.5" /><span>Copy Link</span></>
                }
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-3 mb-3 bg-gray-50 rounded-xl border border-dashed border-gray-200">
          <p className="text-xs text-gray-400 mb-2">No active codes</p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-medium transition-all flex items-center justify-center gap-1.5 mx-auto active:scale-[0.97]"
            data-testid="invite-generate-btn"
          >
            {generating
              ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
              : <><RefreshCw className="w-3 h-3" /><span>Generate invite codes</span></>
            }
          </button>
        </div>
      )}

      {/* Used codes summary */}
      {usedCodes.length > 0 && (
        <div className="flex items-center gap-1.5 px-2 py-1.5 bg-emerald-50 rounded-xl">
          <Check className="w-3 h-3 text-emerald-500" />
          <span className="text-[10px] text-emerald-600">{usedCodes.length} Invites redeemed successfully</span>
        </div>
      )}

      {/* Generate button when some codes active but below max */}
      {data.can_generate && activeCodes.length > 0 && activeCodes.length < 2 && (
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="mt-2 w-full py-2 text-[10px] text-violet-500 hover:text-violet-700 transition-colors flex items-center justify-center gap-1"
          data-testid="invite-generate-more-btn"
        >
          {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <><RefreshCw className="w-3 h-3" /><span>Generate another code</span></>}
        </button>
      )}
    </section>
  );
}

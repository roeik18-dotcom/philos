import { useState, useEffect } from 'react';
import { Copy, Check, UserPlus } from 'lucide-react';
import { track } from '../../../utils/track';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InlineInviteCard() {
  const [code, setCode] = useState(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('philos_auth_token');

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    const fetchOrGenerate = async () => {
      try {
        const res = await fetch(`${API_URL}/api/invites/me`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!res.ok) { setLoading(false); return; }
        const data = await res.json();
        const active = (data.codes || []).find(c => c.status === 'active');
        if (active) {
          setCode(active.code);
        } else if (data.can_generate) {
          const gen = await fetch(`${API_URL}/api/invites/generate`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (gen.ok) {
            const g = await gen.json();
            if (g.generated?.[0]) setCode(g.generated[0]);
          }
        }
      } catch (e) { /* silent */ }
      setLoading(false);
    };
    fetchOrGenerate();
  }, [token]);

  const handleCopy = async () => {
    if (!code) return;
    const url = `${window.location.origin}/join?invite=${code}`;
    try { await navigator.clipboard.writeText(url); } catch {
      const inp = document.createElement('input');
      inp.value = url; document.body.appendChild(inp); inp.select();
      document.execCommand('copy'); document.body.removeChild(inp);
    }
    setCopied(true);
    track('invite_copied', 'user', { code });
    fetch(`${API_URL}/api/invites/share`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ code }),
    }).catch(() => {});
    setTimeout(() => setCopied(false), 2500);
  };

  if (loading || !token || !code) return null;

  return (
    <div className="rounded-2xl border border-violet-100 bg-violet-50/50 p-3.5 flex items-center gap-3" data-testid="inline-invite-card">
      <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
        <UserPlus className="w-5 h-5 text-violet-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-gray-700">Invite someone to the field</p>
        <p className="text-[10px] text-gray-400 truncate font-mono" dir="ltr">{code}</p>
      </div>
      <button
        onClick={handleCopy}
        className={`px-3 py-1.5 rounded-xl text-[10px] font-medium transition-all flex items-center gap-1 flex-shrink-0 ${
          copied ? 'bg-green-100 text-green-700' : 'bg-violet-200 text-violet-700 hover:bg-violet-300'
        }`}
        data-testid="inline-invite-copy-btn"
      >
        {copied ? <><Check className="w-3 h-3" /><span>Copied</span></> : <><Copy className="w-3 h-3" /><span>Copy</span></>}
      </button>
    </div>
  );
}

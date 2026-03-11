import { useState } from 'react';
import { UserPlus, Copy, Check, Link } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InviteSection({ userId }) {
  const [inviteUrl, setInviteUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const handleCreateInvite = async () => {
    if (!effectiveUserId || loading) return;
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/orientation/create-invite/${effectiveUserId}`, { method: 'POST' });
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          const fullUrl = `${window.location.origin}${json.invite_url}`;
          setInviteUrl(fullUrl);
        }
      }
    } catch (e) {
      console.log('Could not create invite:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!inviteUrl) return;
    try {
      await navigator.clipboard.writeText(inviteUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      // Fallback
      const input = document.createElement('input');
      input.value = inviteUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <section className="philos-section bg-gradient-to-br from-violet-50 to-fuchsia-50 border-violet-200 animate-section animate-section-5" dir="rtl" data-testid="invite-section">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-xl bg-violet-100 flex items-center justify-center">
          <UserPlus className="w-5 h-5 text-violet-600" />
        </div>
        <span className="text-sm font-medium text-violet-700">הזמן לשדה</span>
      </div>

      <p className="text-sm text-gray-700 mb-3">הזמן 2 אנשים לשדה ההתמצאות וחזק את הקהילה</p>

      {!inviteUrl ? (
        <button
          onClick={handleCreateInvite}
          disabled={loading}
          className="w-full py-3 px-4 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl font-medium transition-all duration-300 flex items-center justify-center gap-2 active:scale-[0.97]"
          data-testid="create-invite-btn"
        >
          {loading ? (
            <span className="animate-pulse">יוצר קישור...</span>
          ) : (
            <><Link className="w-4 h-4" /><span>צור קישור הזמנה</span></>
          )}
        </button>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2 bg-white rounded-xl p-2 border border-violet-200">
            <input
              type="text"
              readOnly
              value={inviteUrl}
              className="flex-1 text-xs text-gray-600 bg-transparent outline-none truncate"
              dir="ltr"
              data-testid="invite-url-input"
            />
            <button
              onClick={handleCopy}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 flex items-center gap-1 ${
                copied ? 'bg-green-100 text-green-700' : 'bg-violet-100 text-violet-700 hover:bg-violet-200'
              }`}
              data-testid="copy-invite-btn"
            >
              {copied ? <><Check className="w-3 h-3" /><span>הועתק</span></> : <><Copy className="w-3 h-3" /><span>העתק</span></>}
            </button>
          </div>
          <button
            onClick={handleCreateInvite}
            className="text-xs text-violet-600 hover:text-violet-700 transition-colors"
            data-testid="create-new-invite-btn"
          >
            צור קישור חדש
          </button>
        </div>
      )}
    </section>
  );
}

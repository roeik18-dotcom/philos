import { useState, useEffect } from 'react';
import { Users, ArrowLeft, UserPlus, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InvitePage({ code, onEnter }) {
  const [invite, setInvite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInvite = async () => {
      try {
        const res = await fetch(`${API_URL}/api/invites/lookup/${code}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setInvite(json);
          else setError('קוד ההזמנה אינו תקף');
        } else {
          setError('קוד ההזמנה אינו תקף');
        }
      } catch (e) {
        setError('שגיאה בטעינת ההזמנה');
      } finally {
        setLoading(false);
      }
    };
    fetchInvite();
  }, [code]);

  const handleAccept = async () => {
    setAccepting(true);
    const token = localStorage.getItem('philos_auth_token');
    try {
      if (token) {
        // Authenticated user — use new redeem endpoint
        const res = await fetch(`${API_URL}/api/invites/redeem`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ code }),
        });
        if (!res.ok) {
          // Fallback to legacy endpoint
          await fetch(`${API_URL}/api/orientation/accept-invite/${code}/${localStorage.getItem('philos_user_id') || 'unknown'}`, { method: 'POST' });
        }
      } else {
        // Store code for post-registration redemption
        localStorage.setItem('philos_pending_invite', code);
      }
    } catch (e) {
      console.log('Could not accept invite:', e);
    }
    onEnter();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center p-6" data-testid="invite-page-loading">
        <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center p-6" dir="rtl" data-testid="invite-page">
      <div className="max-w-sm w-full text-center space-y-6">
        {/* Icon */}
        <div className="w-16 h-16 rounded-2xl bg-violet-100 flex items-center justify-center mx-auto">
          <UserPlus className="w-8 h-8 text-violet-600" />
        </div>

        {/* Title */}
        <div>
          <h1 className="text-xl font-bold text-gray-800 mb-1" dir="ltr">Measure your trust.</h1>
          <p className="text-sm text-gray-400" dir="ltr">You've been invited to start.</p>
          {invite?.inviter_alias && (
            <p className="text-xs text-violet-600 mt-1">
              הוזמנת על ידי <span className="font-semibold">{invite.inviter_alias}</span>
            </p>
          )}
        </div>

        {error ? (
          <div className="p-4 bg-red-50 rounded-xl border border-red-100">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : null}

        {/* CTA */}
        <button
          onClick={handleAccept}
          disabled={accepting || error}
          className="w-full py-3 px-6 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 text-white rounded-2xl text-sm font-medium transition-all flex items-center justify-center gap-2 active:scale-[0.97]"
          data-testid="invite-accept-btn"
        >
          {accepting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <span>Start the trust test</span>
          )}
        </button>

        {/* Skip */}
        <button
          onClick={onEnter}
          className="text-xs text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-1 mx-auto"
          data-testid="invite-skip-btn"
        >
          <ArrowLeft className="w-3 h-3" />
          <span>המשך בלי הזמנה</span>
        </button>

        {/* Stats */}
        {invite && (
          <div className="flex items-center justify-center gap-1 text-[10px] text-gray-300">
            <Users className="w-3 h-3" />
            <span>{invite.use_count || 0} כבר הצטרפו דרך הזמנה זו</span>
          </div>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Compass, Users, ArrowLeft } from 'lucide-react';
import { getUserId } from '../services/cloudSync';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InvitePage({ code, onEnter }) {
  const [invite, setInvite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    const fetchInvite = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/invite/${code}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setInvite(json);
        }
      } catch (e) {
        console.log('Could not fetch invite:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchInvite();
  }, [code]);

  const handleAccept = async () => {
    setAccepting(true);
    try {
      const userId = getUserId();
      await fetch(`${API_URL}/api/orientation/accept-invite/${code}/${userId}`, { method: 'POST' });
    } catch (e) {
      console.log('Could not accept invite:', e);
    }
    onEnter();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="animate-spin h-8 w-8 border-3 border-violet-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6" dir="rtl" data-testid="invite-page">
      <div className="max-w-sm w-full text-center space-y-6">
        <div className="w-16 h-16 mx-auto rounded-3xl bg-violet-100 flex items-center justify-center">
          <Compass className="w-8 h-8 text-violet-600" />
        </div>

        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Philos Orientation</h1>
          <p className="text-sm text-muted-foreground">הוזמנת להצטרף לשדה ההתמצאות</p>
        </div>

        {invite && (
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <Users className="w-3.5 h-3.5" />
            <span>{invite.use_count} אנשים כבר הצטרפו דרך הזמנה זו</span>
          </div>
        )}

        <button
          onClick={handleAccept}
          disabled={accepting}
          className="w-full py-4 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl font-medium transition-all duration-300 flex items-center justify-center gap-2 active:scale-[0.97]"
          data-testid="accept-invite-btn"
        >
          {accepting ? (
            <span className="animate-pulse">מצטרף...</span>
          ) : (
            <><ArrowLeft className="w-5 h-5" /><span>הצטרף לשדה</span></>
          )}
        </button>

        {!invite && (
          <p className="text-xs text-red-500">קישור הזמנה לא נמצא</p>
        )}
      </div>
    </div>
  );
}

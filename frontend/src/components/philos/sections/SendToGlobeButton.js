import { useState } from 'react';
import { Globe, Check } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};

export default function SendToGlobeButton({ userId, direction }) {
  const [sent, setSent] = useState(false);
  const [sending, setSending] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const handleSend = async () => {
    if (sending || sent) return;
    setSending(true);
    setAnimating(true);

    try {
      const res = await fetch(`${API_URL}/api/orientation/globe-point`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: effectiveUserId,
          direction: direction || 'contribution',
          country_code: 'IL'
        })
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          // Dispatch field-pulse event so globe can show ripple
          window.dispatchEvent(new CustomEvent('globe-field-pulse', {
            detail: {
              lat: json.point.lat,
              lng: json.point.lng,
              color: json.point.color
            }
          }));
          window.dispatchEvent(new CustomEvent('orientation-stage', { detail: { stage: 'field' } }));

          setTimeout(() => {
            setAnimating(false);
            setSent(true);
            setConfirmed(true);
            setTimeout(() => setConfirmed(false), 6000);
          }, 1200);
        }
      }
    } catch (e) {
      console.log('Could not send globe point:', e);
      setAnimating(false);
    } finally {
      setSending(false);
    }
  };

  const color = directionColors[direction] || '#6366f1';

  if (sent) {
    return (
      <div className="relative overflow-hidden" data-testid="send-to-globe-confirmed">
        {confirmed ? (
          <div className="flex items-center justify-center gap-2 py-3 px-4 rounded-2xl border border-green-200 bg-green-50 animate-fadeIn">
            <div className="relative">
              <Check className="w-4 h-4 text-green-600" />
              <div className="absolute inset-0 rounded-full animate-ping opacity-30" style={{ backgroundColor: color }} />
            </div>
            <span className="text-sm font-medium text-green-700">Your action was added to the human field</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2 py-2 text-xs text-gray-400">
            <Globe className="w-3.5 h-3.5" />
            <span>Your point on the globe</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative" data-testid="send-to-globe-button">
      <button
        onClick={handleSend}
        disabled={sending}
        className="w-full py-3 px-4 rounded-2xl font-medium transition-all duration-300 flex items-center justify-center gap-2 bg-[#0a0a1a] text-white hover:bg-[#1a1a2e] active:scale-[0.97] border border-white/10 hover:shadow-lg"
      >
        {animating ? (
          <>
            <div className="relative w-5 h-5">
              <div
                className="absolute inset-0 rounded-full"
                style={{ backgroundColor: color, animation: 'fieldPulseRipple 0.8s ease-out infinite' }}
              />
              <div
                className="absolute inset-1 rounded-full"
                style={{ backgroundColor: color }}
              />
            </div>
            <span className="text-sm">Sending to globe...</span>
          </>
        ) : (
          <>
            <Globe className="w-5 h-5" />
            <span className="text-sm">Send Point to Globe</span>
          </>
        )}
      </button>

      {/* Launch animation - glowing dot rising with ripple trail */}
      {animating && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden rounded-2xl">
          <div
            className="w-3 h-3 rounded-full absolute"
            style={{
              backgroundColor: color,
              boxShadow: `0 0 20px ${color}, 0 0 40px ${color}60`,
              animation: 'globeLaunch 1.2s ease-out forwards'
            }}
          />
          {/* Expanding ripple left behind */}
          <div
            className="w-4 h-4 rounded-full absolute border-2"
            style={{
              borderColor: color,
              animation: 'fieldPulseRipple 1s ease-out 0.3s forwards',
              opacity: 0
            }}
          />
        </div>
      )}
    </div>
  );
}

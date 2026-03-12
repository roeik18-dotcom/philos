import { useState } from 'react';
import { Zap, Loader2, Check, X, Flame, Target, User } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DIRECTIONS = [
  { id: 'contribution', label: 'תרומה', desc: 'לתת', color: '#22c55e' },
  { id: 'recovery', label: 'התאוששות', desc: 'להיטען', color: '#3b82f6' },
  { id: 'order', label: 'סדר', desc: 'לארגן', color: '#6366f1' },
  { id: 'exploration', label: 'חקירה', desc: 'לגלות', color: '#f59e0b' }
];

export default function QuickDecisionButton({ onSubmit }) {
  const [open, setOpen] = useState(false);
  const [phase, setPhase] = useState('pick'); // pick | sending | reward
  const [sending, setSending] = useState(false);
  const [reward, setReward] = useState(null);

  const userId = localStorage.getItem('philos_user_id') || '';

  const handlePickDirection = async (dir) => {
    setPhase('sending');
    setSending(true);
    try {
      const res = await fetch(`${API_URL}/api/onboarding/first-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, direction: dir.id })
      });
      const data = await res.json();
      if (data?.success) {
        // Trigger globe pulse
        window.dispatchEvent(new CustomEvent('globe-field-pulse', { detail: { direction: dir.id } }));
        setReward({ direction: dir, message: data.message_he });
        setPhase('reward');
        // Auto-close after 2.5s
        setTimeout(() => { setOpen(false); setPhase('pick'); setReward(null); }, 2500);
      }
    } catch (e) {
      setPhase('pick');
    } finally {
      setSending(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setPhase('pick');
    setReward(null);
  };

  return (
    <>
      {/* FAB */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-20 right-4 z-40 w-12 h-12 bg-gray-900 text-white rounded-full shadow-2xl flex items-center justify-center hover:bg-gray-800 active:scale-90 transition-all"
        data-testid="quick-action-fab"
      >
        <Zap className="w-5 h-5" />
      </button>

      {/* Fast Action Panel */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/30 backdrop-blur-sm" onClick={handleClose}>
          <div
            className="w-full max-w-md bg-white rounded-t-3xl p-5 pb-8 shadow-2xl"
            dir="rtl"
            onClick={e => e.stopPropagation()}
            data-testid="quick-action-panel"
          >
            {phase === 'pick' && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-gray-800">פעולה מהירה</h3>
                  <button onClick={handleClose} className="text-gray-300 hover:text-gray-500"><X className="w-4 h-4" /></button>
                </div>
                <p className="text-xs text-gray-400 mb-3">בחר כיוון — הנקודה נשלחת לגלובוס מיד</p>
                <div className="grid grid-cols-2 gap-2">
                  {DIRECTIONS.map(d => (
                    <button
                      key={d.id}
                      onClick={() => handlePickDirection(d)}
                      className="p-4 rounded-2xl border-2 transition-all active:scale-[0.95] hover:shadow-md text-right"
                      style={{ borderColor: `${d.color}30`, backgroundColor: `${d.color}05` }}
                      data-testid={`quick-dir-${d.id}`}
                    >
                      <div className="w-6 h-6 rounded-lg mb-2 flex items-center justify-center" style={{ backgroundColor: `${d.color}15` }}>
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                      </div>
                      <p className="text-sm font-bold" style={{ color: d.color }}>{d.label}</p>
                      <p className="text-[10px] text-gray-400">{d.desc}</p>
                    </button>
                  ))}
                </div>
              </>
            )}

            {phase === 'sending' && (
              <div className="flex flex-col items-center justify-center py-8 gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                <span className="text-xs text-gray-400">שולח לגלובוס...</span>
              </div>
            )}

            {phase === 'reward' && reward && (
              <div className="text-center py-4" data-testid="quick-action-reward">
                <div className="w-14 h-14 mx-auto rounded-full flex items-center justify-center mb-3" style={{ backgroundColor: `${reward.direction.color}15` }}>
                  <Check className="w-7 h-7" style={{ color: reward.direction.color }} />
                </div>
                <p className="text-base font-bold text-gray-900 mb-1">{reward.message}</p>
                <p className="text-lg font-black mb-2" style={{ color: reward.direction.color }}>+{(2.5).toFixed(1)} השפעה</p>
                <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
                  <span className="flex items-center gap-0.5" style={{ color: reward.direction.color }}>
                    <Zap className="w-3 h-3" />{reward.direction.label}
                  </span>
                </div>
                {userId && (
                  <a href={`/profile/${userId}`} className="flex items-center justify-center gap-1 text-[10px] text-gray-400 hover:text-indigo-500 mt-3 transition-colors">
                    <User className="w-3 h-3" />צפה ברשומה שלך
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

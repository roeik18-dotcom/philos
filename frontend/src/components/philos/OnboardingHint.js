import { useState, useEffect } from 'react';
import { Globe, Zap, Loader2, Check } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const ONBOARDING_KEY = 'philos_onboarding_complete';

const DIRECTIONS = [
  { id: 'contribution', label: 'תרומה', desc: 'לתת, לעזור, לחזק אחרים', color: '#22c55e', bg: '#f0fdf4' },
  { id: 'recovery', label: 'התאוששות', desc: 'להיטען, לשקם, לנוח', color: '#3b82f6', bg: '#eff6ff' },
  { id: 'order', label: 'סדר', desc: 'לארגן, לתכנן, לייצב', color: '#6366f1', bg: '#eef2ff' },
  { id: 'exploration', label: 'חקירה', desc: 'לגלות, ללמוד, לנסות חדש', color: '#f59e0b', bg: '#fffbeb' }
];

export default function OnboardingHint({ onComplete }) {
  const [step, setStep] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [exiting, setExiting] = useState(false);
  const [selectedDirection, setSelectedDirection] = useState(null);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_KEY);
    if (!completed) setShowHint(true);
  }, []);

  const handleComplete = () => {
    setExiting(true);
    setTimeout(() => {
      localStorage.setItem(ONBOARDING_KEY, 'true');
      setShowHint(false);
      if (onComplete) onComplete();
    }, 300);
  };

  const handleSendToGlobe = async () => {
    if (!selectedDirection) return;
    setSending(true);
    const userId = localStorage.getItem('philos_user_id') || `anon_${Date.now()}`;
    try {
      await fetch(`${API_URL}/api/onboarding/first-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, direction: selectedDirection })
      });
      setSent(true);
      setTimeout(() => {
        // Dispatch globe pulse event
        window.dispatchEvent(new CustomEvent('globe-field-pulse', { detail: { direction: selectedDirection } }));
        handleComplete();
      }, 1200);
    } catch (e) {
      handleComplete();
    } finally {
      setSending(false);
    }
  };

  if (!showHint) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 transition-opacity duration-300 ${exiting ? 'opacity-0' : 'opacity-100'}`}
      data-testid="onboarding-overlay"
    >
      <div className="bg-white rounded-3xl shadow-2xl p-6 max-w-sm w-full" dir="rtl" data-testid="onboarding-modal">
        {/* Progress */}
        <div className="flex justify-center gap-2 mb-5">
          {[0, 1, 2].map(i => (
            <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i === step ? 'w-6 bg-gray-800' : i < step ? 'w-1.5 bg-gray-400' : 'w-1.5 bg-gray-200'}`} />
          ))}
        </div>

        {/* Step 1: Measure your trust */}
        {step === 0 && (
          <div className="text-center py-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-tight" dir="ltr" data-testid="onboarding-title">Measure your trust.</h2>
            <p className="text-sm text-gray-400 mb-8" dir="ltr">Answer one question. See your trust state.</p>
            <button
              onClick={() => setStep(1)}
              className="w-full py-3.5 bg-gray-900 text-white rounded-2xl font-medium hover:bg-gray-800 transition-colors active:scale-[0.97]"
              data-testid="onboarding-next"
            >
              Start the trust test
            </button>
          </div>
        )}

        {/* Step 2: Choose first direction */}
        {step === 1 && (
          <div>
            <div className="text-center mb-4">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-50 flex items-center justify-center mb-3">
                <Zap className="w-7 h-7 text-amber-500" />
              </div>
              <h2 className="text-lg font-bold text-gray-900 mb-1" data-testid="onboarding-title">בחר את הכיוון הראשון שלך</h2>
              <p className="text-xs text-gray-500">מה הכי מושך אותך עכשיו?</p>
            </div>
            <div className="space-y-2 mb-4">
              {DIRECTIONS.map(d => (
                <button
                  key={d.id}
                  onClick={() => setSelectedDirection(d.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-right"
                  style={{
                    backgroundColor: selectedDirection === d.id ? d.bg : 'white',
                    borderColor: selectedDirection === d.id ? d.color : '#e5e7eb'
                  }}
                  data-testid={`onboarding-direction-${d.id}`}
                >
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${d.color}15` }}>
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-bold" style={{ color: d.color }}>{d.label}</p>
                    <p className="text-[10px] text-gray-500">{d.desc}</p>
                  </div>
                  {selectedDirection === d.id && <Check className="w-4 h-4 flex-shrink-0" style={{ color: d.color }} />}
                </button>
              ))}
            </div>
            <button
              onClick={() => selectedDirection && setStep(2)}
              disabled={!selectedDirection}
              className="w-full py-3 bg-gray-900 text-white rounded-2xl font-medium hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-[0.97]"
              data-testid="onboarding-next"
            >
              הבא
            </button>
          </div>
        )}

        {/* Step 3: Send to globe */}
        {step === 2 && (
          <div className="text-center">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-green-50 flex items-center justify-center mb-4">
              <Globe className="w-7 h-7 text-green-600" />
            </div>
            {sent ? (
              <>
                <h2 className="text-xl font-bold text-green-600 mb-2" data-testid="onboarding-title">נשלח!</h2>
                <p className="text-sm text-gray-500 mb-4">הנקודה הראשונה שלך נוספה לשדה הגלובלי</p>
              </>
            ) : (
              <>
                <h2 className="text-lg font-bold text-gray-900 mb-2" data-testid="onboarding-title">שלח את הנקודה הראשונה שלך</h2>
                <p className="text-sm text-gray-500 mb-2">
                  בחרת <span className="font-bold" style={{ color: DIRECTIONS.find(d => d.id === selectedDirection)?.color }}>
                    {DIRECTIONS.find(d => d.id === selectedDirection)?.label}
                  </span>
                </p>
                <p className="text-xs text-gray-400 mb-6">
                  לחץ כדי לשלוח את הפעולה הראשונה שלך לגלובוס ולהצטרף לשדה האנושי.
                </p>
                <button
                  onClick={handleSendToGlobe}
                  disabled={sending}
                  className="w-full py-3 bg-gray-900 text-white rounded-2xl font-medium hover:bg-gray-800 disabled:opacity-60 transition-all active:scale-[0.97] flex items-center justify-center gap-2"
                  data-testid="onboarding-send-to-globe"
                >
                  {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Globe className="w-4 h-4" /> שלח לגלובוס</>}
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function resetOnboarding() {
  localStorage.removeItem(ONBOARDING_KEY);
}

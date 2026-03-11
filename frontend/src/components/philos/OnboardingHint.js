import { useState, useEffect } from 'react';
import { Compass, Sun, Activity } from 'lucide-react';

const ONBOARDING_KEY = 'philos_onboarding_complete';

const steps = [
  {
    Icon: Compass,
    color: '#6366f1',
    bg: 'bg-indigo-50',
    title: 'המצפן שלך',
    description: 'המצפן מראה את המיקום שלך בשדה ההתמצאות — בין ארבעה כיוונים: התאוששות, סדר, תרומה וחקירה. הוא משתנה עם כל פעולה שלך.'
  },
  {
    Icon: Sun,
    color: '#f59e0b',
    bg: 'bg-amber-50',
    title: 'השאלה היומית',
    description: 'כל יום תקבל שאלה אחת שמזמינה אותך לפעול. כשאתה מבצע את הפעולה ומסמן "עשיתי את זה", הרצף שלך גדל והמערכת לומדת את הדפוסים שלך.'
  },
  {
    Icon: Activity,
    color: '#22c55e',
    bg: 'bg-green-50',
    title: 'ההשפעה שלך על השדה',
    description: 'כל פעולה שלך משפיעה על שדה ההתמצאות הקולקטיבי. אתה חלק ממשימה יומית משותפת — ביחד אנחנו מכוונים את השדה.'
  }
];

export default function OnboardingHint({ onComplete }) {
  const [step, setStep] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [exiting, setExiting] = useState(false);

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

  const handleNext = () => {
    if (step < steps.length - 1) setStep(step + 1);
    else handleComplete();
  };

  if (!showHint) return null;

  const current = steps[step];

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 transition-opacity duration-300 ${exiting ? 'opacity-0' : 'opacity-100'}`}
      data-testid="onboarding-overlay"
    >
      <div className="bg-white rounded-3xl shadow-2xl p-6 max-w-sm w-full text-center" dir="rtl" data-testid="onboarding-modal">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-5">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-6 bg-gray-800' : i < step ? 'w-1.5 bg-gray-400' : 'w-1.5 bg-gray-200'
              }`}
            />
          ))}
        </div>

        {/* Icon */}
        <div className={`w-14 h-14 mx-auto rounded-2xl ${current.bg} flex items-center justify-center mb-4`}>
          <current.Icon className="w-7 h-7" style={{ color: current.color }} />
        </div>

        {/* Content */}
        <h2 className="text-xl font-bold text-gray-900 mb-3" data-testid="onboarding-title">
          {current.title}
        </h2>
        <p className="text-sm text-gray-600 leading-relaxed mb-6" data-testid="onboarding-description">
          {current.description}
        </p>

        {/* Buttons */}
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={handleNext}
            className="flex-1 py-3 bg-gray-900 text-white rounded-2xl font-medium hover:bg-gray-800 transition-colors active:scale-[0.97]"
            data-testid="onboarding-next"
          >
            {step < steps.length - 1 ? 'הבא' : 'בואו נתחיל'}
          </button>
          {step < steps.length - 1 && (
            <button
              onClick={handleComplete}
              className="px-4 py-3 text-sm text-gray-400 hover:text-gray-600 transition-colors"
              data-testid="onboarding-skip"
            >
              דלג
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function SectionHelperText({ children, icon = '?' }) {
  return (
    <p className="text-sm text-gray-500 mt-2 flex items-center gap-2" dir="rtl">
      <span>{icon}</span>
      <span>{children}</span>
    </p>
  );
}

export function EmptyState({ title, description, actionText, onAction, icon = null }) {
  return (
    <div className="text-center py-8 px-4" dir="rtl" data-testid="empty-state">
      {icon && <div className="text-4xl mb-4">{icon}</div>}
      <h3 className="text-lg font-medium text-gray-700 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
      {actionText && onAction && (
        <button onClick={onAction} className="px-6 py-2 bg-emerald-100 text-emerald-700 rounded-xl hover:bg-emerald-200 transition-colors" data-testid="empty-state-action">
          {actionText}
        </button>
      )}
    </div>
  );
}

export function resetOnboarding() {
  localStorage.removeItem(ONBOARDING_KEY);
}

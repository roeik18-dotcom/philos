import { useState, useEffect } from 'react';

// LocalStorage key for onboarding
const ONBOARDING_KEY = 'philos_onboarding_complete';

/**
 * OnboardingHint - First-time user onboarding overlay
 */
export default function OnboardingHint({ onComplete }) {
  const [step, setStep] = useState(0);
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    // Check if onboarding was already completed
    const completed = localStorage.getItem(ONBOARDING_KEY);
    if (!completed) {
      setShowHint(true);
    }
  }, []);

  const steps = [
    {
      title: 'ברוכים הבאים!',
      description: 'Philos Orientation עוזר לך לנווט בהחלטות יומיומיות ולהבין את הדפוסים שלך.',
      highlight: null
    },
    {
      title: 'איך זה עובד?',
      description: 'תאר את הפעולה שלך בשדה הקלט, והמערכת תסווג אותה ותציע כיוונים להמשך.',
      highlight: 'action-input'
    },
    {
      title: 'עקוב אחר המלצות',
      description: 'לחץ על "פעל לפי ההמלצה" כדי לקבל הצעות מותאמות למצבך הנוכחי.',
      highlight: 'follow-recommendation'
    },
    {
      title: 'מוכן להתחיל!',
      description: 'עכשיו אתה יכול להתחיל לנווט. בהצלחה!',
      highlight: null
    }
  ];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setShowHint(false);
    if (onComplete) onComplete();
  };

  if (!showHint) return null;

  const currentStep = steps[step];

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      data-testid="onboarding-overlay"
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 text-center"
        dir="rtl"
        data-testid="onboarding-modal"
      >
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-6">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === step ? 'bg-emerald-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        {/* Step content */}
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          {currentStep.title}
        </h2>
        <p className="text-gray-600 mb-8 leading-relaxed">
          {currentStep.description}
        </p>

        {/* Buttons */}
        <div className="flex justify-center gap-4">
          {step < steps.length - 1 && (
            <button
              onClick={handleSkip}
              className="px-6 py-2 text-gray-500 hover:text-gray-700 transition-colors"
              data-testid="onboarding-skip"
            >
              דלג
            </button>
          )}
          <button
            onClick={handleNext}
            className="px-8 py-3 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors"
            data-testid="onboarding-next"
          >
            {step < steps.length - 1 ? 'הבא' : 'התחל!'}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Helper text component for sections
 */
export function SectionHelperText({ children, icon = '💡' }) {
  return (
    <p className="text-sm text-gray-500 mt-2 flex items-center gap-2" dir="rtl">
      <span>{icon}</span>
      <span>{children}</span>
    </p>
  );
}

/**
 * Empty state component for sections with no data
 */
export function EmptyState({ 
  title, 
  description, 
  actionText, 
  onAction,
  icon = '📊'
}) {
  return (
    <div 
      className="text-center py-8 px-4"
      dir="rtl"
      data-testid="empty-state"
    >
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-medium text-gray-700 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-2 bg-emerald-100 text-emerald-700 rounded-xl hover:bg-emerald-200 transition-colors"
          data-testid="empty-state-action"
        >
          {actionText}
        </button>
      )}
    </div>
  );
}

/**
 * Reset onboarding (for testing)
 */
export function resetOnboarding() {
  localStorage.removeItem(ONBOARDING_KEY);
}

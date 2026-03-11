import { useState, useEffect, useCallback, useRef } from 'react';
import { Flame, Check, Sun, Loader2, TrendingUp } from 'lucide-react';
import SendToGlobeButton from './SendToGlobeButton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  recovery: { fill: '#3b82f6', bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', gradient: 'from-blue-50 to-sky-50' },
  order: { fill: '#6366f1', bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', gradient: 'from-indigo-50 to-violet-50' },
  contribution: { fill: '#22c55e', bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', gradient: 'from-green-50 to-emerald-50' },
  exploration: { fill: '#f59e0b', bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', gradient: 'from-amber-50 to-yellow-50' }
};

const directionLabels = {
  recovery: 'התאוששות',
  order: 'סדר',
  contribution: 'תרומה',
  exploration: 'חקירה'
};

export default function DailyOrientationQuestion({ userId, onActionRecorded }) {
  const [questionData, setQuestionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [impactData, setImpactData] = useState(null);
  const sectionRef = useRef(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const fetchQuestion = useCallback(async () => {
    if (!effectiveUserId) return;
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/orientation/daily-question/${effectiveUserId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setQuestionData(data);
          setCompleted(data.already_answered_today);
        }
      }
    } catch (error) {
      console.log('Could not fetch daily question:', error);
    } finally {
      setLoading(false);
    }
  }, [effectiveUserId]);

  useEffect(() => { fetchQuestion(); }, [fetchQuestion]);

  const handleAnswer = async () => {
    if (!questionData?.question_id || submitting) return;
    try {
      setSubmitting(true);
      const response = await fetch(`${API_URL}/api/orientation/daily-answer/${effectiveUserId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: questionData.question_id, action_taken: true })
      });
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setCompleted(true);
          setShowSuccess(true);
          if (result.impact_message) {
            setImpactData({ percent: result.impact_percent, message: result.impact_message });
          }
          setQuestionData(prev => prev ? { ...prev, streak: (prev.streak || 0) + 1, already_answered_today: true } : prev);
          if (onActionRecorded) {
            onActionRecorded({ direction: questionData.suggested_direction, question_id: questionData.question_id, timestamp: new Date().toISOString(), mission_contributed: result.mission_contributed || false });
          }
          setTimeout(() => setShowSuccess(false), 4000);
        }
      }
    } catch (error) {
      console.log('Could not submit answer:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !questionData) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/4 mb-3"></div>
        <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-10 bg-gray-200 rounded w-1/3"></div>
      </section>
    );
  }

  if (!questionData) return null;

  const colors = directionColors[questionData.suggested_direction] || directionColors.recovery;
  const streak = questionData.streak || 0;
  const longestStreak = questionData.longest_streak || 0;

  return (
    <section
      ref={sectionRef}
      className={`philos-section animate-section animate-section-1 ${
        completed
          ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 animate-completion'
          : `bg-gradient-to-br ${colors.gradient} ${colors.border}`
      }`}
      dir="rtl"
      data-testid="daily-orientation-question"
    >
      {/* Header with streak */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center transition-colors duration-300 ${completed ? 'bg-green-100' : colors.bg}`}>
            {completed ? <Check className="w-5 h-5 text-green-600" /> : <Sun className={`w-5 h-5 ${colors.text}`} />}
          </div>
          <span className={`text-sm font-medium transition-colors duration-300 ${completed ? 'text-green-700' : colors.text}`}>התמצאות יומית</span>
        </div>

        <div className="flex items-center gap-2">
          {streak > 0 && (
            <div className="flex items-center gap-1 bg-orange-100 text-orange-700 px-2.5 py-1 rounded-full animate-glow-in" data-testid="streak-badge">
              <Flame className="w-3.5 h-3.5" />
              <span className="text-xs font-bold">{streak}</span>
            </div>
          )}
          {!completed && (
            <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text}`} style={{ backgroundColor: `${colors.fill}15` }}>
              {directionLabels[questionData.suggested_direction]}
            </span>
          )}
        </div>
      </div>

      {/* Streak detail row */}
      {streak > 0 && (
        <div className="flex items-center gap-3 mb-3 text-xs text-gray-500" data-testid="streak-detail">
          <span>{streak} ימים רצופים</span>
          {longestStreak > streak && (
            <span className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              שיא: {longestStreak}
            </span>
          )}
        </div>
      )}

      {/* Question */}
      <p className={`text-lg font-medium mb-4 transition-all duration-500 ${completed ? 'text-green-800 line-through opacity-60' : 'text-gray-800'}`} data-testid="daily-question-text">
        {questionData.question_he}
      </p>

      {/* Action Area */}
      {!completed ? (
        <button
          onClick={handleAnswer}
          disabled={submitting}
          className={`w-full py-3 px-4 rounded-2xl font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
            submitting
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed scale-[0.98]'
              : `bg-white hover:bg-gray-50 text-gray-700 border ${colors.border} hover:shadow-md active:scale-[0.97]`
          }`}
          data-testid="daily-answer-button"
        >
          {submitting ? (
            <><Loader2 className="w-4 h-4 animate-spin" /><span>מעדכן...</span></>
          ) : (
            <><Check className="w-5 h-5" /><span>עשיתי את זה</span></>
          )}
        </button>
      ) : (
        <div className="text-center space-y-2">
          {showSuccess ? (
            <div className="flex items-center justify-center gap-2 text-green-600 animate-glow-in">
              <Check className="w-5 h-5" />
              <span className="font-medium">מצוין! הפעולה נרשמה</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2 text-green-600">
              <Check className="w-5 h-5" />
              <span className="text-sm">הושלם היום</span>
            </div>
          )}

          {impactData && (
            <div className="mt-2 p-3 bg-white/60 rounded-2xl border border-green-100 animate-section animate-section-2" data-testid="impact-message">
              <p className="text-sm text-green-700 font-medium">{impactData.message}</p>
              <p className="text-xs text-green-600 mt-1">
                {impactData.percent > 0 ? `${impactData.percent}% מהשדה היום` : ''}
              </p>
            </div>
          )}

          {/* Send Point to Globe */}
          <div className="mt-3 animate-section animate-section-3">
            <SendToGlobeButton userId={effectiveUserId} direction={questionData.suggested_direction} />
          </div>
        </div>
      )}

      {!completed && (
        <p className="text-xs text-center text-gray-500 mt-3">צעד קטן אחד יכול לשנות את הכיוון</p>
      )}
    </section>
  );
}

import { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Direction colors
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

  // Get user ID from localStorage if not provided
  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  // Fetch daily question
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

  useEffect(() => {
    fetchQuestion();
  }, [fetchQuestion]);

  // Handle answer submission
  const handleAnswer = async () => {
    if (!questionData?.question_id || submitting) return;
    
    try {
      setSubmitting(true);
      
      const response = await fetch(`${API_URL}/api/orientation/daily-answer/${effectiveUserId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: questionData.question_id,
          action_taken: true
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setCompleted(true);
          setShowSuccess(true);
          
          // Notify parent to refresh data
          if (onActionRecorded) {
            onActionRecorded({
              direction: questionData.suggested_direction,
              question_id: questionData.question_id,
              timestamp: new Date().toISOString()
            });
          }
          
          // Hide success message after 3 seconds
          setTimeout(() => setShowSuccess(false), 3000);
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
      <section className="bg-white rounded-3xl p-5 shadow-sm border border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/4 mb-3"></div>
        <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-10 bg-gray-200 rounded w-1/3"></div>
      </section>
    );
  }

  if (!questionData) {
    return null;
  }

  const colors = directionColors[questionData.suggested_direction] || directionColors.recovery;

  return (
    <section 
      className={`rounded-3xl p-5 shadow-sm border transition-all duration-500 ${
        completed 
          ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200' 
          : `bg-gradient-to-br ${colors.gradient} ${colors.border}`
      }`}
      dir="rtl"
      data-testid="daily-orientation-question"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
            completed ? 'bg-green-100' : `${colors.bg}`
          }`}>
            {completed ? (
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className={`w-5 h-5 ${colors.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </div>
          <span className={`text-sm font-medium ${completed ? 'text-green-700' : colors.text}`}>
            התמצאות יומית
          </span>
        </div>
        
        {/* Direction badge */}
        {!completed && (
          <span 
            className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text}`}
            style={{ backgroundColor: `${colors.fill}15` }}
          >
            {directionLabels[questionData.suggested_direction]}
          </span>
        )}
      </div>

      {/* Question */}
      <p 
        className={`text-lg font-medium mb-4 ${
          completed ? 'text-green-800 line-through opacity-60' : 'text-gray-800'
        }`}
        data-testid="daily-question-text"
      >
        {questionData.question_he}
      </p>

      {/* Action Area */}
      {!completed ? (
        <button
          onClick={handleAnswer}
          disabled={submitting}
          className={`w-full py-3 px-4 rounded-2xl font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
            submitting 
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
              : `bg-white hover:bg-gray-50 text-gray-700 border ${colors.border} hover:shadow-sm`
          }`}
          data-testid="daily-answer-button"
        >
          {submitting ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>מעדכן...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>עשיתי את זה</span>
            </>
          )}
        </button>
      ) : (
        <div className="text-center">
          {showSuccess ? (
            <div className="flex items-center justify-center gap-2 text-green-600 animate-pulse">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">מצוין! הפעולה נרשמה</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2 text-green-600">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm">הושלם היום</span>
            </div>
          )}
        </div>
      )}

      {/* Subtle motivational text */}
      {!completed && (
        <p className="text-xs text-center text-gray-500 mt-3">
          צעד קטן אחד יכול לשנות את הכיוון
        </p>
      )}
    </section>
  );
}

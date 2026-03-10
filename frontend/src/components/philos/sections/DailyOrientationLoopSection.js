import { useState, useEffect, useMemo } from 'react';
import { 
  filterYesterdayHistory,
  countValueTags,
  identifyDominantPattern,
  valueLabels 
} from '../../../services/analyticsService';

// Pattern descriptions in Hebrew
const patternDescriptions = {
  contribution: 'מומנטום חיובי של תרומה',
  recovery: 'איזון של התאוששות',
  order: 'מיקוד בסדר וארגון',
  harm: 'דפוס של לחץ ונזק',
  avoidance: 'דפוס של הימנעות',
  balanced: 'מערכת מאוזנת',
  none: 'אין נתונים'
};

// Recommended actions by pattern
const recommendedActions = {
  harm: { direction: 'recovery', action: 'לבצע פעולת התאוששות קטנה' },
  avoidance: { direction: 'order', action: 'לבחור פעולה קטנה של סדר' },
  contribution: { direction: 'contribution', action: 'להמשיך במומנטום החיובי' },
  recovery: { direction: 'order', action: 'להוסיף מעט סדר להתאוששות' },
  order: { direction: 'contribution', action: 'לפתוח לכיוון של תרומה' },
  balanced: { direction: 'contribution', action: 'לבצע פעולה קטנה של תרומה' },
  none: { direction: 'recovery', action: 'להתחיל עם פעולת התאוששות' }
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' }
};

// LocalStorage key for daily orientation
const DAILY_ORIENTATION_KEY = 'philos_daily_orientation';

// Analyze yesterday's pattern using centralized analytics
const analyzeYesterdayPattern = (history) => {
  // Use centralized filtering
  const yesterdayDecisions = filterYesterdayHistory(history);

  if (yesterdayDecisions.length === 0) {
    return { pattern: 'none', count: 0 };
  }

  // Use centralized counting
  const valueCounts = countValueTags(yesterdayDecisions);

  // Find dominant pattern
  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const contributionCount = valueCounts.contribution || 0;
  const recoveryCount = valueCounts.recovery || 0;
  const orderCount = valueCounts.order || 0;

  const total = yesterdayDecisions.length;
  const negativeRatio = (harmCount + avoidanceCount) / total;

  let dominantPattern = 'balanced';

  if (negativeRatio > 0.5) {
    dominantPattern = harmCount > avoidanceCount ? 'harm' : 'avoidance';
  } else {
    const positives = [
      { tag: 'contribution', count: contributionCount },
      { tag: 'recovery', count: recoveryCount },
      { tag: 'order', count: orderCount }
    ].sort((a, b) => b.count - a.count);

    if (positives[0].count > 0) {
      dominantPattern = positives[0].tag;
    }
  }

  return {
    pattern: dominantPattern,
    count: yesterdayDecisions.length,
    valueCounts
  };
};

// Check if this is a new day
const isNewDay = (lastActivity) => {
  if (!lastActivity) return true;
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const lastDate = new Date(lastActivity);
  lastDate.setHours(0, 0, 0, 0);
  
  return today.getTime() > lastDate.getTime();
};

// Get stored daily orientation
const getStoredOrientation = () => {
  try {
    const stored = localStorage.getItem(DAILY_ORIENTATION_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.log('Failed to get stored orientation:', e);
  }
  return null;
};

// Save daily orientation
const saveOrientation = (orientation) => {
  try {
    localStorage.setItem(DAILY_ORIENTATION_KEY, JSON.stringify(orientation));
  } catch (e) {
    console.log('Failed to save orientation:', e);
  }
};

export default function DailyOrientationLoopSection({ history, onStartDay }) {
  const [showOrientation, setShowOrientation] = useState(false);
  const [dayStarted, setDayStarted] = useState(false);

  // Get last activity timestamp from history
  const lastActivity = useMemo(() => {
    if (!history || history.length === 0) return null;
    return history[0]?.timestamp || null;
  }, [history]);

  // Analyze yesterday's pattern
  const yesterdayAnalysis = useMemo(() => {
    return analyzeYesterdayPattern(history);
  }, [history]);

  // Get today's recommendation based on yesterday
  const todayRecommendation = useMemo(() => {
    return recommendedActions[yesterdayAnalysis.pattern] || recommendedActions.none;
  }, [yesterdayAnalysis.pattern]);

  // Check if we should show orientation on mount
  useEffect(() => {
    const storedOrientation = getStoredOrientation();
    const today = new Date().toDateString();

    // If we have a stored orientation for today, day was already started
    if (storedOrientation && storedOrientation.date === today) {
      setDayStarted(true);
      setShowOrientation(false);
      return;
    }

    // Check if it's a new day
    if (isNewDay(lastActivity)) {
      setShowOrientation(true);
      setDayStarted(false);
    } else {
      setShowOrientation(false);
      setDayStarted(true);
    }
  }, [lastActivity]);

  // Handle starting the day
  const handleStartDay = () => {
    const today = new Date();
    const orientation = {
      date: today.toDateString(),
      timestamp: today.toISOString(),
      day_started: true,
      orientation_direction: todayRecommendation.direction,
      orientation_pattern_reference: yesterdayAnalysis.pattern,
      yesterday_count: yesterdayAnalysis.count
    };

    saveOrientation(orientation);
    setDayStarted(true);
    setShowOrientation(false);

    if (onStartDay) {
      onStartDay(orientation);
    }
  };

  // Don't show if day already started or not a new day
  if (!showOrientation || dayStarted) {
    return null;
  }

  const colors = directionColors[todayRecommendation.direction] || directionColors.recovery;

  return (
    <section 
      className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-3xl p-5 shadow-sm border border-amber-200"
      dir="rtl"
      data-testid="daily-orientation-loop-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">התמצאות יומית</h3>
          <p className="text-xs text-amber-700">היום מתחיל מחזור חדש של החלטות.</p>
        </div>
      </div>

      {/* Yesterday's Pattern */}
      <div className="bg-white/60 rounded-xl p-4 mb-3">
        <h4 className="text-sm font-medium text-muted-foreground mb-2">אתמול</h4>
        <p className="text-base font-medium text-foreground" data-testid="yesterday-pattern">
          {yesterdayAnalysis.pattern === 'none' 
            ? 'לא הייתה פעילות.' 
            : `נראה ${patternDescriptions[yesterdayAnalysis.pattern]}.`}
        </p>
        {yesterdayAnalysis.count > 0 && (
          <p className="text-xs text-muted-foreground mt-1">
            {yesterdayAnalysis.count} החלטות
          </p>
        )}
      </div>

      {/* Today's Recommendation */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">היום</h4>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
            {valueLabels[todayRecommendation.direction]}
          </span>
        </div>
        <p className={`text-base font-medium ${colors.text}`} data-testid="today-recommendation">
          מומלץ {todayRecommendation.action}.
        </p>
      </div>

      {/* Start Day Button */}
      <button
        onClick={handleStartDay}
        className="w-full px-4 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-all flex items-center justify-center gap-2"
        data-testid="start-day-btn"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>התחל את היום</span>
      </button>

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-3 text-center">
        ההתמצאות היומית עוזרת ליצור מחזור התנהגותי חיובי
      </p>
    </section>
  );
}

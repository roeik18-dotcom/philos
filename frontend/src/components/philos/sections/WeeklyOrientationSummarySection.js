import { useState, useEffect, useMemo } from 'react';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Pattern descriptions in Hebrew
const patternDescriptions = {
  contribution: 'Positive contribution momentum',
  recovery: 'Recovery balance',
  order: 'Focus on order and organization',
  harm: 'Pressure and Harm',
  avoidance: 'Avoidance',
  balanced: 'Balanced system',
  none: 'No data'
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' }
};

// LocalStorage key for weekly orientation
const WEEKLY_ORIENTATION_KEY = 'philos_weekly_orientation';

// Get week number of the year
const getWeekNumber = (date) => {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
};

// Get week identifier (year-week)
const getWeekId = (date) => {
  const year = date.getFullYear();
  const week = getWeekNumber(date);
  return `${year}-W${week}`;
};

// Analyze last week's patterns
const analyzeLastWeekPatterns = (history) => {
  if (!history || history.length === 0) {
    return {
      dominantPattern: 'none',
      strongestPositive: null,
      strongestNegative: null,
      totalDecisions: 0,
      valueCounts: {}
    };
  }

  const today = new Date();
  const currentWeekStart = new Date(today);
  currentWeekStart.setDate(today.getDate() - today.getDay()); // Start of current week (Sunday)
  currentWeekStart.setHours(0, 0, 0, 0);

  const lastWeekStart = new Date(currentWeekStart);
  lastWeekStart.setDate(lastWeekStart.getDate() - 7);

  const lastWeekEnd = new Date(currentWeekStart);
  lastWeekEnd.setMilliseconds(-1); // End of last week

  // Filter last week's decisions
  const lastWeekDecisions = history.filter(item => {
    if (!item.timestamp) return false;
    const itemDate = new Date(item.timestamp);
    return itemDate >= lastWeekStart && itemDate <= lastWeekEnd;
  });

  if (lastWeekDecisions.length === 0) {
    return {
      dominantPattern: 'none',
      strongestPositive: null,
      strongestNegative: null,
      totalDecisions: 0,
      valueCounts: {}
    };
  }

  // Count value tags
  const valueCounts = {};
  lastWeekDecisions.forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      valueCounts[tag] = (valueCounts[tag] || 0) + 1;
    }
  });

  // Find dominant pattern
  const total = lastWeekDecisions.length;
  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const contributionCount = valueCounts.contribution || 0;
  const recoveryCount = valueCounts.recovery || 0;
  const orderCount = valueCounts.order || 0;

  const negativeRatio = (harmCount + avoidanceCount) / total;

  let dominantPattern = 'balanced';

  // Find strongest positive
  const positives = [
    { tag: 'contribution', count: contributionCount },
    { tag: 'recovery', count: recoveryCount },
    { tag: 'order', count: orderCount }
  ].filter(p => p.count > 0).sort((a, b) => b.count - a.count);

  const strongestPositive = positives.length > 0 ? positives[0] : null;

  // Find strongest negative
  const negatives = [
    { tag: 'harm', count: harmCount },
    { tag: 'avoidance', count: avoidanceCount }
  ].filter(n => n.count > 0).sort((a, b) => b.count - a.count);

  const strongestNegative = negatives.length > 0 ? negatives[0] : null;

  // Determine dominant pattern
  if (negativeRatio > 0.5) {
    dominantPattern = harmCount > avoidanceCount ? 'harm' : 'avoidance';
  } else if (strongestPositive) {
    dominantPattern = strongestPositive.tag;
  }

  return {
    dominantPattern,
    strongestPositive,
    strongestNegative,
    totalDecisions: lastWeekDecisions.length,
    valueCounts
  };
};

// Calculate weekly recommendation
const calculateWeeklyRecommendation = (analysis) => {
  const { dominantPattern, strongestPositive, strongestNegative, valueCounts } = analysis;

  // If there was a negative pattern, recommend the opposite positive
  if (dominantPattern === 'harm') {
    return {
      direction: 'recovery',
      reason: 'negative_balance',
      insight: 'Pressure appears from last week. This week, consider strengthening the direction of recovery.'
    };
  }

  if (dominantPattern === 'avoidance') {
    return {
      direction: 'order',
      reason: 'negative_balance',
      insight: 'An avoidance pattern appears from last week. This week, consider strengthening the direction of order.'
    };
  }

  // Find the weakest positive direction
  const positiveValues = ['contribution', 'recovery', 'order'];
  const positiveCounts = positiveValues.map(v => ({
    direction: v,
    count: valueCounts[v] || 0
  })).sort((a, b) => a.count - b.count);

  const weakestPositive = positiveCounts[0];

  // If there's a clear gap, recommend filling it
  if (weakestPositive.count === 0 && analysis.totalDecisions >= 3) {
    return {
      direction: weakestPositive.direction,
      reason: 'gap',
      insight: `A persistent gap in direction appears ${valueLabels[weakestPositive.direction]} — This is the recommended direction for the coming week.`
    };
  }

  // Continue positive momentum
  if (strongestPositive && strongestPositive.count >= 2) {
    return {
      direction: strongestPositive.tag,
      reason: 'momentum',
      insight: `Last week showed a pattern of ${valueLabels[strongestPositive.tag]}. This week it is recommended to continue the momentum.`
    };
  }

  // Default: recommend contribution
  return {
    direction: 'contribution',
    reason: 'default',
    insight: 'This week it is recommended to strengthen a contribution direction.'
  };
};

// Check if this is a new week
const isNewWeek = (storedOrientation) => {
  if (!storedOrientation) return true;
  
  const currentWeekId = getWeekId(new Date());
  return storedOrientation.weekId !== currentWeekId;
};

// Get stored weekly orientation
const getStoredWeeklyOrientation = () => {
  try {
    const stored = localStorage.getItem(WEEKLY_ORIENTATION_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.log('Failed to get stored weekly orientation:', e);
  }
  return null;
};

// Save weekly orientation
const saveWeeklyOrientation = (orientation) => {
  try {
    localStorage.setItem(WEEKLY_ORIENTATION_KEY, JSON.stringify(orientation));
  } catch (e) {
    console.log('Failed to save weekly orientation:', e);
  }
};

export default function WeeklyOrientationSummarySection({ history, onStartWeek }) {
  const [showOrientation, setShowOrientation] = useState(false);
  const [weekStarted, setWeekStarted] = useState(false);

  // Analyze last week's patterns
  const lastWeekAnalysis = useMemo(() => {
    return analyzeLastWeekPatterns(history);
  }, [history]);

  // Get weekly recommendation
  const weeklyRecommendation = useMemo(() => {
    return calculateWeeklyRecommendation(lastWeekAnalysis);
  }, [lastWeekAnalysis]);

  // Check if we should show orientation on mount
  useEffect(() => {
    const storedOrientation = getStoredWeeklyOrientation();

    if (isNewWeek(storedOrientation)) {
      setShowOrientation(true);
      setWeekStarted(false);
    } else {
      setShowOrientation(false);
      setWeekStarted(true);
    }
  }, []);

  // Handle starting the week
  const handleStartWeek = () => {
    const today = new Date();
    const orientation = {
      weekId: getWeekId(today),
      timestamp: today.toISOString(),
      week_started: true,
      weekly_orientation_direction: weeklyRecommendation.direction,
      weekly_pattern_reference: lastWeekAnalysis.dominantPattern,
      last_week_decisions: lastWeekAnalysis.totalDecisions,
      recommendation_reason: weeklyRecommendation.reason
    };

    saveWeeklyOrientation(orientation);
    setWeekStarted(true);
    setShowOrientation(false);

    if (onStartWeek) {
      onStartWeek(orientation);
    }
  };

  // Don't show if week already started
  if (!showOrientation || weekStarted) {
    return null;
  }

  const { dominantPattern, strongestPositive, strongestNegative, totalDecisions } = lastWeekAnalysis;
  const colors = directionColors[weeklyRecommendation.direction] || directionColors.recovery;

  return (
    <section 
      className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-3xl p-5 shadow-sm border border-purple-200"
      data-testid="weekly-orientation-summary-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-purple-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-purple-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Weekly Summary</h3>
          <p className="text-xs text-purple-700">The new week starts from last week's pattern.</p>
        </div>
      </div>

      {/* Last Week Summary */}
      <div className="bg-white/60 rounded-xl p-4 mb-3">
        <h4 className="text-sm font-medium text-muted-foreground mb-3">Last week</h4>
        
        {totalDecisions === 0 ? (
          <p className="text-base text-foreground" data-testid="last-week-pattern">
            There was no activity last week.
          </p>
        ) : (
          <div className="space-y-2">
            {/* Dominant Pattern */}
            <p className="text-base font-medium text-foreground" data-testid="last-week-pattern">
              A pattern stood out of {patternDescriptions[dominantPattern]}.
            </p>
            
            {/* Strongest Positive */}
            {strongestPositive && (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span className="text-sm text-green-700" data-testid="strongest-positive">
                  Positive: {valueLabels[strongestPositive.tag]} ({strongestPositive.count})
                </span>
              </div>
            )}
            
            {/* Strongest Negative */}
            {strongestNegative && (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
                <span className="text-sm text-red-700" data-testid="strongest-negative">
                  Negative: {valueLabels[strongestNegative.tag]} ({strongestNegative.count})
                </span>
              </div>
            )}

            <p className="text-xs text-muted-foreground mt-1">
              {totalDecisions} decisions last week
            </p>
          </div>
        )}
      </div>

      {/* This Week's Recommendation */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">This week</h4>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
            {valueLabels[weeklyRecommendation.direction]}
          </span>
        </div>
        <p className={`text-base font-medium ${colors.text}`} data-testid="weekly-recommendation">
          {weeklyRecommendation.insight}
        </p>
      </div>

      {/* Start Week Button */}
      <button
        onClick={handleStartWeek}
        className="w-full px-4 py-3 bg-purple-500 text-white rounded-xl font-medium hover:bg-purple-600 transition-all flex items-center justify-center gap-2"
        data-testid="start-week-btn"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Start the week</span>
      </button>

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-3 text-center">
        The weekly summary helps build long-term behavioral direction
      </p>
    </section>
  );
}

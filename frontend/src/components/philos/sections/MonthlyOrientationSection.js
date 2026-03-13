import { useState, useEffect, useMemo } from 'react';
import { 
  filterHistoryByDateRange,
  countValueTags,
  identifyDominantPattern,
  valueLabels,
  valueColors 
} from '../../../services/analyticsService';

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

// Direction colors (from analyticsService but extended)
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' }
};

// Hebrew month names
const hebrewMonths = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

// LocalStorage key for monthly orientation
const MONTHLY_ORIENTATION_KEY = 'philos_monthly_orientation';

// Get month identifier (year-month)
const getMonthId = (date) => {
  const year = date.getFullYear();
  const month = date.getMonth() + 1; // 1-indexed
  return `${year}-M${month.toString().padStart(2, '0')}`;
};

// Get last month's name in Hebrew
const getLastMonthName = () => {
  const today = new Date();
  const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  return hebrewMonths[lastMonth.getMonth()];
};

// Analyze last month's patterns using centralized analytics
const analyzeLastMonthPatterns = (history) => {
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
  const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  currentMonthStart.setHours(0, 0, 0, 0);

  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  lastMonthStart.setHours(0, 0, 0, 0);

  const lastMonthEnd = new Date(currentMonthStart);
  lastMonthEnd.setMilliseconds(-1); // End of last month

  // Use centralized filtering
  const lastMonthDecisions = filterHistoryByDateRange(history, lastMonthStart, lastMonthEnd);

  if (lastMonthDecisions.length === 0) {
    return {
      dominantPattern: 'none',
      strongestPositive: null,
      strongestNegative: null,
      totalDecisions: 0,
      valueCounts: {}
    };
  }

  // Use centralized counting and pattern identification
  const valueCounts = countValueTags(lastMonthDecisions);
  const pattern = identifyDominantPattern(valueCounts);

  return {
    dominantPattern: pattern.dominantPattern || 'balanced',
    strongestPositive: pattern.strongestPositive,
    strongestNegative: pattern.strongestNegative,
    totalDecisions: lastMonthDecisions.length,
    valueCounts
  };
};

// Calculate monthly recommendation
const calculateMonthlyRecommendation = (analysis) => {
  const { dominantPattern, strongestPositive, strongestNegative, valueCounts, totalDecisions } = analysis;

  // If there was a negative pattern, recommend the opposite positive
  if (dominantPattern === 'harm') {
    return {
      direction: 'recovery',
      reason: 'negative_balance',
      insight: 'Pressure appears from last month. This month, consider strengthening the direction of recovery.'
    };
  }

  if (dominantPattern === 'avoidance') {
    return {
      direction: 'order',
      reason: 'negative_balance',
      insight: 'An avoidance pattern appears from last month. This month, consider strengthening the direction of order.'
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
  if (weakestPositive.count === 0 && totalDecisions >= 5) {
    return {
      direction: weakestPositive.direction,
      reason: 'gap',
      insight: `A persistent gap in direction appears ${valueLabels[weakestPositive.direction]} — This is the recommended direction for the coming month.`
    };
  }

  // Continue positive momentum
  if (strongestPositive && strongestPositive.count >= 3) {
    return {
      direction: strongestPositive.tag,
      reason: 'momentum',
      insight: `Last month showed a pattern of ${valueLabels[strongestPositive.tag]}. This month it is recommended to continue the momentum.`
    };
  }

  // Default: recommend contribution
  return {
    direction: 'contribution',
    reason: 'default',
    insight: 'This month it is recommended to strengthen a contribution direction.'
  };
};

// Check if this is a new month
const isNewMonth = (storedOrientation) => {
  if (!storedOrientation) return true;
  
  const currentMonthId = getMonthId(new Date());
  return storedOrientation.monthId !== currentMonthId;
};

// Get stored monthly orientation
const getStoredMonthlyOrientation = () => {
  try {
    const stored = localStorage.getItem(MONTHLY_ORIENTATION_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.log('Failed to get stored monthly orientation:', e);
  }
  return null;
};

// Save monthly orientation
const saveMonthlyOrientation = (orientation) => {
  try {
    localStorage.setItem(MONTHLY_ORIENTATION_KEY, JSON.stringify(orientation));
  } catch (e) {
    console.log('Failed to save monthly orientation:', e);
  }
};

export default function MonthlyOrientationSection({ history, onStartMonth }) {
  const [showOrientation, setShowOrientation] = useState(false);
  const [monthStarted, setMonthStarted] = useState(false);

  // Get last month's name
  const lastMonthName = useMemo(() => getLastMonthName(), []);

  // Analyze last month's patterns
  const lastMonthAnalysis = useMemo(() => {
    return analyzeLastMonthPatterns(history);
  }, [history]);

  // Get monthly recommendation
  const monthlyRecommendation = useMemo(() => {
    return calculateMonthlyRecommendation(lastMonthAnalysis);
  }, [lastMonthAnalysis]);

  // Check if we should show orientation on mount
  useEffect(() => {
    const storedOrientation = getStoredMonthlyOrientation();

    if (isNewMonth(storedOrientation)) {
      setShowOrientation(true);
      setMonthStarted(false);
    } else {
      setShowOrientation(false);
      setMonthStarted(true);
    }
  }, []);

  // Handle starting the month
  const handleStartMonth = () => {
    const today = new Date();
    const orientation = {
      monthId: getMonthId(today),
      timestamp: today.toISOString(),
      month_started: true,
      monthly_orientation_direction: monthlyRecommendation.direction,
      monthly_pattern_reference: lastMonthAnalysis.dominantPattern,
      last_month_decisions: lastMonthAnalysis.totalDecisions,
      recommendation_reason: monthlyRecommendation.reason
    };

    saveMonthlyOrientation(orientation);
    setMonthStarted(true);
    setShowOrientation(false);

    if (onStartMonth) {
      onStartMonth(orientation);
    }
  };

  // Don't show if month already started
  if (!showOrientation || monthStarted) {
    return null;
  }

  const { dominantPattern, strongestPositive, strongestNegative, totalDecisions } = lastMonthAnalysis;
  const colors = directionColors[monthlyRecommendation.direction] || directionColors.recovery;

  return (
    <section 
      className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-teal-200"
      data-testid="monthly-orientation-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-teal-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-teal-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Monthly Orientation</h3>
          <p className="text-xs text-teal-700">The new month starts from last month's pattern.</p>
        </div>
      </div>

      {/* Last Month Summary */}
      <div className="bg-white/60 rounded-xl p-4 mb-3">
        <h4 className="text-sm font-medium text-muted-foreground mb-3">{lastMonthName}</h4>
        
        {totalDecisions === 0 ? (
          <p className="text-base text-foreground" data-testid="last-month-pattern">
            There was no activity last month.
          </p>
        ) : (
          <div className="space-y-2">
            {/* Dominant Pattern */}
            <p className="text-base font-medium text-foreground" data-testid="last-month-pattern">
              A pattern stood out of {patternDescriptions[dominantPattern]}.
            </p>
            
            {/* Strongest Positive */}
            {strongestPositive && (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span className="text-sm text-green-700" data-testid="monthly-strongest-positive">
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
                <span className="text-sm text-red-700" data-testid="monthly-strongest-negative">
                  Negative: {valueLabels[strongestNegative.tag]} ({strongestNegative.count})
                </span>
              </div>
            )}

            <p className="text-xs text-muted-foreground mt-1">
              {totalDecisions} decisions last month
            </p>
          </div>
        )}
      </div>

      {/* This Month's Recommendation */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">This month</h4>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
            {valueLabels[monthlyRecommendation.direction]}
          </span>
        </div>
        <p className={`text-base font-medium ${colors.text}`} data-testid="monthly-recommendation">
          {monthlyRecommendation.insight}
        </p>
      </div>

      {/* Start Month Button */}
      <button
        onClick={handleStartMonth}
        className="w-full px-4 py-3 bg-teal-500 text-white rounded-xl font-medium hover:bg-teal-600 transition-all flex items-center justify-center gap-2"
        data-testid="start-month-btn"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Start the month</span>
      </button>

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-3 text-center">
        Monthly orientation helps build long-term behavioral direction
      </p>
    </section>
  );
}

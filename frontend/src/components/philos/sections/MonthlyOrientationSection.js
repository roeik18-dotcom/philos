import { useState, useEffect, useMemo } from 'react';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Pattern descriptions in Hebrew
const patternDescriptions = {
  contribution: 'מומנטום חיובי של תרומה',
  recovery: 'איזון של התאוששות',
  order: 'מיקוד בסדר וארגון',
  harm: 'לחץ ונזק',
  avoidance: 'הימנעות',
  balanced: 'מערכת מאוזנת',
  none: 'אין נתונים'
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' }
};

// Hebrew month names
const hebrewMonths = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
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

// Analyze last month's patterns
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

  // Filter last month's decisions
  const lastMonthDecisions = history.filter(item => {
    if (!item.timestamp) return false;
    const itemDate = new Date(item.timestamp);
    return itemDate >= lastMonthStart && itemDate <= lastMonthEnd;
  });

  if (lastMonthDecisions.length === 0) {
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
  lastMonthDecisions.forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      valueCounts[tag] = (valueCounts[tag] || 0) + 1;
    }
  });

  // Find dominant pattern
  const total = lastMonthDecisions.length;
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
      insight: 'נראה לחץ בחודש שעבר. החודש מומלץ לחזק כיוון של התאוששות.'
    };
  }

  if (dominantPattern === 'avoidance') {
    return {
      direction: 'order',
      reason: 'negative_balance',
      insight: 'נראה דפוס הימנעות בחודש שעבר. החודש מומלץ לחזק כיוון של סדר.'
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
      insight: `נראה פער מתמשך בכיוון ${valueLabels[weakestPositive.direction]} — זה הכיוון המומלץ לחודש הקרוב.`
    };
  }

  // Continue positive momentum
  if (strongestPositive && strongestPositive.count >= 3) {
    return {
      direction: strongestPositive.tag,
      reason: 'momentum',
      insight: `חודש שעבר בלט דפוס של ${valueLabels[strongestPositive.tag]}. החודש מומלץ להמשיך במומנטום.`
    };
  }

  // Default: recommend contribution
  return {
    direction: 'contribution',
    reason: 'default',
    insight: 'החודש מומלץ לחזק כיוון של תרומה.'
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
      dir="rtl"
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
          <h3 className="text-lg font-semibold text-foreground">התמצאות חודשית</h3>
          <p className="text-xs text-teal-700">החודש החדש מתחיל מתוך הדפוס של החודש שעבר.</p>
        </div>
      </div>

      {/* Last Month Summary */}
      <div className="bg-white/60 rounded-xl p-4 mb-3">
        <h4 className="text-sm font-medium text-muted-foreground mb-3">{lastMonthName}</h4>
        
        {totalDecisions === 0 ? (
          <p className="text-base text-foreground" data-testid="last-month-pattern">
            לא הייתה פעילות בחודש שעבר.
          </p>
        ) : (
          <div className="space-y-2">
            {/* Dominant Pattern */}
            <p className="text-base font-medium text-foreground" data-testid="last-month-pattern">
              בלט דפוס של {patternDescriptions[dominantPattern]}.
            </p>
            
            {/* Strongest Positive */}
            {strongestPositive && (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span className="text-sm text-green-700" data-testid="monthly-strongest-positive">
                  חיובי: {valueLabels[strongestPositive.tag]} ({strongestPositive.count})
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
                  שלילי: {valueLabels[strongestNegative.tag]} ({strongestNegative.count})
                </span>
              </div>
            )}

            <p className="text-xs text-muted-foreground mt-1">
              {totalDecisions} החלטות בחודש שעבר
            </p>
          </div>
        )}
      </div>

      {/* This Month's Recommendation */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">החודש</h4>
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
        <span>התחל את החודש</span>
      </button>

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-3 text-center">
        ההתמצאות החודשית עוזרת לבנות כיוון התנהגותי ארוך טווח
      </p>
    </section>
  );
}

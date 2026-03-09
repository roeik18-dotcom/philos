import { useMemo } from 'react';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Analyze current state from recent decisions
const analyzeCurrentState = (history) => {
  if (!history || history.length === 0) {
    return {
      hasData: false,
      summary: 'אין נתונים עדיין',
      pattern: null,
      todayCount: 0
    };
  }

  // Get today's decisions
  const today = new Date().toDateString();
  const todayDecisions = history.filter(h => {
    const itemDate = h.timestamp ? new Date(h.timestamp).toDateString() : today;
    return itemDate === today;
  });

  // Analyze recent pattern (last 5 decisions)
  const recent = history.slice(0, 5);
  const valueCounts = {};
  recent.forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      valueCounts[tag] = (valueCounts[tag] || 0) + 1;
    }
  });

  // Detect dominant pattern
  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const contributionCount = valueCounts.contribution || 0;
  const recoveryCount = valueCounts.recovery || 0;
  const orderCount = valueCounts.order || 0;

  const negativeRatio = (harmCount + avoidanceCount) / recent.length;
  const positiveRatio = (contributionCount + recoveryCount + orderCount) / recent.length;

  let summary = '';
  let pattern = null;
  let patternType = 'neutral';

  if (negativeRatio > 0.5) {
    if (harmCount > avoidanceCount) {
      pattern = 'harm';
      patternType = 'negative';
      summary = 'נראה דפוס של לחץ ונזק.';
    } else {
      pattern = 'avoidance';
      patternType = 'negative';
      summary = 'נראה דפוס של הימנעות.';
    }
  } else if (positiveRatio > 0.6) {
    if (contributionCount >= recoveryCount && contributionCount >= orderCount) {
      pattern = 'contribution';
      patternType = 'positive';
      summary = 'מומנטום חיובי של תרומה.';
    } else if (recoveryCount >= orderCount) {
      pattern = 'recovery';
      patternType = 'positive';
      summary = 'איזון טוב של התאוששות.';
    } else {
      pattern = 'order';
      patternType = 'positive';
      summary = 'מיקוד בסדר וארגון.';
    }
  } else {
    pattern = 'balanced';
    patternType = 'neutral';
    summary = 'המערכת מאוזנת.';
  }

  // Get last decision info
  const lastDecision = history[0];
  const lastValueTag = lastDecision?.value_tag;

  return {
    hasData: true,
    summary,
    pattern,
    patternType,
    todayCount: todayDecisions.length,
    totalCount: history.length,
    lastValueTag,
    lastAction: lastDecision?.action?.substring(0, 50)
  };
};

export default function HomeNavigationSection({ 
  history, 
  adaptiveScores, 
  replayInsights,
  actionText,
  setActionText,
  evaluateAction,
  recommendationMetadata,
  onClearRecommendation,
  onFollowRecommendation,
  state
}) {
  // Analyze current state
  const currentState = useMemo(() => {
    return analyzeCurrentState(history);
  }, [history]);

  // Get recommendation from NextBestDirection logic (simplified inline)
  const recommendation = useMemo(() => {
    if (!history || history.length === 0) {
      return {
        direction: 'recovery',
        actionSuggestion: 'הפסקה קצרה ומודעת',
        insight: 'התחל עם פעולת התאוששות.'
      };
    }

    // Simplified recommendation based on current state
    const recent = history.slice(0, 10);
    const valueCounts = {};
    recent.forEach(item => {
      if (item.value_tag) valueCounts[item.value_tag] = (valueCounts[item.value_tag] || 0) + 1;
    });

    const harmCount = valueCounts.harm || 0;
    const avoidanceCount = valueCounts.avoidance || 0;
    const negativeRatio = (harmCount + avoidanceCount) / recent.length;

    if (negativeRatio > 0.4) {
      if (avoidanceCount > harmCount) {
        return {
          direction: 'order',
          actionSuggestion: 'לסיים משימה פתוחה אחת',
          insight: 'מומלץ לבצע החלטה קטנה במקום דחייה.'
        };
      } else {
        return {
          direction: 'recovery',
          actionSuggestion: 'הפסקה קצרה ומודעת',
          insight: 'מומלץ לאזן עם התאוששות.'
        };
      }
    }

    // Default positive recommendation
    const lowestPositive = ['contribution', 'recovery', 'order']
      .map(dir => ({ dir, count: valueCounts[dir] || 0 }))
      .sort((a, b) => a.count - b.count)[0];

    const suggestions = {
      contribution: { action: 'פעולה קטנה של עזרה למישהו', insight: 'כדאי לשקול פעולה בכיוון תרומה.' },
      recovery: { action: 'הפסקה קצרה ומודעת', insight: 'התאוששות תמיד בחירה טובה.' },
      order: { action: 'לסיים משימה פתוחה אחת', insight: 'כדאי לשקול פעולה בכיוון סדר.' }
    };

    return {
      direction: lowestPositive.dir,
      actionSuggestion: suggestions[lowestPositive.dir].action,
      insight: suggestions[lowestPositive.dir].insight
    };
  }, [history]);

  // Direction colors
  const directionColors = {
    contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
    recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
    order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' }
  };

  const colors = directionColors[recommendation.direction] || directionColors.recovery;

  // Handle follow recommendation
  const handleFollowRecommendation = () => {
    if (onFollowRecommendation) {
      onFollowRecommendation({
        recommendation_text: recommendation.actionSuggestion,
        recommendation_direction: recommendation.direction,
        recommendation_reason: 'home_navigation',
        recommendation_strength: 50,
        recommendation_insight: recommendation.insight,
        followed_recommendation: true,
        timestamp: new Date().toISOString()
      });
    }
  };

  return (
    <section 
      className="bg-white rounded-3xl p-6 shadow-sm border border-border"
      dir="rtl"
      data-testid="home-navigation-section"
    >
      {/* Current State - מצב נוכחי */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-muted-foreground mb-2">מצב היום</h3>
        <div className={`p-4 rounded-xl ${
          currentState.patternType === 'negative' ? 'bg-amber-50 border border-amber-200' :
          currentState.patternType === 'positive' ? 'bg-green-50 border border-green-200' :
          'bg-gray-50 border border-gray-200'
        }`}>
          <p className={`text-lg font-semibold ${
            currentState.patternType === 'negative' ? 'text-amber-800' :
            currentState.patternType === 'positive' ? 'text-green-800' :
            'text-gray-800'
          }`} data-testid="current-state-summary">
            {currentState.summary}
          </p>
          {currentState.hasData && (
            <p className="text-sm text-muted-foreground mt-1">
              {currentState.todayCount} החלטות היום • {currentState.totalCount} סה״כ
            </p>
          )}
        </div>
      </div>

      {/* Next Best Direction - כיוון מומלץ */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-muted-foreground mb-2">כיוון מומלץ</h3>
        <div className={`p-4 rounded-xl ${colors.bg} border ${colors.border}`}>
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
              {valueLabels[recommendation.direction]}
            </span>
          </div>
          <p className={`text-lg font-semibold ${colors.text}`} data-testid="recommendation-action">
            {recommendation.actionSuggestion}
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            {recommendation.insight}
          </p>
        </div>
      </div>

      {/* Recommendation Indicator (when action originated from recommendation) */}
      {recommendationMetadata && (
        <div 
          className="mb-4 p-3 bg-sky-50 border border-sky-200 rounded-xl flex items-center justify-between"
          data-testid="home-recommendation-indicator"
        >
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span className="text-sm text-sky-700">הפעולה נובעת מהכיוון המומלץ</span>
          </div>
          <button
            onClick={onClearRecommendation}
            className="text-sky-600 hover:text-sky-800 p-1"
            data-testid="home-clear-recommendation"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Action Input */}
      <div className="mb-4">
        <input
          type="text"
          value={actionText}
          onChange={(e) => setActionText(e.target.value)}
          placeholder="הזן פעולה לבדיקה..."
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-right focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          data-testid="home-action-input"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && actionText.trim()) {
              evaluateAction();
            }
          }}
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        {/* Follow Recommendation Button */}
        <button
          onClick={handleFollowRecommendation}
          className={`flex-1 px-4 py-3 ${colors.bg} ${colors.text} border-2 ${colors.border} rounded-xl font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2`}
          data-testid="home-follow-recommendation-btn"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          <span>פעל לפי ההמלצה</span>
        </button>

        {/* Evaluate Custom Action */}
        {actionText.trim() && (
          <button
            onClick={evaluateAction}
            className="px-4 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-all"
            data-testid="home-evaluate-btn"
          >
            בדוק
          </button>
        )}
      </div>
    </section>
  );
}

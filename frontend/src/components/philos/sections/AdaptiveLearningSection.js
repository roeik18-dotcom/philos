// Adaptive Learning Summary Section
// Displays which path types are trusted more/less based on learning history

import { useMemo } from 'react';

// Hebrew labels
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

const valueColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' }
};

export default function AdaptiveLearningSection({ learningHistory, adaptiveScores }) {
  // Calculate insights from learning history
  const insights = useMemo(() => {
    if (!learningHistory || learningHistory.length === 0) {
      return null;
    }

    const results = [];
    const pathTypes = ['recovery', 'order', 'contribution', 'harm', 'avoidance'];
    
    // Analyze each path type
    const typeStats = {};
    pathTypes.forEach(type => {
      const entries = learningHistory.filter(h => h.predicted_value_tag === type);
      if (entries.length > 0) {
        const avgMatchQuality = entries.reduce((sum, e) => {
          const qualityScore = e.match_quality === 'high' ? 3 : e.match_quality === 'medium' ? 2 : 1;
          return sum + qualityScore;
        }, 0) / entries.length;
        
        const betterThanPredicted = entries.filter(e => 
          e.actual_recovery_stability > e.predicted_recovery_stability ||
          e.actual_harm_pressure < e.predicted_harm_pressure
        ).length;
        
        const worseThanPredicted = entries.filter(e =>
          e.actual_harm_pressure > e.predicted_harm_pressure ||
          e.actual_value_tag === 'harm' || e.actual_value_tag === 'avoidance'
        ).length;

        typeStats[type] = {
          count: entries.length,
          avgMatchQuality,
          betterRate: betterThanPredicted / entries.length,
          worseRate: worseThanPredicted / entries.length
        };
      }
    });

    // Generate insights based on adaptive scores
    if (adaptiveScores) {
      // Find boosted types
      const boostedTypes = Object.entries(adaptiveScores)
        .filter(([_, score]) => score > 5)
        .sort((a, b) => b[1] - a[1]);
      
      if (boostedTypes.length > 0) {
        const topBoosted = boostedTypes[0][0];
        results.push({
          type: 'boost',
          text: `${valueLabels[topBoosted]} paths now receive higher priority`,
          pathType: topBoosted
        });
      }

      // Find penalized types
      const penalizedTypes = Object.entries(adaptiveScores)
        .filter(([_, score]) => score < -5)
        .sort((a, b) => a[1] - b[1]);
      
      if (penalizedTypes.length > 0) {
        const topPenalized = penalizedTypes[0][0];
        results.push({
          type: 'penalty',
          text: `Paths with ${valueLabels[topPenalized]} tendency receive reduced weight`,
          pathType: topPenalized
        });
      }
    }

    // Add match quality insight
    const totalEntries = learningHistory.length;
    const highMatchCount = learningHistory.filter(h => h.match_quality === 'high').length;
    const matchRate = (highMatchCount / totalEntries) * 100;

    if (matchRate >= 60) {
      results.push({
        type: 'accuracy',
        text: 'Prediction accuracy is high — the system is learning well',
        pathType: null
      });
    } else if (matchRate < 40) {
      results.push({
        type: 'accuracy',
        text: 'Prediction accuracy is moderate — the system is adjusting',
        pathType: null
      });
    }

    return {
      insights: results,
      typeStats,
      totalLearnings: totalEntries,
      matchRate
    };
  }, [learningHistory, adaptiveScores]);

  // Don't render if no learning history
  if (!learningHistory || learningHistory.length < 2) {
    return (
      <section 
        className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-5 shadow-sm border border-purple-200"
        data-testid="adaptive-learning-section"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Adaptive Learning</h3>
            <p className="text-xs text-muted-foreground">Adjusting path ranking by performance</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-purple-200 flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
        </div>
        <div className="text-center py-6 bg-white/50 rounded-xl">
          <p className="text-muted-foreground">Need at least 2 decisions with path selection to start learning</p>
          <p className="text-xs text-muted-foreground mt-1">Select paths and evaluate them to build learning history</p>
        </div>
      </section>
    );
  }

  return (
    <section 
      className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-5 shadow-sm border border-purple-200"
      data-testid="adaptive-learning-section"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Adaptive Learning</h3>
          <p className="text-xs text-muted-foreground">Adjusting path ranking by performance</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">{insights.totalLearnings} learnings</span>
          <div className="w-10 h-10 rounded-full bg-purple-200 flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Adaptive Scores Display */}
      {adaptiveScores && (
        <div className="bg-white/70 rounded-xl p-4 mb-4">
          <p className="text-sm font-semibold text-foreground mb-3">Current ranking adjustments</p>
          <div className="grid grid-cols-3 gap-2">
            {['recovery', 'order', 'contribution'].map(type => {
              const score = adaptiveScores[type] || 0;
              const colors = valueColors[type];
              return (
                <div key={type} className={`p-2 rounded-lg ${colors.bg} text-center`}>
                  <p className="text-xs text-muted-foreground">{valueLabels[type]}</p>
                  <p className={`text-lg font-bold ${score > 0 ? 'text-green-600' : score < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                    {score > 0 ? '+' : ''}{score}
                  </p>
                </div>
              );
            })}
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {['harm', 'avoidance'].map(type => {
              const score = adaptiveScores[type] || 0;
              const colors = valueColors[type];
              return (
                <div key={type} className={`p-2 rounded-lg ${colors.bg} text-center`}>
                  <p className="text-xs text-muted-foreground">{valueLabels[type]}</p>
                  <p className={`text-lg font-bold ${score > 0 ? 'text-green-600' : score < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                    {score > 0 ? '+' : ''}{score}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Trust Level Bars */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-semibold text-foreground mb-3">Trust level by path type</p>
        <div className="space-y-3">
          {['recovery', 'order', 'contribution'].map(type => {
            const score = adaptiveScores?.[type] || 0;
            const normalizedScore = Math.max(0, Math.min(100, 50 + score * 2));
            const colors = valueColors[type];
            return (
              <div key={type} className="flex items-center gap-3">
                <span className={`text-xs w-16 ${colors.text}`}>{valueLabels[type]}</span>
                <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all ${
                      normalizedScore >= 60 ? 'bg-green-500' : 
                      normalizedScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${normalizedScore}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground w-8">{normalizedScore}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Match Accuracy */}
      <div className="bg-white/70 rounded-xl p-3 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Overall prediction accuracy</span>
          <span className={`text-sm font-bold ${
            insights.matchRate >= 60 ? 'text-green-600' : 
            insights.matchRate >= 40 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {Math.round(insights.matchRate)}%
          </span>
        </div>
        <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full ${
              insights.matchRate >= 60 ? 'bg-green-500' : 
              insights.matchRate >= 40 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${insights.matchRate}%` }}
          />
        </div>
      </div>

      {/* Insights */}
      {insights.insights.length > 0 && (
        <div className="bg-purple-100/50 border border-purple-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-purple-800 mb-2">Adaptive insights:</p>
          <div className="space-y-2">
            {insights.insights.map((insight, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className={`text-lg ${
                  insight.type === 'boost' ? 'text-green-500' : 
                  insight.type === 'penalty' ? 'text-red-500' : 'text-purple-500'
                }`}>
                  {insight.type === 'boost' ? '↑' : insight.type === 'penalty' ? '↓' : '•'}
                </span>
                <p className="text-sm text-purple-700">{insight.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

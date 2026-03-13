// Hebrew value tag labels
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Value colors for visual indicators
const boostedColors = {
  contribution: 'bg-green-100 text-green-700 border-green-300',
  recovery: 'bg-blue-100 text-blue-700 border-blue-300',
  order: 'bg-indigo-100 text-indigo-700 border-indigo-300'
};

const penalizedColors = {
  harm: 'bg-red-100 text-red-700 border-red-300',
  avoidance: 'bg-gray-100 text-gray-600 border-gray-300'
};

export default function ReplayAdaptiveEffectSection({ 
  adjustments, 
  adaptiveScores,
  replayInsights 
}) {
  // Don't render if no adjustments
  if (!adjustments || (adjustments.boosted.length === 0 && adjustments.penalized.length === 0)) {
    return null;
  }

  // Calculate score bar widths (normalize to 0-100%)
  const maxScore = 25;
  const getBarWidth = (score) => {
    const normalized = Math.max(0, Math.min(100, ((score + maxScore) / (maxScore * 2)) * 100));
    return normalized;
  };

  return (
    <section 
      className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-emerald-200"
      data-testid="replay-adaptive-effect-section"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 bg-emerald-200 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">
            Impact of replays on paths
          </h3>
          <p className="text-xs text-muted-foreground">
            Automatic adjustments based on {replayInsights?.total_replays || 0} repeat activations
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Boosted Directions */}
        {adjustments.boosted.length > 0 && (
          <div className="bg-white/60 rounded-xl p-4">
            <h4 className="text-sm font-medium text-emerald-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
              Boosted directions
            </h4>
            <div className="space-y-2">
              {adjustments.boosted.map((item, idx) => (
                <div 
                  key={`boost-${idx}`} 
                  className="flex items-center gap-3"
                  data-testid={`boosted-item-${idx}`}
                >
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${boostedColors[item.type] || 'bg-gray-100'}`}>
                    {valueLabels[item.type]}
                  </span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${getBarWidth(adaptiveScores?.[item.type] || 0)}%` }}
                    />
                  </div>
                  <span className="text-xs text-emerald-600 font-medium min-w-[40px]">
                    +{item.boost}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Penalized Directions */}
        {adjustments.penalized.length > 0 && (
          <div className="bg-white/60 rounded-xl p-4">
            <h4 className="text-sm font-medium text-red-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              Weakened directions
            </h4>
            <div className="space-y-2">
              {adjustments.penalized.map((item, idx) => (
                <div 
                  key={`penalty-${idx}`} 
                  className="flex items-center gap-3"
                  data-testid={`penalized-item-${idx}`}
                >
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${penalizedColors[item.type] || 'bg-gray-100'}`}>
                    {valueLabels[item.type]}
                  </span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-red-300 to-red-400 rounded-full transition-all duration-500"
                      style={{ width: `${getBarWidth(adaptiveScores?.[item.type] || 0)}%` }}
                    />
                  </div>
                  <span className="text-xs text-red-600 font-medium min-w-[40px]">
                    -{item.penalty}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hebrew Insights */}
        {adjustments.insights && adjustments.insights.length > 0 && (
          <div className="bg-gradient-to-r from-emerald-100 to-teal-100 rounded-xl p-4 border border-emerald-200">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-emerald-200 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div className="space-y-2">
                <h5 className="text-sm font-semibold text-emerald-800">Match Insights</h5>
                {adjustments.insights.map((insight, idx) => (
                  <p 
                    key={idx} 
                    className="text-sm text-emerald-700"
                    data-testid={`adaptive-insight-${idx}`}
                  >
                    {insight}
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Score Summary */}
        <div className="grid grid-cols-5 gap-2 pt-2">
          {['contribution', 'recovery', 'order', 'harm', 'avoidance'].map(type => {
            const score = adaptiveScores?.[type] || 0;
            const isBoosted = adjustments.boosted.some(b => b.type === type);
            const isPenalized = adjustments.penalized.some(p => p.type === type);
            
            return (
              <div 
                key={type}
                className={`text-center p-2 rounded-lg ${
                  isBoosted ? 'bg-emerald-50 border border-emerald-200' :
                  isPenalized ? 'bg-red-50 border border-red-200' :
                  'bg-white/50'
                }`}
                data-testid={`score-summary-${type}`}
              >
                <div className={`text-lg font-bold ${
                  score > 0 ? 'text-emerald-600' :
                  score < 0 ? 'text-red-600' :
                  'text-gray-500'
                }`}>
                  {score > 0 ? '+' : ''}{score}
                </div>
                <div className="text-xs text-muted-foreground">{valueLabels[type]}</div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

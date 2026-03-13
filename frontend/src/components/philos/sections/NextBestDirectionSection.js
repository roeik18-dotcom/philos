import { useMemo } from 'react';
import { 
  calculateRecommendation, 
  valueLabels,
  directionColors
} from '../../../services/recommendationService';

export default function NextBestDirectionSection({ history, onFollowRecommendation }) {
  // Calculate recommendation using centralized theory-based service
  // Only history is needed - the model is based on theoretical framework
  const recommendation = useMemo(() => {
    return calculateRecommendation({ history });
  }, [history]);

  // Don't render if no recommendation
  if (!recommendation) {
    return null;
  }

  const { direction, strength, insight, actionSuggestion, reason, theoryPath } = recommendation;
  const colors = directionColors[direction] || directionColors.recovery;

  // Handler for following recommendation
  const handleFollowRecommendation = () => {
    if (onFollowRecommendation) {
      onFollowRecommendation({
        recommendation_text: actionSuggestion,
        recommendation_direction: direction,
        recommendation_reason: reason,
        recommendation_strength: strength,
        recommendation_insight: insight,
        followed_recommendation: true,
        timestamp: new Date().toISOString()
      });
    }
  };

  // SVG compass indicator
  const compassAngle = {
    contribution: -45,
    recovery: 45,
    order: 0,
    exploration: -90,
    harm: 135,
    avoidance: 180
  }[direction] || 0;

  return (
    <section 
      className="bg-gradient-to-br from-sky-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-sky-200"
      data-testid="next-best-direction-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-sky-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-sky-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Recommended direction</h3>
          <p className="text-xs text-muted-foreground">
            Behavioral navigation based on patterns
          </p>
        </div>
      </div>

      {/* Direction Card */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {/* Direction compass SVG */}
            <svg width="48" height="48" viewBox="0 0 48 48" data-testid="direction-compass">
              {/* Background circle */}
              <circle cx="24" cy="24" r="22" fill="white" stroke={colors.fill} strokeWidth="2" opacity="0.3" />
              
              {/* Strength arc */}
              <path
                d={`M 24 4 A 20 20 0 ${strength > 50 ? 1 : 0} 1 ${24 + 20 * Math.sin(strength * 3.6 * Math.PI / 180)} ${24 - 20 * Math.cos(strength * 3.6 * Math.PI / 180)}`}
                fill="none"
                stroke={colors.fill}
                strokeWidth="3"
                strokeLinecap="round"
              />
              
              {/* Direction arrow */}
              <g transform={`rotate(${compassAngle}, 24, 24)`}>
                <path
                  d="M 24 8 L 28 20 L 24 16 L 20 20 Z"
                  fill={colors.fill}
                />
                <circle cx="24" cy="24" r="4" fill={colors.fill} />
              </g>
              
              {/* Center dot */}
              <circle cx="24" cy="24" r="2" fill="white" />
            </svg>

            <div>
              <span className={`text-lg font-bold ${colors.text}`}>
                {valueLabels[direction]}
              </span>
              <div className="flex items-center gap-1 mt-1">
                <span className="text-xs text-muted-foreground">Strength:</span>
                <div className="w-16 h-1.5 bg-white/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${strength}%`, backgroundColor: colors.fill }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">{strength}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action suggestion */}
        <div className="bg-white/60 rounded-lg px-4 py-3" data-testid="action-suggestion">
          <p className={`text-sm font-medium ${colors.text}`}>
            Recommended direction for today: {actionSuggestion}
          </p>
        </div>
      </div>

      {/* Insight */}
      <div className="bg-white/60 rounded-xl p-4" data-testid="direction-insight">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-sky-200 rounded-full flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-sky-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <p className="text-sm text-sky-800">{insight}</p>
            {theoryPath && (
              <p className="text-xs text-sky-600 mt-1 font-medium">
                Descriptive path: {theoryPath}
              </p>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              {reason === 'theory_balancing' && 'Based on theoretical balance path'}
              {reason === 'theory_reinforcement' && 'Based on positive direction reinforcement'}
              {reason === 'no_history' && 'Initial recommendation'}
              {reason === 'default' && 'General recommendation'}
            </p>
          </div>
        </div>
      </div>

      {/* Follow Recommendation Button */}
      <button
        onClick={handleFollowRecommendation}
        className={`w-full mt-4 px-4 py-3 ${colors.bg} ${colors.text} border-2 ${colors.border} rounded-xl font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2`}
        data-testid="follow-recommendation-btn"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
        <span>Act on the recommendation</span>
      </button>
    </section>
  );
}

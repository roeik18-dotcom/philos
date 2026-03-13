import { useMemo } from 'react';

// Hebrew labels
const directionLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', fill: '#6366f1' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', fill: '#9ca3af' }
};

// Reason labels in Hebrew
const reasonLabels = {
  negative_harm_drift: 'drifting Harm Negative',
  negative_avoidance_drift: 'Avoidance pattern',
  collective_gap: 'Collective gap',
  replay_blind_spot: 'Blind spot',
  positive_contribution_momentum: 'Contribution momentum',
  replay_preference: 'Replay preference',
  balance_deficit: 'Balance deficit',
  general_balance: 'General Balance',
  default: 'Default'
};

// Calculate analytics from history
const calculateAnalytics = (history) => {
  if (!history || history.length === 0) {
    return null;
  }

  // Filter decisions that followed recommendations
  const followedDecisions = history.filter(d => d.followed_recommendation === true);
  
  // Get total decisions and calculate follow rate
  const totalDecisions = history.length;
  const followedCount = followedDecisions.length;
  const followRate = totalDecisions > 0 ? (followedCount / totalDecisions) * 100 : 0;

  if (followedCount === 0) {
    return null;
  }

  // Count by recommendation direction
  const directionCounts = {};
  const directionAlignments = {};
  const reasonCounts = {};
  const reasonSuccess = {};

  followedDecisions.forEach(decision => {
    const recDir = decision.recommendation_direction;
    const actualTag = decision.value_tag;
    const reason = decision.recommendation_reason;

    // Count directions
    directionCounts[recDir] = (directionCounts[recDir] || 0) + 1;

    // Track alignment (did the actual value_tag match recommendation direction?)
    if (!directionAlignments[recDir]) {
      directionAlignments[recDir] = { aligned: 0, total: 0 };
    }
    directionAlignments[recDir].total++;
    
    // Check alignment - recommendation direction matches actual outcome
    if (recDir === actualTag) {
      directionAlignments[recDir].aligned++;
    }

    // Count reasons
    if (reason) {
      reasonCounts[reason] = (reasonCounts[reason] || 0) + 1;
      if (!reasonSuccess[reason]) {
        reasonSuccess[reason] = { aligned: 0, total: 0 };
      }
      reasonSuccess[reason].total++;
      if (recDir === actualTag) {
        reasonSuccess[reason].aligned++;
      }
    }
  });

  // Find most and least followed directions
  const directionEntries = Object.entries(directionCounts).sort((a, b) => b[1] - a[1]);
  const mostFollowed = directionEntries.length > 0 ? directionEntries[0] : null;
  const leastFollowed = directionEntries.length > 1 ? directionEntries[directionEntries.length - 1] : null;

  // Calculate overall alignment rate
  let totalAligned = 0;
  let totalTracked = 0;
  Object.values(directionAlignments).forEach(({ aligned, total }) => {
    totalAligned += aligned;
    totalTracked += total;
  });
  const overallAlignmentRate = totalTracked > 0 ? (totalAligned / totalTracked) * 100 : 0;

  // Find strongest and weakest recommendation patterns
  const patternStrengths = Object.entries(directionAlignments)
    .filter(([_, data]) => data.total >= 2)
    .map(([dir, data]) => ({
      direction: dir,
      alignmentRate: (data.aligned / data.total) * 100,
      count: data.total
    }))
    .sort((a, b) => b.alignmentRate - a.alignmentRate);

  const strongestPattern = patternStrengths.length > 0 ? patternStrengths[0] : null;
  const weakestPattern = patternStrengths.length > 1 ? patternStrengths[patternStrengths.length - 1] : null;

  // Find most successful reason
  const reasonStrengths = Object.entries(reasonSuccess)
    .filter(([_, data]) => data.total >= 2)
    .map(([reason, data]) => ({
      reason,
      successRate: (data.aligned / data.total) * 100,
      count: data.total
    }))
    .sort((a, b) => b.successRate - a.successRate);

  const bestReason = reasonStrengths.length > 0 ? reasonStrengths[0] : null;

  return {
    totalDecisions,
    followedCount,
    followRate,
    directionCounts,
    directionAlignments,
    mostFollowed,
    leastFollowed,
    overallAlignmentRate,
    strongestPattern,
    weakestPattern,
    bestReason,
    patternStrengths
  };
};

// Generate Hebrew insights
const generateInsights = (analytics) => {
  const insights = [];

  if (!analytics) return insights;

  const { mostFollowed, leastFollowed, overallAlignmentRate, strongestPattern, weakestPattern } = analytics;

  // Most followed direction insight
  if (mostFollowed) {
    insights.push({
      type: 'most_followed',
      text: `Paths of ${directionLabels[mostFollowed[0]]} have the highest follow-through rate (${mostFollowed[1]} times)`,
      direction: mostFollowed[0],
      priority: 'high'
    });
  }

  // Alignment insight
  if (overallAlignmentRate > 60) {
    insights.push({
      type: 'strong_alignment',
      text: `Recommendations lead to matching results in ${Math.round(overallAlignmentRate)}% of cases`,
      priority: 'positive'
    });
  } else if (overallAlignmentRate < 40 && analytics.followedCount >= 3) {
    insights.push({
      type: 'weak_alignment',
      text: `There is a significant gap between recommendations and actual results (${Math.round(overallAlignmentRate)}% match)`,
      priority: 'warning'
    });
  }

  // Strongest pattern insight
  if (strongestPattern && strongestPattern.alignmentRate > 70) {
    insights.push({
      type: 'strongest_pattern',
      text: `Recommendations for ${directionLabels[strongestPattern.direction]} actually led to matching results in most cases (${Math.round(strongestPattern.alignmentRate)}%)`,
      direction: strongestPattern.direction,
      priority: 'positive'
    });
  }

  // Gap insight for weak patterns
  if (weakestPattern && weakestPattern.alignmentRate < 40 && leastFollowed) {
    insights.push({
      type: 'gap',
      text: `There is a gap between recommendations for ${directionLabels[weakestPattern.direction]} and the actual actions`,
      direction: weakestPattern.direction,
      priority: 'warning'
    });
  }

  return insights;
};

export default function RecommendationFollowThroughSection({ history }) {
  // Calculate analytics
  const analytics = useMemo(() => {
    return calculateAnalytics(history);
  }, [history]);

  // Generate insights
  const insights = useMemo(() => {
    return generateInsights(analytics);
  }, [analytics]);

  // Don't render if no recommendation data
  if (!analytics || analytics.followedCount < 2) {
    return null;
  }

  const { 
    followRate, 
    followedCount, 
    totalDecisions, 
    overallAlignmentRate,
    directionCounts,
    mostFollowed,
    leastFollowed,
    strongestPattern,
    weakestPattern,
    patternStrengths
  } = analytics;

  // Prepare data for SVG visualization
  const maxCount = Math.max(...Object.values(directionCounts));

  return (
    <section 
      className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-violet-200"
      data-testid="recommendation-follow-through-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-violet-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-violet-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Recommendation Follow-Through</h3>
          <p className="text-xs text-muted-foreground">
            Analysis of recommendation engine effectiveness
          </p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {/* Follow Rate */}
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <div className="text-2xl font-bold text-violet-700">{Math.round(followRate)}%</div>
          <div className="text-xs text-muted-foreground">Follow-through rate</div>
          <div className="text-xs text-violet-600">{followedCount}/{totalDecisions}</div>
        </div>

        {/* Alignment Rate */}
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <div className={`text-2xl font-bold ${overallAlignmentRate > 50 ? 'text-green-600' : 'text-amber-600'}`}>
            {Math.round(overallAlignmentRate)}%
          </div>
          <div className="text-xs text-muted-foreground">Result alignment</div>
          <div className="text-xs text-violet-600">Recommendation ↔ Action</div>
        </div>

        {/* Most Followed */}
        <div className="bg-white/60 rounded-xl p-3 text-center">
          {mostFollowed ? (
            <>
              <div className={`text-lg font-bold ${directionColors[mostFollowed[0]]?.text || 'text-violet-700'}`}>
                {directionLabels[mostFollowed[0]]}
              </div>
              <div className="text-xs text-muted-foreground">Most followed</div>
              <div className="text-xs text-violet-600">{mostFollowed[1]} times</div>
            </>
          ) : (
            <div className="text-sm text-muted-foreground">No data</div>
          )}
        </div>
      </div>

      {/* SVG Visual Summary - Direction Distribution */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <h4 className="text-sm font-medium text-foreground mb-3">Follow-through distribution by direction</h4>
        <svg width="100%" height="120" viewBox="0 0 300 120" data-testid="follow-through-chart">
          {Object.entries(directionCounts).map(([direction, count], index) => {
            const barWidth = (count / maxCount) * 180;
            const y = index * 24;
            const colors = directionColors[direction] || directionColors.recovery;
            const alignment = analytics.directionAlignments[direction];
            const alignRate = alignment ? (alignment.aligned / alignment.total) * 100 : 0;
            
            return (
              <g key={direction} transform={`translate(0, ${y})`}>
                {/* Direction label */}
                <text x="60" y="15" textAnchor="end" className="text-xs fill-current" style={{ fontSize: '11px' }}>
                  {directionLabels[direction]}
                </text>
                
                {/* Bar background */}
                <rect x="70" y="4" width="180" height="14" fill="#e5e7eb" rx="3" />
                
                {/* Follow count bar */}
                <rect 
                  x="70" 
                  y="4" 
                  width={barWidth} 
                  height="14" 
                  fill={colors.fill} 
                  rx="3"
                  opacity={alignRate > 50 ? 1 : 0.6}
                />
                
                {/* Count label */}
                <text x="260" y="15" className="text-xs fill-current" style={{ fontSize: '10px' }}>
                  {count} ({Math.round(alignRate)}%)
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Pattern Analysis */}
      {(strongestPattern || weakestPattern) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {/* Strongest Pattern */}
          {strongestPattern && (
            <div className={`${directionColors[strongestPattern.direction]?.bg || 'bg-green-100'} rounded-xl p-3`}>
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-xs font-medium text-green-700">Most effective</span>
              </div>
              <div className={`font-bold ${directionColors[strongestPattern.direction]?.text || 'text-green-700'}`}>
                {directionLabels[strongestPattern.direction]}
              </div>
              <div className="text-xs text-muted-foreground">
                {Math.round(strongestPattern.alignmentRate)}% match
              </div>
            </div>
          )}

          {/* Weakest Pattern */}
          {weakestPattern && weakestPattern.alignmentRate < 50 && (
            <div className="bg-amber-50 rounded-xl p-3">
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="text-xs font-medium text-amber-700">Needs improvement</span>
              </div>
              <div className="font-bold text-amber-700">
                {directionLabels[weakestPattern.direction]}
              </div>
              <div className="text-xs text-muted-foreground">
                {Math.round(weakestPattern.alignmentRate)}% match
              </div>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="space-y-2">
          {insights.slice(0, 3).map((insight, index) => (
            <div 
              key={index}
              className={`flex items-start gap-2 p-3 rounded-lg ${
                insight.priority === 'positive' ? 'bg-green-50 border border-green-200' :
                insight.priority === 'warning' ? 'bg-amber-50 border border-amber-200' :
                'bg-white/60'
              }`}
              data-testid={`insight-${insight.type}`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                insight.priority === 'positive' ? 'bg-green-200' :
                insight.priority === 'warning' ? 'bg-amber-200' :
                'bg-violet-200'
              }`}>
                {insight.priority === 'positive' ? (
                  <svg className="w-3 h-3 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : insight.priority === 'warning' ? (
                  <svg className="w-3 h-3 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                  </svg>
                ) : (
                  <svg className="w-3 h-3 text-violet-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>
              <p className={`text-sm ${
                insight.priority === 'positive' ? 'text-green-800' :
                insight.priority === 'warning' ? 'text-amber-800' :
                'text-violet-800'
              }`}>
                {insight.text}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-4 text-center">
        Based on {followedCount} decisions that stemmed from recommendations
      </p>
    </section>
  );
}

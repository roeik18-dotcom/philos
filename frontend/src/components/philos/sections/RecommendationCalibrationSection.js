import { useMemo } from 'react';

// Hebrew labels
const directionLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', fill: '#6366f1' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', fill: '#9ca3af' }
};

// Calculate calibration weights from follow-through data
// Returns weights bounded between -5 and +5
export const calculateCalibrationWeights = (history) => {
  // Initialize base weights (0 = no calibration)
  const weights = {
    contribution: 0,
    recovery: 0,
    order: 0,
    harm: 0,
    avoidance: 0
  };

  if (!history || history.length === 0) {
    return { weights, hasData: false, insights: [] };
  }

  // Filter decisions that followed recommendations
  const followedDecisions = history.filter(d => d.followed_recommendation === true);
  const totalDecisions = history.length;
  const followedCount = followedDecisions.length;

  // Need at least 3 followed recommendations to calibrate
  if (followedCount < 3) {
    return { weights, hasData: false, insights: [] };
  }

  // Calculate follow rate and alignment by direction
  const directionStats = {};
  const positiveDirections = ['contribution', 'recovery', 'order'];

  positiveDirections.forEach(dir => {
    directionStats[dir] = {
      followCount: 0,
      alignedCount: 0,
      totalRecommended: 0
    };
  });

  // Count recommendations by direction
  followedDecisions.forEach(decision => {
    const recDir = decision.recommendation_direction;
    const actualTag = decision.value_tag;
    
    if (directionStats[recDir]) {
      directionStats[recDir].followCount++;
      directionStats[recDir].totalRecommended++;
      
      // Check if outcome aligned with recommendation
      if (recDir === actualTag) {
        directionStats[recDir].alignedCount++;
      }
    }
  });

  // Calculate calibration weights based on follow-through and alignment
  const insights = [];
  let strongestDir = null;
  let strongestWeight = -Infinity;
  let weakestDir = null;
  let weakestWeight = Infinity;

  positiveDirections.forEach(dir => {
    const stats = directionStats[dir];
    
    // Only calculate weight if this direction has been recommended at least once
    if (stats.totalRecommended >= 1) {
      // Calculate follow rate for this direction
      const followRate = stats.followCount / followedCount;
      
      // Calculate alignment rate for this direction
      const alignmentRate = stats.totalRecommended > 0 
        ? stats.alignedCount / stats.totalRecommended 
        : 0;

      // Calibration formula:
      // - High follow rate (>0.3) + High alignment (>0.5) = positive weight (+1 to +5)
      // - High follow rate + Low alignment (<0.3) = slight negative (-1 to -2)
      // - Low follow rate (<0.2) = slight negative (-1)
      
      let weight = 0;

      if (alignmentRate > 0.6) {
        // Strong alignment - significant boost
        weight = Math.round(alignmentRate * 5);
        insights.push({
          type: 'boost',
          direction: dir,
          text: `מסלולי ${directionLabels[dir]} קיבלו חיזוק בעקבות התאמה גבוהה לתוצאות בפועל (${Math.round(alignmentRate * 100)}%)`,
          priority: 'positive'
        });
      } else if (alignmentRate > 0.4) {
        // Moderate alignment - small boost
        weight = Math.round((alignmentRate - 0.3) * 5);
      } else if (alignmentRate < 0.3 && stats.totalRecommended >= 1) {
        // Weak alignment - reduce weight
        weight = -Math.round((0.3 - alignmentRate) * 5);
        if (stats.totalRecommended >= 2) {
          insights.push({
            type: 'reduce',
            direction: dir,
            text: `מסלולי ${directionLabels[dir]} מקבלים כרגע משקל נמוך יותר עקב פער בין המלצה לתוצאה (${Math.round(alignmentRate * 100)}% התאמה)`,
            priority: 'warning'
          });
        }
      }

      // Adjust based on follow rate
      if (followRate > 0.4 && weight > 0) {
        // High follow rate amplifies positive weight
        weight = Math.min(5, weight + 1);
      } else if (followRate < 0.2 && stats.totalRecommended >= 1) {
        // Low follow rate suggests less engagement
        weight = Math.max(-3, weight - 1);
      }

      // Bound weights between -5 and +5
      weights[dir] = Math.max(-5, Math.min(5, weight));

      // Track strongest and weakest
      if (weights[dir] > strongestWeight) {
        strongestWeight = weights[dir];
        strongestDir = dir;
      }
      if (weights[dir] < weakestWeight) {
        weakestWeight = weights[dir];
        weakestDir = dir;
      }
    }
  });

  // Add summary insight if significant calibration exists
  const hasSignificantCalibration = Object.values(weights).some(w => Math.abs(w) >= 2);
  if (hasSignificantCalibration && strongestDir && strongestDir !== weakestDir) {
    insights.push({
      type: 'summary',
      text: `הכיול הנוכחי מעדיף ${directionLabels[strongestDir]} על פני ${directionLabels[weakestDir]}`,
      priority: 'info'
    });
  }

  return {
    weights,
    hasData: true,
    insights: insights.slice(0, 3),
    strongestDir,
    weakestDir,
    directionStats
  };
};

export default function RecommendationCalibrationSection({ history }) {
  // Calculate calibration weights
  const calibration = useMemo(() => {
    return calculateCalibrationWeights(history);
  }, [history]);

  // Don't render if not enough data
  if (!calibration.hasData) {
    return null;
  }

  const { weights, insights, strongestDir, weakestDir, directionStats } = calibration;

  // Prepare data for visualization
  const weightEntries = Object.entries(weights)
    .filter(([dir]) => ['contribution', 'recovery', 'order'].includes(dir))
    .sort((a, b) => b[1] - a[1]);

  const maxAbsWeight = Math.max(...Object.values(weights).map(Math.abs), 1);

  return (
    <section 
      className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-5 shadow-sm border border-amber-200"
      dir="rtl"
      data-testid="recommendation-calibration-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">כיול המלצות</h3>
          <p className="text-xs text-muted-foreground">
            התאמת משקלים בהתבסס על תוצאות בפועל
          </p>
        </div>
      </div>

      {/* Calibrated Weights Visualization */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <h4 className="text-sm font-medium text-foreground mb-3">משקלים מכוילים</h4>
        <svg width="100%" height="100" viewBox="0 0 300 100" data-testid="calibration-chart">
          {weightEntries.map(([direction, weight], index) => {
            const y = index * 32 + 10;
            const colors = directionColors[direction] || directionColors.recovery;
            const stats = directionStats[direction] || {};
            
            // Calculate bar width (center at 150, extend left for negative, right for positive)
            const barWidth = Math.abs(weight) / maxAbsWeight * 60;
            const barX = weight >= 0 ? 150 : 150 - barWidth;
            
            return (
              <g key={direction} transform={`translate(0, ${y})`}>
                {/* Direction label */}
                <text x="55" y="12" textAnchor="end" className="text-xs fill-current" style={{ fontSize: '11px' }}>
                  {directionLabels[direction]}
                </text>
                
                {/* Center line */}
                <line x1="150" y1="0" x2="150" y2="20" stroke="#d1d5db" strokeWidth="1" />
                
                {/* Background track */}
                <rect x="90" y="4" width="120" height="12" fill="#f3f4f6" rx="2" />
                
                {/* Weight bar */}
                {weight !== 0 && (
                  <rect 
                    x={barX} 
                    y="4" 
                    width={barWidth} 
                    height="12" 
                    fill={weight > 0 ? colors.fill : '#f59e0b'}
                    rx="2"
                    opacity={0.8}
                  />
                )}
                
                {/* Weight value */}
                <text x="225" y="12" className="text-xs fill-current" style={{ fontSize: '10px' }}>
                  {weight > 0 ? `+${weight}` : weight}
                  {stats.totalRecommended > 0 && ` (${stats.alignedCount}/${stats.totalRecommended})`}
                </text>
              </g>
            );
          })}
          
          {/* Legend */}
          <g transform="translate(0, 90)">
            <text x="90" y="0" className="text-xs fill-current" style={{ fontSize: '9px', fill: '#9ca3af' }}>
              ← החלשה
            </text>
            <text x="150" y="0" textAnchor="middle" className="text-xs fill-current" style={{ fontSize: '9px', fill: '#9ca3af' }}>
              בסיס
            </text>
            <text x="210" y="0" textAnchor="end" className="text-xs fill-current" style={{ fontSize: '9px', fill: '#9ca3af' }}>
              חיזוק →
            </text>
          </g>
        </svg>
      </div>

      {/* Strongest and Weakest */}
      {(strongestDir || weakestDir) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {/* Strongest Calibrated */}
          {strongestDir && weights[strongestDir] > 0 && (
            <div className={`${directionColors[strongestDir]?.bg || 'bg-green-100'} rounded-xl p-3`}>
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span className="text-xs font-medium text-green-700">הכי מחוזק</span>
              </div>
              <div className={`font-bold ${directionColors[strongestDir]?.text || 'text-green-700'}`}>
                {directionLabels[strongestDir]}
              </div>
              <div className="text-xs text-muted-foreground">
                +{weights[strongestDir]} משקל
              </div>
            </div>
          )}

          {/* Weakest Calibrated */}
          {weakestDir && weights[weakestDir] < 0 && (
            <div className="bg-amber-100 rounded-xl p-3">
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
                <span className="text-xs font-medium text-amber-700">מופחת</span>
              </div>
              <div className="font-bold text-amber-700">
                {directionLabels[weakestDir]}
              </div>
              <div className="text-xs text-muted-foreground">
                {weights[weakestDir]} משקל
              </div>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="space-y-2">
          {insights.map((insight, index) => (
            <div 
              key={index}
              className={`flex items-start gap-2 p-3 rounded-lg ${
                insight.priority === 'positive' ? 'bg-green-50 border border-green-200' :
                insight.priority === 'warning' ? 'bg-amber-50 border border-amber-200' :
                'bg-white/60'
              }`}
              data-testid={`calibration-insight-${insight.type}`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                insight.priority === 'positive' ? 'bg-green-200' :
                insight.priority === 'warning' ? 'bg-amber-200' :
                'bg-amber-100'
              }`}>
                {insight.priority === 'positive' ? (
                  <svg className="w-3 h-3 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                ) : insight.priority === 'warning' ? (
                  <svg className="w-3 h-3 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                ) : (
                  <svg className="w-3 h-3 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>
              <p className={`text-sm ${
                insight.priority === 'positive' ? 'text-green-800' :
                insight.priority === 'warning' ? 'text-amber-800' :
                'text-amber-800'
              }`}>
                {insight.text}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <p className="text-xs text-muted-foreground mt-4 text-center">
        הכיול מתבצע אוטומטית בהתבסס על ביצועי ההמלצות
      </p>
    </section>
  );
}

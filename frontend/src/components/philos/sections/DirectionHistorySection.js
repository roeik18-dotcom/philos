import { useState, useMemo } from 'react';

// Direction colors
const directionColors = {
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', fill: '#6366f1' },
  contribution: { bg: 'bg-green-100', text: 'text-green-700', fill: '#22c55e' },
  exploration: { bg: 'bg-amber-100', text: 'text-amber-700', fill: '#f59e0b' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', fill: '#9ca3af' }
};

// Hebrew labels
const directionLabels = {
  recovery: 'התאוששות',
  order: 'סדר',
  contribution: 'תרומה',
  exploration: 'חקירה',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Timeframe options
const timeframes = [
  { id: 'today', label: 'היום', days: 1 },
  { id: 'week', label: '7 ימים', days: 7 },
  { id: 'all', label: 'הכל', days: 9999 }
];

// Pattern detection functions
const detectPatterns = (movements) => {
  const patterns = [];
  
  if (movements.length < 3) return patterns;

  // Count direction occurrences
  const directionCounts = {};
  movements.forEach(m => {
    directionCounts[m.to] = (directionCounts[m.to] || 0) + 1;
  });

  // Find dominant direction
  const sortedDirections = Object.entries(directionCounts)
    .sort((a, b) => b[1] - a[1]);
  
  if (sortedDirections.length > 0) {
    const [dominant, count] = sortedDirections[0];
    if (count >= 3) {
      patterns.push({
        type: 'tendency',
        text: `אתה נוטה לנוע לכיוון ${directionLabels[dominant] || dominant}.`,
        priority: 'info'
      });
    }
  }

  // Detect transition patterns (e.g., harm → recovery)
  const transitionCounts = {};
  for (let i = 0; i < movements.length - 1; i++) {
    const key = `${movements[i].to}→${movements[i + 1].to}`;
    transitionCounts[key] = (transitionCounts[key] || 0) + 1;
  }

  const repeatedTransitions = Object.entries(transitionCounts)
    .filter(([_, count]) => count >= 2)
    .sort((a, b) => b[1] - a[1]);

  if (repeatedTransitions.length > 0) {
    const [transition, count] = repeatedTransitions[0];
    const [from, to] = transition.split('→');
    patterns.push({
      type: 'transition',
      text: `יש חזרתיות ב${directionLabels[from] || from} ולאחריה ${directionLabels[to] || to}.`,
      priority: 'warning'
    });
  }

  // Detect positive momentum
  const positiveDirections = ['contribution', 'recovery', 'order', 'exploration'];
  const recentPositive = movements.slice(0, 5).filter(m => 
    positiveDirections.includes(m.to)
  ).length;

  if (recentPositive >= 4) {
    patterns.push({
      type: 'momentum',
      text: 'נראה מעבר מתמשך לכיוון חיובי.',
      priority: 'positive'
    });
  }

  // Detect negative drift
  const negativeDirections = ['harm', 'avoidance'];
  const recentNegative = movements.slice(0, 5).filter(m => 
    negativeDirections.includes(m.to)
  ).length;

  if (recentNegative >= 3) {
    patterns.push({
      type: 'drift',
      text: 'זוהה דפוס של נטייה שלילית. מומלץ לשקול כיוון מאזן.',
      priority: 'warning'
    });
  }

  return patterns.slice(0, 3); // Max 3 patterns
};

export default function DirectionHistorySection({ history }) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');

  // Filter history by timeframe
  const filteredHistory = useMemo(() => {
    if (!history || history.length === 0) return [];

    const timeframe = timeframes.find(t => t.id === selectedTimeframe);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - timeframe.days);

    return history.filter(h => {
      if (!h.timestamp) return true;
      return new Date(h.timestamp) >= cutoffDate;
    });
  }, [history, selectedTimeframe]);

  // Calculate direction movements
  const movements = useMemo(() => {
    if (filteredHistory.length < 2) return [];

    const result = [];
    for (let i = filteredHistory.length - 1; i > 0; i--) {
      const from = filteredHistory[i];
      const to = filteredHistory[i - 1];
      result.push({
        from: from.value_tag,
        to: to.value_tag,
        timestamp: to.timestamp,
        action: to.action?.substring(0, 30)
      });
    }
    return result.reverse(); // Most recent first
  }, [filteredHistory]);

  // Detect patterns
  const patterns = useMemo(() => {
    return detectPatterns(movements);
  }, [movements]);

  // Calculate direction distribution
  const distribution = useMemo(() => {
    const counts = {};
    filteredHistory.forEach(h => {
      if (h.value_tag) {
        counts[h.value_tag] = (counts[h.value_tag] || 0) + 1;
      }
    });
    
    const total = filteredHistory.length || 1;
    return Object.entries(counts)
      .map(([direction, count]) => ({
        direction,
        count,
        percentage: Math.round((count / total) * 100)
      }))
      .sort((a, b) => b.count - a.count);
  }, [filteredHistory]);

  // Calculate compass trail positions
  const trailPositions = useMemo(() => {
    const positions = {
      recovery: { x: 25, y: 75 },
      order: { x: 25, y: 25 },
      contribution: { x: 75, y: 25 },
      exploration: { x: 75, y: 75 },
      harm: { x: 15, y: 85 },
      avoidance: { x: 50, y: 90 }
    };

    return filteredHistory.slice(0, 10).map((h, idx) => ({
      ...positions[h.value_tag] || { x: 50, y: 50 },
      valueTag: h.value_tag,
      opacity: Math.max(0.2, 1 - (idx * 0.08))
    }));
  }, [filteredHistory]);

  return (
    <section 
      className="bg-white rounded-3xl p-6 shadow-sm border border-border"
      dir="rtl"
      data-testid="direction-history-section"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">היסטוריית כיוונים</h3>
          <p className="text-xs text-muted-foreground">תנועה בין כיוונים לאורך זמן</p>
        </div>
        
        {/* Timeframe Selector */}
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
          {timeframes.map(tf => (
            <button
              key={tf.id}
              onClick={() => setSelectedTimeframe(tf.id)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                selectedTimeframe === tf.id
                  ? 'bg-white text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              data-testid={`timeframe-${tf.id}`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Trail Compass Mini */}
      {trailPositions.length > 0 && (
        <div className="relative w-full aspect-square max-w-[200px] mx-auto mb-4 bg-gray-50 rounded-xl border border-gray-200">
          {/* Axes */}
          <div className="absolute top-1/2 left-0 right-0 h-px bg-gray-200"></div>
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-200"></div>
          
          {/* Trail */}
          <svg className="absolute inset-0 w-full h-full">
            {/* Trail line */}
            {trailPositions.length > 1 && (
              <polyline
                points={trailPositions.map(p => `${p.x}%,${p.y}%`).join(' ')}
                fill="none"
                stroke="#9ca3af"
                strokeWidth="1.5"
                strokeDasharray="4,2"
                opacity="0.6"
              />
            )}
            {/* Trail dots */}
            {trailPositions.map((pos, idx) => (
              <circle
                key={idx}
                cx={`${pos.x}%`}
                cy={`${pos.y}%`}
                r={idx === 0 ? 6 : 4}
                fill={directionColors[pos.valueTag]?.fill || '#9ca3af'}
                opacity={pos.opacity}
                stroke={idx === 0 ? 'white' : 'none'}
                strokeWidth={idx === 0 ? 2 : 0}
              />
            ))}
          </svg>
          
          {/* Quadrant Labels */}
          <span className="absolute top-[10%] left-[10%] text-[8px] text-gray-400">סדר</span>
          <span className="absolute top-[10%] right-[10%] text-[8px] text-gray-400">תרומה</span>
          <span className="absolute bottom-[10%] left-[10%] text-[8px] text-gray-400">התאוששות</span>
          <span className="absolute bottom-[10%] right-[10%] text-[8px] text-gray-400">חקירה</span>
        </div>
      )}

      {/* Patterns */}
      {patterns.length > 0 && (
        <div className="mb-4 space-y-2">
          {patterns.map((pattern, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl text-sm ${
                pattern.priority === 'positive' 
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : pattern.priority === 'warning'
                  ? 'bg-amber-50 text-amber-700 border border-amber-200'
                  : 'bg-blue-50 text-blue-700 border border-blue-200'
              }`}
              data-testid={`pattern-${pattern.type}`}
            >
              {pattern.text}
            </div>
          ))}
        </div>
      )}

      {/* Distribution */}
      {distribution.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-muted-foreground mb-2">התפלגות כיוונים</p>
          <div className="space-y-2">
            {distribution.slice(0, 4).map(({ direction, count, percentage }) => (
              <div key={direction} className="flex items-center gap-2">
                <span 
                  className={`px-2 py-0.5 rounded text-xs font-medium ${directionColors[direction]?.bg} ${directionColors[direction]?.text}`}
                >
                  {directionLabels[direction] || direction}
                </span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: directionColors[direction]?.fill || '#9ca3af'
                    }}
                  ></div>
                </div>
                <span className="text-xs text-muted-foreground w-8">{percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Movement Timeline */}
      {movements.length > 0 && (
        <div>
          <p className="text-xs text-muted-foreground mb-2">מעברים אחרונים</p>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {movements.slice(0, 8).map((movement, idx) => (
              <div 
                key={idx}
                className="flex items-center gap-2 text-xs p-2 rounded-lg bg-gray-50"
              >
                <span 
                  className={`px-2 py-0.5 rounded ${directionColors[movement.from]?.bg} ${directionColors[movement.from]?.text}`}
                >
                  {directionLabels[movement.from] || movement.from}
                </span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span 
                  className={`px-2 py-0.5 rounded ${directionColors[movement.to]?.bg} ${directionColors[movement.to]?.text}`}
                >
                  {directionLabels[movement.to] || movement.to}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredHistory.length < 2 && (
        <div className="text-center py-6">
          <p className="text-sm text-muted-foreground">אין מספיק נתונים להצגת היסטוריה.</p>
          <p className="text-xs text-muted-foreground mt-1">בצע מספר פעולות כדי לראות דפוסים.</p>
        </div>
      )}
    </section>
  );
}

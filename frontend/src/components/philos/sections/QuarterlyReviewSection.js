import { useMemo } from 'react';

// Hebrew value labels
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Value categories
const positiveValues = ['contribution', 'recovery', 'order'];
const negativeValues = ['harm', 'avoidance'];

// Category colors
const categoryColors = {
  recovery: '#22c55e',
  harm: '#ef4444',
  correction: '#3b82f6',
  growth: '#10b981',
  warning: '#f59e0b'
};

// Category labels
const categoryLabels = {
  recovery: 'Recovery',
  harm: 'Harm',
  correction: 'Correction',
  growth: 'Growth',
  warning: 'Warning'
};

// Month names in Hebrew
const hebrewMonths = ['Month 1', 'Month 2', 'Month 3'];

export default function QuarterlyReviewSection({ history }) {
  // Calculate quarterly report with monthly breakdown
  const reportData = useMemo(() => {
    if (!history || history.length === 0) return null;

    const now = new Date();
    const months = [];

    // Create 3 month periods (each ~30 days)
    for (let m = 0; m < 3; m++) {
      const monthEnd = new Date(now.getTime() - m * 30 * 24 * 60 * 60 * 1000);
      const monthStart = new Date(monthEnd.getTime() - 30 * 24 * 60 * 60 * 1000);
      months.push({ start: monthStart, end: monthEnd, index: 2 - m });
    }
    months.reverse();

    // Analyze chains for each month
    const monthlyStats = months.map(month => {
      const monthHistory = history.filter(item => {
        const itemDate = item.timestamp ? new Date(item.timestamp) : new Date();
        return itemDate >= month.start && itemDate < month.end;
      });

      if (monthHistory.length < 2) {
        return { 
          monthIndex: month.index,
          recovery: 0, harm: 0, correction: 0, growth: 0, warning: 0,
          totalChains: 0, totalDecisions: monthHistory.length,
          consistencyScore: 0
        };
      }

      // Build chains
      const items = monthHistory.map((item, idx) => ({
        ...item,
        id: item.id || `node_${idx}`
      }));

      const nodeMap = {};
      items.forEach(item => {
        nodeMap[item.id] = { ...item, children: [] };
      });

      const roots = [];
      items.forEach(item => {
        if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
          nodeMap[item.parent_decision_id].children.push(nodeMap[item.id]);
        } else {
          roots.push(nodeMap[item.id]);
        }
      });

      const chains = [];
      const extractChains = (node, currentChain = []) => {
        const newChain = [...currentChain, node];
        if (!node.children || node.children.length === 0) {
          if (newChain.length >= 2) chains.push(newChain);
        } else {
          node.children.forEach(child => extractChains(child, newChain));
        }
      };
      roots.forEach(root => extractChains(root));

      if (chains.length === 0) {
        items.forEach(item => {
          if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
            chains.push([nodeMap[item.parent_decision_id], nodeMap[item.id]]);
          }
        });
      }

      // Analyze
      const stats = { recovery: 0, harm: 0, correction: 0, growth: 0, warning: 0 };

      chains.forEach(chain => {
        const values = chain.map(n => n.value_tag);
        const firstValue = values[0];
        const lastValue = values[values.length - 1];

        if (negativeValues.includes(firstValue) && positiveValues.includes(lastValue)) {
          stats.recovery++;
        }
        if (positiveValues.includes(firstValue) && negativeValues.includes(lastValue)) {
          stats.harm++;
        }
        for (let i = 1; i < values.length - 1; i++) {
          if (negativeValues.includes(values[i]) && positiveValues.includes(values[i + 1])) {
            stats.correction++;
            break;
          }
        }
        if (values.every(v => positiveValues.includes(v)) && chain.length >= 2) {
          stats.growth++;
        }
        if (values.every(v => negativeValues.includes(v)) && chain.length >= 2) {
          stats.warning++;
        }
      });

      // Calculate consistency score (ratio of positive to total)
      const positiveCount = stats.recovery + stats.growth + stats.correction;
      const negativeCount = stats.harm + stats.warning;
      const total = positiveCount + negativeCount || 1;
      const consistencyScore = Math.round((positiveCount / total) * 100);

      return {
        monthIndex: month.index,
        ...stats,
        totalChains: chains.length,
        totalDecisions: monthHistory.length,
        consistencyScore
      };
    });

    // Check if we have meaningful data
    const hasData = monthlyStats.some(m => m.totalChains > 0);
    if (!hasData) return null;

    // Calculate quarterly trends
    const sumStats = (months, key) => months.reduce((s, m) => s + m[key], 0);

    const quarterlyTotals = {
      recovery: sumStats(monthlyStats, 'recovery'),
      harm: sumStats(monthlyStats, 'harm'),
      correction: sumStats(monthlyStats, 'correction'),
      growth: sumStats(monthlyStats, 'growth'),
      warning: sumStats(monthlyStats, 'warning')
    };

    // Calculate month-over-month changes
    const monthlyChanges = [];
    for (let i = 1; i < monthlyStats.length; i++) {
      const prev = monthlyStats[i - 1];
      const curr = monthlyStats[i];
      monthlyChanges.push({
        recovery: curr.recovery - prev.recovery,
        harm: curr.harm - prev.harm,
        correction: curr.correction - prev.correction,
        growth: curr.growth - prev.growth,
        warning: curr.warning - prev.warning
      });
    }

    // Find consistent improvements (positive change in both transitions)
    const consistentImprovement = ['recovery', 'growth', 'correction'].find(key =>
      monthlyChanges.every(change => change[key] >= 0) && 
      monthlyChanges.some(change => change[key] > 0)
    );

    // Find consistent risks (increase in negative patterns)
    const consistentRisk = ['harm', 'warning'].find(key =>
      monthlyChanges.every(change => change[key] >= 0) && 
      monthlyChanges.some(change => change[key] > 0)
    );

    // Determine dominant quarterly pattern
    const dominantCategory = Object.entries(quarterlyTotals)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || 'recovery';

    // Calculate stability metrics
    const recoveryStability = monthlyStats.every(m => m.recovery > 0) ? 'stable' :
      monthlyStats.filter(m => m.recovery > 0).length >= 2 ? 'improving' : 'unstable';

    const correctionConsistency = monthlyStats.filter(m => m.correction > 0).length;

    // Generate insights
    const insights = [];

    // Recovery stability
    if (recoveryStability === 'stable') {
      insights.push('Last quarter saw consistent recovery stability built');
    } else if (recoveryStability === 'improving') {
      insights.push('Recovery patterns are getting stronger');
    }

    // Harm trend
    const harmTrend = monthlyStats[2].harm - monthlyStats[0].harm;
    if (harmTrend < 0) {
      insights.push('A continued decrease in harm patterns is observed');
    } else if (harmTrend > 0) {
      insights.push('There is an increase in harm patterns over the quarter — a point of attention');
    }

    // Correction consistency
    if (correctionConsistency >= 2) {
      insights.push('Correction patterns have become a stable part of behavior');
    }

    // Growth pattern
    const growthTrend = monthlyStats[2].growth - monthlyStats[0].growth;
    if (growthTrend > 0) {
      insights.push('Growth streaks have become more frequent');
    }

    // Overall assessment
    const positiveTotal = quarterlyTotals.recovery + quarterlyTotals.growth + quarterlyTotals.correction;
    const negativeTotal = quarterlyTotals.harm + quarterlyTotals.warning;

    if (positiveTotal > negativeTotal * 2) {
      insights.push('The quarter ends with a clear positive trend');
    } else if (negativeTotal > positiveTotal) {
      insights.push('There is room for improvement — the next quarter can be better');
    }

    // Consistency trend
    const avgConsistency = Math.round(monthlyStats.reduce((s, m) => s + m.consistencyScore, 0) / 3);

    return {
      monthlyStats,
      quarterlyTotals,
      monthlyChanges,
      dominantCategory,
      consistentImprovement,
      consistentRisk,
      recoveryStability,
      correctionConsistency,
      insights: insights.slice(0, 4),
      avgConsistency,
      totalDecisions: monthlyStats.reduce((s, m) => s + m.totalDecisions, 0),
      totalChains: monthlyStats.reduce((s, m) => s + m.totalChains, 0)
    };
  }, [history]);

  // Check if we have chains
  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id || 
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  if (!hasChains || !reportData) return null;

  const { 
    monthlyStats, quarterlyTotals, dominantCategory, 
    consistentImprovement, consistentRisk, recoveryStability,
    correctionConsistency, insights, avgConsistency,
    totalDecisions, totalChains 
  } = reportData;

  // Get max for scaling
  const maxMonthlyTotal = Math.max(
    ...monthlyStats.map(m => m.recovery + m.harm + m.correction + m.growth + m.warning),
    1
  );

  return (
    <section 
      className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-3xl p-5 shadow-sm border border-indigo-200"
      data-testid="quarterly-review-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">Quarterly Review</h3>
        <p className="text-xs text-muted-foreground">Behavioral trends from the last 3 months</p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-2 mb-4">
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-lg font-bold text-indigo-600">{totalDecisions}</p>
          <p className="text-[10px] text-muted-foreground">decisions</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-lg font-bold text-indigo-600">{totalChains}</p>
          <p className="text-[10px] text-muted-foreground">chains</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-lg font-bold text-indigo-600">3</p>
          <p className="text-[10px] text-muted-foreground">months</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-lg font-bold text-indigo-600">{avgConsistency}%</p>
          <p className="text-[10px] text-muted-foreground">Consistency</p>
        </div>
      </div>

      {/* Monthly trend visualization - Line chart style */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <p className="text-xs text-muted-foreground mb-3">Monthly trend</p>
        
        <svg width="100%" height="160" className="block" style={{ direction: 'ltr' }}>
          {/* Grid */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={`grid-${i}`}
              x1="50"
              y1={20 + i * 28}
              x2="95%"
              y2={20 + i * 28}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}

          {/* Area fills for each category */}
          {Object.entries(categoryColors).map(([category, color]) => {
            const points = monthlyStats.map((m, idx) => {
              const x = 70 + idx * 100;
              const y = 130 - (m[category] / maxMonthlyTotal) * 100;
              return `${x},${y}`;
            });
            
            const areaPoints = [
              `70,130`,
              ...points,
              `${70 + (monthlyStats.length - 1) * 100},130`
            ].join(' ');

            return (
              <polygon
                key={`area-${category}`}
                points={areaPoints}
                fill={color}
                fillOpacity="0.1"
              />
            );
          })}

          {/* Lines for each category */}
          {Object.entries(categoryColors).map(([category, color]) => {
            const points = monthlyStats.map((m, idx) => {
              const x = 70 + idx * 100;
              const y = 130 - (m[category] / maxMonthlyTotal) * 100;
              return `${x},${y}`;
            }).join(' ');

            return (
              <polyline
                key={`line-${category}`}
                points={points}
                fill="none"
                stroke={color}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            );
          })}

          {/* Data points */}
          {Object.entries(categoryColors).map(([category, color]) => (
            monthlyStats.map((m, idx) => {
              const x = 70 + idx * 100;
              const y = 130 - (m[category] / maxMonthlyTotal) * 100;
              if (m[category] === 0) return null;
              return (
                <circle
                  key={`point-${category}-${idx}`}
                  cx={x}
                  cy={y}
                  r="4"
                  fill={color}
                  stroke="white"
                  strokeWidth="2"
                />
              );
            })
          ))}

          {/* Month labels */}
          {hebrewMonths.map((label, idx) => (
            <text
              key={`label-${idx}`}
              x={70 + idx * 100}
              y="152"
              textAnchor="middle"
              fontSize="10"
              fill="#666"
            >
              {label}
            </text>
          ))}

          {/* Y-axis label */}
          <text x="20" y="80" fontSize="9" fill="#999" transform="rotate(-90, 20, 80)">chains</text>
        </svg>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mt-2 text-xs justify-center">
          {Object.entries(categoryColors).map(([key, color]) => (
            <div key={key} className="flex items-center gap-1">
              <div className="w-3 h-0.5 rounded" style={{ backgroundColor: color }} />
              <span>{categoryLabels[key]}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Quarterly totals */}
      <div className="grid grid-cols-5 gap-2 mb-4">
        {Object.entries(quarterlyTotals).map(([key, value]) => (
          <div 
            key={key}
            className="rounded-lg p-2 text-center bg-white/60"
          >
            <div 
              className="w-6 h-6 rounded-full mx-auto mb-1 flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: categoryColors[key] }}
            >
              {value}
            </div>
            <p className="text-[9px] text-muted-foreground">{categoryLabels[key]}</p>
          </div>
        ))}
      </div>

      {/* Dominant pattern & stability */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/80 rounded-xl p-3 border border-indigo-100">
          <div className="flex items-center gap-2">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg"
              style={{ backgroundColor: categoryColors[dominantCategory] }}
            >
              {dominantCategory === 'recovery' && '🌱'}
              {dominantCategory === 'harm' && '⚠️'}
              {dominantCategory === 'correction' && '🔄'}
              {dominantCategory === 'growth' && '📈'}
              {dominantCategory === 'warning' && '🔻'}
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Dominant pattern</p>
              <p className="font-semibold text-sm">{categoryLabels[dominantCategory]}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 rounded-xl p-3 border border-indigo-100">
          <div className="flex items-center gap-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
              recoveryStability === 'stable' ? 'bg-green-100 text-green-600' :
              recoveryStability === 'improving' ? 'bg-blue-100 text-blue-600' :
              'bg-gray-100 text-gray-600'
            }`}>
              {recoveryStability === 'stable' && '✓'}
              {recoveryStability === 'improving' && '↑'}
              {recoveryStability === 'unstable' && '~'}
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Recovery Stability</p>
              <p className="font-semibold text-sm">
                {recoveryStability === 'stable' && 'Stable'}
                {recoveryStability === 'improving' && 'Improving'}
                {recoveryStability === 'unstable' && 'Not stable'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Consistent patterns */}
      {(consistentImprovement || consistentRisk) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {consistentImprovement && (
            <div className="bg-green-50 rounded-xl p-3 border border-green-200">
              <p className="text-xs text-green-600 font-medium mb-1">Consistent improvement</p>
              <p className="text-sm font-semibold text-green-700">
                {categoryLabels[consistentImprovement]}
              </p>
              <p className="text-xs text-green-600">Consistent increase over the quarter</p>
            </div>
          )}
          {consistentRisk && (
            <div className="bg-red-50 rounded-xl p-3 border border-red-200">
              <p className="text-xs text-red-600 font-medium mb-1">Risk point</p>
              <p className="text-sm font-semibold text-red-700">
                {categoryLabels[consistentRisk]}
              </p>
              <p className="text-xs text-red-600">Consistent increase — recommended to address</p>
            </div>
          )}
        </div>
      )}

      {/* Correction consistency indicator */}
      <div className="bg-white/60 rounded-xl p-3 mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-muted-foreground">Correction consistency</span>
          <span className="text-xs font-medium">{correctionConsistency}/3 months</span>
        </div>
        <div className="flex gap-1">
          {[0, 1, 2].map(i => (
            <div 
              key={i}
              className={`flex-1 h-2 rounded-full ${
                monthlyStats[i]?.correction > 0 ? 'bg-blue-500' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Insights */}
      {insights.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">Quarterly insights</p>
          {insights.map((insight, idx) => (
            <div 
              key={idx}
              className="bg-white/60 rounded-lg px-3 py-2 text-sm flex items-center gap-2"
            >
              <span className="text-indigo-500">●</span>
              <span>{insight}</span>
            </div>
          ))}
        </div>
      )}

      {/* Overall progress indicator */}
      <div className="mt-4 pt-3 border-t border-indigo-200">
        <div className="flex justify-between text-xs text-muted-foreground mb-2">
          <span>Overall quarterly trend</span>
          <span>{avgConsistency}% Positive</span>
        </div>
        <div className="h-4 bg-gray-200 rounded-full overflow-hidden flex">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all"
            style={{ width: `${avgConsistency}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] mt-1 text-muted-foreground">
          <span>0%</span>
          <span>100%</span>
        </div>
      </div>
    </section>
  );
}

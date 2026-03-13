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

export default function MonthlyProgressReportSection({ history }) {
  // Calculate monthly report with weekly breakdown
  const reportData = useMemo(() => {
    if (!history || history.length === 0) return null;

    const now = new Date();
    const weeks = [];

    // Create 4 week periods
    for (let w = 0; w < 4; w++) {
      const weekEnd = new Date(now.getTime() - w * 7 * 24 * 60 * 60 * 1000);
      const weekStart = new Date(weekEnd.getTime() - 7 * 24 * 60 * 60 * 1000);
      weeks.push({ start: weekStart, end: weekEnd, index: 3 - w }); // Reverse so week 0 is oldest
    }
    weeks.reverse();

    // Analyze chains for each week
    const weeklyStats = weeks.map(week => {
      const weekHistory = history.filter(item => {
        const itemDate = item.timestamp ? new Date(item.timestamp) : new Date();
        return itemDate >= week.start && itemDate < week.end;
      });

      if (weekHistory.length < 2) {
        return { 
          weekIndex: week.index,
          recovery: 0, harm: 0, correction: 0, growth: 0, warning: 0,
          totalChains: 0, totalDecisions: weekHistory.length
        };
      }

      // Build chains for this week
      const items = weekHistory.map((item, idx) => ({
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

      return {
        weekIndex: week.index,
        ...stats,
        totalChains: chains.length,
        totalDecisions: weekHistory.length
      };
    });

    // Check if we have meaningful data
    const hasData = weeklyStats.some(w => w.totalChains > 0);
    if (!hasData) return null;

    // Calculate trends (compare first half vs second half of month)
    const firstHalf = weeklyStats.slice(0, 2);
    const secondHalf = weeklyStats.slice(2, 4);

    const sumStats = (weeks, key) => weeks.reduce((s, w) => s + w[key], 0);

    const trends = {
      recovery: sumStats(secondHalf, 'recovery') - sumStats(firstHalf, 'recovery'),
      harm: sumStats(secondHalf, 'harm') - sumStats(firstHalf, 'harm'),
      correction: sumStats(secondHalf, 'correction') - sumStats(firstHalf, 'correction'),
      growth: sumStats(secondHalf, 'growth') - sumStats(firstHalf, 'growth'),
      warning: sumStats(secondHalf, 'warning') - sumStats(firstHalf, 'warning')
    };

    // Find dominant monthly pattern
    const totals = {
      recovery: sumStats(weeklyStats, 'recovery'),
      harm: sumStats(weeklyStats, 'harm'),
      correction: sumStats(weeklyStats, 'correction'),
      growth: sumStats(weeklyStats, 'growth'),
      warning: sumStats(weeklyStats, 'warning')
    };

    const dominantCategory = Object.entries(totals)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || 'recovery';

    // Find strongest shifts
    const positiveShifts = ['recovery', 'growth', 'correction']
      .map(key => ({ key, change: trends[key] }))
      .filter(s => s.change > 0)
      .sort((a, b) => b.change - a.change);

    const negativeShifts = ['harm', 'warning']
      .map(key => ({ key, change: trends[key] }))
      .filter(s => s.change > 0)
      .sort((a, b) => b.change - a.change);

    // Generate insights
    const insights = [];

    // Recovery trend
    if (trends.recovery > 0) {
      insights.push(`Last month showed an increase in recovery chains (+${trends.recovery})`);
    } else if (trends.recovery < 0) {
      insights.push(`A decrease in recovery chains was recorded (${trends.recovery})`);
    }

    // Harm trend
    if (trends.harm < 0) {
      insights.push(`A consistent decrease in harm patterns appears (${trends.harm})`);
    } else if (trends.harm > 0) {
      insights.push(`There is an increase in harm patterns — pay attention (+${trends.harm})`);
    }

    // Correction trend
    if (trends.correction > 0) {
      insights.push(`Correction patterns became more frequent over the month (+${trends.correction})`);
    }

    // Growth trend
    if (trends.growth > 0) {
      insights.push(`There is an increase in positive growth streaks (+${trends.growth})`);
    }

    // Warning trend
    if (trends.warning > 0) {
      insights.push(`There are more warning chains — recommended to address (+${trends.warning})`);
    } else if (trends.warning < 0) {
      insights.push(`Fewer warning chains than at the start of the month — progress!`);
    }

    // Overall assessment
    const positiveTotal = trends.recovery + trends.growth + trends.correction;
    const negativeTotal = trends.harm + trends.warning;

    if (positiveTotal > negativeTotal && positiveTotal > 0) {
      insights.push('Overall positive trend this month');
    } else if (negativeTotal > positiveTotal && negativeTotal > 0) {
      insights.push('Negative trend this month — opportunity for change');
    }

    return {
      weeklyStats,
      trends,
      totals,
      dominantCategory,
      positiveShifts,
      negativeShifts,
      insights: insights.slice(0, 4),
      totalDecisions: weeklyStats.reduce((s, w) => s + w.totalDecisions, 0),
      totalChains: weeklyStats.reduce((s, w) => s + w.totalChains, 0)
    };
  }, [history]);

  // Check if we have chains
  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id || 
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  if (!hasChains || !reportData) return null;

  const { weeklyStats, trends, totals, dominantCategory, positiveShifts, negativeShifts, insights, totalDecisions, totalChains } = reportData;

  // Get max value for scaling
  const maxWeeklyTotal = Math.max(
    ...weeklyStats.map(w => w.recovery + w.harm + w.correction + w.growth + w.warning),
    1
  );

  return (
    <section 
      className="bg-gradient-to-br from-rose-50 to-pink-50 rounded-3xl p-5 shadow-sm border border-rose-200"
      data-testid="monthly-progress-report-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">Monthly Progress Report</h3>
        <p className="text-xs text-muted-foreground">Behavioral trends from the last 4 weeks</p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-xl font-bold text-rose-600">{totalDecisions}</p>
          <p className="text-xs text-muted-foreground">decisions</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-xl font-bold text-rose-600">{totalChains}</p>
          <p className="text-xs text-muted-foreground">chains</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-xl font-bold text-rose-600">4</p>
          <p className="text-xs text-muted-foreground">weeks</p>
        </div>
      </div>

      {/* Weekly trend visualization */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <p className="text-xs text-muted-foreground mb-3">Weekly trend</p>
        
        <svg width="100%" height="140" className="block" style={{ direction: 'ltr' }}>
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={`grid-${i}`}
              x1="40"
              y1={20 + i * 25}
              x2="100%"
              y2={20 + i * 25}
              stroke="#f3f4f6"
              strokeWidth="1"
            />
          ))}

          {/* Week labels */}
          {['Week 1', 'Week 2', 'Week 3', 'Week 4'].map((label, idx) => (
            <text
              key={`label-${idx}`}
              x={60 + idx * 70}
              y="135"
              textAnchor="middle"
              fontSize="9"
              fill="#666"
            >
              {label}
            </text>
          ))}

          {/* Stacked bars for each week */}
          {weeklyStats.map((week, weekIdx) => {
            const categories = ['recovery', 'growth', 'correction', 'harm', 'warning'];
            let currentY = 120;
            const barWidth = 50;
            const x = 35 + weekIdx * 70;
            const maxHeight = 100;

            return (
              <g key={`week-${weekIdx}`}>
                {categories.map(cat => {
                  const value = week[cat];
                  const height = maxWeeklyTotal > 0 ? (value / maxWeeklyTotal) * maxHeight : 0;
                  const y = currentY - height;
                  currentY = y;

                  if (height === 0) return null;

                  return (
                    <rect
                      key={`${weekIdx}-${cat}`}
                      x={x}
                      y={y}
                      width={barWidth}
                      height={height}
                      fill={categoryColors[cat]}
                      rx="2"
                    />
                  );
                })}
              </g>
            );
          })}

          {/* Y-axis label */}
          <text x="15" y="70" fontSize="9" fill="#999" transform="rotate(-90, 15, 70)">chains</text>
        </svg>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mt-2 text-xs justify-center">
          {Object.entries(categoryColors).map(([key, color]) => (
            <div key={key} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: color }} />
              <span>{categoryLabels[key]}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Trend indicators */}
      <div className="grid grid-cols-5 gap-2 mb-4">
        {Object.entries(trends).map(([key, value]) => {
          const isPositive = ['recovery', 'growth', 'correction'].includes(key);
          const isGood = isPositive ? value > 0 : value < 0;
          const isBad = isPositive ? value < 0 : value > 0;
          
          return (
            <div 
              key={key}
              className={`rounded-lg p-2 text-center ${
                isGood ? 'bg-green-50 border border-green-200' :
                isBad ? 'bg-red-50 border border-red-200' :
                'bg-gray-50 border border-gray-200'
              }`}
            >
              <p className="text-lg font-bold">
                {value > 0 ? `+${value}` : value}
              </p>
              <p className="text-[10px] text-muted-foreground">{categoryLabels[key]}</p>
            </div>
          );
        })}
      </div>

      {/* Dominant pattern */}
      <div className="bg-white/80 rounded-xl p-4 mb-4 border border-rose-100">
        <div className="flex items-center gap-3">
          <div 
            className="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl"
            style={{ backgroundColor: categoryColors[dominantCategory] }}
          >
            {dominantCategory === 'recovery' && '🌱'}
            {dominantCategory === 'harm' && '⚠️'}
            {dominantCategory === 'correction' && '🔄'}
            {dominantCategory === 'growth' && '📈'}
            {dominantCategory === 'warning' && '🔻'}
          </div>
          <div>
            <p className="font-semibold">Dominant pattern this month</p>
            <p className="text-sm text-muted-foreground">
              {categoryLabels[dominantCategory]} ({totals[dominantCategory]} chains)
            </p>
          </div>
        </div>
      </div>

      {/* Strongest shifts */}
      {(positiveShifts.length > 0 || negativeShifts.length > 0) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {positiveShifts.length > 0 && (
            <div className="bg-green-50 rounded-xl p-3 border border-green-200">
              <p className="text-xs text-green-600 font-medium mb-1">Strong improvement</p>
              <p className="text-sm font-semibold text-green-700">
                {categoryLabels[positiveShifts[0].key]}
              </p>
              <p className="text-xs text-green-600">+{positiveShifts[0].change} compared to the start of the month</p>
            </div>
          )}
          {negativeShifts.length > 0 && (
            <div className="bg-red-50 rounded-xl p-3 border border-red-200">
              <p className="text-xs text-red-600 font-medium mb-1">Area for improvement</p>
              <p className="text-sm font-semibold text-red-700">
                {categoryLabels[negativeShifts[0].key]}
              </p>
              <p className="text-xs text-red-600">+{negativeShifts[0].change} compared to the start of the month</p>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">Monthly insights</p>
          {insights.map((insight, idx) => (
            <div 
              key={idx}
              className="bg-white/60 rounded-lg px-3 py-2 text-sm flex items-center gap-2"
            >
              <span className="text-rose-500">●</span>
              <span>{insight}</span>
            </div>
          ))}
        </div>
      )}

      {/* Monthly progress bar */}
      <div className="mt-4 pt-3 border-t border-rose-200">
        <div className="flex justify-between text-xs text-muted-foreground mb-2">
          <span>Overall trend</span>
          <span>
            {(trends.recovery + trends.growth + trends.correction) - (trends.harm + trends.warning) > 0 
              ? 'positive' 
              : (trends.recovery + trends.growth + trends.correction) - (trends.harm + trends.warning) < 0
                ? 'Negative'
                : 'Stable'
            }
          </span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          {(() => {
            const positive = trends.recovery + trends.growth + trends.correction;
            const negative = trends.harm + trends.warning;
            const total = Math.abs(positive) + Math.abs(negative) || 1;
            const positiveWidth = (Math.abs(positive) / total) * 100;
            const isNetPositive = positive > negative;
            
            return (
              <div 
                className={`h-full transition-all ${isNetPositive ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${positiveWidth}%` }}
              />
            );
          })()}
        </div>
        <div className="flex justify-between text-xs mt-1">
          <span className="text-green-600">Positive</span>
          <span className="text-red-600">Negative</span>
        </div>
      </div>
    </section>
  );
}

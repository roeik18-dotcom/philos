import { useMemo, useState, useEffect } from 'react';
import { getUserId } from '../../../services/cloudSync';

// Hebrew value labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Value categories
const positiveValues = ['contribution', 'recovery', 'order'];
const negativeValues = ['harm', 'avoidance'];

// Category colors for SVG
const categoryColors = {
  recovery: '#22c55e',
  harm: '#ef4444',
  correction: '#3b82f6',
  growth: '#10b981',
  warning: '#f59e0b',
  pattern: '#8b5cf6'
};

// Value colors for SVG
const valueColors = {
  contribution: '#22c55e',
  recovery: '#3b82f6',
  order: '#6366f1',
  harm: '#ef4444',
  avoidance: '#9ca3af'
};

export default function WeeklyBehavioralReportSection({ history, user }) {
  // State for replay insights
  const [replayInsights, setReplayInsights] = useState(null);

  // Fetch replay insights
  useEffect(() => {
    const fetchReplayInsights = async () => {
      // Use authenticated user ID or persistent anonymous ID
      const userId = user?.id || getUserId();

      try {
        const API_URL = process.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API_URL}/api/memory/replay-insights/${userId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setReplayInsights(data);
          }
        }
      } catch (error) {
        console.log('Failed to fetch replay insights:', error);
      }
    };

    fetchReplayInsights();
  }, [user]);
  // Calculate weekly report data
  const reportData = useMemo(() => {
    if (!history || history.length === 0) {
      return null;
    }

    // Filter to last 7 days
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const weeklyHistory = history.filter(item => {
      const itemDate = item.timestamp ? new Date(item.timestamp) : new Date();
      return itemDate >= weekAgo;
    });

    if (weeklyHistory.length < 2) {
      return null;
    }

    // Build chains
    const items = weeklyHistory.map((item, idx) => ({
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

    // Extract chains
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

    // Also check for simple parent-child pairs
    if (chains.length === 0) {
      items.forEach(item => {
        if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
          chains.push([nodeMap[item.parent_decision_id], nodeMap[item.id]]);
        }
      });
    }

    if (chains.length === 0) {
      return null;
    }

    // Analyze chains
    const stats = {
      recovery: 0,
      harm: 0,
      correction: 0,
      growth: 0,
      warning: 0,
      pattern: 0,
      totalChains: chains.length
    };

    const movements = {
      positiveMovements: [],
      negativeMovements: []
    };

    const patternCounts = {};

    chains.forEach(chain => {
      const values = chain.map(n => n.value_tag);
      const firstValue = values[0];
      const lastValue = values[values.length - 1];
      
      const startsNegative = negativeValues.includes(firstValue);
      const endsPositive = positiveValues.includes(lastValue);
      const startsPositive = positiveValues.includes(firstValue);
      const endsNegative = negativeValues.includes(lastValue);

      // Recovery: negative → positive
      if (startsNegative && endsPositive) {
        stats.recovery++;
        movements.positiveMovements.push({
          from: firstValue,
          to: lastValue,
          strength: chain.length
        });
      }

      // Harm: positive → negative
      if (startsPositive && endsNegative) {
        stats.harm++;
        movements.negativeMovements.push({
          from: firstValue,
          to: lastValue,
          strength: chain.length
        });
      }

      // Mid-chain correction
      for (let i = 1; i < values.length - 1; i++) {
        if (negativeValues.includes(values[i]) && positiveValues.includes(values[i + 1])) {
          stats.correction++;
          break;
        }
      }

      // Consistent positive
      if (values.every(v => positiveValues.includes(v)) && chain.length >= 2) {
        stats.growth++;
      }

      // Consistent negative
      if (values.every(v => negativeValues.includes(v)) && chain.length >= 2) {
        stats.warning++;
      }

      // Track patterns
      const pattern = values.join('→');
      patternCounts[pattern] = (patternCounts[pattern] || 0) + 1;
    });

    // Count repeated patterns
    Object.values(patternCounts).forEach(count => {
      if (count >= 2) stats.pattern++;
    });

    // Find dominant pattern
    const sortedStats = Object.entries(stats)
      .filter(([key]) => key !== 'totalChains')
      .sort(([, a], [, b]) => b - a);
    
    const dominantCategory = sortedStats[0]?.[0] || 'recovery';
    const dominantCount = sortedStats[0]?.[1] || 0;

    // Find strongest movements
    const strongestPositive = movements.positiveMovements
      .sort((a, b) => b.strength - a.strength)[0];
    const strongestNegative = movements.negativeMovements
      .sort((a, b) => b.strength - a.strength)[0];

    // Generate insights
    const insights = [];

    // Dominant pattern insight
    const categoryLabels = {
      recovery: 'שרשראות התאוששות',
      harm: 'שרשראות נזק',
      correction: 'שרשראות תיקון',
      growth: 'שרשראות צמיחה',
      warning: 'שרשראות אזהרה',
      pattern: 'דפוסים חוזרים'
    };

    if (dominantCount > 0) {
      insights.push(`השבוע בלטו יותר ${categoryLabels[dominantCategory]} (${dominantCount})`);
    }

    // Positive trend
    if (stats.recovery > stats.harm) {
      insights.push('יש עלייה בדפוסי התאוששות');
    }

    // Negative trend
    if (stats.harm > stats.recovery) {
      insights.push('יש עלייה בדפוסי נזק - שים לב');
    }

    // Correction frequency
    if (stats.correction >= 2) {
      insights.push(`נמצאו ${stats.correction} תיקונים באמצע מסלולים`);
    }

    // Pattern detection
    if (stats.pattern > 0) {
      insights.push('נראה דפוס חוזר של תגובה ואחריה תיקון');
    }

    // Growth streak
    if (stats.growth >= 2) {
      insights.push('יש רצף של החלטות חיוביות - המשך כך!');
    }

    // Warning
    if (stats.warning >= 2) {
      insights.push('נמצאו שרשראות בעייתיות - שקול לשנות כיוון');
    }

    return {
      stats,
      dominantCategory,
      dominantCount,
      strongestPositive,
      strongestNegative,
      insights: insights.slice(0, 4),
      totalDecisions: weeklyHistory.length,
      totalChains: chains.length,
      actualValueDistribution: calculateActualValueDistribution(weeklyHistory)
    };
  }, [history]);

  // Calculate replay comparison data
  const replayComparison = useMemo(() => {
    if (!replayInsights || !replayInsights.total_replays || replayInsights.total_replays === 0) {
      return null;
    }

    const altCounts = replayInsights.alternative_path_counts || {};
    const transitions = replayInsights.transition_patterns || [];
    const origTags = replayInsights.most_replayed_original_tags || {};

    // Most explored alternative this week
    const sortedAltPaths = Object.entries(altCounts)
      .filter(([_, count]) => count > 0)
      .sort((a, b) => b[1] - a[1]);
    
    const mostExploredAlt = sortedAltPaths[0] ? sortedAltPaths[0][0] : null;
    const mostExploredCount = sortedAltPaths[0] ? sortedAltPaths[0][1] : 0;

    // Most common missed positive path (positive alternatives explored after negative choices)
    const missedPositive = transitions
      .filter(t => negativeValues.includes(t.from) && positiveValues.includes(t.to))
      .sort((a, b) => b.count - a.count)[0];

    // Most common avoided risky path (negative alternatives that were explored but not taken)
    const avoidedRisky = transitions
      .filter(t => positiveValues.includes(t.from) && negativeValues.includes(t.to))
      .sort((a, b) => b.count - a.count)[0];

    // Calculate gap: compare actual choices vs replay preferences
    let gapAnalysis = null;
    if (reportData && reportData.actualValueDistribution) {
      const actual = reportData.actualValueDistribution;
      const replay = altCounts;
      
      // Find biggest discrepancy
      let maxGap = 0;
      let gapType = null;
      let gapDirection = '';

      positiveValues.forEach(type => {
        const actualPct = actual[type] || 0;
        const replayPct = replay[type] || 0;
        const totalReplay = Object.values(replay).reduce((a, b) => a + b, 0) || 1;
        const replayNormalized = (replayPct / totalReplay) * 100;
        
        const gap = replayNormalized - actualPct;
        if (Math.abs(gap) > Math.abs(maxGap)) {
          maxGap = gap;
          gapType = type;
          gapDirection = gap > 0 ? 'replay_higher' : 'actual_higher';
        }
      });

      if (gapType && Math.abs(maxGap) > 10) {
        gapAnalysis = {
          type: gapType,
          gap: Math.round(maxGap),
          direction: gapDirection
        };
      }
    }

    // Generate replay-specific insights
    const replayInsightTexts = [];

    if (mostExploredAlt && mostExploredCount >= 2) {
      replayInsightTexts.push(
        `השבוע נבדקו שוב ושוב מסלולי ${valueLabels[mostExploredAlt]} שלא נבחרו בזמן אמת`
      );
    }

    if (gapAnalysis) {
      if (gapAnalysis.direction === 'replay_higher') {
        replayInsightTexts.push(
          `מסלולי ${valueLabels[gapAnalysis.type]} בלטו יותר בהפעלות חוזרות מאשר בהחלטות בפועל`
        );
      } else {
        replayInsightTexts.push(
          `נראה פער עקבי בין הבחירות בפועל לבין העדפות הבדיקה החוזרת`
        );
      }
    }

    if (missedPositive && missedPositive.count >= 2) {
      replayInsightTexts.push(
        `${missedPositive.count} פעמים בדקת מעבר מ${valueLabels[missedPositive.from]} ל${valueLabels[missedPositive.to]}`
      );
    }

    return {
      mostExploredAlt,
      mostExploredCount,
      missedPositive,
      avoidedRisky,
      gapAnalysis,
      replayCount: replayInsights.total_replays,
      recentReplayCount: replayInsights.recent_replay_count || 0,
      replayInsightTexts: replayInsightTexts.slice(0, 3),
      altCounts
    };
  }, [replayInsights, reportData]);

  // Helper function to calculate actual value distribution
  function calculateActualValueDistribution(weeklyHistory) {
    const counts = {
      contribution: 0,
      recovery: 0,
      order: 0,
      harm: 0,
      avoidance: 0
    };
    
    weeklyHistory.forEach(item => {
      if (item.value_tag && counts.hasOwnProperty(item.value_tag)) {
        counts[item.value_tag]++;
      }
    });

    const total = weeklyHistory.length || 1;
    const percentages = {};
    Object.keys(counts).forEach(key => {
      percentages[key] = Math.round((counts[key] / total) * 100);
    });

    return percentages;
  }

  // Check if we have enough data
  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id || 
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  if (!hasChains || !reportData) return null;

  const { stats, dominantCategory, insights, totalDecisions, totalChains, strongestPositive, strongestNegative } = reportData;

  // Calculate total for percentage
  const total = Math.max(1, stats.recovery + stats.harm + stats.correction + stats.growth + stats.warning);

  // Bar data for visualization
  const barData = [
    { key: 'recovery', label: 'התאוששות', count: stats.recovery, color: categoryColors.recovery },
    { key: 'harm', label: 'נזק', count: stats.harm, color: categoryColors.harm },
    { key: 'correction', label: 'תיקון', count: stats.correction, color: categoryColors.correction },
    { key: 'growth', label: 'צמיחה', count: stats.growth, color: categoryColors.growth },
    { key: 'warning', label: 'אזהרה', count: stats.warning, color: categoryColors.warning }
  ].filter(d => d.count > 0);

  const maxCount = Math.max(...barData.map(d => d.count), 1);

  return (
    <section 
      className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-3xl p-5 shadow-sm border border-amber-200"
      dir="rtl"
      data-testid="weekly-behavioral-report-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">דוח התנהגותי שבועי</h3>
        <p className="text-xs text-muted-foreground">סיכום מגמות מ-7 הימים האחרונים</p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-2xl font-bold text-amber-600">{totalDecisions}</p>
          <p className="text-xs text-muted-foreground">החלטות</p>
        </div>
        <div className="bg-white/60 rounded-xl p-3 text-center">
          <p className="text-2xl font-bold text-amber-600">{totalChains}</p>
          <p className="text-xs text-muted-foreground">שרשראות</p>
        </div>
      </div>

      {/* Visual distribution - SVG bars */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <p className="text-xs text-muted-foreground mb-3">התפלגות סוגי שרשראות</p>
        
        <svg width="100%" height={barData.length * 36 + 10} className="block">
          {barData.map((item, idx) => {
            const barWidth = (item.count / maxCount) * 100;
            const y = idx * 36;
            
            return (
              <g key={item.key}>
                {/* Background bar */}
                <rect
                  x="70"
                  y={y + 4}
                  width="calc(100% - 100px)"
                  height="24"
                  rx="4"
                  fill="#f3f4f6"
                />
                {/* Value bar */}
                <rect
                  x="70"
                  y={y + 4}
                  width={`${barWidth}%`}
                  height="24"
                  rx="4"
                  fill={item.color}
                  style={{ maxWidth: 'calc(100% - 100px)' }}
                />
                {/* Label */}
                <text
                  x="65"
                  y={y + 20}
                  textAnchor="end"
                  fontSize="11"
                  fill="#666"
                >
                  {item.label}
                </text>
                {/* Count */}
                <text
                  x="75"
                  y={y + 20}
                  fontSize="11"
                  fill="#fff"
                  fontWeight="600"
                >
                  {item.count}
                </text>
              </g>
            );
          })}
        </svg>

        {barData.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-4">
            אין מספיק נתונים להצגה
          </p>
        )}
      </div>

      {/* Dominant pattern highlight */}
      <div className="bg-white/80 rounded-xl p-4 mb-4 border border-amber-100">
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg"
            style={{ backgroundColor: categoryColors[dominantCategory] }}
          >
            {dominantCategory === 'recovery' && '🌱'}
            {dominantCategory === 'harm' && '⚠️'}
            {dominantCategory === 'correction' && '🔄'}
            {dominantCategory === 'growth' && '📈'}
            {dominantCategory === 'warning' && '🔻'}
            {dominantCategory === 'pattern' && '🔁'}
          </div>
          <div>
            <p className="font-semibold text-sm">דפוס דומיננטי השבוע</p>
            <p className="text-xs text-muted-foreground">
              {dominantCategory === 'recovery' && 'התאוששות - מעבר מהימנעות להתאוששות'}
              {dominantCategory === 'harm' && 'נזק - מעבר לכיוון שלילי'}
              {dominantCategory === 'correction' && 'תיקון - זיהוי ותיקון באמצע המסלול'}
              {dominantCategory === 'growth' && 'צמיחה - רצף של החלטות חיוביות'}
              {dominantCategory === 'warning' && 'אזהרה - רצף של החלטות בעייתיות'}
              {dominantCategory === 'pattern' && 'דפוס חוזר'}
            </p>
          </div>
        </div>
      </div>

      {/* Movement highlights */}
      {(strongestPositive || strongestNegative) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {strongestPositive && (
            <div className="bg-green-50 rounded-xl p-3 border border-green-200">
              <p className="text-xs text-green-600 font-medium mb-1">תנועה חיובית חזקה</p>
              <p className="text-sm">
                {valueLabels[strongestPositive.from]} → {valueLabels[strongestPositive.to]}
              </p>
            </div>
          )}
          {strongestNegative && (
            <div className="bg-red-50 rounded-xl p-3 border border-red-200">
              <p className="text-xs text-red-600 font-medium mb-1">תנועה שלילית חזקה</p>
              <p className="text-sm">
                {valueLabels[strongestNegative.from]} → {valueLabels[strongestNegative.to]}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">תובנות שבועיות</p>
          {insights.map((insight, idx) => (
            <div 
              key={idx}
              className="bg-white/60 rounded-lg px-3 py-2 text-sm flex items-center gap-2"
            >
              <span className="text-amber-500">●</span>
              <span>{insight}</span>
            </div>
          ))}
        </div>
      )}

      {/* Stacked distribution bar */}
      <div className="mt-4 pt-3 border-t border-amber-200">
        <p className="text-xs text-muted-foreground mb-2">התפלגות יחסית</p>
        <div className="h-6 rounded-full overflow-hidden flex" style={{ direction: 'ltr' }}>
          {barData.map((item, idx) => {
            const width = (item.count / total) * 100;
            return (
              <div
                key={item.key}
                style={{ 
                  width: `${width}%`, 
                  backgroundColor: item.color,
                  minWidth: width > 0 ? '8px' : '0'
                }}
                title={`${item.label}: ${item.count}`}
                className="transition-all"
              />
            );
          })}
        </div>
        <div className="flex flex-wrap gap-3 mt-2 text-xs">
          {barData.map(item => (
            <div key={item.key} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Replay Insights Integration */}
      {replayComparison && replayComparison.replayCount > 0 && (
        <div className="mt-4 pt-4 border-t border-amber-200" data-testid="replay-integration-section">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <div>
              <h4 className="text-sm font-semibold text-foreground">השוואה להפעלות חוזרות</h4>
              <p className="text-xs text-muted-foreground">
                {replayComparison.replayCount} הפעלות חוזרות | {replayComparison.recentReplayCount} השבוע
              </p>
            </div>
          </div>

          {/* Visual Comparison SVG */}
          {reportData?.actualValueDistribution && (
            <div className="bg-white/60 rounded-xl p-4 mb-3" data-testid="actual-vs-replay-comparison">
              <p className="text-xs text-muted-foreground mb-3">בחירות בפועל vs הפעלות חוזרות</p>
              
              <svg width="100%" height="140" className="block">
                {/* Actual choices bars */}
                <text x="10" y="15" fontSize="10" fill="#666" fontWeight="600">בפועל</text>
                {positiveValues.map((type, idx) => {
                  const actual = reportData.actualValueDistribution[type] || 0;
                  const barWidth = Math.min(actual * 2, 100);
                  const y = 25 + idx * 22;
                  
                  return (
                    <g key={`actual-${type}`}>
                      <rect x="60" y={y} width="140" height="16" rx="3" fill="#e5e7eb" />
                      <rect x="60" y={y} width={barWidth * 1.4} height="16" rx="3" fill={valueColors[type]} opacity="0.8" />
                      <text x="55" y={y + 12} textAnchor="end" fontSize="9" fill="#666">
                        {valueLabels[type]}
                      </text>
                      <text x="205" y={y + 12} fontSize="9" fill="#666">{actual}%</text>
                    </g>
                  );
                })}

                {/* Replay preferences bars */}
                <text x="10" y="100" fontSize="10" fill="#666" fontWeight="600">הפעלה חוזרת</text>
                {(() => {
                  const totalReplay = Object.values(replayComparison.altCounts).reduce((a, b) => a + b, 0) || 1;
                  return positiveValues.map((type, idx) => {
                    const count = replayComparison.altCounts[type] || 0;
                    const pct = Math.round((count / totalReplay) * 100);
                    const barWidth = Math.min(pct * 2, 100);
                    const y = 110 + idx * 22;
                    
                    return (
                      <g key={`replay-${type}`}>
                        <rect x="60" y={y - 20} width="140" height="16" rx="3" fill="#e5e7eb" />
                        <rect x="60" y={y - 20} width={barWidth * 1.4} height="16" rx="3" fill={valueColors[type]} opacity="0.5" />
                        <text x="55" y={y - 8} textAnchor="end" fontSize="9" fill="#666">
                          {valueLabels[type]}
                        </text>
                        <text x="205" y={y - 8} fontSize="9" fill="#666">{pct}%</text>
                      </g>
                    );
                  });
                })()}

                {/* Gap indicator line */}
                {replayComparison.gapAnalysis && (
                  <g>
                    <line x1="230" y1="25" x2="230" y2="130" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="4 2" />
                    <text x="235" y="80" fontSize="8" fill="#8b5cf6" transform="rotate(90, 235, 80)">פער</text>
                  </g>
                )}
              </svg>
            </div>
          )}

          {/* Replay Stats Grid */}
          <div className="grid grid-cols-3 gap-2 mb-3">
            {replayComparison.mostExploredAlt && (
              <div className="bg-purple-50 rounded-lg p-2 text-center border border-purple-200" data-testid="most-explored-stat">
                <p className="text-lg font-bold text-purple-600">{valueLabels[replayComparison.mostExploredAlt]}</p>
                <p className="text-xs text-muted-foreground">הכי נבדק</p>
              </div>
            )}
            {replayComparison.missedPositive && (
              <div className="bg-green-50 rounded-lg p-2 text-center border border-green-200" data-testid="missed-positive-stat">
                <p className="text-lg font-bold text-green-600">{valueLabels[replayComparison.missedPositive.to]}</p>
                <p className="text-xs text-muted-foreground">הוחמץ</p>
              </div>
            )}
            {replayComparison.avoidedRisky ? (
              <div className="bg-red-50 rounded-lg p-2 text-center border border-red-200" data-testid="avoided-risky-stat">
                <p className="text-lg font-bold text-red-600">{valueLabels[replayComparison.avoidedRisky.to]}</p>
                <p className="text-xs text-muted-foreground">נמנע</p>
              </div>
            ) : (
              <div className="bg-emerald-50 rounded-lg p-2 text-center border border-emerald-200">
                <p className="text-lg font-bold text-emerald-600">0</p>
                <p className="text-xs text-muted-foreground">מסלולי סיכון</p>
              </div>
            )}
          </div>

          {/* Gap Analysis */}
          {replayComparison.gapAnalysis && (
            <div className="bg-purple-50 rounded-xl p-3 mb-3 border border-purple-200" data-testid="gap-analysis">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-purple-800">פער זוהה</p>
                  <p className="text-xs text-purple-600">
                    {replayComparison.gapAnalysis.direction === 'replay_higher' 
                      ? `${valueLabels[replayComparison.gapAnalysis.type]} נבדק יותר (+${replayComparison.gapAnalysis.gap}%) מאשר נבחר בפועל`
                      : `${valueLabels[replayComparison.gapAnalysis.type]} נבחר יותר בפועל מאשר נבדק בהפעלות חוזרות`
                    }
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Replay Insights */}
          {replayComparison.replayInsightTexts.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">תובנות הפעלה חוזרת</p>
              {replayComparison.replayInsightTexts.map((insight, idx) => (
                <div 
                  key={idx}
                  className="bg-purple-50/60 rounded-lg px-3 py-2 text-sm flex items-center gap-2"
                  data-testid={`replay-insight-${idx}`}
                >
                  <span className="text-purple-500">●</span>
                  <span className="text-purple-800">{insight}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

import { useMemo } from 'react';

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

export default function WeeklyBehavioralReportSection({ history }) {
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
      totalChains: chains.length
    };
  }, [history]);

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
    </section>
  );
}

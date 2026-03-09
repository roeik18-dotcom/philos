import { useState, useEffect, useMemo } from 'react';
import { getUserId } from '../../../services/cloudSync';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Hebrew labels for metrics
const metricLabels = {
  recovery: 'התאוששות',
  harm_pressure: 'לחץ נזק',
  order_drift: 'מגמת סדר',
  contribution: 'תרומה קולקטיבית',
  replay_exploration: 'חקירת מסלולים'
};

// Metric colors for SVG
const metricColors = {
  recovery: '#3b82f6',
  harm_pressure: '#ef4444',
  order_drift: '#6366f1',
  contribution: '#22c55e',
  replay_exploration: '#8b5cf6'
};

// Calculate user metrics from history and learning
const calculateUserMetrics = (history, learningHistory, replayInsights) => {
  if (!history || history.length === 0) {
    return null;
  }

  // Calculate from history
  let totalRecovery = 0;
  let totalHarmPressure = 0;
  let totalOrderDrift = 0;
  let totalContribution = 0;
  let count = 0;

  history.forEach(item => {
    const tag = item.value_tag;
    if (tag === 'recovery') totalRecovery++;
    if (tag === 'harm') totalHarmPressure++;
    if (tag === 'order') totalOrderDrift++;
    if (tag === 'contribution') totalContribution++;
    count++;
  });

  // Calculate percentages
  const recoveryPct = count > 0 ? (totalRecovery / count) * 100 : 0;
  const harmPressurePct = count > 0 ? (totalHarmPressure / count) * 100 : 0;
  const orderDriftPct = count > 0 ? (totalOrderDrift / count) * 100 : 0;
  const contributionPct = count > 0 ? (totalContribution / count) * 100 : 0;

  // Learning history metrics (averages)
  let avgHarmPressure = 0;
  let avgRecoveryStability = 0;
  let avgOrderDrift = 0;

  if (learningHistory && learningHistory.length > 0) {
    let harmSum = 0, recSum = 0, orderSum = 0, lCount = 0;
    learningHistory.forEach(entry => {
      if (entry.actual_harm_pressure !== undefined) {
        harmSum += entry.actual_harm_pressure;
        lCount++;
      }
      if (entry.actual_recovery_stability !== undefined) {
        recSum += entry.actual_recovery_stability;
      }
      if (entry.actual_order_drift !== undefined) {
        orderSum += entry.actual_order_drift;
      }
    });
    if (lCount > 0) {
      avgHarmPressure = harmSum / lCount;
      avgRecoveryStability = recSum / lCount;
      avgOrderDrift = orderSum / lCount;
    }
  }

  // Replay exploration rate
  const replayExplorationRate = replayInsights?.total_replays 
    ? Math.min(100, (replayInsights.total_replays / Math.max(count, 1)) * 100)
    : 0;

  return {
    recovery: Math.round(recoveryPct + avgRecoveryStability),
    harm_pressure: Math.round(harmPressurePct + Math.abs(avgHarmPressure)),
    order_drift: Math.round(orderDriftPct + avgOrderDrift),
    contribution: Math.round(contributionPct),
    replay_exploration: Math.round(replayExplorationRate),
    totalDecisions: count
  };
};

// Generate Hebrew insights based on comparison
const generateInsights = (userMetrics, collectiveMetrics) => {
  if (!userMetrics || !collectiveMetrics) return [];

  const insights = [];

  // Recovery comparison
  const recoveryDiff = userMetrics.recovery - collectiveMetrics.recovery;
  if (recoveryDiff > 10) {
    insights.push({
      type: 'positive',
      text: 'התאוששות אצלך גבוהה מהממוצע הקולקטיבי',
      metric: 'recovery'
    });
  } else if (recoveryDiff < -10) {
    insights.push({
      type: 'neutral',
      text: 'מסלולי התאוששות נבחרים פחות מהממוצע',
      metric: 'recovery'
    });
  }

  // Harm pressure comparison
  const harmDiff = userMetrics.harm_pressure - collectiveMetrics.harm_pressure;
  if (harmDiff < -5) {
    insights.push({
      type: 'positive',
      text: 'לחץ הנזק אצלך השבוע נמוך מהממוצע',
      metric: 'harm_pressure'
    });
  } else if (harmDiff > 10) {
    insights.push({
      type: 'warning',
      text: 'לחץ הנזק אצלך גבוה מהממוצע הקולקטיבי',
      metric: 'harm_pressure'
    });
  }

  // Order drift comparison
  const orderDiff = userMetrics.order_drift - collectiveMetrics.order_drift;
  if (orderDiff > 10) {
    insights.push({
      type: 'positive',
      text: 'מגמת הסדר אצלך חזקה מהממוצע',
      metric: 'order_drift'
    });
  } else if (orderDiff < -10) {
    insights.push({
      type: 'neutral',
      text: 'מסלולי סדר נבחרים פחות מהממוצע',
      metric: 'order_drift'
    });
  }

  // Contribution comparison
  const contribDiff = userMetrics.contribution - collectiveMetrics.contribution;
  if (contribDiff > 10) {
    insights.push({
      type: 'positive',
      text: 'התרומה הקולקטיבית שלך גבוהה מהממוצע',
      metric: 'contribution'
    });
  }

  // Replay exploration comparison
  const replayDiff = userMetrics.replay_exploration - collectiveMetrics.replay_exploration;
  if (replayDiff > 15) {
    insights.push({
      type: 'positive',
      text: 'אתה חוקר יותר מסלולים חלופיים מהממוצע',
      metric: 'replay_exploration'
    });
  }

  // Default insight if none generated
  if (insights.length === 0) {
    insights.push({
      type: 'neutral',
      text: 'הדפוסים שלך דומים לממוצע הקולקטיבי',
      metric: null
    });
  }

  return insights.slice(0, 3);
};

export default function CollectiveMirrorSection({ history, learningHistory, replayInsights }) {
  const [collectiveData, setCollectiveData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch collective data
  useEffect(() => {
    const fetchCollectiveData = async () => {
      try {
        const response = await fetch(`${API_URL}/api/collective/layer`);
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setCollectiveData(data);
          }
        }
      } catch (error) {
        console.log('Failed to fetch collective data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCollectiveData();
  }, []);

  // Calculate user metrics
  const userMetrics = useMemo(() => {
    return calculateUserMetrics(history, learningHistory, replayInsights);
  }, [history, learningHistory, replayInsights]);

  // Calculate collective metrics
  const collectiveMetrics = useMemo(() => {
    if (!collectiveData) return null;

    const { value_distribution, avg_order_drift, avg_harm_pressure, avg_recovery_stability, total_decisions } = collectiveData;
    
    // Normalize to percentages
    const total = Object.values(value_distribution || {}).reduce((a, b) => a + b, 0) || 1;
    
    return {
      recovery: Math.round(((value_distribution?.recovery || 0) / total) * 100 + (avg_recovery_stability || 0)),
      harm_pressure: Math.round(((value_distribution?.harm || 0) / total) * 100 + Math.abs(avg_harm_pressure || 0)),
      order_drift: Math.round(((value_distribution?.order || 0) / total) * 100 + (avg_order_drift || 0)),
      contribution: Math.round(((value_distribution?.contribution || 0) / total) * 100),
      replay_exploration: 25, // Estimated average replay exploration
      totalDecisions: total_decisions || 0
    };
  }, [collectiveData]);

  // Generate insights
  const insights = useMemo(() => {
    return generateInsights(userMetrics, collectiveMetrics);
  }, [userMetrics, collectiveMetrics]);

  // Don't render if no user data
  if (!userMetrics || !collectiveMetrics) {
    return null;
  }

  // Metrics to compare
  const comparisonMetrics = ['recovery', 'harm_pressure', 'order_drift', 'contribution', 'replay_exploration'];

  // Get max value for bar scaling
  const maxValue = Math.max(
    ...comparisonMetrics.map(m => Math.max(userMetrics[m] || 0, collectiveMetrics[m] || 0)),
    50
  );

  return (
    <section 
      className="bg-gradient-to-br from-cyan-50 to-sky-50 rounded-3xl p-5 shadow-sm border border-cyan-200"
      dir="rtl"
      data-testid="collective-mirror-section"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-cyan-200 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-cyan-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">מראה קולקטיבית</h3>
            <p className="text-xs text-muted-foreground">
              השוואת הדפוסים שלך לשדה הקולקטיבי
            </p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="flex gap-2 text-xs">
          <div className="bg-white/70 rounded-lg px-3 py-1.5 border border-cyan-200">
            <span className="text-cyan-700 font-medium">{userMetrics.totalDecisions}</span>
            <span className="text-muted-foreground mr-1">ההחלטות שלך</span>
          </div>
          <div className="bg-white/70 rounded-lg px-3 py-1.5 border border-cyan-200">
            <span className="text-cyan-700 font-medium">{collectiveData?.total_users || 0}</span>
            <span className="text-muted-foreground mr-1">משתמשים</span>
          </div>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        <div className="flex items-center gap-4 mb-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-cyan-500 rounded"></div>
            <span>אתה</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-gray-300 rounded"></div>
            <span>ממוצע קולקטיבי</span>
          </div>
        </div>

        {/* SVG Comparison Bars */}
        <svg width="100%" height="200" className="block" data-testid="comparison-chart">
          {comparisonMetrics.map((metric, idx) => {
            const y = idx * 38 + 15;
            const userValue = userMetrics[metric] || 0;
            const collectiveValue = collectiveMetrics[metric] || 0;
            const userBarWidth = (userValue / maxValue) * 180;
            const collectiveBarWidth = (collectiveValue / maxValue) * 180;
            const isHigher = userValue > collectiveValue;

            return (
              <g key={metric} data-testid={`comparison-${metric}`}>
                {/* Metric label */}
                <text x="85" y={y + 5} textAnchor="end" fontSize="11" fill="#334155" fontWeight="500">
                  {metricLabels[metric]}
                </text>
                
                {/* Background track */}
                <rect x="95" y={y - 12} width="190" height="28" rx="4" fill="#f1f5f9" />
                
                {/* Collective bar (bottom) */}
                <rect 
                  x="95" 
                  y={y + 2} 
                  width={collectiveBarWidth} 
                  height="10" 
                  rx="2" 
                  fill="#cbd5e1"
                />
                
                {/* User bar (top) */}
                <rect 
                  x="95" 
                  y={y - 10} 
                  width={userBarWidth} 
                  height="10" 
                  rx="2" 
                  fill={metricColors[metric]}
                  opacity="0.9"
                />
                
                {/* Values */}
                <text x="290" y={y - 3} fontSize="10" fill={metricColors[metric]} fontWeight="600">
                  {userValue}
                </text>
                <text x="290" y={y + 10} fontSize="10" fill="#94a3b8">
                  {collectiveValue}
                </text>
                
                {/* Difference indicator */}
                {Math.abs(userValue - collectiveValue) > 5 && (
                  <g>
                    {isHigher ? (
                      <path 
                        d={`M305,${y - 5} l5,-5 l5,5`} 
                        fill="none" 
                        stroke="#22c55e" 
                        strokeWidth="2"
                      />
                    ) : (
                      <path 
                        d={`M305,${y - 5} l5,5 l5,-5`} 
                        fill="none" 
                        stroke="#f59e0b" 
                        strokeWidth="2"
                      />
                    )}
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Insights */}
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground mb-2">תובנות השוואה</p>
        {insights.map((insight, idx) => (
          <div 
            key={idx}
            className={`rounded-xl px-4 py-3 flex items-center gap-3 ${
              insight.type === 'positive' 
                ? 'bg-emerald-50 border border-emerald-200' 
                : insight.type === 'warning'
                ? 'bg-amber-50 border border-amber-200'
                : 'bg-gray-50 border border-gray-200'
            }`}
            data-testid={`mirror-insight-${idx}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              insight.type === 'positive' 
                ? 'bg-emerald-200' 
                : insight.type === 'warning'
                ? 'bg-amber-200'
                : 'bg-gray-200'
            }`}>
              {insight.type === 'positive' ? (
                <svg className="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              ) : insight.type === 'warning' ? (
                <svg className="w-4 h-4 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                </svg>
              )}
            </div>
            <p className={`text-sm ${
              insight.type === 'positive' 
                ? 'text-emerald-800' 
                : insight.type === 'warning'
                ? 'text-amber-800'
                : 'text-gray-700'
            }`}>
              {insight.text}
            </p>
          </div>
        ))}
      </div>

      {/* Footer note */}
      <p className="text-xs text-muted-foreground mt-4 text-center">
        הנתונים מבוססים על {collectiveData?.total_decisions || 0} החלטות מ-{collectiveData?.total_users || 0} משתמשים
      </p>
    </section>
  );
}

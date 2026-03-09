import { useState, useEffect, useMemo } from 'react';
import { fetchCollectiveLayer } from '../../../services/dataService';

// Hebrew labels for metrics
const metricLabels = {
  recovery: 'התאוששות',
  harm_pressure: 'לחץ נזק',
  order_drift: 'מגמת סדר',
  contribution: 'תרומה'
};

// Metric colors for SVG
const metricColors = {
  recovery: '#3b82f6',
  harm_pressure: '#ef4444',
  order_drift: '#6366f1',
  contribution: '#22c55e'
};

// Calculate weekly user metrics from history
const calculateWeeklyUserMetrics = (history) => {
  if (!history || history.length === 0) return [];

  // Group by week
  const weeklyData = {};
  const now = new Date();
  
  history.forEach(item => {
    const itemDate = new Date(item.timestamp || item.time || now);
    const weekStart = new Date(itemDate);
    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
    const weekKey = weekStart.toISOString().split('T')[0];
    
    if (!weeklyData[weekKey]) {
      weeklyData[weekKey] = {
        recovery: 0,
        harm: 0,
        order: 0,
        contribution: 0,
        total: 0
      };
    }
    
    const tag = item.value_tag;
    if (tag === 'recovery') weeklyData[weekKey].recovery++;
    if (tag === 'harm') weeklyData[weekKey].harm++;
    if (tag === 'order') weeklyData[weekKey].order++;
    if (tag === 'contribution') weeklyData[weekKey].contribution++;
    weeklyData[weekKey].total++;
  });

  // Convert to percentages and sort by date
  return Object.entries(weeklyData)
    .sort((a, b) => new Date(a[0]) - new Date(b[0]))
    .slice(-4) // Last 4 weeks
    .map(([week, data]) => ({
      week,
      recovery: data.total > 0 ? Math.round((data.recovery / data.total) * 100) : 0,
      harm_pressure: data.total > 0 ? Math.round((data.harm / data.total) * 100) : 0,
      order_drift: data.total > 0 ? Math.round((data.order / data.total) * 100) : 0,
      contribution: data.total > 0 ? Math.round((data.contribution / data.total) * 100) : 0,
      total: data.total
    }));
};

// Calculate trajectory (is user moving closer or farther from collective)
const calculateTrajectory = (userWeekly, collectiveAvg) => {
  if (!userWeekly || userWeekly.length < 2 || !collectiveAvg) return {};

  const metrics = ['recovery', 'harm_pressure', 'order_drift', 'contribution'];
  const trajectories = {};

  metrics.forEach(metric => {
    const collectiveValue = collectiveAvg[metric] || 0;
    
    // Calculate distances from collective for first and last week
    const firstWeek = userWeekly[0];
    const lastWeek = userWeekly[userWeekly.length - 1];
    
    const firstDistance = Math.abs(firstWeek[metric] - collectiveValue);
    const lastDistance = Math.abs(lastWeek[metric] - collectiveValue);
    
    // Calculate trend direction
    const userTrend = lastWeek[metric] - firstWeek[metric];
    const isAboveCollective = lastWeek[metric] > collectiveValue;
    
    // Determine trajectory
    if (lastDistance < firstDistance) {
      trajectories[metric] = {
        direction: 'converging',
        change: Math.round(firstDistance - lastDistance),
        isAbove: isAboveCollective,
        trend: userTrend
      };
    } else if (lastDistance > firstDistance) {
      trajectories[metric] = {
        direction: 'diverging',
        change: Math.round(lastDistance - firstDistance),
        isAbove: isAboveCollective,
        trend: userTrend
      };
    } else {
      trajectories[metric] = {
        direction: 'stable',
        change: 0,
        isAbove: isAboveCollective,
        trend: userTrend
      };
    }
  });

  return trajectories;
};

// Generate Hebrew insights based on trajectory
const generateTrajectoryInsights = (trajectories, userWeekly) => {
  if (!trajectories || Object.keys(trajectories).length === 0) return [];

  const insights = [];

  // Recovery trajectory
  if (trajectories.recovery) {
    const t = trajectories.recovery;
    if (t.direction === 'converging' && t.change > 5) {
      insights.push({
        type: 'positive',
        text: 'אתה מתקרב בהדרגה למגמת ההתאוששות הקולקטיבית',
        metric: 'recovery'
      });
    } else if (t.direction === 'diverging' && t.isAbove && t.change > 5) {
      insights.push({
        type: 'positive',
        text: 'ההתאוששות שלך נעה מעל הממוצע הקולקטיבי לאורך זמן',
        metric: 'recovery'
      });
    }
  }

  // Order drift trajectory
  if (trajectories.order_drift) {
    const t = trajectories.order_drift;
    if (t.direction === 'diverging' && !t.isAbove && t.change > 5) {
      insights.push({
        type: 'warning',
        text: 'נראה ריחוק גובר ממגמת הסדר הקולקטיבית',
        metric: 'order_drift'
      });
    } else if (t.direction === 'converging' && t.change > 5) {
      insights.push({
        type: 'positive',
        text: 'מגמת הסדר שלך מתקרבת לממוצע הקולקטיבי',
        metric: 'order_drift'
      });
    }
  }

  // Contribution trajectory
  if (trajectories.contribution) {
    const t = trajectories.contribution;
    if (t.isAbove && t.trend > 0) {
      insights.push({
        type: 'positive',
        text: 'תרומתך נעה מעל הממוצע הקולקטיבי לאורך זמן',
        metric: 'contribution'
      });
    } else if (t.direction === 'converging') {
      insights.push({
        type: 'neutral',
        text: 'רמת התרומה שלך מתקרבת לממוצע הקולקטיבי',
        metric: 'contribution'
      });
    }
  }

  // Harm pressure trajectory
  if (trajectories.harm_pressure) {
    const t = trajectories.harm_pressure;
    if (!t.isAbove && t.trend < 0) {
      insights.push({
        type: 'positive',
        text: 'לחץ הנזק שלך יורד מתחת לממוצע הקולקטיבי',
        metric: 'harm_pressure'
      });
    } else if (t.isAbove && t.direction === 'diverging') {
      insights.push({
        type: 'warning',
        text: 'לחץ הנזק שלך מתרחק מעלה מהממוצע הקולקטיבי',
        metric: 'harm_pressure'
      });
    }
  }

  // Default insight
  if (insights.length === 0) {
    insights.push({
      type: 'neutral',
      text: 'המגמות שלך יציבות ביחס לשדה הקולקטיבי',
      metric: null
    });
  }

  return insights.slice(0, 3);
};

export default function CollectiveTrajectorySection({ history }) {
  const [collectiveData, setCollectiveData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch collective data using cached service
  useEffect(() => {
    const loadCollectiveData = async () => {
      setLoading(true);
      try {
        const data = await fetchCollectiveLayer();
        if (data.success) {
          setCollectiveData(data);
          setError(null);
        } else {
          setError(data.error || 'שגיאה בטעינת נתונים');
        }
      } catch (err) {
        console.error('Failed to fetch collective data:', err);
        setError('שגיאה בחיבור לשרת');
      } finally {
        setLoading(false);
      }
    };

    loadCollectiveData();
  }, []);

  // Calculate user weekly metrics
  const userWeekly = useMemo(() => {
    return calculateWeeklyUserMetrics(history);
  }, [history]);

  // Calculate collective averages
  const collectiveAvg = useMemo(() => {
    if (!collectiveData) return null;

    const { value_distribution, total_decisions } = collectiveData;
    const total = Object.values(value_distribution || {}).reduce((a, b) => a + b, 0) || 1;

    return {
      recovery: Math.round(((value_distribution?.recovery || 0) / total) * 100),
      harm_pressure: Math.round(((value_distribution?.harm || 0) / total) * 100),
      order_drift: Math.round(((value_distribution?.order || 0) / total) * 100),
      contribution: Math.round(((value_distribution?.contribution || 0) / total) * 100)
    };
  }, [collectiveData]);

  // Calculate trajectories
  const trajectories = useMemo(() => {
    return calculateTrajectory(userWeekly, collectiveAvg);
  }, [userWeekly, collectiveAvg]);

  // Generate insights
  const insights = useMemo(() => {
    return generateTrajectoryInsights(trajectories, userWeekly);
  }, [trajectories, userWeekly]);

  // Show loading state
  if (loading) {
    return (
      <section 
        className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-indigo-200"
        dir="rtl"
        data-testid="collective-trajectory-section"
      >
        <div className="animate-pulse">
          <div className="h-6 bg-indigo-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-indigo-100 rounded w-2/3 mb-2"></div>
          <div className="h-32 bg-indigo-100 rounded"></div>
        </div>
      </section>
    );
  }

  // Show error state
  if (error) {
    return (
      <section 
        className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-indigo-200"
        dir="rtl"
        data-testid="collective-trajectory-section"
      >
        <h3 className="text-lg font-semibold text-foreground mb-2">מסלול קולקטיבי</h3>
        <p className="text-sm text-red-500">{error}</p>
      </section>
    );
  }

  // Don't render if not enough data
  if (!history || history.length < 3 || !collectiveAvg) {
    return null;
  }

  // If only one week of data, show a simplified view
  const hasMultipleWeeks = userWeekly.length >= 2;

  const metrics = ['recovery', 'harm_pressure', 'order_drift', 'contribution'];
  const chartWidth = 320;
  const chartHeight = 120;
  const padding = { top: 20, right: 30, bottom: 30, left: 60 };

  return (
    <section 
      className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-teal-200"
      dir="rtl"
      data-testid="collective-trajectory-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-teal-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-teal-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">מסלול קולקטיבי</h3>
          <p className="text-xs text-muted-foreground">
            תנועת הדפוסים שלך ביחס לשדה הקולקטיבי לאורך זמן
          </p>
        </div>
      </div>

      {/* Trajectory Chart */}
      <div className="bg-white/60 rounded-xl p-4 mb-4">
        {hasMultipleWeeks ? (
          <>
            <p className="text-xs text-muted-foreground mb-3">מגמה לאורך {userWeekly.length} שבועות</p>
            
            <svg 
              width="100%" 
              height="180" 
              viewBox={`0 0 ${chartWidth} 180`} 
              className="block"
              data-testid="trajectory-chart"
            >
          {/* Y-axis labels */}
          <text x="55" y="25" textAnchor="end" fontSize="9" fill="#666">100%</text>
          <text x="55" y="70" textAnchor="end" fontSize="9" fill="#666">50%</text>
          <text x="55" y="115" textAnchor="end" fontSize="9" fill="#666">0%</text>

          {/* Grid lines */}
          <line x1="60" y1="20" x2="300" y2="20" stroke="#e5e7eb" strokeWidth="1" />
          <line x1="60" y1="65" x2="300" y2="65" stroke="#e5e7eb" strokeWidth="1" strokeDasharray="4 2" />
          <line x1="60" y1="110" x2="300" y2="110" stroke="#e5e7eb" strokeWidth="1" />

          {/* Metric lines */}
          {metrics.map((metric, mIdx) => {
            if (userWeekly.length < 2) return null;
            
            const points = userWeekly.map((week, idx) => {
              const x = 60 + (idx / (userWeekly.length - 1)) * 240;
              const y = 110 - (week[metric] / 100) * 90;
              return `${x},${y}`;
            }).join(' ');

            // Collective average line
            const collectiveY = 110 - (collectiveAvg[metric] / 100) * 90;

            return (
              <g key={metric}>
                {/* Collective average line (dashed) */}
                <line 
                  x1="60" 
                  y1={collectiveY} 
                  x2="300" 
                  y2={collectiveY} 
                  stroke={metricColors[metric]} 
                  strokeWidth="1" 
                  strokeDasharray="4 2"
                  opacity="0.4"
                />
                
                {/* User trend line */}
                <polyline
                  points={points}
                  fill="none"
                  stroke={metricColors[metric]}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                
                {/* Data points */}
                {userWeekly.map((week, idx) => {
                  const x = 60 + (idx / (userWeekly.length - 1)) * 240;
                  const y = 110 - (week[metric] / 100) * 90;
                  return (
                    <circle
                      key={idx}
                      cx={x}
                      cy={y}
                      r="4"
                      fill={metricColors[metric]}
                      stroke="white"
                      strokeWidth="2"
                    />
                  );
                })}
              </g>
            );
          })}

          {/* Week labels */}
          {userWeekly.map((week, idx) => {
            const x = 60 + (idx / (userWeekly.length - 1)) * 240;
            const weekNum = userWeekly.length - idx;
            return (
              <text key={idx} x={x} y="130" textAnchor="middle" fontSize="9" fill="#666">
                {weekNum === 1 ? 'עכשיו' : `לפני ${weekNum - 1}ש'`}
              </text>
            );
          })}

          {/* Legend */}
          {metrics.map((metric, idx) => (
            <g key={metric} transform={`translate(${60 + idx * 60}, 150)`}>
              <circle cx="5" cy="5" r="4" fill={metricColors[metric]} />
              <text x="12" y="8" fontSize="8" fill="#666">{metricLabels[metric]}</text>
            </g>
          ))}
        </svg>
          </>
        ) : (
          <div className="text-center py-4" data-testid="trajectory-chart">
            <p className="text-sm text-muted-foreground mb-3">נתוני השבוע הנוכחי ביחס לקולקטיב</p>
            <div className="flex justify-center gap-4">
              {metrics.map(metric => {
                const currentValue = userWeekly[0]?.[metric] || 0;
                const collectiveValue = collectiveAvg[metric] || 0;
                const diff = currentValue - collectiveValue;
                const isAbove = diff > 0;
                
                return (
                  <div key={metric} className="text-center bg-white/60 rounded-lg px-3 py-2">
                    <div className="text-xs text-muted-foreground mb-1">{metricLabels[metric]}</div>
                    <div className={`text-lg font-bold ${isAbove ? 'text-emerald-600' : diff < 0 ? 'text-amber-600' : 'text-gray-600'}`}>
                      {currentValue}%
                    </div>
                    <div className={`text-xs ${isAbove ? 'text-emerald-600' : diff < 0 ? 'text-amber-600' : 'text-gray-500'}`}>
                      {isAbove ? '↑' : diff < 0 ? '↓' : '='} vs {collectiveValue}%
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-muted-foreground mt-4">המשך להוסיף החלטות כדי לראות מגמות לאורך זמן</p>
          </div>
        )}
      </div>

      {/* Trajectory Indicators - only show when we have trajectory data */}
      {hasMultipleWeeks && (
        <div className="grid grid-cols-2 gap-2 mb-4">
          {metrics.map(metric => {
            const t = trajectories[metric];
            if (!t) return null;

            const isPositive = (metric === 'harm_pressure') 
              ? (!t.isAbove || t.direction === 'converging')
              : (t.isAbove || t.direction === 'converging');

            return (
              <div 
                key={metric}
                className={`rounded-xl p-3 border ${
                  isPositive ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'
                }`}
                data-testid={`trajectory-${metric}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-foreground">{metricLabels[metric]}</span>
                  {t.direction === 'converging' ? (
                    <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  ) : t.direction === 'diverging' ? (
                    <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                    </svg>
                  )}
                </div>
                <p className={`text-xs ${isPositive ? 'text-emerald-700' : 'text-amber-700'}`}>
                  {t.direction === 'converging' ? 'מתקרב לממוצע' : 
                   t.direction === 'diverging' ? (t.isAbove ? 'מעל ומתרחק' : 'מתחת ומתרחק') : 
                   'יציב'}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Insights */}
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground">תובנות מגמה</p>
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
            data-testid={`trajectory-insight-${idx}`}
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              ) : insight.type === 'warning' ? (
                <svg className="w-4 h-4 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
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
    </section>
  );
}

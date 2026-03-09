import { useState, useEffect, useMemo } from 'react';
import { fetchCollectiveTrends } from '../../../services/dataService';

// Hebrew labels
const metricLabels = {
  order_drift: 'סחף סדר',
  collective_drift: 'סחף קולקטיבי',
  harm_pressure: 'לחץ נזק',
  recovery_stability: 'יציבות התאוששות'
};

// Simple SVG Sparkline component
const Sparkline = ({ data, color = '#10b981', height = 40, width = 120 }) => {
  const points = useMemo(() => {
    if (!data || data.length === 0) return '';
    
    const max = Math.max(...data, 0.1);
    const min = Math.min(...data, 0);
    const range = max - min || 1;
    
    const xStep = width / (data.length - 1 || 1);
    
    return data.map((value, i) => {
      const x = i * xStep;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');
  }, [data, height, width]);

  if (!data || data.length === 0) {
    return (
      <svg width={width} height={height} className="opacity-30">
        <line x1="0" y1={height/2} x2={width} y2={height/2} stroke={color} strokeWidth="2" strokeDasharray="4" />
      </svg>
    );
  }

  return (
    <svg width={width} height={height}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
      {/* End dot */}
      {data.length > 0 && (
        <circle
          cx={width}
          cy={height - ((data[data.length - 1] - Math.min(...data)) / (Math.max(...data) - Math.min(...data) || 1)) * height}
          r="3"
          fill={color}
        />
      )}
    </svg>
  );
};

// Bar chart component for value distribution
const ValueBars = ({ current, previous }) => {
  const values = ['contribution', 'recovery', 'order'];
  const labels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר' };
  const colors = { contribution: '#10b981', recovery: '#3b82f6', order: '#6366f1' };
  
  const maxVal = Math.max(
    ...values.map(v => Math.max(current[v] || 0, previous[v] || 0)),
    1
  );

  return (
    <div className="flex justify-center gap-6">
      {values.map(value => {
        const currVal = current[value] || 0;
        const prevVal = previous[value] || 0;
        const currHeight = (currVal / maxVal) * 60;
        const prevHeight = (prevVal / maxVal) * 60;
        
        return (
          <div key={value} className="flex flex-col items-center">
            <div className="flex items-end gap-1 h-16">
              {/* Previous bar */}
              <div 
                className="w-4 bg-gray-300 rounded-t transition-all"
                style={{ height: `${prevHeight}px` }}
                title={`תקופה קודמת: ${prevVal}`}
              />
              {/* Current bar */}
              <div 
                className="w-4 rounded-t transition-all"
                style={{ height: `${currHeight}px`, backgroundColor: colors[value] }}
                title={`תקופה נוכחית: ${currVal}`}
              />
            </div>
            <span className="text-xs text-muted-foreground mt-1">{labels[value]}</span>
          </div>
        );
      })}
    </div>
  );
};

export default function CollectiveTrendsSection() {
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTrendsData = async (forceRefresh = false) => {
      try {
        const data = await fetchCollectiveTrends(forceRefresh);
        if (data.success) {
          setTrendsData(data);
          setError(null);
        } else {
          setError(data.error || 'שגיאה בטעינת נתונים');
        }
      } catch (err) {
        console.error('Collective trends error:', err);
        setError('שגיאה בחיבור לשרת');
      } finally {
        setLoading(false);
      }
    };

    loadTrendsData();
    // Refresh every 60 seconds with force refresh
    const interval = setInterval(() => loadTrendsData(true), 60000);
    return () => clearInterval(interval);
  }, []);

  // Extract trend data for sparklines
  const trendLines = useMemo(() => {
    if (!trendsData?.daily_trends) return {};
    
    // Reverse to get chronological order (oldest first)
    const trends = [...trendsData.daily_trends].reverse().slice(-7);
    
    return {
      decisions: trends.map(t => t.total_decisions),
      orderDrift: trends.map(t => t.avg_order_drift),
      collectiveDrift: trends.map(t => t.avg_collective_drift),
      harmPressure: trends.map(t => t.avg_harm_pressure),
      recoveryStability: trends.map(t => t.avg_recovery_stability)
    };
  }, [trendsData]);

  if (loading) {
    return (
      <section 
        className="bg-gradient-to-br from-sky-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-sky-200"
        dir="rtl"
      >
        <div className="animate-pulse">
          <div className="h-6 bg-sky-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-sky-100 rounded w-2/3 mb-2"></div>
          <div className="h-40 bg-sky-100 rounded"></div>
        </div>
      </section>
    );
  }

  if (error || !trendsData) {
    return (
      <section 
        className="bg-gradient-to-br from-sky-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-sky-200"
        data-testid="collective-trends-section"
        dir="rtl"
      >
        <h3 className="text-lg font-semibold text-foreground mb-2">מגמות קולקטיביות</h3>
        <p className="text-sm text-muted-foreground">טוען נתוני מגמות...</p>
      </section>
    );
  }

  const { comparison, insights } = trendsData;
  const { current_period, previous_period, changes } = comparison;

  // Get change indicator
  const getChangeIndicator = (change) => {
    if (change > 0) return { icon: '↑', color: 'text-green-600', bg: 'bg-green-100' };
    if (change < 0) return { icon: '↓', color: 'text-red-600', bg: 'bg-red-100' };
    return { icon: '→', color: 'text-gray-600', bg: 'bg-gray-100' };
  };

  return (
    <section 
      className="bg-gradient-to-br from-sky-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-sky-200"
      data-testid="collective-trends-section"
      dir="rtl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">מגמות קולקטיביות</h3>
          <p className="text-xs text-muted-foreground">השוואת 7 ימים אחרונים מול תקופה קודמת</p>
        </div>
        <div className="w-10 h-10 rounded-full bg-sky-200 flex items-center justify-center">
          <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
      </div>

      {/* Trend Lines Grid */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-medium text-muted-foreground mb-3">מגמות 7 ימים אחרונים</p>
        
        <div className="grid grid-cols-2 gap-4">
          {/* Order Drift Trend */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">{metricLabels.order_drift}</p>
              <p className={`text-sm font-bold ${current_period.avg_order_drift > 0 ? 'text-green-600' : current_period.avg_order_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {current_period.avg_order_drift > 0 ? '+' : ''}{current_period.avg_order_drift}
              </p>
            </div>
            <Sparkline 
              data={trendLines.orderDrift} 
              color={current_period.avg_order_drift >= 0 ? '#10b981' : '#ef4444'}
              width={80}
              height={30}
            />
          </div>

          {/* Collective Drift Trend */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">{metricLabels.collective_drift}</p>
              <p className={`text-sm font-bold ${current_period.avg_collective_drift > 0 ? 'text-green-600' : current_period.avg_collective_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {current_period.avg_collective_drift > 0 ? '+' : ''}{current_period.avg_collective_drift}
              </p>
            </div>
            <Sparkline 
              data={trendLines.collectiveDrift} 
              color={current_period.avg_collective_drift >= 0 ? '#10b981' : '#ef4444'}
              width={80}
              height={30}
            />
          </div>

          {/* Harm Pressure Trend */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">{metricLabels.harm_pressure}</p>
              <p className={`text-sm font-bold ${current_period.avg_harm_pressure < 0 ? 'text-green-600' : current_period.avg_harm_pressure > 10 ? 'text-red-600' : 'text-yellow-600'}`}>
                {current_period.avg_harm_pressure > 0 ? '+' : ''}{current_period.avg_harm_pressure}%
              </p>
            </div>
            <Sparkline 
              data={trendLines.harmPressure} 
              color={current_period.avg_harm_pressure <= 0 ? '#10b981' : '#ef4444'}
              width={80}
              height={30}
            />
          </div>

          {/* Recovery Stability Trend */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">{metricLabels.recovery_stability}</p>
              <p className={`text-sm font-bold ${current_period.avg_recovery_stability > 10 ? 'text-green-600' : current_period.avg_recovery_stability > 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
                {current_period.avg_recovery_stability > 0 ? '+' : ''}{current_period.avg_recovery_stability}%
              </p>
            </div>
            <Sparkline 
              data={trendLines.recoveryStability} 
              color={current_period.avg_recovery_stability >= 0 ? '#3b82f6' : '#ef4444'}
              width={80}
              height={30}
            />
          </div>
        </div>
      </div>

      {/* Period Comparison */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-medium text-muted-foreground mb-3">השוואת תקופות</p>
        
        {/* Value Distribution Bars */}
        <div className="mb-4">
          <div className="flex justify-center gap-4 text-xs text-muted-foreground mb-2">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-gray-300 rounded"></span>
              תקופה קודמת
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-emerald-500 rounded"></span>
              תקופה נוכחית
            </span>
          </div>
          <ValueBars 
            current={current_period.value_counts || {}}
            previous={previous_period.value_counts || {}}
          />
        </div>

        {/* Changes Grid */}
        <div className="grid grid-cols-2 gap-3 mt-4">
          {/* Order Drift Change */}
          <div className={`p-2 rounded-lg ${getChangeIndicator(changes.order_drift_change).bg}`}>
            <p className="text-xs text-muted-foreground">שינוי סחף סדר</p>
            <div className="flex items-center gap-1">
              <span className={`text-lg ${getChangeIndicator(changes.order_drift_change).color}`}>
                {getChangeIndicator(changes.order_drift_change).icon}
              </span>
              <span className={`text-sm font-bold ${getChangeIndicator(changes.order_drift_change).color}`}>
                {changes.order_drift_change > 0 ? '+' : ''}{changes.order_drift_change}
              </span>
            </div>
          </div>

          {/* Collective Drift Change */}
          <div className={`p-2 rounded-lg ${getChangeIndicator(changes.collective_drift_change).bg}`}>
            <p className="text-xs text-muted-foreground">שינוי סחף קולקטיבי</p>
            <div className="flex items-center gap-1">
              <span className={`text-lg ${getChangeIndicator(changes.collective_drift_change).color}`}>
                {getChangeIndicator(changes.collective_drift_change).icon}
              </span>
              <span className={`text-sm font-bold ${getChangeIndicator(changes.collective_drift_change).color}`}>
                {changes.collective_drift_change > 0 ? '+' : ''}{changes.collective_drift_change}
              </span>
            </div>
          </div>

          {/* Harm Pressure Change */}
          <div className={`p-2 rounded-lg ${getChangeIndicator(-changes.harm_pressure_change).bg}`}>
            <p className="text-xs text-muted-foreground">שינוי לחץ נזק</p>
            <div className="flex items-center gap-1">
              <span className={`text-lg ${getChangeIndicator(-changes.harm_pressure_change).color}`}>
                {getChangeIndicator(-changes.harm_pressure_change).icon}
              </span>
              <span className={`text-sm font-bold ${getChangeIndicator(-changes.harm_pressure_change).color}`}>
                {changes.harm_pressure_change > 0 ? '+' : ''}{changes.harm_pressure_change}%
              </span>
            </div>
          </div>

          {/* Recovery Stability Change */}
          <div className={`p-2 rounded-lg ${getChangeIndicator(changes.recovery_stability_change).bg}`}>
            <p className="text-xs text-muted-foreground">שינוי יציבות</p>
            <div className="flex items-center gap-1">
              <span className={`text-lg ${getChangeIndicator(changes.recovery_stability_change).color}`}>
                {getChangeIndicator(changes.recovery_stability_change).icon}
              </span>
              <span className={`text-sm font-bold ${getChangeIndicator(changes.recovery_stability_change).color}`}>
                {changes.recovery_stability_change > 0 ? '+' : ''}{changes.recovery_stability_change}%
              </span>
            </div>
          </div>
        </div>

        {/* Activity Change */}
        <div className="mt-3 text-center">
          <span className="text-xs text-muted-foreground">שינוי בפעילות: </span>
          <span className={`text-sm font-bold ${changes.decisions_percent > 0 ? 'text-green-600' : changes.decisions_percent < 0 ? 'text-red-600' : 'text-gray-600'}`}>
            {changes.decisions_percent > 0 ? '+' : ''}{changes.decisions_percent}%
          </span>
        </div>
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="bg-sky-100/50 border border-sky-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-sky-800 mb-2">תובנות מגמתיות:</p>
          <div className="space-y-1">
            {insights.map((insight, idx) => (
              <p key={idx} className="text-sm text-sky-700">• {insight}</p>
            ))}
          </div>
        </div>
      )}

      {/* Anonymous Notice */}
      <p className="text-xs text-center text-muted-foreground mt-4">
        כל הנתונים מוצגים באופן אנונימי ומצטבר
      </p>
    </section>
  );
}

export default function GlobalTrendSection({ trendHistory }) {
  if (!trendHistory || trendHistory.length < 2) return null;
  
  // Take last 10 sessions for visualization
  const recentSessions = trendHistory.slice(-10);
  
  // Calculate metrics for each session
  const dataPoints = recentSessions.map(session => {
    const total = session.totalDecisions || 1;
    return {
      date: session.date,
      orderDrift: (session.order + session.recovery) - (session.harm + session.avoidance),
      collectiveDrift: session.contribution - session.harm,
      harmPressure: Math.round((session.harm / total) * 100),
      recoveryStability: Math.round((session.recovery / total) * 100)
    };
  });
  
  // Calculate trend direction for each metric
  const calculateTrend = (key) => {
    if (dataPoints.length < 2) return 'stable';
    const first = dataPoints.slice(0, Math.ceil(dataPoints.length / 2));
    const second = dataPoints.slice(Math.ceil(dataPoints.length / 2));
    const firstAvg = first.reduce((sum, d) => sum + d[key], 0) / first.length;
    const secondAvg = second.reduce((sum, d) => sum + d[key], 0) / second.length;
    const diff = secondAvg - firstAvg;
    if (Math.abs(diff) < 0.5) return 'stable';
    return diff > 0 ? 'increasing' : 'decreasing';
  };
  
  const trends = {
    orderDrift: calculateTrend('orderDrift'),
    collectiveDrift: calculateTrend('collectiveDrift'),
    harmPressure: calculateTrend('harmPressure'),
    recoveryStability: calculateTrend('recoveryStability')
  };
  
  // Generate insights
  const insights = [];
  if (trends.orderDrift === 'increasing') {
    insights.push('סחף סדר עולה - אתה מתקדם לכיוון יציבות.');
  } else if (trends.orderDrift === 'decreasing') {
    insights.push('סחף סדר יורד - שים לב לאיזון.');
  }
  
  if (trends.harmPressure === 'decreasing') {
    insights.push('לחץ נזק יורד - שיפור חיובי!');
  } else if (trends.harmPressure === 'increasing') {
    insights.push('לחץ נזק עולה - כדאי להתמקד בהתאוששות.');
  }
  
  if (trends.recoveryStability === 'increasing') {
    insights.push('יציבות התאוששות מתחזקת.');
  } else if (trends.recoveryStability === 'decreasing') {
    insights.push('יציבות התאוששות נחלשת - הוסף פעולות התאוששות.');
  }
  
  if (trends.collectiveDrift === 'increasing') {
    insights.push('מגמה חיובית לכיוון תרומה חברתית.');
  }
  
  if (insights.length === 0) {
    insights.push('המגמות יציבות - המשך במסלול הנוכחי.');
  }
  
  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return '↑';
    if (trend === 'decreasing') return '↓';
    return '→';
  };
  
  const getTrendColor = (trend, isPositiveGood = true) => {
    if (trend === 'stable') return 'text-gray-500';
    if (trend === 'increasing') {
      return isPositiveGood ? 'text-green-600' : 'text-red-600';
    }
    return isPositiveGood ? 'text-red-600' : 'text-green-600';
  };
  
  return (
    <section className="bg-gradient-to-br from-rose-50 to-amber-50 rounded-3xl p-5 shadow-sm border border-rose-200" data-testid="global-trend-section">
      <h3 className="text-lg font-semibold text-foreground mb-2">מגמות לאורך זמן</h3>
      <p className="text-xs text-muted-foreground mb-4">{recentSessions.length} סשנים אחרונים</p>
      
      {/* Sparkline Charts */}
      <div className="bg-white/70 rounded-xl p-4 mb-4 space-y-4">
        <p className="text-xs text-muted-foreground mb-3">גרף מגמות</p>
        
        {/* Order Drift Sparkline */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-indigo-600 font-medium">סחף סדר</span>
            <span className="text-xs text-muted-foreground">{dataPoints[dataPoints.length - 1]?.orderDrift || 0}</span>
          </div>
          <div className="flex items-end gap-1 h-8">
            {dataPoints.map((dp, i) => {
              const val = dp.orderDrift;
              const maxVal = Math.max(...dataPoints.map(d => Math.abs(d.orderDrift)), 1);
              const height = Math.max(15, 30 + (val / maxVal) * 30);
              return (
                <div
                  key={i}
                  className="flex-1 bg-indigo-500 rounded-t transition-all"
                  style={{ 
                    height: `${height}%`,
                    opacity: 0.4 + (i / dataPoints.length) * 0.6
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* Collective Drift Sparkline */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-green-600 font-medium">סחף חברתי</span>
            <span className="text-xs text-muted-foreground">{dataPoints[dataPoints.length - 1]?.collectiveDrift || 0}</span>
          </div>
          <div className="flex items-end gap-1 h-8">
            {dataPoints.map((dp, i) => {
              const val = dp.collectiveDrift;
              const maxVal = Math.max(...dataPoints.map(d => Math.abs(d.collectiveDrift)), 1);
              const height = Math.max(15, 30 + (val / maxVal) * 30);
              return (
                <div
                  key={i}
                  className="flex-1 bg-green-500 rounded-t transition-all"
                  style={{ 
                    height: `${height}%`,
                    opacity: 0.4 + (i / dataPoints.length) * 0.6
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* Harm Pressure Sparkline */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-red-600 font-medium">לחץ נזק</span>
            <span className="text-xs text-muted-foreground">{dataPoints[dataPoints.length - 1]?.harmPressure || 0}%</span>
          </div>
          <div className="flex items-end gap-1 h-8">
            {dataPoints.map((dp, i) => {
              const val = dp.harmPressure;
              const maxVal = Math.max(...dataPoints.map(d => d.harmPressure), 1);
              const height = Math.max(15, (val / maxVal) * 100);
              return (
                <div
                  key={i}
                  className="flex-1 bg-red-500 rounded-t transition-all"
                  style={{ 
                    height: `${height}%`,
                    opacity: 0.4 + (i / dataPoints.length) * 0.6
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* Recovery Stability Sparkline */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-blue-600 font-medium">יציבות התאוששות</span>
            <span className="text-xs text-muted-foreground">{dataPoints[dataPoints.length - 1]?.recoveryStability || 0}%</span>
          </div>
          <div className="flex items-end gap-1 h-8">
            {dataPoints.map((dp, i) => {
              const val = dp.recoveryStability;
              const maxVal = Math.max(...dataPoints.map(d => d.recoveryStability), 1);
              const height = Math.max(15, (val / maxVal) * 100);
              return (
                <div
                  key={i}
                  className="flex-1 bg-blue-500 rounded-t transition-all"
                  style={{ 
                    height: `${height}%`,
                    opacity: 0.4 + (i / dataPoints.length) * 0.6
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* Timeline Labels */}
        <div className="flex justify-between text-xs text-muted-foreground pt-2 border-t border-gray-100">
          <span>ישן</span>
          <span>חדש</span>
        </div>
      </div>
      
      {/* Trend Indicators */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">סחף סדר</p>
          <div className="flex items-center justify-between">
            <span className={`text-lg font-bold ${getTrendColor(trends.orderDrift, true)}`}>
              {getTrendIcon(trends.orderDrift)}
            </span>
            <span className="text-xs text-muted-foreground">
              {trends.orderDrift === 'increasing' ? 'עולה' : trends.orderDrift === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
        </div>
        
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">סחף חברתי</p>
          <div className="flex items-center justify-between">
            <span className={`text-lg font-bold ${getTrendColor(trends.collectiveDrift, true)}`}>
              {getTrendIcon(trends.collectiveDrift)}
            </span>
            <span className="text-xs text-muted-foreground">
              {trends.collectiveDrift === 'increasing' ? 'עולה' : trends.collectiveDrift === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
        </div>
        
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">לחץ נזק</p>
          <div className="flex items-center justify-between">
            <span className={`text-lg font-bold ${getTrendColor(trends.harmPressure, false)}`}>
              {getTrendIcon(trends.harmPressure)}
            </span>
            <span className="text-xs text-muted-foreground">
              {trends.harmPressure === 'increasing' ? 'עולה' : trends.harmPressure === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
        </div>
        
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">יציבות התאוששות</p>
          <div className="flex items-center justify-between">
            <span className={`text-lg font-bold ${getTrendColor(trends.recoveryStability, true)}`}>
              {getTrendIcon(trends.recoveryStability)}
            </span>
            <span className="text-xs text-muted-foreground">
              {trends.recoveryStability === 'increasing' ? 'עולה' : trends.recoveryStability === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Trend Insight */}
      <div className="bg-rose-100/50 border border-rose-200 rounded-xl p-4">
        <p className="text-sm font-semibold text-rose-800 mb-2">תובנות מגמה</p>
        <div className="space-y-1">
          {insights.slice(0, 3).map((insight, idx) => (
            <p key={idx} className="text-sm text-rose-700">• {insight}</p>
          ))}
        </div>
      </div>
    </section>
  );
}

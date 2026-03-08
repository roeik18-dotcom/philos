import { useMemo } from 'react';

const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות',
  neutral: 'ניטרלי'
};

const valueColors = {
  contribution: 'bg-green-500',
  recovery: 'bg-blue-500',
  order: 'bg-indigo-500',
  harm: 'bg-red-500',
  avoidance: 'bg-gray-500'
};

export default function WeeklySummarySection({ trendHistory, globalStats }) {
  // Calculate weekly metrics
  const weeklyData = useMemo(() => {
    if (!trendHistory || trendHistory.length === 0) {
      return null;
    }
    
    // Get last 7 days
    const today = new Date();
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const weekSessions = trendHistory.filter(session => {
      const sessionDate = new Date(session.date);
      return sessionDate >= sevenDaysAgo;
    });
    
    if (weekSessions.length === 0) {
      return null;
    }
    
    // Aggregate metrics
    let totalDecisions = 0;
    let totalOrderDrift = 0;
    let totalCollectiveDrift = 0;
    let totalHarmPressure = 0;
    let totalRecoveryStability = 0;
    const valueCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
    
    weekSessions.forEach(session => {
      const count = session.totalDecisions || 0;
      totalDecisions += count;
      
      // Accumulate value counts
      valueCounts.contribution += session.contribution || 0;
      valueCounts.recovery += session.recovery || 0;
      valueCounts.harm += session.harm || 0;
      valueCounts.order += session.order || 0;
      valueCounts.avoidance += session.avoidance || 0;
      
      // Calculate drifts for each session
      const orderDrift = (session.order + session.recovery) - (session.harm + session.avoidance);
      const collectiveDrift = session.contribution - session.harm;
      const harmPressure = count > 0 ? (session.harm / count) * 100 : 0;
      const recoveryStability = count > 0 ? (session.recovery / count) * 100 : 0;
      
      totalOrderDrift += orderDrift;
      totalCollectiveDrift += collectiveDrift;
      totalHarmPressure += harmPressure;
      totalRecoveryStability += recoveryStability;
    });
    
    const sessionCount = weekSessions.length;
    const avgOrderDrift = Math.round(totalOrderDrift / sessionCount * 10) / 10;
    const avgCollectiveDrift = Math.round(totalCollectiveDrift / sessionCount * 10) / 10;
    const avgHarmPressure = Math.round(totalHarmPressure / sessionCount);
    const avgRecoveryStability = Math.round(totalRecoveryStability / sessionCount);
    
    // Find dominant value
    const dominantValue = Object.entries(valueCounts)
      .sort((a, b) => b[1] - a[1])[0];
    
    // Calculate trends (compare first half to second half of week)
    const midpoint = Math.ceil(weekSessions.length / 2);
    const firstHalf = weekSessions.slice(0, midpoint);
    const secondHalf = weekSessions.slice(midpoint);
    
    const calcAvg = (sessions, key) => {
      if (sessions.length === 0) return 0;
      return sessions.reduce((sum, s) => {
        const count = s.totalDecisions || 1;
        if (key === 'harmPressure') return sum + (s.harm / count) * 100;
        if (key === 'recoveryStability') return sum + (s.recovery / count) * 100;
        if (key === 'orderDrift') return sum + ((s.order + s.recovery) - (s.harm + s.avoidance));
        if (key === 'collectiveDrift') return sum + (s.contribution - s.harm);
        return sum;
      }, 0) / sessions.length;
    };
    
    const harmTrend = calcAvg(secondHalf, 'harmPressure') - calcAvg(firstHalf, 'harmPressure');
    const recoveryTrend = calcAvg(secondHalf, 'recoveryStability') - calcAvg(firstHalf, 'recoveryStability');
    const orderTrend = calcAvg(secondHalf, 'orderDrift') - calcAvg(firstHalf, 'orderDrift');
    const collectiveTrend = calcAvg(secondHalf, 'collectiveDrift') - calcAvg(firstHalf, 'collectiveDrift');
    
    return {
      sessionCount,
      totalDecisions,
      dominantValue: dominantValue[0],
      dominantValueCount: dominantValue[1],
      avgOrderDrift,
      avgCollectiveDrift,
      avgHarmPressure,
      avgRecoveryStability,
      valueCounts,
      trends: {
        harm: harmTrend < -5 ? 'decreasing' : harmTrend > 5 ? 'increasing' : 'stable',
        recovery: recoveryTrend > 5 ? 'increasing' : recoveryTrend < -5 ? 'decreasing' : 'stable',
        order: orderTrend > 1 ? 'increasing' : orderTrend < -1 ? 'decreasing' : 'stable',
        collective: collectiveTrend > 1 ? 'increasing' : collectiveTrend < -1 ? 'decreasing' : 'stable'
      }
    };
  }, [trendHistory]);

  // Generate insights
  const insights = useMemo(() => {
    if (!weeklyData) return [];
    
    const lines = [];
    const { trends, avgOrderDrift, avgCollectiveDrift, dominantValue } = weeklyData;
    
    // Direction insight
    const directions = [];
    if (avgOrderDrift > 1) directions.push('סדר');
    if (avgOrderDrift < -1) directions.push('כאוס');
    if (avgCollectiveDrift > 1) directions.push('תרומה חברתית');
    if (avgCollectiveDrift < -1) directions.push('התמקדות עצמית');
    
    if (directions.length > 0) {
      lines.push(`השבוע נע לכיוון ${directions.join(' ו')}.`);
    }
    
    // Dominant value insight
    if (dominantValue && dominantValue !== 'neutral') {
      lines.push(`הערך השולט השבוע: ${valueLabels[dominantValue]}.`);
    }
    
    // Harm trend
    if (trends.harm === 'decreasing') {
      lines.push('לחץ נזק ירד - מגמה חיובית!');
    } else if (trends.harm === 'increasing') {
      lines.push('לחץ נזק עלה - שים לב להתאוששות.');
    }
    
    // Recovery trend
    if (trends.recovery === 'increasing') {
      lines.push('יציבות התאוששות התחזקה.');
    } else if (trends.recovery === 'decreasing') {
      lines.push('יציבות התאוששות נחלשה.');
    }
    
    if (lines.length === 0) {
      lines.push('שבוע מאוזן - המשך במסלול.');
    }
    
    return lines.slice(0, 4);
  }, [weeklyData]);

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return '↑';
    if (trend === 'decreasing') return '↓';
    return '→';
  };

  const getTrendColor = (trend, isLowerBetter = false) => {
    if (trend === 'stable') return 'text-gray-500 bg-gray-100';
    if (trend === 'increasing') {
      return isLowerBetter ? 'text-red-600 bg-red-100' : 'text-green-600 bg-green-100';
    }
    return isLowerBetter ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100';
  };

  if (!weeklyData) {
    return (
      <section className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-3xl p-5 shadow-sm border border-amber-200" data-testid="weekly-summary-section">
        <h3 className="text-lg font-semibold text-foreground mb-2">סיכום שבועי</h3>
        <p className="text-xs text-muted-foreground mb-4">סקירה קוגניטיבית של 7 הימים האחרונים</p>
        <div className="text-center py-8 bg-white/50 rounded-xl">
          <p className="text-muted-foreground">אין מספיק נתונים לסיכום שבועי</p>
          <p className="text-xs text-muted-foreground mt-1">המשך להשתמש באפליקציה כדי לצבור נתונים</p>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-3xl p-5 shadow-sm border border-amber-200" data-testid="weekly-summary-section">
      <h3 className="text-lg font-semibold text-foreground mb-2">סיכום שבועי</h3>
      <p className="text-xs text-muted-foreground mb-4">סקירה קוגניטיבית של 7 הימים האחרונים</p>
      
      {/* Overview Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">סה״כ החלטות</p>
          <p className="text-2xl font-bold text-amber-600">{weeklyData.totalDecisions}</p>
        </div>
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">סשנים</p>
          <p className="text-2xl font-bold text-amber-600">{weeklyData.sessionCount}</p>
        </div>
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">ערך דומיננטי</p>
          <p className="text-sm font-bold text-amber-700">{valueLabels[weeklyData.dominantValue]}</p>
        </div>
      </div>
      
      {/* Average Metrics */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-semibold text-foreground mb-3">ממוצעים שבועיים</p>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center justify-between p-2 bg-amber-50 rounded-lg">
            <span className="text-xs text-muted-foreground">סחף סדר</span>
            <span className="text-sm font-bold text-foreground">
              {weeklyData.avgOrderDrift > 0 ? '+' : ''}{weeklyData.avgOrderDrift}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-2 bg-amber-50 rounded-lg">
            <span className="text-xs text-muted-foreground">סחף חברתי</span>
            <span className="text-sm font-bold text-foreground">
              {weeklyData.avgCollectiveDrift > 0 ? '+' : ''}{weeklyData.avgCollectiveDrift}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-2 bg-amber-50 rounded-lg">
            <span className="text-xs text-muted-foreground">לחץ נזק</span>
            <span className="text-sm font-bold text-foreground">{weeklyData.avgHarmPressure}%</span>
          </div>
          
          <div className="flex items-center justify-between p-2 bg-amber-50 rounded-lg">
            <span className="text-xs text-muted-foreground">יציבות התאוששות</span>
            <span className="text-sm font-bold text-foreground">{weeklyData.avgRecoveryStability}%</span>
          </div>
        </div>
      </div>
      
      {/* Trends */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-semibold text-foreground mb-3">מגמות השבוע</p>
        
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center justify-between p-2 rounded-lg border border-gray-100">
            <span className="text-xs text-muted-foreground">סדר</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(weeklyData.trends.order)}`}>
              {getTrendIcon(weeklyData.trends.order)} {weeklyData.trends.order === 'increasing' ? 'עולה' : weeklyData.trends.order === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-2 rounded-lg border border-gray-100">
            <span className="text-xs text-muted-foreground">חברתי</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(weeklyData.trends.collective)}`}>
              {getTrendIcon(weeklyData.trends.collective)} {weeklyData.trends.collective === 'increasing' ? 'עולה' : weeklyData.trends.collective === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-2 rounded-lg border border-gray-100">
            <span className="text-xs text-muted-foreground">נזק</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(weeklyData.trends.harm, true)}`}>
              {getTrendIcon(weeklyData.trends.harm)} {weeklyData.trends.harm === 'increasing' ? 'עולה' : weeklyData.trends.harm === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-2 rounded-lg border border-gray-100">
            <span className="text-xs text-muted-foreground">התאוששות</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(weeklyData.trends.recovery)}`}>
              {getTrendIcon(weeklyData.trends.recovery)} {weeklyData.trends.recovery === 'increasing' ? 'עולה' : weeklyData.trends.recovery === 'decreasing' ? 'יורד' : 'יציב'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Value Distribution Bar */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-semibold text-foreground mb-3">התפלגות ערכים שבועית</p>
        <div className="flex h-4 rounded-full overflow-hidden bg-gray-100">
          {Object.entries(weeklyData.valueCounts)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([tag, count]) => (
              <div
                key={tag}
                className={`h-full ${valueColors[tag]} transition-all`}
                style={{ width: `${(count / weeklyData.totalDecisions) * 100}%` }}
                title={`${valueLabels[tag]}: ${count}`}
              />
            ))}
        </div>
        <div className="flex justify-center flex-wrap gap-3 mt-2">
          {Object.entries(weeklyData.valueCounts)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([tag, count]) => (
              <div key={tag} className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${valueColors[tag]}`} />
                <span className="text-xs text-muted-foreground">{valueLabels[tag]} ({count})</span>
              </div>
            ))}
        </div>
      </div>
      
      {/* Weekly Insights */}
      <div className="bg-amber-100/50 border border-amber-200 rounded-xl p-4">
        <p className="text-sm font-semibold text-amber-800 mb-2">תובנות שבועיות</p>
        <div className="space-y-1">
          {insights.map((insight, idx) => (
            <p key={idx} className="text-sm text-amber-700">• {insight}</p>
          ))}
        </div>
      </div>
    </section>
  );
}

import { useState, useEffect } from 'react';
import { getUserId } from '../../../services/cloudSync';
import { fetchReplayInsights } from '../../../services/dataService';
import { ReplaySkeleton } from '../LoadingSkeletons';

// Hebrew value tag labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Value tag colors for bars
const valueColors = {
  contribution: 'bg-green-500',
  recovery: 'bg-blue-500',
  order: 'bg-indigo-500',
  harm: 'bg-red-500',
  avoidance: 'bg-gray-400'
};

// Value tag text colors
const valueTextColors = {
  contribution: 'text-green-700',
  recovery: 'text-blue-700',
  order: 'text-indigo-700',
  harm: 'text-red-700',
  avoidance: 'text-gray-600'
};

export default function ReplayInsightsSummarySection({ user, replayCount = 0 }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadInsights = async () => {
      // Use authenticated user ID or persistent anonymous ID
      const userId = user?.id || getUserId();

      setLoading(true);
      setError(null);

      try {
        const data = await fetchReplayInsights(userId, replayCount > 0);
        if (data.success) {
          setInsights(data);
        } else if (data.error) {
          setError('שגיאה בטעינת תובנות');
        }
      } catch (err) {
        console.error('Failed to fetch replay insights:', err);
        setError('שגיאה בחיבור לשרת');
      } finally {
        setLoading(false);
      }
    };

    loadInsights();
    
    // Refresh when user changes or new replays are added
  }, [user, replayCount]);

  // Show loading skeleton only if user might have data
  if (loading && replayCount > 0) {
    return <ReplaySkeleton />;
  }
  
  if (loading) {
    return null; // No skeleton for first load if no known replays
  }

  // Don't show section if no data
  if (!insights || insights.total_replays === 0) {
    return null;
  }

  // Calculate max for bar scaling
  const maxAltCount = Math.max(...Object.values(insights.alternative_path_counts || {}), 1);
  const totalAltCount = Object.values(insights.alternative_path_counts || {}).reduce((a, b) => a + b, 0);

  // Sort alternative paths by count
  const sortedAltPaths = Object.entries(insights.alternative_path_counts || {})
    .filter(([_, count]) => count > 0)
    .sort((a, b) => b[1] - a[1]);

  return (
    <section 
      className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-violet-200"
      dir="rtl"
      data-testid="replay-insights-summary-section"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            סיכום תובנות הפעלה חוזרת
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            {insights.total_replays} הפעלות חוזרות | {insights.recent_replay_count} בשבוע האחרון
          </p>
        </div>
      </div>

      {loading && (
        <div className="text-center py-4 text-sm text-muted-foreground">
          טוען תובנות...
        </div>
      )}

      {error && (
        <div className="text-center py-4 text-sm text-red-500">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-4">
          {/* Most Explored Alternative Paths */}
          {sortedAltPaths.length > 0 && (
            <div className="bg-white/60 rounded-xl p-4">
              <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                המסלולים החלופיים הנבדקים ביותר
              </h4>
              <div className="space-y-2">
                {sortedAltPaths.map(([tag, count]) => {
                  const percentage = totalAltCount > 0 ? Math.round((count / totalAltCount) * 100) : 0;
                  const barWidth = Math.round((count / maxAltCount) * 100);
                  
                  return (
                    <div key={tag} className="flex items-center gap-3" data-testid={`alt-path-bar-${tag}`}>
                      <span className={`text-xs font-medium w-20 ${valueTextColors[tag]}`}>
                        {valueLabels[tag]}
                      </span>
                      <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${valueColors[tag]} rounded-full transition-all duration-500`}
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground w-12 text-left">
                        {percentage}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Transition Patterns */}
          {insights.transition_patterns && insights.transition_patterns.length > 0 && (
            <div className="bg-white/60 rounded-xl p-4">
              <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
                דפוסי מעבר נפוצים
              </h4>
              <div className="space-y-2">
                {insights.transition_patterns.slice(0, 5).map((pattern, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-center gap-2 text-xs"
                    data-testid={`transition-pattern-${idx}`}
                  >
                    <span className={`px-2 py-1 rounded-full bg-opacity-20 ${valueColors[pattern.from]} bg-opacity-20 ${valueTextColors[pattern.from]}`}>
                      {valueLabels[pattern.from]}
                    </span>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                    <span className={`px-2 py-1 rounded-full bg-opacity-20 ${valueColors[pattern.to]} bg-opacity-20 ${valueTextColors[pattern.to]}`}>
                      {valueLabels[pattern.to]}
                    </span>
                    <span className="text-muted-foreground mr-auto">
                      {pattern.count} פעמים
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Blind Spots */}
          {insights.blind_spots && insights.blind_spots.length > 0 && (
            <div className="bg-amber-50/70 rounded-xl p-4 border border-amber-200">
              <h4 className="text-sm font-medium text-amber-800 mb-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                נקודות עיוורות אפשריות
              </h4>
              <div className="space-y-2">
                {insights.blind_spots.map((spot, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-center gap-2 text-xs text-amber-700"
                    data-testid={`blind-spot-${idx}`}
                  >
                    <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                    <span>
                      מעולם לא בדקת מסלול <strong>{valueLabels[spot.to]}</strong> אחרי החלטת <strong>{valueLabels[spot.from]}</strong>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Hebrew Insights */}
          {insights.insights && insights.insights.length > 0 && (
            <div className="bg-gradient-to-r from-violet-100 to-purple-100 rounded-xl p-4 border border-violet-200">
              <h4 className="text-sm font-semibold text-violet-800 mb-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                תובנות התנהגותיות
              </h4>
              <div className="space-y-3">
                {insights.insights.map((insight, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-start gap-2"
                    data-testid={`insight-text-${idx}`}
                  >
                    <span className="w-5 h-5 rounded-full bg-violet-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs font-medium text-violet-700">{idx + 1}</span>
                    </span>
                    <p className="text-sm text-violet-700 leading-relaxed">
                      {insight}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-violet-600">{insights.total_replays}</div>
              <div className="text-xs text-muted-foreground">סה״כ הפעלות</div>
            </div>
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-violet-600">
                {insights.transition_patterns?.length || 0}
              </div>
              <div className="text-xs text-muted-foreground">דפוסי מעבר</div>
            </div>
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-amber-600">
                {insights.blind_spots?.length || 0}
              </div>
              <div className="text-xs text-muted-foreground">נקודות עיוורות</div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

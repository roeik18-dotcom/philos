import { useState, useEffect } from 'react';
import { listSavedSessions, getSessionById } from '../../../services/cloudSync';

const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance',
  neutral: 'Neutral'
};

export default function SessionComparisonSection({ cloudAvailable }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [sessionA, setSessionA] = useState(null);
  const [sessionB, setSessionB] = useState(null);
  const [sessionAData, setSessionAData] = useState(null);
  const [sessionBData, setSessionBData] = useState(null);
  const [loadingComparison, setLoadingComparison] = useState(false);

  // Load sessions list when expanded
  useEffect(() => {
    if (expanded && cloudAvailable) {
      loadSessions();
    }
  }, [expanded, cloudAvailable]);

  const loadSessions = async () => {
    setLoading(true);
    const result = await listSavedSessions();
    if (result.success) {
      setSessions(result.sessions || []);
    }
    setLoading(false);
  };

  // Load full session data when selected
  const loadSessionData = async (sessionId, setData) => {
    if (!sessionId) {
      setData(null);
      return;
    }
    setLoadingComparison(true);
    const result = await getSessionById(sessionId);
    if (result.success && result.session) {
      // Calculate metrics from history
      const history = result.session.history || [];
      const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
      
      history.forEach(h => {
        if (tagCounts.hasOwnProperty(h.value_tag)) {
          tagCounts[h.value_tag]++;
        }
      });
      
      const total = history.length || 1;
      const orderDrift = (tagCounts.order + tagCounts.recovery) - (tagCounts.harm + tagCounts.avoidance);
      const collectiveDrift = tagCounts.contribution - tagCounts.harm;
      const harmPressure = Math.round((tagCounts.harm / total) * 100);
      const recoveryStability = Math.round((tagCounts.recovery / total) * 100);
      const dominantValue = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])[0];
      
      setData({
        ...result.session,
        metrics: {
          decisionCount: total,
          dominantValue: dominantValue[0],
          dominantValueCount: dominantValue[1],
          orderDrift,
          collectiveDrift,
          harmPressure,
          recoveryStability,
          tagCounts
        }
      });
    }
    setLoadingComparison(false);
  };

  useEffect(() => {
    loadSessionData(sessionA, setSessionAData);
  }, [sessionA]);

  useEffect(() => {
    loadSessionData(sessionB, setSessionBData);
  }, [sessionB]);

  // Generate comparison insights
  const generateInsights = () => {
    if (!sessionAData?.metrics || !sessionBData?.metrics) return [];
    
    const insights = [];
    const a = sessionAData.metrics;
    const b = sessionBData.metrics;
    
    // Recovery comparison
    if (b.recoveryStability > a.recoveryStability + 10) {
      insights.push('Session B shows higher recovery stability.');
    } else if (a.recoveryStability > b.recoveryStability + 10) {
      insights.push('Session A shows higher recovery stability.');
    }
    
    // Harm comparison
    if (b.harmPressure < a.harmPressure - 5) {
      insights.push('Session B shows lower harm pressure.');
    } else if (a.harmPressure < b.harmPressure - 5) {
      insights.push('Session A shows lower harm pressure.');
    }
    
    // Order drift comparison
    if (b.orderDrift > a.orderDrift + 1) {
      insights.push('Session B leans more towards order direction.');
    } else if (a.orderDrift > b.orderDrift + 1) {
      insights.push('Session A leans more towards order direction.');
    }
    
    // Collective drift comparison
    if (b.collectiveDrift > a.collectiveDrift + 1) {
      insights.push('Session B shows stronger social tendency.');
    } else if (a.collectiveDrift > b.collectiveDrift + 1) {
      insights.push('Session A shows stronger social tendency.');
    }
    
    // Decision count
    if (b.decisionCount > a.decisionCount * 1.5) {
      insights.push('Session B has more decisions.');
    } else if (a.decisionCount > b.decisionCount * 1.5) {
      insights.push('Session A has more decisions.');
    }
    
    if (insights.length === 0) {
      insights.push('Both sessions are similar in key metrics.');
    }
    
    return insights.slice(0, 3);
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Comparison bar component
  const ComparisonBar = ({ label, valueA, valueB, maxValue, unit = '', isLowerBetter = false }) => {
    const max = Math.max(valueA, valueB, maxValue || 1);
    const widthA = (valueA / max) * 100;
    const widthB = (valueB / max) * 100;
    
    const getColor = (value, isThis) => {
      if (isLowerBetter) {
        return value <= Math.min(valueA, valueB) ? 'bg-green-500' : 'bg-red-400';
      }
      return value >= Math.max(valueA, valueB) ? 'bg-green-500' : 'bg-blue-400';
    };
    
    return (
      <div className="mb-3">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>{label}</span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs w-8 text-right">A</span>
            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div 
                className={`h-full ${getColor(valueA, true)} transition-all rounded-full`}
                style={{ width: `${widthA}%` }}
              />
            </div>
            <span className="text-xs w-12 text-left font-medium">{valueA}{unit}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs w-8 text-right">B</span>
            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div 
                className={`h-full ${getColor(valueB, false)} transition-all rounded-full`}
                style={{ width: `${widthB}%` }}
              />
            </div>
            <span className="text-xs w-12 text-left font-medium">{valueB}{unit}</span>
          </div>
        </div>
      </div>
    );
  };

  if (!cloudAvailable) return null;

  return (
    <section className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-cyan-200" data-testid="session-comparison-section">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <h3 className="text-lg font-semibold text-foreground">Session Comparison</h3>
          <p className="text-xs text-muted-foreground">
            Compare two saved sessions
          </p>
        </div>
        <button className="text-2xl text-cyan-600 transition-transform" style={{ transform: expanded ? 'rotate(180deg)' : 'none' }}>
          ▼
        </button>
      </div>
      
      {expanded && (
        <div className="mt-4 space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <span className="text-muted-foreground animate-pulse">Loading sessions...</span>
            </div>
          ) : sessions.length < 2 ? (
            <div className="text-center py-8 bg-white/50 rounded-xl">
              <p className="text-muted-foreground">Need at least 2 saved sessions for comparison</p>
              <p className="text-xs text-muted-foreground mt-1">Save more sessions in the session library</p>
            </div>
          ) : (
            <>
              {/* Session Selectors */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/70 rounded-xl p-3">
                  <label className="text-xs text-muted-foreground block mb-2">Session A</label>
                  <select
                    value={sessionA || ''}
                    onChange={(e) => setSessionA(e.target.value || null)}
                    className="w-full px-3 py-2 border border-cyan-200 rounded-lg text-sm bg-white"
                    data-testid="session-a-select"
                  >
                    <option value="">Select session...</option>
                    {sessions.map(s => (
                      <option key={s.session_id} value={s.session_id} disabled={s.session_id === sessionB}>
                        {formatDate(s.date)} ({s.total_decisions} decisions)
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="bg-white/70 rounded-xl p-3">
                  <label className="text-xs text-muted-foreground block mb-2">Session B</label>
                  <select
                    value={sessionB || ''}
                    onChange={(e) => setSessionB(e.target.value || null)}
                    className="w-full px-3 py-2 border border-cyan-200 rounded-lg text-sm bg-white"
                    data-testid="session-b-select"
                  >
                    <option value="">Select session...</option>
                    {sessions.map(s => (
                      <option key={s.session_id} value={s.session_id} disabled={s.session_id === sessionA}>
                        {formatDate(s.date)} ({s.total_decisions} decisions)
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              {/* Comparison Results */}
              {loadingComparison ? (
                <div className="text-center py-8">
                  <span className="text-muted-foreground animate-pulse">Loading comparison...</span>
                </div>
              ) : sessionAData && sessionBData ? (
                <div className="space-y-4">
                  {/* Dominant Values */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/70 rounded-xl p-3 text-center">
                      <p className="text-xs text-muted-foreground mb-1">Dominant value A</p>
                      <p className="text-lg font-bold text-cyan-700">
                        {valueLabels[sessionAData.metrics.dominantValue]}
                      </p>
                    </div>
                    <div className="bg-white/70 rounded-xl p-3 text-center">
                      <p className="text-xs text-muted-foreground mb-1">Dominant value B</p>
                      <p className="text-lg font-bold text-teal-700">
                        {valueLabels[sessionBData.metrics.dominantValue]}
                      </p>
                    </div>
                  </div>
                  
                  {/* Comparison Bars */}
                  <div className="bg-white/70 rounded-xl p-4">
                    <p className="text-sm font-semibold text-foreground mb-3">Metrics Comparison</p>
                    
                    <ComparisonBar 
                      label="Number of decisions"
                      valueA={sessionAData.metrics.decisionCount}
                      valueB={sessionBData.metrics.decisionCount}
                      maxValue={20}
                    />
                    
                    <ComparisonBar 
                      label="Order Drift"
                      valueA={sessionAData.metrics.orderDrift}
                      valueB={sessionBData.metrics.orderDrift}
                      maxValue={10}
                    />
                    
                    <ComparisonBar 
                      label="Social drift"
                      valueA={sessionAData.metrics.collectiveDrift}
                      valueB={sessionBData.metrics.collectiveDrift}
                      maxValue={10}
                    />
                    
                    <ComparisonBar 
                      label="Harm Pressure"
                      valueA={sessionAData.metrics.harmPressure}
                      valueB={sessionBData.metrics.harmPressure}
                      maxValue={100}
                      unit="%"
                      isLowerBetter={true}
                    />
                    
                    <ComparisonBar 
                      label="Recovery Stability"
                      valueA={sessionAData.metrics.recoveryStability}
                      valueB={sessionBData.metrics.recoveryStability}
                      maxValue={100}
                      unit="%"
                    />
                  </div>
                  
                  {/* Insights */}
                  <div className="bg-cyan-100/50 border border-cyan-200 rounded-xl p-4">
                    <p className="text-sm font-semibold text-cyan-800 mb-2">Comparison insights</p>
                    <div className="space-y-1">
                      {generateInsights().map((insight, idx) => (
                        <p key={idx} className="text-sm text-cyan-700">• {insight}</p>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 bg-white/50 rounded-xl">
                  <p className="text-muted-foreground">Select two sessions for comparison</p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </section>
  );
}

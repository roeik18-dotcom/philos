import { useState, useEffect } from 'react';
import { fetchCollectiveLayer } from '../../../services/dataService';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Colors for value tags
const valueColors = {
  contribution: { bg: 'bg-green-500', light: 'bg-green-100', text: 'text-green-700' },
  recovery: { bg: 'bg-blue-500', light: 'bg-blue-100', text: 'text-blue-700' },
  order: { bg: 'bg-indigo-500', light: 'bg-indigo-100', text: 'text-indigo-700' },
  harm: { bg: 'bg-red-500', light: 'bg-red-100', text: 'text-red-700' },
  avoidance: { bg: 'bg-gray-500', light: 'bg-gray-100', text: 'text-gray-700' }
};

export default function CollectiveLayerSection() {
  const [collectiveData, setCollectiveData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadCollectiveData = async (forceRefresh = false) => {
      try {
        const data = await fetchCollectiveLayer(forceRefresh);
        if (data.success) {
          setCollectiveData(data);
          setError(null);
        } else {
          setError(data.error || 'Error loading data');
        }
      } catch (err) {
        console.error('Collective layer error:', err);
        setError('Error connecting to server');
      } finally {
        setLoading(false);
      }
    };

    loadCollectiveData();
    // Refresh every 30 seconds with force refresh
    const interval = setInterval(() => loadCollectiveData(true), 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section 
        className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-emerald-200"
      >
        <div className="animate-pulse">
          <div className="h-6 bg-emerald-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-emerald-100 rounded w-2/3 mb-2"></div>
          <div className="h-32 bg-emerald-100 rounded"></div>
        </div>
      </section>
    );
  }

  if (error || !collectiveData) {
    return (
      <section 
        className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-emerald-200"
        data-testid="collective-layer-section"
      >
        <h3 className="text-lg font-semibold text-foreground mb-2">Collective Field</h3>
        <p className="text-sm text-muted-foreground">Loading collective data...</p>
      </section>
    );
  }

  const { 
    total_users, 
    total_decisions, 
    value_counts, 
    avg_order_drift, 
    avg_collective_drift, 
    avg_harm_pressure, 
    avg_recovery_stability,
    dominant_value,
    dominant_direction,
    insights 
  } = collectiveData;

  // Calculate max for normalization
  const positiveValues = ['contribution', 'recovery', 'order'];
  const maxCount = Math.max(...Object.values(value_counts), 1);

  return (
    <section 
      className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-emerald-200"
      data-testid="collective-layer-section"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Collective Field</h3>
          <p className="text-xs text-muted-foreground">Anonymous data from all users</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-emerald-600 bg-emerald-100 px-2 py-1 rounded-full">
            {total_users} users
          </span>
          <span className="text-xs text-emerald-600 bg-emerald-100 px-2 py-1 rounded-full">
            {total_decisions} decisions
          </span>
        </div>
      </div>

      {/* Value Distribution Visualization - Clustered Circles */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-medium text-muted-foreground mb-3">Collective Value Distribution</p>
        
        {/* Circles Visualization */}
        <div className="flex items-end justify-center gap-4 h-40">
          {positiveValues.map(value => {
            const count = value_counts[value] || 0;
            const size = Math.max(30, Math.min(100, (count / maxCount) * 100));
            const colors = valueColors[value];
            
            return (
              <div key={value} className="flex flex-col items-center gap-2">
                <div 
                  className={`${colors.bg} rounded-full flex items-center justify-center text-white font-bold transition-all shadow-lg`}
                  style={{ 
                    width: `${size}px`, 
                    height: `${size}px`,
                    fontSize: size > 50 ? '14px' : '10px'
                  }}
                >
                  {count}
                </div>
                <span className={`text-xs font-medium ${colors.text}`}>
                  {valueLabels[value]}
                </span>
              </div>
            );
          })}
        </div>

        {/* Negative values (smaller) */}
        <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-200">
          {['harm', 'avoidance'].map(value => {
            const count = value_counts[value] || 0;
            const colors = valueColors[value];
            
            return (
              <div key={value} className="flex items-center gap-2">
                <div 
                  className={`${colors.bg} rounded-full flex items-center justify-center text-white text-xs font-bold w-8 h-8`}
                >
                  {count}
                </div>
                <span className={`text-xs ${colors.text}`}>
                  {valueLabels[value]}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Order Drift */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Average Order Drift</p>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${avg_order_drift > 0 ? 'text-green-600' : avg_order_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
              {avg_order_drift > 0 ? '+' : ''}{avg_order_drift}
            </span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${avg_order_drift > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(100, Math.abs(avg_order_drift) * 3)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Collective Drift */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Average Collective Drift</p>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${avg_collective_drift > 0 ? 'text-green-600' : avg_collective_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
              {avg_collective_drift > 0 ? '+' : ''}{avg_collective_drift}
            </span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${avg_collective_drift > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(100, Math.abs(avg_collective_drift) * 3)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Harm Pressure */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Average Harm Pressure</p>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${avg_harm_pressure < 0 ? 'text-green-600' : avg_harm_pressure > 10 ? 'text-red-600' : 'text-yellow-600'}`}>
              {avg_harm_pressure > 0 ? '+' : ''}{avg_harm_pressure}%
            </span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${avg_harm_pressure < 0 ? 'bg-green-500' : avg_harm_pressure > 10 ? 'bg-red-500' : 'bg-yellow-500'}`}
                style={{ width: `${Math.min(100, Math.abs(avg_harm_pressure) * 3)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Recovery Stability */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Recovery Stability</p>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${avg_recovery_stability > 10 ? 'text-green-600' : avg_recovery_stability > 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
              {avg_recovery_stability > 0 ? '+' : ''}{avg_recovery_stability}%
            </span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${avg_recovery_stability > 10 ? 'bg-green-500' : avg_recovery_stability > 0 ? 'bg-blue-500' : 'bg-yellow-500'}`}
                style={{ width: `${Math.min(100, Math.abs(avg_recovery_stability) * 3)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Dominant Indicators */}
      <div className="flex flex-wrap gap-2 mb-4">
        {dominant_value && (
          <div className={`px-3 py-1.5 rounded-full text-sm font-medium ${valueColors[dominant_value]?.light} ${valueColors[dominant_value]?.text}`}>
            Dominant value: {valueLabels[dominant_value]}
          </div>
        )}
        {dominant_direction && dominant_direction !== 'balanced' && (
          <div className="px-3 py-1.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">
            Direction: {dominant_direction === 'order' ? 'Order' : dominant_direction === 'collective' ? 'Collective' : dominant_direction === 'ego' ? 'Ego' : 'Chaos'}
          </div>
        )}
        {dominant_direction === 'balanced' && (
          <div className="px-3 py-1.5 rounded-full text-sm font-medium bg-emerald-100 text-emerald-700">
            Direction: Balanced
          </div>
        )}
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="bg-emerald-100/50 border border-emerald-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-emerald-800 mb-2">Collective insights:</p>
          <div className="space-y-1">
            {insights.map((insight, idx) => (
              <p key={idx} className="text-sm text-emerald-700">• {insight}</p>
            ))}
          </div>
        </div>
      )}

      {/* Anonymous Notice */}
      <p className="text-xs text-center text-muted-foreground mt-4">
        All data is displayed anonymously and in aggregate
      </p>
    </section>
  );
}

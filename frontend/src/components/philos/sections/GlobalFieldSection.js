import { useState, useEffect, useMemo } from 'react';
import { fetchCollectiveLayer } from '../../../services/dataService';

// Hebrew labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Colors for values
const valueColors = {
  contribution: '#10b981', // green
  recovery: '#3b82f6',     // blue
  order: '#6366f1',        // indigo
  harm: '#ef4444',         // red
  avoidance: '#6b7280'     // gray
};

// SVG Field Visualization Component
const FieldVisualization = ({ data }) => {
  const width = 320;
  const height = 280;
  const centerX = width / 2;
  const centerY = height / 2;

  // Calculate field positions based on data
  const fieldData = useMemo(() => {
    if (!data) return null;

    const { value_counts, avg_order_drift, avg_collective_drift, avg_harm_pressure, avg_recovery_stability } = data;
    const total = Object.values(value_counts).reduce((a, b) => a + b, 1);

    // Normalize values
    const normalize = (val, max = 100) => Math.min(1, Math.max(0, (val + max) / (2 * max)));

    // Calculate positions on the field
    // X-axis: chaos (-) to order (+)
    // Y-axis: ego (-) to collective (+)
    const orderPosition = normalize(avg_order_drift, 30) * 0.8 + 0.1; // 0.1 to 0.9
    const collectivePosition = normalize(avg_collective_drift, 30) * 0.8 + 0.1;

    // Value cluster sizes
    const clusters = Object.entries(value_counts).map(([key, count]) => ({
      key,
      count,
      size: Math.max(15, Math.min(50, (count / total) * 200 + 15)),
      color: valueColors[key],
      label: valueLabels[key]
    }));

    // Harm and recovery zone intensities
    const harmIntensity = Math.max(0, avg_harm_pressure / 30);
    const recoveryIntensity = Math.max(0, avg_recovery_stability / 30);

    return {
      orderPosition,
      collectivePosition,
      clusters,
      harmIntensity,
      recoveryIntensity,
      direction: avg_order_drift > 5 ? 'order' : avg_order_drift < -5 ? 'chaos' : 'balanced'
    };
  }, [data]);

  if (!fieldData) {
    return (
      <svg width={width} height={height} className="opacity-30">
        <rect x="0" y="0" width={width} height={height} fill="#f0f9ff" rx="16" />
        <text x={centerX} y={centerY} textAnchor="middle" fill="#94a3b8" fontSize="14">טוען...</text>
      </svg>
    );
  }

  const { orderPosition, collectivePosition, clusters, harmIntensity, recoveryIntensity, direction } = fieldData;

  // Calculate cluster positions around center
  const getClusterPosition = (index, total) => {
    const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
    const radius = 80;
    return {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius
    };
  };

  // Direction indicator position
  const directionX = centerX + (orderPosition - 0.5) * (width - 80);
  const directionY = centerY - (collectivePosition - 0.5) * (height - 80);

  return (
    <svg width={width} height={height} className="mx-auto">
      <defs>
        {/* Gradient for harm zone */}
        <radialGradient id="harmGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ef4444" stopOpacity={harmIntensity * 0.5} />
          <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
        </radialGradient>
        {/* Gradient for recovery zone */}
        <radialGradient id="recoveryGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity={recoveryIntensity * 0.5} />
          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
        </radialGradient>
        {/* Gradient for order zone */}
        <linearGradient id="orderGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6b7280" stopOpacity="0.1" />
          <stop offset="100%" stopColor="#6366f1" stopOpacity="0.2" />
        </linearGradient>
        {/* Glow filter */}
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Background */}
      <rect x="0" y="0" width={width} height={height} fill="#f8fafc" rx="16" />
      
      {/* Order/Chaos gradient background */}
      <rect x="10" y="10" width={width - 20} height={height - 20} fill="url(#orderGradient)" rx="12" />

      {/* Grid lines */}
      <line x1={centerX} y1="20" x2={centerX} y2={height - 20} stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4" />
      <line x1="20" y1={centerY} x2={width - 20} y2={centerY} stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4" />

      {/* Harm pressure zone (bottom-left) */}
      <ellipse 
        cx="60" 
        cy={height - 60} 
        rx="50" 
        ry="50" 
        fill="url(#harmGradient)"
      />
      
      {/* Recovery zone (top-right) */}
      <ellipse 
        cx={width - 60} 
        cy="60" 
        rx="50" 
        ry="50" 
        fill="url(#recoveryGradient)"
      />

      {/* Value clusters */}
      {clusters.filter(c => c.count > 0).map((cluster, i) => {
        const pos = getClusterPosition(i, clusters.filter(c => c.count > 0).length);
        return (
          <g key={cluster.key}>
            <circle
              cx={pos.x}
              cy={pos.y}
              r={cluster.size}
              fill={cluster.color}
              opacity="0.7"
              filter="url(#glow)"
            />
            <text
              x={pos.x}
              y={pos.y + cluster.size + 14}
              textAnchor="middle"
              fill="#475569"
              fontSize="10"
              fontWeight="500"
            >
              {cluster.label}
            </text>
            <text
              x={pos.x}
              y={pos.y + 4}
              textAnchor="middle"
              fill="white"
              fontSize="12"
              fontWeight="bold"
            >
              {cluster.count}
            </text>
          </g>
        );
      })}

      {/* Direction indicator (pulsing dot) */}
      <circle
        cx={directionX}
        cy={directionY}
        r="8"
        fill="#f59e0b"
        opacity="0.9"
        filter="url(#glow)"
      >
        <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.9;0.5;0.9" dur="2s" repeatCount="indefinite" />
      </circle>

      {/* Axis labels */}
      <text x={width - 25} y={centerY - 8} textAnchor="end" fill="#6366f1" fontSize="10" fontWeight="bold">סדר</text>
      <text x="25" y={centerY - 8} textAnchor="start" fill="#6b7280" fontSize="10" fontWeight="bold">כאוס</text>
      <text x={centerX} y="22" textAnchor="middle" fill="#10b981" fontSize="10" fontWeight="bold">קולקטיב</text>
      <text x={centerX} y={height - 12} textAnchor="middle" fill="#f59e0b" fontSize="10" fontWeight="bold">אגו</text>

      {/* Legend indicators */}
      <g transform={`translate(${width - 45}, ${height - 45})`}>
        <circle cx="0" cy="0" r="6" fill="#3b82f6" opacity="0.5" />
        <text x="10" y="4" fill="#64748b" fontSize="8">התאוששות</text>
      </g>
      <g transform="translate(25, 235)">
        <circle cx="0" cy="0" r="6" fill="#ef4444" opacity="0.5" />
        <text x="10" y="4" fill="#64748b" fontSize="8">נזק</text>
      </g>
    </svg>
  );
};

export default function GlobalFieldSection() {
  const [fieldData, setFieldData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadFieldData = async (forceRefresh = false) => {
      try {
        const data = await fetchCollectiveLayer(forceRefresh);
        if (data.success) {
          setFieldData(data);
          setError(null);
        } else {
          setError(data.error || 'שגיאה בטעינת נתונים');
        }
      } catch (err) {
        console.error('Global field error:', err);
        setError('שגיאה בחיבור לשרת');
      } finally {
        setLoading(false);
      }
    };

    loadFieldData();
    // Refresh every 30 seconds with force refresh
    const interval = setInterval(() => loadFieldData(true), 30000);
    return () => clearInterval(interval);
  }, []);

  // Generate insight based on field state
  const insight = useMemo(() => {
    if (!fieldData) return '';

    const { dominant_value, dominant_direction, avg_harm_pressure, avg_recovery_stability } = fieldData;
    const insights = [];

    // Direction insight
    if (dominant_direction === 'order') {
      insights.push('השדה העולמי נוטה לכיוון סדר ומבנה.');
    } else if (dominant_direction === 'collective') {
      insights.push('השדה העולמי נוטה לכיוון קולקטיבי.');
    } else if (dominant_direction === 'balanced') {
      insights.push('השדה העולמי מאוזן יחסית.');
    }

    // Harm/Recovery insight
    if (avg_harm_pressure < -5) {
      insights.push('אזור הנזק חלש - מצב בריא.');
    } else if (avg_harm_pressure > 10) {
      insights.push('יש לחץ נזק גבוה בשדה.');
    }

    if (avg_recovery_stability > 15) {
      insights.push('אזור ההתאוששות חזק.');
    }

    return insights.join(' ');
  }, [fieldData]);

  // Determine field state description
  const fieldState = useMemo(() => {
    if (!fieldData) return { label: 'טוען...', color: 'text-gray-500' };

    const { avg_harm_pressure, avg_recovery_stability, avg_order_drift } = fieldData;

    if (avg_harm_pressure > 10) {
      return { label: 'מצב מתוח', color: 'text-red-600' };
    }
    if (avg_recovery_stability > 15 && avg_harm_pressure < 0) {
      return { label: 'מצב בריא', color: 'text-green-600' };
    }
    if (avg_order_drift > 10) {
      return { label: 'מצב מאורגן', color: 'text-indigo-600' };
    }
    return { label: 'מצב מאוזן', color: 'text-blue-600' };
  }, [fieldData]);

  if (loading) {
    return (
      <section 
        className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-slate-200"
        dir="rtl"
      >
        <div className="animate-pulse">
          <div className="h-6 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-slate-100 rounded"></div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section 
        className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-slate-200"
        data-testid="global-field-section"
        dir="rtl"
      >
        <h3 className="text-lg font-semibold text-foreground mb-2">שדה עולמי</h3>
        <p className="text-sm text-muted-foreground">שגיאה בטעינת נתונים</p>
      </section>
    );
  }

  return (
    <section 
      className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-slate-200"
      data-testid="global-field-section"
      dir="rtl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">שדה עולמי</h3>
          <p className="text-xs text-muted-foreground">מפת הערכים הקולקטיבית החיה</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${fieldState.color}`}>
            {fieldState.label}
          </span>
          <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center">
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Field Visualization */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <FieldVisualization data={fieldData} />
      </div>

      {/* Field Metrics */}
      {fieldData && (
        <div className="grid grid-cols-4 gap-2 mb-4">
          <div className="bg-white/70 rounded-xl p-2 text-center">
            <p className="text-xs text-muted-foreground">סחף סדר</p>
            <p className={`text-sm font-bold ${fieldData.avg_order_drift > 0 ? 'text-indigo-600' : 'text-gray-600'}`}>
              {fieldData.avg_order_drift > 0 ? '+' : ''}{fieldData.avg_order_drift}
            </p>
          </div>
          <div className="bg-white/70 rounded-xl p-2 text-center">
            <p className="text-xs text-muted-foreground">סחף קולקטיבי</p>
            <p className={`text-sm font-bold ${fieldData.avg_collective_drift > 0 ? 'text-green-600' : 'text-gray-600'}`}>
              {fieldData.avg_collective_drift > 0 ? '+' : ''}{fieldData.avg_collective_drift}
            </p>
          </div>
          <div className="bg-white/70 rounded-xl p-2 text-center">
            <p className="text-xs text-muted-foreground">לחץ נזק</p>
            <p className={`text-sm font-bold ${fieldData.avg_harm_pressure < 0 ? 'text-green-600' : 'text-red-600'}`}>
              {fieldData.avg_harm_pressure}%
            </p>
          </div>
          <div className="bg-white/70 rounded-xl p-2 text-center">
            <p className="text-xs text-muted-foreground">התאוששות</p>
            <p className={`text-sm font-bold ${fieldData.avg_recovery_stability > 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
              +{fieldData.avg_recovery_stability}%
            </p>
          </div>
        </div>
      )}

      {/* Insight */}
      {insight && (
        <div className="bg-slate-100/50 border border-slate-200 rounded-xl p-3">
          <p className="text-sm text-slate-700 text-center">{insight}</p>
        </div>
      )}

      {/* Anonymous notice */}
      <p className="text-xs text-center text-muted-foreground mt-3">
        כל הנתונים מוצגים באופן אנונימי
      </p>
    </section>
  );
}

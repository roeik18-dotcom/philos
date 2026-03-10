import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Direction configuration
const directionConfig = {
  contribution: { 
    label: 'תרומה', 
    color: '#22c55e', 
    bgClass: 'bg-green-500',
    lightBg: 'bg-green-100'
  },
  recovery: { 
    label: 'התאוששות', 
    color: '#3b82f6', 
    bgClass: 'bg-blue-500',
    lightBg: 'bg-blue-100'
  },
  order: { 
    label: 'סדר', 
    color: '#6366f1', 
    bgClass: 'bg-indigo-500',
    lightBg: 'bg-indigo-100'
  },
  exploration: { 
    label: 'חקירה', 
    color: '#f59e0b', 
    bgClass: 'bg-amber-500',
    lightBg: 'bg-amber-100'
  }
};

// Display order
const displayOrder = ['contribution', 'recovery', 'order', 'exploration'];

export default function OrientationFieldToday() {
  const [fieldData, setFieldData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch field data
  useEffect(() => {
    const fetchFieldToday = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/orientation/field-today`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setFieldData(data);
          }
        }
      } catch (error) {
        console.log('Could not fetch field today:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchFieldToday();
  }, []);

  if (loading && !fieldData) {
    return (
      <section className="bg-white rounded-3xl p-5 shadow-sm border border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-6 bg-gray-200 rounded"></div>
          ))}
        </div>
      </section>
    );
  }

  if (!fieldData) {
    return null;
  }

  return (
    <section 
      className="bg-white rounded-3xl p-5 shadow-sm border border-border"
      dir="rtl"
      data-testid="orientation-field-today"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-800">שדה ההתמצאות היום</h3>
            <p className="text-[10px] text-gray-500">
              {fieldData.active_users > 0 
                ? `${fieldData.active_users} משתמשים פעילים · ${fieldData.total_actions} פעולות`
                : 'מבוסס על נתונים היסטוריים'}
            </p>
          </div>
        </div>
      </div>

      {/* Distribution Bars */}
      <div className="space-y-3" data-testid="distribution-bars">
        {displayOrder.map(direction => {
          const config = directionConfig[direction];
          const percentage = fieldData.distribution[direction] || 0;
          const isDominant = direction === fieldData.dominant_direction;
          
          return (
            <div key={direction} className="space-y-1">
              {/* Label row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: config.color }}
                  />
                  <span className={`text-xs ${isDominant ? 'font-semibold text-gray-800' : 'text-gray-600'}`}>
                    {config.label}
                  </span>
                  {isDominant && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-violet-100 text-violet-700">
                      מוביל
                    </span>
                  )}
                </div>
                <span className={`text-xs font-medium ${isDominant ? 'text-gray-800' : 'text-gray-500'}`}>
                  {percentage}%
                </span>
              </div>
              
              {/* Progress bar */}
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-700 ease-out"
                  style={{ 
                    width: `${percentage}%`,
                    backgroundColor: config.color
                  }}
                  data-testid={`bar-${direction}`}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Insight */}
      {fieldData.insight && (
        <div className="mt-4 p-3 rounded-xl bg-violet-50 border border-violet-100">
          <p className="text-xs text-violet-700" data-testid="field-insight">
            {fieldData.insight}
          </p>
        </div>
      )}
    </section>
  );
}

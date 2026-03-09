import { useState } from 'react';

// Hebrew value tag labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Value tag colors
const valueColors = {
  contribution: 'bg-green-100 text-green-700',
  recovery: 'bg-blue-100 text-blue-700',
  order: 'bg-indigo-100 text-indigo-700',
  harm: 'bg-red-100 text-red-700',
  avoidance: 'bg-gray-100 text-gray-600'
};

export default function DecisionHistorySection({ history, onAddFollowUp, onReplayDecision }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!history || history.length === 0) {
    return null;
  }

  // Build chain information
  const getChainInfo = (item) => {
    if (!item.parent_decision_id) return null;
    const parent = history.find(h => h.id === item.parent_decision_id);
    return parent ? parent.action : null;
  };

  // Count children for each decision
  const getChildCount = (itemId) => {
    return history.filter(h => h.parent_decision_id === itemId).length;
  };

  return (
    <section 
      className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-5 shadow-sm border border-amber-200"
      dir="rtl"
      data-testid="decision-history-section"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">היסטוריית החלטות</h3>
          <p className="text-xs text-muted-foreground">{history.length} החלטות בסשן</p>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {history.map((item, idx) => {
          const childCount = getChildCount(item.id);
          const parentAction = getChainInfo(item);
          const isExpanded = expandedId === item.id;

          return (
            <div
              key={item.id || idx}
              className={`bg-white/70 rounded-xl p-3 transition-all ${
                item.parent_decision_id ? 'mr-4 border-r-2 border-amber-300' : ''
              }`}
              data-testid={`history-item-${idx}`}
            >
              {/* Parent reference */}
              {parentAction && (
                <div className="text-xs text-amber-600 mb-1 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                  </svg>
                  <span>המשך ל: {parentAction.slice(0, 30)}{parentAction.length > 30 ? '...' : ''}</span>
                </div>
              )}

              {/* Main content */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {item.action}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${valueColors[item.value_tag] || 'bg-gray-100 text-gray-600'}`}>
                      {valueLabels[item.value_tag] || item.value_tag}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {item.time}
                    </span>
                    {childCount > 0 && (
                      <span className="text-xs text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full">
                        {childCount} המשכים
                      </span>
                    )}
                  </div>
                </div>

                {/* Decision status */}
                <span className={`px-2 py-1 rounded-lg text-xs font-medium ${
                  item.decision === 'Allowed' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {item.decision === 'Allowed' ? 'מאושר' : 'נחסם'}
                </span>
              </div>

              {/* Metrics (collapsed by default) */}
              {isExpanded && (
                <div className="mt-2 pt-2 border-t border-gray-100 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-muted-foreground">סדר/כאוס:</span>
                    <span className="font-medium mr-1">{item.chaos_order}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">אגו/קולקטיב:</span>
                    <span className="font-medium mr-1">{item.ego_collective}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">איזון:</span>
                    <span className="font-medium mr-1">{item.balance_score}</span>
                  </div>
                </div>
              )}

              {/* Actions row */}
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-100">
                <button
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  {isExpanded ? 'פחות' : 'עוד'}
                </button>
                
                <button
                  onClick={() => onAddFollowUp(item)}
                  className="flex items-center gap-1 text-xs text-amber-600 hover:text-amber-800 hover:bg-amber-50 px-2 py-1 rounded-lg transition-colors"
                  data-testid={`followup-btn-${idx}`}
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>הוסף המשך</span>
                </button>
                
                <button
                  onClick={() => onReplayDecision && onReplayDecision(item)}
                  className="flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 hover:bg-purple-50 px-2 py-1 rounded-lg transition-colors"
                  data-testid={`replay-btn-${idx}`}
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>בדוק מסלול חלופי</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Chain legend */}
      <div className="mt-3 pt-3 border-t border-amber-200 flex items-center gap-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-2 h-4 border-r-2 border-amber-300"></div>
          <span>החלטת המשך</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-600">N</span>
          <span>מספר המשכים</span>
        </div>
      </div>
    </section>
  );
}

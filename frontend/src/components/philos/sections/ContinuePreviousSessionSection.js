import { useMemo } from 'react';

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
  contribution: 'bg-green-100 text-green-700 border-green-300',
  recovery: 'bg-blue-100 text-blue-700 border-blue-300',
  order: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  harm: 'bg-red-100 text-red-700 border-red-300',
  avoidance: 'bg-gray-100 text-gray-600 border-gray-300'
};

// Format relative time in Hebrew
const formatRelativeTime = (timestamp) => {
  if (!timestamp) return '';
  
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'לפני רגע';
  if (diffMins < 60) return `לפני ${diffMins} דקות`;
  if (diffHours < 24) return `לפני ${diffHours} שעות`;
  if (diffDays === 1) return 'אתמול';
  if (diffDays < 7) return `לפני ${diffDays} ימים`;
  if (diffDays < 30) return `לפני ${Math.floor(diffDays / 7)} שבועות`;
  return `לפני ${Math.floor(diffDays / 30)} חודשים`;
};

// Calculate dominant pattern from history
const calculateDominantPattern = (history) => {
  if (!history || history.length < 3) return null;
  
  const counts = {};
  history.slice(0, 10).forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      counts[tag] = (counts[tag] || 0) + 1;
    }
  });
  
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  if (sorted.length > 0 && sorted[0][1] >= 2) {
    return sorted[0][0];
  }
  return null;
};

export default function ContinuePreviousSessionSection({ history, onContinue }) {
  // Calculate session data
  const sessionData = useMemo(() => {
    if (!history || history.length === 0) {
      return null;
    }

    // Get last decision
    const lastDecision = history[0];
    const dominantPattern = calculateDominantPattern(history);
    
    // Calculate session stats
    const totalDecisions = history.length;
    const todayDecisions = history.filter(item => {
      const itemDate = new Date(item.timestamp || item.time);
      const today = new Date();
      return itemDate.toDateString() === today.toDateString();
    }).length;

    return {
      lastDecision,
      lastAction: lastDecision.action || lastDecision.decision_data?.action || '',
      lastValueTag: lastDecision.value_tag || lastDecision.decision_data?.value_tag,
      lastTimestamp: lastDecision.timestamp || lastDecision.time,
      dominantPattern,
      totalDecisions,
      todayDecisions,
      hasChains: history.some(item => item.parent_decision_id)
    };
  }, [history]);

  // Don't render if no session data or this is a new user
  if (!sessionData) {
    return null;
  }

  const handleContinue = () => {
    // Scroll to action input
    const actionInput = document.querySelector('[data-testid="action-input"]');
    if (actionInput) {
      actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => {
        actionInput.focus();
      }, 500);
    }
    
    // Call parent callback if provided
    if (onContinue) {
      onContinue(sessionData);
    }
  };

  return (
    <section 
      className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-5 shadow-sm border border-amber-200 mb-4"
      dir="rtl"
      data-testid="continue-session-section"
    >
      {/* Header with welcome back message */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              המשך מהמפגש הקודם
            </h3>
            <p className="text-sm text-amber-700">
              המערכת זיהתה שכבר התחלת תהליך קודם
            </p>
          </div>
        </div>
        
        {/* Stats badges */}
        <div className="flex gap-2">
          <div className="bg-white/70 rounded-lg px-3 py-1.5 text-center border border-amber-200">
            <div className="text-lg font-bold text-amber-700">{sessionData.totalDecisions}</div>
            <div className="text-xs text-muted-foreground">החלטות</div>
          </div>
          {sessionData.todayDecisions > 0 && (
            <div className="bg-white/70 rounded-lg px-3 py-1.5 text-center border border-amber-200">
              <div className="text-lg font-bold text-amber-600">{sessionData.todayDecisions}</div>
              <div className="text-xs text-muted-foreground">היום</div>
            </div>
          )}
        </div>
      </div>

      {/* Last decision card */}
      <div className="bg-white/60 rounded-xl p-4 mb-4 border border-amber-200">
        <div className="flex items-center gap-2 mb-2">
          <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span className="text-sm font-medium text-foreground">ההחלטה האחרונה שלך הייתה:</span>
          <span className="text-xs text-muted-foreground mr-auto">
            {formatRelativeTime(sessionData.lastTimestamp)}
          </span>
        </div>
        
        <p className="text-base text-foreground mb-3 pr-6" data-testid="last-decision-text">
          "{sessionData.lastAction}"
        </p>
        
        <div className="flex items-center gap-3 pr-6">
          {sessionData.lastValueTag && (
            <span 
              className={`px-3 py-1 rounded-full text-xs font-medium border ${valueColors[sessionData.lastValueTag] || 'bg-gray-100'}`}
              data-testid="last-value-tag"
            >
              {valueLabels[sessionData.lastValueTag] || sessionData.lastValueTag}
            </span>
          )}
          
          {sessionData.dominantPattern && (
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              דפוס שולט: 
              <span className="font-medium">{valueLabels[sessionData.dominantPattern]}</span>
            </span>
          )}
          
          {sessionData.hasChains && (
            <span className="text-xs text-amber-600 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              יש שרשראות החלטות
            </span>
          )}
        </div>
      </div>

      {/* Continue message and button */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-amber-700">
          ניתן להמשיך מאותה נקודה בדיוק
        </p>
        
        <button
          onClick={handleContinue}
          className="bg-amber-500 hover:bg-amber-600 text-white px-5 py-2.5 rounded-xl font-medium transition-colors flex items-center gap-2 shadow-sm"
          data-testid="continue-session-btn"
        >
          <span>המשך מכאן</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      </div>
    </section>
  );
}

import { useState, useEffect } from 'react';
import { getUserDecisionStats } from '../../services/cloudSync';

// Decision templates with guiding questions
const DECISION_TEMPLATES = [
  { id: 'personal', label: 'אישי', icon: '👤', prompt: 'מהי הפעולה שאני שוקל כרגע?' },
  { id: 'social', label: 'חברתי', icon: '👥', prompt: 'איך בחרתי להגיב באינטראקציה החברתית?' },
  { id: 'work', label: 'עבודה', icon: '💼', prompt: 'מה עשיתי כדי להתקדם במשימה?' },
  { id: 'emotional', label: 'רגשי', icon: '💭', prompt: 'איך הגבתי לרגש שהרגשתי?' },
  { id: 'ethical', label: 'אתי', icon: '⚖️', prompt: 'מה הייתה ההחלטה המוסרית שקיבלתי?' }
];

export default function QuickDecisionButton({ onSubmit }) {
  const [isOpen, setIsOpen] = useState(false);
  const [quickAction, setQuickAction] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [stats, setStats] = useState({ today_decisions: 0, total_decisions: 0 });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch stats on mount and after submissions
  useEffect(() => {
    const fetchStats = async () => {
      const result = await getUserDecisionStats();
      if (result.success !== false) {
        setStats(result);
      }
    };
    fetchStats();
  }, []);

  const handleSubmit = async () => {
    if (!quickAction.trim()) return;
    
    setIsSubmitting(true);
    await onSubmit(quickAction.trim());
    setQuickAction('');
    setSelectedTemplate(null);
    setIsSubmitting(false);
    setIsOpen(false);
    
    // Update stats after submission
    const result = await getUserDecisionStats();
    if (result.success !== false) {
      setStats(result);
    }
  };

  const handleTemplateSelect = (template) => {
    if (selectedTemplate?.id === template.id) {
      // Deselect if clicking same template
      setSelectedTemplate(null);
      setQuickAction('');
    } else {
      setSelectedTemplate(template);
      setQuickAction(template.prompt + ' ');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    if (e.key === 'Escape') {
      setIsOpen(false);
      setQuickAction('');
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 left-6 z-50 w-14 h-14 rounded-full shadow-lg transition-all duration-300 flex items-center justify-center ${
          isOpen 
            ? 'bg-red-500 hover:bg-red-600 rotate-45' 
            : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-110'
        }`}
        data-testid="quick-decision-fab"
        aria-label={isOpen ? 'סגור' : 'החלטה מהירה'}
      >
        <svg 
          className="w-6 h-6 text-white" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 4v16m8-8H4" 
          />
        </svg>
      </button>

      {/* Stats Badge */}
      {!isOpen && stats.today_decisions > 0 && (
        <div 
          className="fixed bottom-[72px] left-6 z-50 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow"
          data-testid="today-decisions-badge"
        >
          {stats.today_decisions} היום
        </div>
      )}

      {/* Expanded Quick Input Panel */}
      {isOpen && (
        <div 
          className="fixed bottom-24 left-6 z-50 w-72 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden animate-in slide-in-from-bottom-4 duration-200"
          dir="rtl"
          data-testid="quick-decision-panel"
        >
          {/* Header */}
          <div className="bg-gradient-to-l from-indigo-600 to-indigo-500 px-4 py-3">
            <h3 className="text-white font-semibold text-sm">החלטה מהירה</h3>
            <p className="text-indigo-100 text-xs">מה עשית או מתכנן לעשות?</p>
          </div>

          {/* Input */}
          <div className="p-4">
            {/* Template Selector */}
            <div className="mb-3">
              <p className="text-xs text-gray-500 mb-2">בחר סוג החלטה:</p>
              <div className="flex flex-wrap gap-1.5">
                {DECISION_TEMPLATES.map(template => (
                  <button
                    key={template.id}
                    onClick={() => handleTemplateSelect(template)}
                    className={`px-2.5 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1 ${
                      selectedTemplate?.id === template.id
                        ? 'bg-indigo-100 text-indigo-700 ring-1 ring-indigo-300'
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                    }`}
                    data-testid={`template-${template.id}`}
                  >
                    <span>{template.icon}</span>
                    <span>{template.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <textarea
              value={quickAction}
              onChange={(e) => setQuickAction(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedTemplate ? selectedTemplate.prompt : "הקלד פעולה..."}
              className="w-full h-20 px-3 py-2 text-sm border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              autoFocus
              data-testid="quick-decision-input"
            />
            
            {/* Quick suggestions */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {['הליכה', 'מנוחה', 'עזרה', 'עבודה'].map(suggestion => (
                <button
                  key={suggestion}
                  onClick={() => setQuickAction(prev => prev ? `${prev} ${suggestion}` : suggestion)}
                  className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"
                  data-testid={`suggestion-${suggestion}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={!quickAction.trim() || isSubmitting}
              className="w-full mt-3 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium text-sm rounded-xl transition-colors"
              data-testid="quick-decision-submit"
            >
              {isSubmitting ? 'שומר...' : 'הוסף החלטה'}
            </button>
          </div>

          {/* Stats Footer */}
          <div className="bg-gray-50 px-4 py-2 flex justify-between text-xs text-gray-500 border-t">
            <span>היום: {stats.today_decisions}</span>
            <span>סה״כ: {stats.total_decisions}</span>
          </div>
        </div>
      )}

      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/20"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}

import { useMemo } from 'react';

// Daily prompts that rotate based on the day
const dailyPrompts = [
  { question: 'What small decision did you make today?', placeholder: 'I decided to...' },
  { question: 'How did you react to an unexpected situation today?', placeholder: 'When ... happened, I reacted by...' },
  { question: "Was there an emotional reaction you'd like to analyze?", placeholder: 'I felt... and then...' },
  { question: 'What decision influenced your day?', placeholder: 'The decision to... affected...' },
  { question: 'What did you do to move forward today?', placeholder: 'I took a step forward when...' },
  { question: 'Did you avoid something today?', placeholder: 'I avoided...' },
  { question: 'How did you help someone today?', placeholder: 'I helped ... with...' }
];

export default function DailyDecisionPromptSection({ onAddDecision, todayDecisions = 0 }) {
  // Get today's prompt based on day of year
  const todayPrompt = useMemo(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const diff = now - start;
    const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
    return dailyPrompts[dayOfYear % dailyPrompts.length];
  }, []);

  const handleClick = () => {
    if (onAddDecision) {
      onAddDecision(todayPrompt.placeholder);
    }
  };

  return (
    <section 
      className="bg-gradient-to-l from-sky-100 to-cyan-50 rounded-2xl p-4 shadow-sm border border-sky-200"
      data-testid="daily-decision-prompt-section"
    >
      <div className="flex items-center justify-between gap-4">
        {/* Prompt content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">💭</span>
            <h3 className="text-sm font-semibold text-sky-800">Question of the day</h3>
            {todayDecisions > 0 && (
              <span className="px-2 py-0.5 bg-sky-200 text-sky-700 text-xs rounded-full">
                {todayDecisions} Today
              </span>
            )}
          </div>
          <p className="text-sky-700 text-sm leading-relaxed">
            {todayPrompt.question}
          </p>
        </div>

        {/* Add button */}
        <button
          onClick={handleClick}
          className="flex-shrink-0 px-4 py-2.5 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-xl transition-colors shadow-sm flex items-center gap-2"
          data-testid="daily-prompt-add-btn"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Add decision</span>
        </button>
      </div>
    </section>
  );
}

import { Play, Clock } from 'lucide-react';

export default function TaskCard({ task, onStart }) {
  if (!task) return null;

  const getCategoryColor = (category) => {
    const colors = {
      body: { bg: '#E8F0ED', accent: '#A7C4BC', text: '#2C4A40' },
      emotion: { bg: '#F7EBEB', accent: '#D4A5A5', text: '#5A3A3A' },
      mind: { bg: '#EBF4F8', accent: '#A0C1D1', text: '#2A4550' },
    };
    return colors[category] || colors.body;
  };

  const colors = getCategoryColor(task.category);

  return (
    <div 
      data-testid="task-card"
      className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-lg rounded-[2rem] p-8 text-center flex flex-col items-center gap-6"
    >
      <div 
        className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-md"
        style={{ backgroundColor: colors.accent }}
      >
        <Clock className="w-8 h-8" style={{ color: colors.text }} />
      </div>
      
      <h3 className="text-2xl font-medium text-foreground leading-relaxed">
        {task.title}
      </h3>
      
      <div className="flex items-center gap-2 text-muted-foreground">
        <Clock className="w-5 h-5" />
        <span className="text-lg">{task.minutes} minutes</span>
      </div>

      <button
        data-testid="start-task-button"
        onClick={onStart}
        className="mt-4 rounded-full h-14 px-10 shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center gap-3 text-lg font-medium tracking-wide"
        style={{ 
          backgroundColor: colors.accent,
          color: colors.text 
        }}
      >
        <Play className="w-5 h-5" />
        <span>Start</span>
      </button>
    </div>
  );
}

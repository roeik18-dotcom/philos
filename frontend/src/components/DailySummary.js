import { CheckCircle2, Circle, Clock } from 'lucide-react';

export default function DailySummary({ todayTasks, onNewTask }) {
  const completed = todayTasks.filter(t => t.status === 'completed').length;
  const partial = todayTasks.filter(t => t.status === 'partial').length;
  const notCompleted = todayTasks.filter(t => t.status === 'not_completed').length;

  return (
    <div 
      data-testid="daily-summary"
      className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-lg rounded-[2rem] p-6 flex flex-col gap-6"
    >
      <h2 className="text-2xl font-semibold text-foreground text-center">סיכום היום</h2>
      
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between p-4 rounded-2xl bg-background/50">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-[#A7C4BC]" />
            <span className="text-lg">הושלמו</span>
          </div>
          <span className="text-2xl font-bold text-foreground">{completed}</span>
        </div>

        <div className="flex items-center justify-between p-4 rounded-2xl bg-background/50">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-[#E6CBA5]" />
            <span className="text-lg">חלקיות</span>
          </div>
          <span className="text-2xl font-bold text-foreground">{partial}</span>
        </div>

        <div className="flex items-center justify-between p-4 rounded-2xl bg-background/50">
          <div className="flex items-center gap-3">
            <Circle className="w-6 h-6 text-muted-foreground" />
            <span className="text-lg">לא הושלמו</span>
          </div>
          <span className="text-2xl font-bold text-foreground">{notCompleted}</span>
        </div>
      </div>

      <button
        data-testid="new-task-button"
        onClick={onNewTask}
        className="mt-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 shadow-md hover:shadow-lg transition-all active:scale-95 text-lg font-medium tracking-wide"
      >
        משימה חדשה
      </button>
    </div>
  );
}

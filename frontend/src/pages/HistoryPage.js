import { format, parseISO, startOfDay, isSameDay } from 'date-fns';
import { he } from 'date-fns/locale';
import { CheckCircle2, Circle, Clock, Calendar as CalendarIcon } from 'lucide-react';

export default function HistoryPage({ history }) {
  const groupedByDate = history.reduce((acc, task) => {
    const date = startOfDay(parseISO(task.completedAt || task.startedAt));
    const dateKey = date.toISOString();
    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    acc[dateKey].push(task);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedByDate).sort((a, b) => 
    new Date(b) - new Date(a)
  );

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-[#A7C4BC]" />;
      case 'partial':
        return <Clock className="w-5 h-5 text-[#E6CBA5]" />;
      default:
        return <Circle className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'הושלם';
      case 'partial':
        return 'חלקי';
      default:
        return 'לא הושלם';
    }
  };

  if (sortedDates.length === 0) {
    return (
      <div className="flex-1 px-6 py-8 pb-24 flex flex-col items-center justify-center gap-4">
        <CalendarIcon className="w-16 h-16 text-muted-foreground" />
        <p className="text-lg text-muted-foreground text-center">אין היסטוריה עדיין</p>
        <p className="text-base text-muted-foreground/70 text-center">התחל משימה ראשונה כדי לראות את ההתקדמות שלך</p>
      </div>
    );
  }

  return (
    <div data-testid="history-page" className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-foreground">
        היסטוריה
      </h1>

      <div className="flex flex-col gap-4">
        {sortedDates.map(dateKey => {
          const date = parseISO(dateKey);
          const tasks = groupedByDate[dateKey];
          const isToday = isSameDay(date, new Date());

          return (
            <div 
              key={dateKey}
              className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-sm rounded-3xl p-6 flex flex-col gap-4"
            >
              <div className="flex items-center gap-3">
                <CalendarIcon className="w-5 h-5 text-muted-foreground" />
                <h3 className="text-lg font-medium text-foreground">
                  {isToday ? 'היום' : format(date, 'd MMMM yyyy', { locale: he })}
                </h3>
              </div>

              <div className="flex flex-col gap-2">
                {tasks.map((task, idx) => (
                  <div 
                    key={`${task.id}-${idx}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-background/30"
                  >
                    <div className="flex items-center gap-3">
                      {getStatusIcon(task.status)}
                      <div className="flex flex-col">
                        <span className="text-base text-foreground">{task.title}</span>
                        <span className="text-sm text-muted-foreground">{task.minutes} דקות</span>
                      </div>
                    </div>
                    <span className="text-sm text-muted-foreground">{getStatusLabel(task.status)}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import { format, parseISO, startOfDay, isSameDay } from 'date-fns';
import { Heart, Circle, Clock, Calendar as CalendarIcon, RefreshCw } from 'lucide-react';

export default function HistoryPage({ history }) {
  const groupedByDate = history.reduce((acc, request) => {
    const date = startOfDay(parseISO(request.completedAt || request.startedAt));
    const dateKey = date.toISOString();
    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    acc[dateKey].push(request);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedByDate).sort((a, b) => 
    new Date(b) - new Date(a)
  );

  // Helper function to check if this is a repeat request
  const isRepeatRequest = (currentRequest, currentRequestIndex) => {
    const completedHistory = history.filter(r => r.status === 'completed');
    
    // Find if the same person was helped before this specific request
    const previousHelps = completedHistory.filter((r, idx) => {
      return r.name === currentRequest.name && idx < currentRequestIndex;
    });
    
    return previousHelps.length > 0;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <Heart className="w-5 h-5 text-[#A7C4BC]" />;
      case 'partial':
        return <Clock className="w-5 h-5 text-[#E6CBA5]" />;
      default:
        return <Circle className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'Helped';
      case 'partial':
        return 'Started';
      default:
        return 'Did not help';
    }
  };

  if (sortedDates.length === 0) {
    return (
      <div className="flex-1 px-6 py-8 pb-24 flex flex-col items-center justify-center gap-4">
        <CalendarIcon className="w-16 h-16 text-muted-foreground" />
        <p className="text-lg text-muted-foreground text-center">No history yet</p>
        <p className="text-base text-muted-foreground/70 text-center">Complete your first help request to see your history</p>
      </div>
    );
  }

  return (
    <div data-testid="history-page" className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-foreground">
        History
      </h1>

      <div className="flex flex-col gap-4">
        {sortedDates.map(dateKey => {
          const date = parseISO(dateKey);
          const requests = groupedByDate[dateKey];
          const isToday = isSameDay(date, new Date());

          return (
            <div 
              key={dateKey}
              className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-sm rounded-3xl p-6 flex flex-col gap-4"
            >
              <div className="flex items-center gap-3">
                <CalendarIcon className="w-5 h-5 text-muted-foreground" />
                <h3 className="text-lg font-medium text-foreground">
                  {isToday ? 'Today' : format(date, 'd MMMM yyyy')}
                </h3>
              </div>

              <div className="flex flex-col gap-2">
                {requests.map((request, idx) => {
                  // Get the global index in history for proper repeat detection
                  const globalIndex = history.findIndex(h => 
                    h.id === request.id && 
                    h.startedAt === request.startedAt &&
                    h.completedAt === request.completedAt
                  );
                  const isRepeat = request.status === 'completed' && isRepeatRequest(request, globalIndex);
                  
                  return (
                    <div 
                      key={`${request.id}-${idx}`}
                      className="flex items-center justify-between p-3 rounded-2xl bg-background/30"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(request.status)}
                        <div className="flex flex-col flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-base text-foreground">{request.name} - {request.need}</span>
                            {isRepeat && (
                              <span 
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                                style={{ backgroundColor: '#A7C4BC20', color: '#2C4A40' }}
                                data-testid="repeat-badge"
                              >
                                <RefreshCw className="w-3 h-3" />
                                Repeat request
                              </span>
                            )}
                          </div>
                          <span className="text-sm text-muted-foreground">{request.minutes} min</span>
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground mr-2">{getStatusLabel(request.status)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

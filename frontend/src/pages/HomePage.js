import { useState } from 'react';
import CategoryCard from '../components/CategoryCard';
import RequestCard from '../components/RequestCard';
import Timer from '../components/Timer';
import DailySummary from '../components/DailySummary';
import { getRandomRequestByCategory } from '../data/requests';
import { ChevronRight } from 'lucide-react';

export default function HomePage({ todayRequests, onSaveRequest }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentRequest, setCurrentRequest] = useState(null);
  const [timerActive, setTimerActive] = useState(false);
  const [showSummary, setShowSummary] = useState(false);

  const handleCategorySelect = (category) => {
    const request = getRandomRequestByCategory(category);
    setSelectedCategory(category);
    setCurrentRequest(request);
    setTimerActive(false);
    setShowSummary(false);
  };

  const handleAcceptRequest = () => {
    setTimerActive(true);
    onSaveRequest({
      ...currentRequest,
      status: 'partial',
      startedAt: new Date().toISOString(),
    });
  };

  const handleFinishRequest = () => {
    onSaveRequest({
      ...currentRequest,
      status: 'completed',
      completedAt: new Date().toISOString(),
    });
    setTimerActive(false);
    setShowSummary(true);
  };

  const handleNewRequest = () => {
    setSelectedCategory(null);
    setCurrentRequest(null);
    setTimerActive(false);
    setShowSummary(false);
  };

  const handleBack = () => {
    if (timerActive) {
      const confirmed = window.confirm('האם אתה בטוח? ההתקדמות תישמר כהתחלתי');
      if (!confirmed) return;
    }
    handleNewRequest();
  };

  return (
    <div className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      {!selectedCategory && (
        <>
          <div className="text-center mb-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-none text-foreground mb-3">
              עזרה לקהילה
            </h1>
            <p className="text-base md:text-lg text-muted-foreground leading-relaxed">
              בחר תחום לעזרה היום
            </p>
          </div>
          
          <div className="flex flex-col gap-4" data-testid="category-selection">
            <CategoryCard category="body" onClick={() => handleCategorySelect('body')} />
            <CategoryCard category="emotion" onClick={() => handleCategorySelect('emotion')} />
            <CategoryCard category="mind" onClick={() => handleCategorySelect('mind')} />
          </div>
        </>
      )}

      {selectedCategory && !timerActive && !showSummary && (
        <>
          <div className="flex items-center gap-4 mb-4">
            <button
              data-testid="back-button"
              onClick={handleBack}
              className="rounded-full hover:bg-muted text-muted-foreground hover:text-foreground h-10 w-10 p-0 flex items-center justify-center transition-all"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-semibold text-foreground">בקשת עזרה</h2>
          </div>
          <RequestCard request={currentRequest} onAccept={handleAcceptRequest} />
        </>
      )}

      {timerActive && !showSummary && (
        <>
          <div className="flex items-center gap-4 mb-4">
            <button
              data-testid="back-button-timer"
              onClick={handleBack}
              className="rounded-full hover:bg-muted text-muted-foreground hover:text-foreground h-10 w-10 p-0 flex items-center justify-center transition-all"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-semibold text-foreground">עוזר עכשיו</h2>
          </div>
          <Timer request={currentRequest} onFinish={handleFinishRequest} />
        </>
      )}

      {showSummary && (
        <DailySummary todayRequests={todayRequests} onNewRequest={handleNewRequest} />
      )}
    </div>
  );
}

import { useState } from 'react';
import CategoryCard from '../components/CategoryCard';
import RequestCard from '../components/RequestCard';
import Timer from '../components/Timer';
import DailySummary from '../components/DailySummary';
import CreateRequestModal from '../components/CreateRequestModal';
import { getRandomRequestByCategory } from '../data/requests';
import { ChevronRight, HandHeart } from 'lucide-react';
import { useLocalStorage } from '../hooks/useLocalStorage';

export default function HomePage({ todayRequests, onSaveRequest }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentRequest, setCurrentRequest] = useState(null);
  const [timerActive, setTimerActive] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [userRequests, setUserRequests] = useLocalStorage('user-submitted-requests', []);

  const handleCategorySelect = (category) => {
    // Combine preset requests with user-submitted requests that are waiting
    const availableUserRequests = userRequests.filter(
      req => req.category === category && req.status === 'waiting'
    );
    
    // Randomly choose between preset and user-submitted
    const allRequests = [...availableUserRequests];
    const presetRequest = getRandomRequestByCategory(category);
    if (presetRequest) {
      allRequests.push(presetRequest);
    }
    
    const request = allRequests.length > 0
      ? allRequests[Math.floor(Math.random() * allRequests.length)]
      : presetRequest;
    
    setSelectedCategory(category);
    setCurrentRequest(request);
    setTimerActive(false);
    setShowSummary(false);
  };

  const handleAcceptRequest = () => {
    // Update request status to 'accepted'
    if (currentRequest.isUserSubmitted) {
      setUserRequests(prev => 
        prev.map(req => 
          req.id === currentRequest.id 
            ? { ...req, status: 'accepted', acceptedAt: new Date().toISOString() }
            : req
        )
      );
    }
    
    setTimerActive(true);
    onSaveRequest({
      ...currentRequest,
      status: 'partial',
      startedAt: new Date().toISOString(),
    });
  };

  const handleStartTimer = () => {
    // Update request status to 'in_progress' when timer actually starts
    if (currentRequest.isUserSubmitted) {
      setUserRequests(prev => 
        prev.map(req => 
          req.id === currentRequest.id 
            ? { ...req, status: 'in_progress', inProgressAt: new Date().toISOString() }
            : req
        )
      );
    }
  };

  const handleFinishRequest = () => {
    onSaveRequest({
      ...currentRequest,
      status: 'completed',
      completedAt: new Date().toISOString(),
    });
    
    // Update request status to 'completed'
    if (currentRequest.isUserSubmitted) {
      setUserRequests(prev => 
        prev.map(req => 
          req.id === currentRequest.id 
            ? { ...req, status: 'completed', completedAt: new Date().toISOString() }
            : req
        )
      );
    }
    
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

  const handleCreateRequest = (formData) => {
    // Check if person already has an active request (not completed)
    const existingActiveRequest = userRequests.find(
      req => req.name === formData.name && req.status !== 'completed'
    );
    
    if (existingActiveRequest) {
      alert(`${formData.name} כבר יש בקשה פעילה. נא להמתין עד שמישהו יעזור לך.`);
      return;
    }

    const newRequest = {
      id: `user-${Date.now()}`,
      ...formData,
      isUserSubmitted: true,
      status: 'waiting',
      createdAt: new Date().toISOString()
    };

    setUserRequests(prev => [...prev, newRequest]);
    alert('הבקשה נשלחה בהצלחה! מישהו בקהילה יעזור לך בקרוב.');
  };

  // Call handleStartTimer when timer component mounts
  const onTimerMount = () => {
    handleStartTimer();
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

          {/* Create Request Button */}
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-6 rounded-full bg-secondary text-secondary-foreground hover:bg-secondary/80 h-14 px-8 shadow-sm hover:shadow-md transition-all active:scale-95 flex items-center justify-center gap-3 text-lg font-medium tracking-wide border-2 border-border/50"
            data-testid="open-create-request-button"
          >
            <HandHeart className="w-6 h-6" />
            <span>צריך עזרה?</span>
          </button>
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
          <Timer request={currentRequest} onFinish={handleFinishRequest} onMount={onTimerMount} />
        </>
      )}

      {showSummary && (
        <DailySummary todayRequests={todayRequests} onNewRequest={handleNewRequest} />
      )}

      <CreateRequestModal 
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateRequest}
      />
    </div>
  );
}

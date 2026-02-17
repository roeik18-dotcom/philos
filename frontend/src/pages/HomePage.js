import { useState, useEffect } from 'react';
import CategoryCard from '../components/CategoryCard';
import RequestCard from '../components/RequestCard';
import Timer from '../components/Timer';
import DailySummary from '../components/DailySummary';
import CreateRequestModal from '../components/CreateRequestModal';
import { getRandomRequestByCategory } from '../data/requests';
import { fetchWaitingRequests, updateRequestStatus, createRequest, hasActiveRequest } from '../lib/supabase';
import { ChevronRight, HandHeart, Loader2 } from 'lucide-react';

export default function HomePage({ todayRequests, onSaveRequest }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentRequest, setCurrentRequest] = useState(null);
  const [timerActive, setTimerActive] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCategorySelect = async (category) => {
    setLoading(true);
    try {
      // Fetch waiting requests from Supabase
      const supabaseRequests = await fetchWaitingRequests(category);
      
      // Combine with preset requests
      const allRequests = [...supabaseRequests];
      const presetRequest = getRandomRequestByCategory(category);
      if (presetRequest) {
        allRequests.push(presetRequest);
      }
      
      const request = allRequests.length > 0
        ? allRequests[Math.floor(Math.random() * allRequests.length)]
        : presetRequest;
      
      // Transform Supabase request to match our format
      if (request && request.description) {
        request.need = request.description;
        request.isSupabaseRequest = true;
      }
      
      setSelectedCategory(category);
      setCurrentRequest(request);
      setTimerActive(false);
      setShowSummary(false);
    } catch (error) {
      console.error('Error fetching requests:', error);
      alert('שגיאה בטעינת בקשות. נסה שוב.');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async () => {
    try {
      // Update Supabase request status to 'accepted'
      if (currentRequest.isSupabaseRequest) {
        await updateRequestStatus(currentRequest.id, 'accepted');
      }
      
      setTimerActive(true);
      onSaveRequest({
        ...currentRequest,
        status: 'partial',
        startedAt: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error accepting request:', error);
    }
  };

  const handleStartTimer = async () => {
    try {
      // Update request status to 'in_progress' when timer actually starts
      if (currentRequest.isSupabaseRequest) {
        await updateRequestStatus(currentRequest.id, 'in_progress');
      }
    } catch (error) {
      console.error('Error updating to in_progress:', error);
    }
  };

  const handleFinishRequest = async () => {
    try {
      onSaveRequest({
        ...currentRequest,
        status: 'completed',
        completedAt: new Date().toISOString(),
      });
      
      // Update request status to 'completed'
      if (currentRequest.isSupabaseRequest) {
        await updateRequestStatus(currentRequest.id, 'completed');
      }
      
      setTimerActive(false);
      setShowSummary(true);
    } catch (error) {
      console.error('Error completing request:', error);
    }
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

  const handleCreateRequest = async (formData) => {
    try {
      // Check if person already has an active request
      const hasActive = await hasActiveRequest(formData.name);
      
      if (hasActive) {
        alert(`${formData.name} כבר יש בקשה פעילה. נא להמתין עד שמישהו יעזור לך.`);
        return;
      }

      // Create request in Supabase
      await createRequest(formData);
      alert('הבקשה נשלחה בהצלחה! מישהו בקהילה יעזור לך בקרוב.');
    } catch (error) {
      console.error('Error creating request:', error);
      alert('שגיאה ביצירת הבקשה. נסה שוב.');
    }
  };

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

      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      )}

      {!loading && selectedCategory && !timerActive && !showSummary && (
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
          {currentRequest ? (
            <RequestCard request={currentRequest} onAccept={handleAcceptRequest} />
          ) : (
            <div className="text-center p-8 text-muted-foreground">
              אין בקשות זמינות בתחום זה
            </div>
          )}
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

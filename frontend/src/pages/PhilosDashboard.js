import { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { ActiveUsersIndicator, OrientationShareCard } from '../components/philos/sections';
import QuickDecisionButton from '../components/philos/QuickDecisionButton';
import OnboardingHint from '../components/philos/OnboardingHint';
import usePhilosState from '../hooks/usePhilosState';
import HomeTab from './tabs/HomeTab';
import FeedTab from './tabs/FeedTab';
import InsightsTab from './tabs/InsightsTab';
import SystemTab from './tabs/SystemTab';
import TheoryTab from './tabs/TheoryTab';
import HistoryTab from './tabs/HistoryTab';

// Tab definitions
const TABS = {
  HOME: 'home',
  FEED: 'feed',
  INSIGHTS: 'insights',
  SYSTEM: 'system',
  THEORY: 'theory',
  HISTORY: 'history'
};

// Tab labels in Hebrew
const TAB_LABELS = {
  [TABS.HOME]: 'בית',
  [TABS.FEED]: 'פיד',
  [TABS.INSIGHTS]: 'תובנות',
  [TABS.SYSTEM]: 'מערכת',
  [TABS.THEORY]: 'תיאוריה',
  [TABS.HISTORY]: 'היסטוריה'
};

export default function PhilosDashboard({ user, onLogout, onShowAuth }) {
  // Active tab state
  const [activeTab, setActiveTab] = useState(TABS.HOME);
  const [missionContributed, setMissionContributed] = useState(false);

  // Use the custom hook for all state management
  const {
    state,
    setState,
    actionText,
    setActionText,
    decisionResult,
    history,
    globalStats,
    trendHistory,
    selectedPathData,
    learningHistory,
    adaptiveScores,
    syncStatus,
    performCloudSync,
    showShareCard,
    setShowShareCard,
    resetSession,
    resetGlobalStats,
    getTrajectoryDirection,
    exportSession,
    handlePathSelection,
    evaluateAction,
    parentDecision,
    setParentDecision,
    handleAddFollowUp,
    handleReplayDecision,
    replayDecision,
    closeReplay,
    saveReplayMetadata,
    replayHistory,
    replayInsights,
    replayAdaptiveAdjustments,
    loadSessionFromLibrary
  } = usePhilosState(user);

  const shareCardRef = useRef(null);
  
  // State for tracking recommendation metadata
  const [recommendationMetadata, setRecommendationMetadata] = useState(null);

  // Handler for following recommendation
  const handleFollowRecommendation = (metadata) => {
    setRecommendationMetadata(metadata);
    setActionText(metadata.recommendation_text);
    
    setTimeout(() => {
      const actionInput = document.querySelector('[data-testid="home-action-input"]');
      if (actionInput) {
        actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => actionInput.focus(), 400);
      }
    }, 100);
  };

  // Handler to clear recommendation metadata
  const handleClearRecommendation = () => {
    setRecommendationMetadata(null);
  };

  // Wrap evaluateAction to include recommendation metadata
  const evaluateActionWithRecommendation = async () => {
    await evaluateAction(recommendationMetadata);
    setRecommendationMetadata(null);
  };

  // Download share card as image
  const downloadShareCard = async () => {
    if (!shareCardRef.current) return;
    try {
      const dataUrl = await toPng(shareCardRef.current, { quality: 0.95 });
      const link = document.createElement('a');
      link.download = `philos-decision-${new Date().toISOString().slice(0,10)}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Error generating image:', err);
    }
  };

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 pb-24">
      {/* Onboarding Hint for first-time users */}
      <OnboardingHint />
      
      <div className="max-w-2xl mx-auto space-y-5">
        
        {/* Compact Header */}
        <div className="text-center mb-2">
          <div className="flex items-center justify-between mb-2" dir="rtl">
            {/* Auth Status */}
            <div className="flex items-center gap-2">
              {user ? (
                <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-full px-3 py-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span className="text-xs text-green-700">{user.email}</span>
                  <button
                    onClick={onLogout}
                    className="text-xs text-red-500 hover:text-red-700"
                    data-testid="logout-btn"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <button
                  onClick={onShowAuth}
                  className="text-xs text-amber-600 hover:text-amber-700"
                  data-testid="show-auth-btn"
                >
                  התחבר
                </button>
              )}
            </div>
            
            {/* Sync Status */}
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${syncStatus.cloudAvailable ? 'bg-green-500' : 'bg-gray-400'}`}></span>
              <span className="text-xs text-muted-foreground">
                {syncStatus.cloudAvailable ? 'מסונכרן' : 'לא מקוון'}
              </span>
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-foreground">Philos Orientation</h1>
          <p className="text-xs text-muted-foreground">Mental Navigation System</p>
          {/* Active Users Indicator */}
          <ActiveUsersIndicator />
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center gap-1 p-1 bg-gray-100/80 rounded-2xl backdrop-blur-sm" dir="rtl" data-testid="tab-navigation">
          {Object.values(TABS).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-2 py-2.5 text-xs font-medium rounded-xl transition-all duration-300 ${
                activeTab === tab 
                  ? 'bg-white text-primary shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-white/50'
              }`}
              data-testid={`tab-${tab}`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>

        {activeTab === TABS.HOME && (
          <HomeTab
            user={user}
            history={history}
            state={state}
            actionText={actionText}
            setActionText={setActionText}
            evaluateAction={evaluateActionWithRecommendation}
            recommendationMetadata={recommendationMetadata}
            onClearRecommendation={handleClearRecommendation}
            onFollowRecommendation={handleFollowRecommendation}
            decisionResult={decisionResult}
            adaptiveScores={adaptiveScores}
            replayInsights={replayInsights}
            missionContributed={missionContributed}
            setMissionContributed={setMissionContributed}
            setShowShareCard={setShowShareCard}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === TABS.FEED && (
          <FeedTab user={user} setActiveTab={setActiveTab} />
        )}

        {activeTab === TABS.INSIGHTS && (
          <InsightsTab
            user={user}
            history={history}
            state={state}
            decisionResult={decisionResult}
            handlePathSelection={handlePathSelection}
            adaptiveScores={adaptiveScores}
            selectedPathData={selectedPathData}
            learningHistory={learningHistory}
            replayHistory={replayHistory}
          />
        )}

        {activeTab === TABS.SYSTEM && (
          <SystemTab
            history={history}
            learningHistory={learningHistory}
            replayInsights={replayInsights}
            replayAdaptiveAdjustments={replayAdaptiveAdjustments}
            adaptiveScores={adaptiveScores}
          />
        )}

        {activeTab === TABS.THEORY && (
          <TheoryTab history={history} />
        )}

        {activeTab === TABS.HISTORY && (
          <HistoryTab
            history={history}
            state={state}
            decisionResult={decisionResult}
            trendHistory={trendHistory}
            globalStats={globalStats}
            handleAddFollowUp={handleAddFollowUp}
            handleReplayDecision={handleReplayDecision}
            replayDecision={replayDecision}
            closeReplay={closeReplay}
            saveReplayMetadata={saveReplayMetadata}
            adaptiveScores={adaptiveScores}
            loadSessionFromLibrary={loadSessionFromLibrary}
            resetGlobalStats={resetGlobalStats}
            resetSession={resetSession}
            getTrajectoryDirection={getTrajectoryDirection}
            exportSession={exportSession}
            setShowShareCard={setShowShareCard}
          />
        )}

      </div>

      {/* Share Card Modal */}
      {showShareCard && (
        <OrientationShareCard userId={user?.id} onClose={() => setShowShareCard(false)} />
      )}

      {/* Floating Quick Decision Button */}
      <QuickDecisionButton onSubmit={evaluateAction} />
    </div>
  );
}

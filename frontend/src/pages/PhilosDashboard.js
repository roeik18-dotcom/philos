import { useRef } from 'react';
import { toPng } from 'html-to-image';
import {
  DailyOrientationSection,
  ActionEvaluationSection,
  DecisionMapSection,
  PersonalMapSection,
  CollectiveValueMapSection,
  OrientationFieldSection,
  GlobalValueFieldSection,
  GlobalTrendSection,
  SessionSummarySection,
  SessionLibrarySection,
  ValueConstellationSection,
  SessionComparisonSection,
  WeeklySummarySection,
  DecisionPathEngineSection,
  PathLearningSection,
  AdaptiveLearningSection,
  CollectiveLayerSection,
  CollectiveTrendsSection,
  GlobalFieldSection,
  DecisionHistorySection,
  DecisionTreeSection,
  ChainInsightsSection,
  WeeklyBehavioralReportSection,
  MonthlyProgressReportSection,
  QuarterlyReviewSection,
  DailyDecisionPromptSection,
  DecisionReplaySection
} from '../components/philos/sections';
import QuickDecisionButton from '../components/philos/QuickDecisionButton';
import usePhilosState, { calculateSuggestedVector, analyzePersonalMap } from '../hooks/usePhilosState';

export default function PhilosDashboard({ user, onLogout, onShowAuth }) {
  // Use the custom hook for all state management (pass user for multi-device sync)
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
    parentDecision,
    setParentDecision,
    handleAddFollowUp,
    replayDecision,
    handleReplayDecision,
    closeReplay,
    saveReplayMetadata,
    balanceScore,
    evaluateAction,
    resetSession,
    resetGlobalStats,
    handlePathSelection,
    loadSessionFromLibrary,
    getTrajectoryDirection,
    exportSession
  } = usePhilosState(user);

  const shareCardRef = useRef(null);

  // Download share card as image
  const downloadShareCard = async () => {
    if (shareCardRef.current === null) return;
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
    <div className="min-h-screen bg-background p-6 pb-24">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          {/* Auth Status Bar */}
          <div className="flex items-center justify-center gap-4 mb-4" dir="rtl">
            {user ? (
              <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-full px-4 py-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span className="text-sm text-green-700">{user.email}</span>
                <button
                  onClick={onLogout}
                  className="text-xs text-red-500 hover:text-red-700 underline"
                  data-testid="logout-btn"
                >
                  התנתק
                </button>
              </div>
            ) : (
              <button
                onClick={onShowAuth}
                className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-full px-4 py-2 hover:bg-amber-100 transition-colors"
                data-testid="show-auth-btn"
              >
                <span className="text-sm text-amber-700">התחבר לסנכרון בין מכשירים</span>
                <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </button>
            )}
          </div>
          
          <h1 className="text-4xl font-bold text-foreground">Philos Orientation</h1>
          <p className="text-lg text-primary font-medium mt-1">Mental Navigation System</p>
          <p className="text-sm text-muted-foreground mt-1">Navigate your decisions in real time</p>
          {history.length > 0 && (
            <p className="text-xs text-muted-foreground mt-2">
              Session: {history.length} decisions saved
            </p>
          )}
          {/* Cloud Sync Status */}
          <div className="flex flex-col items-center gap-1 mt-2">
            <div className="flex items-center justify-center gap-2">
              {syncStatus.cloudAvailable ? (
                <>
                  <span className={`w-2 h-2 rounded-full ${syncStatus.syncing ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></span>
                  <span className="text-xs text-muted-foreground">
                    {syncStatus.syncing ? 'מסנכרן...' : 'מסונכרן לענן'}
                  </span>
                  {syncStatus.lastSynced && !syncStatus.syncing && (
                    <button
                      onClick={() => performCloudSync(true)}
                      className="text-xs text-blue-500 hover:text-blue-700 underline"
                      data-testid="manual-sync-btn"
                    >
                      סנכרן עכשיו
                    </button>
                  )}
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-gray-400"></span>
                  <span className="text-xs text-muted-foreground">מצב לא מקוון</span>
                </>
              )}
            </div>
            {/* Multi-device sync status for authenticated users */}
            {user && syncStatus.deviceSynced && (
              <div className="flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-full px-3 py-1">
                <svg className="w-3 h-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-xs text-blue-600 font-medium">מסונכרן בין מכשירים</span>
              </div>
            )}
            {syncStatus.syncing && syncStatus.syncMessage && (
              <span className="text-xs text-yellow-600">{syncStatus.syncMessage}</span>
            )}
          </div>
        </div>

        {/* Reset Session Button */}
        {history.length > 0 && (
          <div className="flex justify-center">
            <button
              onClick={resetSession}
              className="text-xs text-red-500 hover:text-red-700 underline"
              data-testid="reset-session-btn"
            >
              איפוס סשן
            </button>
          </div>
        )}

        {/* Daily Decision Prompt - at the top */}
        <DailyDecisionPromptSection 
          onAddDecision={(placeholder) => {
            setActionText(placeholder);
            const actionInput = document.querySelector('[data-testid="action-input"]');
            if (actionInput) {
              actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
              setTimeout(() => actionInput.focus(), 300);
            }
          }}
          todayDecisions={history.filter(h => {
            const today = new Date().toDateString();
            const itemDate = h.timestamp ? new Date(h.timestamp).toDateString() : today;
            return itemDate === today;
          }).length}
        />

        {/* Daily Orientation Section */}
        <DailyOrientationSection 
          state={state} 
          setState={setState} 
        />

        {/* Action Evaluation Section */}
        <ActionEvaluationSection
          actionText={actionText}
          setActionText={setActionText}
          evaluateAction={evaluateAction}
          decisionResult={decisionResult}
          state={state}
          calculateSuggestedVector={calculateSuggestedVector}
          parentDecision={parentDecision}
          onClearParent={() => setParentDecision(null)}
        />

        {/* Decision History with Chains */}
        <DecisionHistorySection
          history={history}
          onAddFollowUp={handleAddFollowUp}
          onReplayDecision={handleReplayDecision}
        />

        {/* Decision Replay Section - appears when a decision is selected for replay */}
        {replayDecision && (
          <DecisionReplaySection
            replayDecision={replayDecision}
            onClose={closeReplay}
            onSaveReplay={saveReplayMetadata}
            adaptiveScores={adaptiveScores}
          />
        )}

        {/* Decision Tree Visualization */}
        <DecisionTreeSection history={history} />

        {/* Chain Insights - Behavioral Pattern Analysis */}
        <ChainInsightsSection history={history} />

        {/* Weekly Behavioral Report */}
        <WeeklyBehavioralReportSection history={history} />

        {/* Monthly Progress Report */}
        <MonthlyProgressReportSection history={history} />

        {/* Quarterly Review */}
        <QuarterlyReviewSection history={history} />

        {/* Decision Path Engine Section */}
        <DecisionPathEngineSection
          state={state}
          history={history}
          onSelectPath={handlePathSelection}
          adaptiveScores={adaptiveScores}
        />

        {/* Path Learning Section - shows after evaluation when a path was selected */}
        <PathLearningSection
          selectedPath={selectedPathData}
          actualOutcome={decisionResult}
        />

        {/* Adaptive Learning Summary Section */}
        <AdaptiveLearningSection
          learningHistory={learningHistory}
          adaptiveScores={adaptiveScores}
        />

        {/* Decision Map Section */}
        <DecisionMapSection
          state={state}
          decisionResult={decisionResult}
          history={history}
          calculateSuggestedVector={calculateSuggestedVector}
        />

        {/* Orientation Status Section */}
        <OrientationFieldSection history={history} />

        {/* Personal Map Section */}
        <PersonalMapSection
          history={history}
          analyzePersonalMap={analyzePersonalMap}
        />

        {/* Collective Value Map */}
        <CollectiveValueMapSection history={history} />

        {/* Value Constellation Map */}
        <ValueConstellationSection history={history} />

        {/* Global Value Field */}
        <GlobalValueFieldSection
          globalStats={globalStats}
          resetGlobalStats={resetGlobalStats}
        />

        {/* Collective Layer - Cross-User Analytics */}
        <CollectiveLayerSection />

        {/* Collective Trends - Time-Based Analytics */}
        <CollectiveTrendsSection />

        {/* Global World Field - Living Value System Map */}
        <GlobalFieldSection />

        {/* Global Trend Over Time */}
        <GlobalTrendSection trendHistory={trendHistory} />

        {/* Session Library */}
        <SessionLibrarySection
          history={history}
          onLoadSession={loadSessionFromLibrary}
        />

        {/* Session Comparison Engine */}
        <SessionComparisonSection />

        {/* Weekly Cognitive Report */}
        <WeeklySummarySection trendHistory={trendHistory} />

        {/* Session Summary */}
        <SessionSummarySection 
          history={history}
          state={state}
          getTrajectoryDirection={getTrajectoryDirection}
          exportSession={exportSession}
          setShowShareCard={setShowShareCard}
          decisionResult={decisionResult}
        />

      </div>

      {/* Floating Quick Decision Button */}
      <QuickDecisionButton onSubmit={evaluateAction} />
    </div>
  );
}

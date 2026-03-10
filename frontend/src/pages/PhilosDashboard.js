import { useRef, useState } from 'react';
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
  DecisionReplaySection,
  ReplayInsightsSummarySection,
  ReplayAdaptiveEffectSection,
  ContinuePreviousSessionSection,
  CollectiveMirrorSection,
  CollectiveTrajectorySection,
  NextBestDirectionSection,
  RecommendationFollowThroughSection,
  RecommendationCalibrationSection,
  HomeNavigationSection,
  DailyOrientationLoopSection,
  WeeklyOrientationSummarySection,
  MonthlyOrientationSection,
  TheorySection,
  OrientationCompassSection,
  DirectionHistorySection,
  DecisionPathSection,
  OrientationIdentitySection,
  DailyOrientationQuestion,
  OrientationFieldToday,
  OrientationShareCard,
  WeeklyInsightSection,
  OrientationIndexPage
} from '../components/philos/sections';
import QuickDecisionButton from '../components/philos/QuickDecisionButton';
import OnboardingHint from '../components/philos/OnboardingHint';
import usePhilosState, { calculateSuggestedVector, analyzePersonalMap } from '../hooks/usePhilosState';
import { Share2 } from 'lucide-react';

// Tab definitions
const TABS = {
  HOME: 'home',
  INSIGHTS: 'insights',
  SYSTEM: 'system',
  THEORY: 'theory',
  HISTORY: 'history'
};

// Tab labels in Hebrew
const TAB_LABELS = {
  [TABS.HOME]: 'בית',
  [TABS.INSIGHTS]: 'תובנות',
  [TABS.SYSTEM]: 'מערכת',
  [TABS.THEORY]: 'תיאוריה',
  [TABS.HISTORY]: 'היסטוריה'
};

export default function PhilosDashboard({ user, onLogout, onShowAuth }) {
  // Active tab state
  const [activeTab, setActiveTab] = useState(TABS.HOME);

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
    <div className="min-h-screen bg-background p-4 pb-24">
      {/* Onboarding Hint for first-time users */}
      <OnboardingHint />
      
      <div className="max-w-2xl mx-auto space-y-4">
        
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
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center gap-1 p-1 bg-gray-100 rounded-xl" dir="rtl" data-testid="tab-navigation">
          {Object.values(TABS).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === tab 
                  ? 'bg-white text-primary shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              data-testid={`tab-${tab}`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>

        {/* ==================== HOME TAB ==================== */}
        {activeTab === TABS.HOME && (
          <div className="space-y-4">
            {/* Daily Orientation Question - TOP PRIORITY */}
            <DailyOrientationQuestion 
              userId={user?.id}
              onActionRecorded={(actionData) => {
                // Refresh data after action is recorded
                console.log('Daily action recorded:', actionData);
                // Trigger a refresh of the dashboard data
                window.location.reload();
              }}
            />

            {/* Monthly Orientation - New Month Welcome */}
            <MonthlyOrientationSection
              history={history}
              onStartMonth={(orientation) => {
                // When month starts, scroll to action input
                setTimeout(() => {
                  const actionInput = document.querySelector('[data-testid="home-action-input"]');
                  if (actionInput) {
                    actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }
                }, 300);
              }}
            />

            {/* Weekly Orientation Summary - New Week Welcome */}
            <WeeklyOrientationSummarySection
              history={history}
              onStartWeek={(orientation) => {
                // When week starts, scroll to action input
                setTimeout(() => {
                  const actionInput = document.querySelector('[data-testid="home-action-input"]');
                  if (actionInput) {
                    actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }
                }, 300);
              }}
            />

            {/* Daily Orientation Loop - New Day Welcome */}
            <DailyOrientationLoopSection
              history={history}
              onStartDay={(orientation) => {
                // When day starts, scroll to action input
                setTimeout(() => {
                  const actionInput = document.querySelector('[data-testid="home-action-input"]');
                  if (actionInput) {
                    actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }
                }, 300);
              }}
            />

            {/* Home Navigation - Clean Entry Screen */}
            <HomeNavigationSection
              history={history}
              adaptiveScores={adaptiveScores}
              replayInsights={replayInsights}
              actionText={actionText}
              setActionText={setActionText}
              evaluateAction={evaluateActionWithRecommendation}
              recommendationMetadata={recommendationMetadata}
              onClearRecommendation={handleClearRecommendation}
              onFollowRecommendation={handleFollowRecommendation}
              state={state}
            />

            {/* Decision Result (shows after evaluation) */}
            {decisionResult && (
              <div className="bg-white rounded-3xl p-4 shadow-sm border border-border" dir="rtl" data-testid="decision-result">
                <h3 className="text-sm font-medium text-muted-foreground mb-2">תוצאת הערכה</h3>
                <div className="flex items-center gap-3">
                  <span className={`text-2xl font-bold ${
                    decisionResult.value_tag === 'contribution' ? 'text-green-600' :
                    decisionResult.value_tag === 'recovery' ? 'text-blue-600' :
                    decisionResult.value_tag === 'order' ? 'text-indigo-600' :
                    decisionResult.value_tag === 'harm' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {decisionResult.value_tag === 'contribution' && 'תרומה'}
                    {decisionResult.value_tag === 'recovery' && 'התאוששות'}
                    {decisionResult.value_tag === 'order' && 'סדר'}
                    {decisionResult.value_tag === 'harm' && 'נזק'}
                    {decisionResult.value_tag === 'avoidance' && 'הימנעות'}
                  </span>
                  <span className="text-sm text-muted-foreground">{decisionResult.decision}</span>
                </div>
              </div>
            )}

            {/* Recent History (compact) */}
            {history.length > 0 && (
              <div className="bg-white rounded-3xl p-4 shadow-sm border border-border" dir="rtl" data-testid="recent-history">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-muted-foreground">החלטות אחרונות</h3>
                  <button
                    onClick={() => setActiveTab(TABS.HISTORY)}
                    className="text-xs text-primary hover:underline"
                    data-testid="show-all-history"
                  >
                    הצג הכל
                  </button>
                </div>
                <div className="space-y-2">
                  {history.slice(0, 3).map((item, index) => (
                    <div key={item.id || index} className="flex items-center gap-2 text-sm">
                      <span className={`w-2 h-2 rounded-full ${
                        item.value_tag === 'contribution' ? 'bg-green-500' :
                        item.value_tag === 'recovery' ? 'bg-blue-500' :
                        item.value_tag === 'order' ? 'bg-indigo-500' :
                        item.value_tag === 'harm' ? 'bg-red-500' :
                        'bg-gray-400'
                      }`}></span>
                      <span className="truncate flex-1">{item.action}</span>
                      <span className="text-xs text-muted-foreground">{item.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Orientation Compass - Visual Map */}
            <OrientationCompassSection history={history} state={state} userId={user?.id} />

            {/* Orientation Identity - Who You Are */}
            <OrientationIdentitySection userId={user?.id} />

            {/* Orientation Field Today - Collective Distribution */}
            <OrientationFieldToday />

            {/* Share Orientation Button */}
            <button
              onClick={() => setShowShareCard(true)}
              className="w-full py-3 px-4 bg-white rounded-2xl shadow-sm border border-border flex items-center justify-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              dir="rtl"
              data-testid="open-share-card-btn"
            >
              <Share2 className="w-4 h-4" />
              <span>שתף את ההתמצאות שלך</span>
            </button>

            {/* Decision Path Engine - Concrete Action Recommendation */}
            <DecisionPathSection 
              userId={user?.id}
              onActionFollowed={(actionData) => {
                // Log action follow-through
                console.log('Action followed:', actionData);
              }}
            />
          </div>
        )}

        {/* ==================== INSIGHTS TAB ==================== */}
        {activeTab === TABS.INSIGHTS && (
          <div className="space-y-6">
            {/* Weekly Orientation Insight */}
            <WeeklyInsightSection userId={user?.id} />

            {/* Chain Insights */}
            <ChainInsightsSection history={history} />

            {/* Recommendation Follow-Through Analytics */}
            <RecommendationFollowThroughSection history={history} />

            {/* Weekly Behavioral Report */}
            <WeeklyBehavioralReportSection history={history} user={user} />

            {/* Monthly Progress Report */}
            <MonthlyProgressReportSection history={history} />

            {/* Quarterly Review */}
            <QuarterlyReviewSection history={history} />

            {/* Replay Insights Summary */}
            <ReplayInsightsSummarySection user={user} replayCount={replayHistory?.length || 0} />

            {/* Decision Path Engine */}
            <DecisionPathEngineSection
              state={state}
              history={history}
              onSelectPath={handlePathSelection}
              adaptiveScores={adaptiveScores}
            />

            {/* Path Learning */}
            <PathLearningSection
              selectedPath={selectedPathData}
              actualOutcome={decisionResult}
            />

            {/* Adaptive Learning */}
            <AdaptiveLearningSection
              learningHistory={learningHistory}
              adaptiveScores={adaptiveScores}
            />
          </div>
        )}

        {/* ==================== SYSTEM TAB ==================== */}
        {activeTab === TABS.SYSTEM && (
          <div className="space-y-6">
            {/* Orientation Index - Global Public View */}
            <OrientationIndexPage />

            {/* Recommendation Calibration */}
            <RecommendationCalibrationSection history={history} />

            {/* Replay Adaptive Effect */}
            <ReplayAdaptiveEffectSection 
              adjustments={replayAdaptiveAdjustments}
              adaptiveScores={adaptiveScores}
              replayInsights={replayInsights}
            />

            {/* Collective Mirror */}
            <CollectiveMirrorSection
              history={history}
              learningHistory={learningHistory}
              replayInsights={replayInsights}
            />

            {/* Collective Trajectory */}
            <CollectiveTrajectorySection history={history} />

            {/* Collective Layer */}
            <CollectiveLayerSection />

            {/* Collective Trends */}
            <CollectiveTrendsSection />

            {/* Global Field */}
            <GlobalFieldSection />

            {/* Value Constellation */}
            <ValueConstellationSection history={history} />

            {/* Personal Map */}
            <PersonalMapSection
              history={history}
              analyzePersonalMap={analyzePersonalMap}
            />

            {/* Collective Value Map */}
            <CollectiveValueMapSection history={history} />
          </div>
        )}

        {/* ==================== THEORY TAB ==================== */}
        {activeTab === TABS.THEORY && (
          <div className="space-y-6">
            {/* Theoretical Framework */}
            <TheorySection />

            {/* Direction History with Patterns */}
            <DirectionHistorySection history={history} />
          </div>
        )}

        {/* ==================== HISTORY TAB ==================== */}
        {activeTab === TABS.HISTORY && (
          <div className="space-y-6">
            {/* Decision History with Chains */}
            <DecisionHistorySection
              history={history}
              onAddFollowUp={handleAddFollowUp}
              onReplayDecision={handleReplayDecision}
            />

            {/* Decision Replay Section */}
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

            {/* Decision Map */}
            <DecisionMapSection
              state={state}
              decisionResult={decisionResult}
              history={history}
              calculateSuggestedVector={calculateSuggestedVector}
            />

            {/* Orientation Status */}
            <OrientationFieldSection history={history} />

            {/* Session Library */}
            <SessionLibrarySection
              history={history}
              onLoadSession={loadSessionFromLibrary}
            />

            {/* Session Comparison */}
            <SessionComparisonSection />

            {/* Weekly Cognitive Report */}
            <WeeklySummarySection trendHistory={trendHistory} />

            {/* Global Value Field */}
            <GlobalValueFieldSection
              globalStats={globalStats}
              resetGlobalStats={resetGlobalStats}
            />

            {/* Global Trend */}
            <GlobalTrendSection trendHistory={trendHistory} />

            {/* Session Summary */}
            <SessionSummarySection 
              history={history}
              state={state}
              getTrajectoryDirection={getTrajectoryDirection}
              exportSession={exportSession}
              setShowShareCard={setShowShareCard}
              decisionResult={decisionResult}
            />

            {/* Reset Session */}
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
          </div>
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

import {
  DecisionHistorySection,
  DecisionReplaySection,
  DecisionTreeSection,
  DecisionMapSection,
  OrientationFieldSection,
  SessionLibrarySection,
  SessionComparisonSection,
  WeeklySummarySection,
  GlobalValueFieldSection,
  GlobalTrendSection,
  SessionSummarySection
} from '../../components/philos/sections';
import { calculateSuggestedVector } from '../../hooks/usePhilosState';

export default function HistoryTab({
  history,
  state,
  decisionResult,
  trendHistory,
  globalStats,
  handleAddFollowUp,
  handleReplayDecision,
  replayDecision,
  closeReplay,
  saveReplayMetadata,
  adaptiveScores,
  loadSessionFromLibrary,
  resetGlobalStats,
  resetSession,
  getTrajectoryDirection,
  exportSession,
  setShowShareCard
}) {
  return (
    <div className="space-y-5">
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
            Reset session
          </button>
        </div>
      )}
    </div>
  );
}

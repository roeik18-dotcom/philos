import { Share2 } from 'lucide-react';
import {
  DailyOpeningSection,
  DailyOrientationQuestion,
  FieldMissionSection,
  RelativeScoreSection,
  MonthlyOrientationSection,
  WeeklyOrientationSummarySection,
  DailyOrientationLoopSection,
  HomeNavigationSection,
  OrientationCompassSection,
  OrientationIdentitySection,
  OrientationFieldToday,
  OrientationCirclesSection,
  CommunityStreakSection,
  OrientationFeedSection,
  DaySummarySection,
  InviteSection,
  DecisionPathSection
} from '../../components/philos/sections';

export default function HomeTab({
  user,
  history,
  state,
  actionText,
  setActionText,
  evaluateAction,
  recommendationMetadata,
  onClearRecommendation,
  onFollowRecommendation,
  decisionResult,
  adaptiveScores,
  replayInsights,
  missionContributed,
  setMissionContributed,
  setShowShareCard,
  setActiveTab
}) {
  return (
    <div className="space-y-5">
      {/* Daily Opening - Start of Day State */}
      <DailyOpeningSection userId={user?.id} />

      {/* Daily Orientation Question - TOP PRIORITY */}
      <DailyOrientationQuestion 
        userId={user?.id}
        onActionRecorded={(actionData) => {
          console.log('Daily action recorded:', actionData);
          if (actionData.mission_contributed) {
            setMissionContributed(true);
          }
        }}
      />

      {/* Field Mission - Daily Community Challenge */}
      <FieldMissionSection missionContributed={missionContributed} />

      {/* Relative Orientation Score */}
      <RelativeScoreSection userId={user?.id} />

      {/* Monthly Orientation - New Month Welcome */}
      <MonthlyOrientationSection
        history={history}
        onStartMonth={() => {
          setTimeout(() => {
            const el = document.querySelector('[data-testid="home-action-input"]');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 300);
        }}
      />

      {/* Weekly Orientation Summary - New Week Welcome */}
      <WeeklyOrientationSummarySection
        history={history}
        onStartWeek={() => {
          setTimeout(() => {
            const el = document.querySelector('[data-testid="home-action-input"]');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 300);
        }}
      />

      {/* Daily Orientation Loop - New Day Welcome */}
      <DailyOrientationLoopSection
        history={history}
        onStartDay={() => {
          setTimeout(() => {
            const el = document.querySelector('[data-testid="home-action-input"]');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
        evaluateAction={evaluateAction}
        recommendationMetadata={recommendationMetadata}
        onClearRecommendation={onClearRecommendation}
        onFollowRecommendation={onFollowRecommendation}
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
              onClick={() => setActiveTab('history')}
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

      {/* Orientation Circles */}
      <OrientationCirclesSection />

      {/* Community Streak Overview */}
      <CommunityStreakSection />

      {/* Live Orientation Feed */}
      <OrientationFeedSection />

      {/* End of Day Summary */}
      <DaySummarySection userId={user?.id} />

      {/* Invite to Field */}
      <InviteSection userId={user?.id} />

      {/* Share Orientation Button */}
      <button
        onClick={() => setShowShareCard(true)}
        className="w-full py-3 px-4 bg-white rounded-2xl shadow-sm border border-border flex items-center justify-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:shadow-md active:scale-[0.98] transition-all duration-300 animate-section animate-section-8"
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
          console.log('Action followed:', actionData);
        }}
      />
    </div>
  );
}

import { useState } from 'react';
import { Share2, ChevronDown, ChevronUp, Users } from 'lucide-react';
import {
  EntryLayer,
  DailyOpeningSection,
  OppositionLayer,
  DailyOrientationQuestion,
  FieldImpactLayer,
  ClosingLayer,
  FieldMissionSection,
  OrientationFeedSection,
  CommunityStreakSection,
  InviteSection,
  DecisionPathSection,
  GlobalFieldDashboard,
  CompassAISection,
  FieldGlobeSection
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
  const [showCommunity, setShowCommunity] = useState(false);
  const [actionCompleted, setActionCompleted] = useState(false);
  const [actionDirection, setActionDirection] = useState(null);

  return (
    <div className="space-y-4">

      {/* ═══ GLOBAL FIELD STATE ═══ */}
      <GlobalFieldDashboard />

      {/* ═══ 3D FIELD GLOBE ═══ */}
      <FieldGlobeSection />

      {/* ═══ LAYER 1: ENTRY — "Why am I here?" ═══ */}
      <EntryLayer />

      {/* ═══ LAYER 2: PERSONAL ORIENTATION — "Where am I now?" ═══ */}
      <DailyOpeningSection userId={user?.id} />

      {/* ═══ LAYER 3: OPPOSITION — "Between which poles am I moving?" ═══ */}
      <OppositionLayer userId={user?.id} />

      {/* ═══ LAYER 4: ACTION — "What do I do now?" ═══ */}
      <DailyOrientationQuestion
        userId={user?.id}
        onActionRecorded={(actionData) => {
          setActionCompleted(true);
          setActionDirection(actionData?.direction || actionData?.suggested_direction || null);
          if (actionData?.mission_contributed) setMissionContributed(true);
        }}
      />

      {/* ═══ LAYER 5: FIELD — "How does my action affect the world?" ═══ */}
      <FieldImpactLayer
        userId={user?.id}
        actionCompleted={actionCompleted}
        actionDirection={actionDirection}
      />

      {/* ═══ LAYER 6: CLOSING — "What changed today?" ═══ */}
      <ClosingLayer userId={user?.id} />

      {/* ═══ PERSONAL COMPASS AI ═══ */}
      <CompassAISection userId={user?.id} />

      {/* ─── Divider: narrative ends, community begins ─── */}
      <div className="pt-2">
        <button
          onClick={() => setShowCommunity(!showCommunity)}
          className="w-full flex items-center justify-center gap-2 py-2.5 text-xs text-gray-400 hover:text-gray-600 transition-colors"
          data-testid="toggle-community-section"
        >
          <Users className="w-3.5 h-3.5" />
          <span>{showCommunity ? 'הסתר קהילה' : 'קהילה ושדה משותף'}</span>
          {showCommunity ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* ─── Community & Secondary Features ─── */}
      {showCommunity && (
        <div className="space-y-4 animate-fadeIn">
          <FieldMissionSection missionContributed={missionContributed} />
          <OrientationFeedSection />
          <CommunityStreakSection />
          <InviteSection userId={user?.id} />

          <button
            onClick={() => setShowShareCard(true)}
            className="w-full py-3 px-4 bg-white rounded-2xl shadow-sm border border-border flex items-center justify-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:shadow-md active:scale-[0.98] transition-all duration-300"
            dir="rtl"
            data-testid="open-share-card-btn"
          >
            <Share2 className="w-4 h-4" />
            <span>שתף את ההתמצאות שלך</span>
          </button>

          <DecisionPathSection
            userId={user?.id}
            onActionFollowed={() => {}}
          />
        </div>
      )}
    </div>
  );
}

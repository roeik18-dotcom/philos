import { Globe, MapPin, Star, Zap, MessageCircle, Target, Users } from 'lucide-react';

const dirColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};

export default function FeedCard({ card, onShowOnGlobe }) {
  if (card.type === 'action') return <ActionCard card={card} onShowOnGlobe={onShowOnGlobe} />;
  if (card.type === 'question') return <QuestionCard card={card} />;
  if (card.type === 'reflection') return <ReflectionCard card={card} />;
  if (card.type === 'leader') return <LeaderCard card={card} />;
  if (card.type === 'mission') return <MissionCard card={card} />;
  return null;
}

function ActionCard({ card, onShowOnGlobe }) {
  const color = dirColors[card.direction] || '#6366f1';
  const profileUrl = card.user_id ? `/profile/${card.user_id}` : null;
  return (
    <div className="bg-white rounded-2xl p-4 border border-border shadow-sm" dir="rtl" data-testid={`feed-card-action`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {profileUrl ? (
            <a href={profileUrl} className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold hover:ring-2 hover:ring-offset-1 transition-all" style={{ backgroundColor: color, ringColor: color }} data-testid="feed-profile-link">
              {card.alias?.charAt(0) || '?'}
            </a>
          ) : (
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: color }}>
              {card.alias?.charAt(0) || '?'}
            </div>
          )}
          <div>
            <div className="flex items-center gap-1.5">
              {profileUrl ? (
                <a href={profileUrl} className="text-sm font-semibold text-gray-800 hover:underline">{card.alias}</a>
              ) : (
                <span className="text-sm font-semibold text-gray-800">{card.alias}</span>
              )}
              {card.leader && <Star className="w-3 h-3 text-amber-500" />}
            </div>
            <div className="flex items-center gap-1 text-[10px] text-gray-400">
              <MapPin className="w-2.5 h-2.5" />
              <span>{card.country}</span>
              <span className="mx-0.5">·</span>
              <span style={{ color }}>{card.direction_he}</span>
            </div>
          </div>
        </div>
        <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${color}12`, color }}>{card.impact_score}</span>
      </div>
      <p className="text-sm text-gray-700 mb-2 leading-relaxed">{card.action_text}</p>
      <div className="flex items-center justify-between">
        {card.niche_tag && <span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">{card.niche_tag}</span>}
        <button
          onClick={() => onShowOnGlobe?.(card)}
          className="flex items-center gap-1 text-[10px] text-purple-500 hover:text-purple-700 transition-colors"
          data-testid="feed-show-on-globe"
        >
          <Globe className="w-3 h-3" />
          <span>ראה על הגלובוס</span>
        </button>
      </div>
    </div>
  );
}

function QuestionCard({ card }) {
  const color = dirColors[card.direction] || '#6366f1';
  return (
    <div className="rounded-2xl p-4 border shadow-sm" dir="rtl" data-testid="feed-card-question" style={{ backgroundColor: `${color}08`, borderColor: `${color}20` }}>
      <div className="flex items-center gap-2 mb-2">
        <MessageCircle className="w-4 h-4" style={{ color }} />
        <span className="text-xs font-semibold" style={{ color }}>שאלה להתמצאות</span>
      </div>
      <p className="text-sm font-medium text-gray-800">{card.question_he}</p>
    </div>
  );
}

function ReflectionCard({ card }) {
  return (
    <div className="bg-violet-50 rounded-2xl p-4 border border-violet-100 shadow-sm" dir="rtl" data-testid="feed-card-reflection">
      <div className="flex items-center gap-2 mb-2">
        <Zap className="w-4 h-4 text-violet-500" />
        <span className="text-xs font-semibold text-violet-600">תובנה מהשדה</span>
      </div>
      <p className="text-sm text-violet-800 leading-relaxed">{card.reflection_he}</p>
    </div>
  );
}

function LeaderCard({ card }) {
  const profileUrl = card.user_id ? `/profile/${card.user_id}` : null;
  return (
    <div className="bg-gradient-to-l from-amber-50 to-orange-50 rounded-2xl p-4 border border-amber-200 shadow-sm" dir="rtl" data-testid="feed-card-leader">
      <div className="flex items-center gap-2 mb-2">
        <Star className="w-4 h-4 text-amber-500" />
        <span className="text-xs font-semibold text-amber-700">מוביל שדה</span>
      </div>
      <div className="flex items-center gap-3">
        {profileUrl ? (
          <a href={profileUrl} className="w-10 h-10 rounded-full bg-amber-200 flex items-center justify-center text-amber-800 font-bold hover:ring-2 hover:ring-amber-400 hover:ring-offset-1 transition-all" data-testid="leader-profile-link">{card.alias?.charAt(0)}</a>
        ) : (
          <div className="w-10 h-10 rounded-full bg-amber-200 flex items-center justify-center text-amber-800 font-bold">{card.alias?.charAt(0)}</div>
        )}
        <div>
          {profileUrl ? (
            <a href={profileUrl} className="text-sm font-semibold text-gray-800 hover:underline">{card.alias} · {card.country}</a>
          ) : (
            <p className="text-sm font-semibold text-gray-800">{card.alias} · {card.country}</p>
          )}
          <p className="text-[10px] text-gray-500">{card.niche_tag} · ערך: {card.total_value}</p>
        </div>
      </div>
    </div>
  );
}

function MissionCard({ card }) {
  const color = dirColors[card.mission_direction] || '#6366f1';
  const progress = card.target > 0 ? Math.min(100, (card.participants / card.target) * 100) : 0;
  return (
    <div className="rounded-2xl p-4 border shadow-sm bg-[#0a0a1a] text-white" dir="rtl" data-testid="feed-card-mission">
      <div className="flex items-center gap-2 mb-2">
        <Target className="w-4 h-4" style={{ color }} />
        <span className="text-xs font-semibold">משימת שדה</span>
        <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ backgroundColor: `${color}30`, color }}>{card.mission_direction_he}</span>
      </div>
      <div className="flex items-center gap-2 mt-2">
        <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, backgroundColor: color }} />
        </div>
        <div className="flex items-center gap-1 text-[10px] text-gray-400">
          <Users className="w-3 h-3" />
          <span>{card.participants}/{card.target}</span>
        </div>
      </div>
    </div>
  );
}

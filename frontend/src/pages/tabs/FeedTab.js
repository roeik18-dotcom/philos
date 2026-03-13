import { useState, useEffect } from 'react';
import { Rss, Loader2 } from 'lucide-react';
import FeedCard from '../../components/philos/sections/FeedCard';
import HighlightedRecords from '../../components/philos/sections/HighlightedRecords';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FeedTab({ user, setActiveTab }) {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userNicheHe, setUserNicheHe] = useState('');

  const effectiveUserId = user?.id || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) { setLoading(false); return; }
    fetch(`${API_URL}/api/orientation/feed/for-you/${effectiveUserId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.success) {
          setCards(d.cards || []);
          setUserNicheHe(d.user_niche_he || '');
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [effectiveUserId]);

  const handleShowOnGlobe = () => {
    setActiveTab('home');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3">
        <Loader2 className="w-6 h-6 text-purple-500 animate-spin" />
        <span className="text-xs text-gray-400">Loading Feed...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3" data-testid="feed-tab">
      {/* Highlighted Records — ambient discovery */}
      <HighlightedRecords />

      {/* Feed header */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-purple-50 flex items-center justify-center">
            <Rss className="w-4 h-4 text-purple-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">For You</span>
            {userNicheHe && <p className="text-[10px] text-gray-400">Tailored to {userNicheHe}</p>}
          </div>
        </div>
        <span className="text-[10px] text-gray-400">{cards.length} cards</span>
      </div>

      {/* Feed cards */}
      {cards.map((card, i) => (
        <FeedCard key={i} card={card} onShowOnGlobe={handleShowOnGlobe} />
      ))}

      {cards.length === 0 && (
        <div className="text-center py-10 text-sm text-gray-400">
          No content in your feed yet
        </div>
      )}
    </div>
  );
}

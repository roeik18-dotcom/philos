import { useState, useEffect, useRef } from 'react';
import { toPng } from 'html-to-image';
import { Share2, Download, Flame, Compass, X } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  'התאוששות': '#3b82f6',
  'סדר': '#6366f1',
  'תרומה': '#22c55e',
  'חקירה': '#f59e0b',
  'איזון': '#8b5cf6'
};

export default function OrientationShareCard({ userId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const cardRef = useRef(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchData = async () => {
      if (!effectiveUserId) return;
      try {
        const res = await fetch(`${API_URL}/api/orientation/share/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setData(json);
        }
      } catch (e) {
        console.log('Could not fetch share card:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [effectiveUserId]);

  const handleDownload = async () => {
    if (!cardRef.current) return;
    try {
      setDownloading(true);
      const dataUrl = await toPng(cardRef.current, { quality: 0.95, pixelRatio: 2 });
      const link = document.createElement('a');
      link.download = `philos-orientation-${new Date().toISOString().slice(0, 10)}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Error generating image:', err);
    } finally {
      setDownloading(false);
    }
  };

  const handleShare = async () => {
    if (!cardRef.current) return;
    try {
      const dataUrl = await toPng(cardRef.current, { quality: 0.95, pixelRatio: 2 });
      const blob = await (await fetch(dataUrl)).blob();
      const file = new File([blob], 'philos-orientation.png', { type: 'image/png' });
      if (navigator.share) {
        await navigator.share({ title: 'Philos Orientation', text: data?.message_he || '', files: [file] });
      } else {
        handleDownload();
      }
    } catch (e) {
      handleDownload();
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl p-8 animate-pulse w-72 h-96"></div>
      </div>
    );
  }

  if (!data) return null;

  const accentColor = directionColors[data.orientation] || '#8b5cf6';

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" data-testid="share-card-modal">
      <div className="relative max-w-sm w-full">
        {/* Close button */}
        <button onClick={onClose} className="absolute -top-3 -left-3 z-10 w-8 h-8 bg-white rounded-full shadow flex items-center justify-center" data-testid="share-card-close">
          <X className="w-4 h-4 text-gray-600" />
        </button>

        {/* The card (rendered for export) */}
        <div
          ref={cardRef}
          className="rounded-3xl overflow-hidden shadow-xl"
          style={{ background: `linear-gradient(135deg, ${accentColor}15 0%, ${accentColor}08 50%, white 100%)` }}
          dir="rtl"
        >
          <div className="p-6 space-y-5">
            {/* Logo */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5" style={{ color: accentColor }} />
                <span className="text-sm font-bold text-gray-800">Philos Orientation</span>
              </div>
              <span className="text-xs text-gray-400">{new Date().toLocaleDateString('he-IL')}</span>
            </div>

            {/* Main orientation */}
            <div className="text-center py-4">
              <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-3" style={{ backgroundColor: `${accentColor}20`, border: `3px solid ${accentColor}` }}>
                <span className="text-2xl font-black" style={{ color: accentColor }}>
                  {data.orientation?.charAt(0) || '?'}
                </span>
              </div>
              <p className="text-xl font-bold text-gray-900">{data.orientation}</p>
              <p className="text-sm text-gray-600 mt-1">{data.message_he}</p>
            </div>

            {/* Streak */}
            {data.streak > 0 && (
              <div className="flex items-center justify-center gap-2 bg-orange-50 rounded-2xl py-2 px-4">
                <Flame className="w-4 h-4 text-orange-500" />
                <span className="text-sm font-bold text-orange-700">{data.streak} ימים רצופים</span>
              </div>
            )}

            {/* Mini compass visual */}
            <div className="relative w-full h-24 bg-gray-50 rounded-2xl overflow-hidden">
              <svg viewBox="0 0 100 80" className="w-full h-full">
                {/* Axes */}
                <line x1="50" y1="5" x2="50" y2="75" stroke="#e5e7eb" strokeWidth="0.5" />
                <line x1="10" y1="40" x2="90" y2="40" stroke="#e5e7eb" strokeWidth="0.5" />
                {/* Labels */}
                <text x="50" y="12" textAnchor="middle" fill="#9ca3af" fontSize="5">סדר</text>
                <text x="50" y="74" textAnchor="middle" fill="#9ca3af" fontSize="5">חקירה</text>
                <text x="14" y="42" textAnchor="middle" fill="#9ca3af" fontSize="5">התאוששות</text>
                <text x="86" y="42" textAnchor="middle" fill="#9ca3af" fontSize="5">תרומה</text>
                {/* User position dot */}
                <circle cx={data.compass_position?.x || 50} cy={data.compass_position?.y || 40} r="5" fill={accentColor} opacity="0.8" />
                <circle cx={data.compass_position?.x || 50} cy={data.compass_position?.y || 40} r="8" fill={accentColor} opacity="0.2" />
              </svg>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex-1 py-3 bg-white rounded-2xl shadow flex items-center justify-center gap-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            data-testid="share-card-download"
          >
            <Download className="w-4 h-4" />
            <span>{downloading ? 'מוריד...' : 'הורדה'}</span>
          </button>
          <button
            onClick={handleShare}
            className="flex-1 py-3 rounded-2xl shadow flex items-center justify-center gap-2 text-sm font-medium text-white transition-colors"
            style={{ backgroundColor: accentColor }}
            data-testid="share-card-share"
          >
            <Share2 className="w-4 h-4" />
            <span>שיתוף</span>
          </button>
        </div>
      </div>
    </div>
  );
}

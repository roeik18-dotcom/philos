import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Globe as GlobeIcon, RefreshCw, Activity, X, TrendingUp, MapPin } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionLabels = {
  contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה'
};

const defaultColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};

export default function FieldGlobeSection() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [colorMap, setColorMap] = useState({});
  const [totalPoints, setTotalPoints] = useState(0);
  const [todayStats, setTodayStats] = useState(null);
  const [missionGlow, setMissionGlow] = useState(null);
  const [GlobeComponent, setGlobeComponent] = useState(null);
  const [regionPopup, setRegionPopup] = useState(null);
  const [regionLoading, setRegionLoading] = useState(false);
  const globeContainerRef = useRef(null);
  const globeRef = useRef(null);

  // Lazy load react-globe.gl
  useEffect(() => {
    let cancelled = false;
    import('react-globe.gl').then(mod => {
      if (!cancelled) setGlobeComponent(() => mod.default);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/orientation/globe-activity`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          setPoints((json.points || []).slice(0, 80));
          setColorMap(json.color_map || {});
          setTotalPoints(json.total_points || 0);
          setTodayStats(json.today_stats || null);
          setMissionGlow(json.mission_glow || null);
        }
      }
    } catch (e) {
      console.log('Could not fetch globe activity:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Auto-rotate + setup globe
  useEffect(() => {
    if (globeRef.current) {
      const controls = globeRef.current.controls();
      if (controls) {
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.6;
      }
      globeRef.current.pointOfView({ lat: 31, lng: 35, altitude: 2.2 }, 1500);
    }
  }, [GlobeComponent, points]);

  // Handle point click for region interaction
  const handlePointClick = useCallback(async (point) => {
    const cc = point.country_code;
    if (!cc) return;
    setRegionLoading(true);
    setRegionPopup({ loading: true, country_code: cc });
    try {
      const res = await fetch(`${API_URL}/api/orientation/globe-region/${cc}`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          setRegionPopup(json);
        }
      }
    } catch (e) {
      console.log('Region fetch error:', e);
      setRegionPopup(null);
    } finally {
      setRegionLoading(false);
    }
  }, []);

  // Direction distribution from points
  const dirDist = useMemo(() => {
    const dist = { contribution: 0, recovery: 0, order: 0, exploration: 0 };
    points.forEach(p => { if (dist[p.direction] !== undefined) dist[p.direction]++; });
    return dist;
  }, [points]);

  const cm = { ...defaultColors, ...colorMap };
  const atmosphereColor = missionGlow?.color || '#6366f1';

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3 overflow-hidden" dir="rtl" data-testid="field-globe-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-purple-50 flex items-center justify-center">
            <GlobeIcon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">שדה גלובלי</span>
            <p className="text-[10px] text-gray-400">{totalPoints} פעולות פעילות</p>
          </div>
        </div>
        <button
          onClick={fetchData}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          data-testid="globe-refresh-btn"
        >
          <RefreshCw className={`w-4 h-4 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Live Globe Header - Today's Stats */}
      {todayStats && todayStats.total_actions > 0 && (
        <div className="flex items-center gap-3 mb-3 p-2 bg-gray-50 rounded-xl" data-testid="globe-live-header">
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-purple-500" />
            <span className="text-xs font-medium text-gray-700">{todayStats.total_actions} פעולות היום</span>
          </div>
          {todayStats.dominant_direction_he && (
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cm[todayStats.dominant_direction] || '#6366f1' }} />
              <span className="text-xs text-gray-600">כיוון מוביל: <strong>{todayStats.dominant_direction_he}</strong></span>
            </div>
          )}
        </div>
      )}

      {/* Mission Glow Indicator */}
      {missionGlow && (
        <div className="flex items-center gap-1.5 mb-2 text-[10px] text-gray-400" data-testid="globe-mission-glow">
          <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: missionGlow.color }} />
          <span>זוהר משימה: {directionLabels[missionGlow.direction] || ''}</span>
        </div>
      )}

      {/* Globe container */}
      <div ref={globeContainerRef} className="relative w-full rounded-2xl bg-[#0a0a1a] overflow-hidden" style={{ height: 280 }} data-testid="globe-canvas">
        {GlobeComponent && points.length > 0 ? (
          <GlobeComponent
            ref={globeRef}
            width={globeContainerRef.current?.offsetWidth || 360}
            height={280}
            globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
            backgroundColor="#0a0a1a"
            pointsData={points}
            pointLat="lat"
            pointLng="lng"
            pointColor="color"
            pointAltitude={d => d.is_user ? 0.08 : 0.04}
            pointRadius={d => d.is_user ? 0.5 : 0.35}
            pointsMerge={false}
            atmosphereColor={atmosphereColor}
            atmosphereAltitude={0.15}
            animateIn={false}
            onPointClick={handlePointClick}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            {loading ? (
              <div className="flex flex-col items-center gap-2">
                <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs text-gray-400">טוען שדה גלובלי...</span>
              </div>
            ) : (
              <span className="text-xs text-gray-500">אין נתונים זמינים</span>
            )}
          </div>
        )}

        {/* Region Popup Overlay */}
        {regionPopup && !regionPopup.loading && (
          <div
            className="absolute bottom-3 left-3 right-3 bg-[#1a1a2e]/95 backdrop-blur-md rounded-xl p-3 border border-white/10 animate-fadeIn z-10"
            data-testid="globe-region-popup"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-sm font-semibold text-white">{regionPopup.country_name_he}</span>
              </div>
              <button onClick={() => setRegionPopup(null)} className="text-gray-400 hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-2 mb-2">
              <div className="text-center">
                <p className="text-lg font-bold text-white">{regionPopup.total_actions}</p>
                <p className="text-[9px] text-gray-400">פעולות</p>
              </div>
              <div className="text-center">
                <p className="text-sm font-bold" style={{ color: cm[regionPopup.dominant_direction] || '#fff' }}>
                  {regionPopup.dominant_direction_he || '—'}
                </p>
                <p className="text-[9px] text-gray-400">כיוון מוביל</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-0.5">
                  <TrendingUp className="w-3 h-3 text-purple-400" />
                  <p className="text-sm font-bold text-white">{regionPopup.trend_he}</p>
                </div>
                <p className="text-[9px] text-gray-400">מגמה</p>
              </div>
            </div>
            {/* Mini direction bars */}
            <div className="space-y-1">
              {Object.entries(regionPopup.direction_counts || {}).map(([d, c]) => c > 0 && (
                <div key={d} className="flex items-center gap-1.5">
                  <span className="text-[9px] text-gray-400 w-12">{directionLabels[d]}</span>
                  <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{
                      width: `${regionPopup.total_actions > 0 ? (c / regionPopup.total_actions) * 100 : 0}%`,
                      backgroundColor: cm[d]
                    }} />
                  </div>
                  <span className="text-[9px] text-gray-500 w-4 text-left">{c}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Direction distribution mini-legend */}
      <div className="flex gap-2 mt-3 flex-wrap">
        {Object.entries(dirDist).map(([dir, count]) => (
          <div key={dir} className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-gray-50" data-testid={`globe-legend-${dir}`}>
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cm[dir] }} />
            <span className="text-[10px] text-gray-600">{directionLabels[dir]}</span>
            <span className="text-[10px] font-medium text-gray-800">{count}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

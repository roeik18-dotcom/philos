import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { RefreshCw, X, MapPin } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

const HOTSPOT_COORDS = [
  { lat: 31.5, lng: 34.8, name: 'ישראל' },
  { lat: 48.8, lng: 2.3, name: 'צרפת' },
  { lat: 40.7, lng: -74.0, name: 'ארה"ב' },
  { lat: 51.5, lng: -0.1, name: 'בריטניה' },
  { lat: 35.7, lng: 139.7, name: 'יפן' },
  { lat: 52.5, lng: 13.4, name: 'גרמניה' },
  { lat: -33.9, lng: 18.4, name: 'דרום אפריקה' },
  { lat: -23.5, lng: -46.6, name: 'ברזיל' }
];

export default function FieldGlobeSection() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [colorMap, setColorMap] = useState({});
  const [totalPoints, setTotalPoints] = useState(0);
  const [todayStats, setTodayStats] = useState(null);
  const [missionGlow, setMissionGlow] = useState(null);
  const [fieldData, setFieldData] = useState(null);
  const [GlobeComponent, setGlobeComponent] = useState(null);
  const [regionPopup, setRegionPopup] = useState(null);
  const [ringsData, setRingsData] = useState([]);
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

  const fetchGlobeData = useCallback(async () => {
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
    } catch (e) {}
    finally { setLoading(false); }
  }, []);

  const fetchFieldState = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/orientation/field-dashboard`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) setFieldData(json);
      }
    } catch (e) {}
  }, []);

  // Initial load
  useEffect(() => { fetchGlobeData(); fetchFieldState(); }, [fetchGlobeData, fetchFieldState]);

  // Auto-refresh: globe every 45s, field state every 30s
  useEffect(() => {
    const g = setInterval(fetchGlobeData, 45000);
    const f = setInterval(fetchFieldState, 30000);
    return () => { clearInterval(g); clearInterval(f); };
  }, [fetchGlobeData, fetchFieldState]);

  // === AMBIENT PULSE — one clean pulse at a time, direction-coded ===
  useEffect(() => {
    const dirs = Object.keys(dirColors);
    const pulse = () => {
      const d = dirs[Math.floor(Math.random() * dirs.length)];
      const hotspot = HOTSPOT_COORDS[Math.floor(Math.random() * HOTSPOT_COORDS.length)];
      const ring = {
        lat: hotspot.lat + (Math.random() - 0.5) * 5,
        lng: hotspot.lng + (Math.random() - 0.5) * 5,
        maxR: 5,
        propagationSpeed: 0.8,
        repeatPeriod: 3000,
        color: dirColors[d]
      };
      setRingsData(prev => [...prev.slice(-2), ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 6000);
    };
    const interval = setInterval(pulse, 8000 + Math.random() * 4000);
    return () => clearInterval(interval);
  }, []);

  // === DOMINANT DIRECTION SPIKE — periodic, bigger, from active region ===
  useEffect(() => {
    const spike = () => {
      const dominant = fieldData?.dominant_direction || 'contribution';
      const hotspot = HOTSPOT_COORDS[Math.floor(Math.random() * 3)];
      const ring = {
        lat: hotspot.lat,
        lng: hotspot.lng,
        maxR: 10,
        propagationSpeed: 0.5,
        repeatPeriod: 4000,
        color: dirColors[dominant]
      };
      setRingsData(prev => [...prev.slice(-2), ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 8000);
    };
    const interval = setInterval(spike, 25000 + Math.random() * 10000);
    return () => clearInterval(interval);
  }, [fieldData]);

  // Listen for user-triggered field-pulse events
  useEffect(() => {
    const handlePulse = (e) => {
      const { lat, lng, color, direction } = e.detail || {};
      const resolvedColor = color || dirColors[direction] || '#6366f1';
      const ring = {
        lat: lat ?? 31 + (Math.random() * 10 - 5),
        lng: lng ?? 35 + (Math.random() * 10 - 5),
        maxR: 8,
        propagationSpeed: 2,
        repeatPeriod: 1200,
        color: resolvedColor
      };
      setRingsData(prev => [...prev.slice(-3), ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 4000);
    };
    window.addEventListener('globe-field-pulse', handlePulse);
    return () => window.removeEventListener('globe-field-pulse', handlePulse);
  }, []);

  // Auto-rotate globe
  useEffect(() => {
    if (globeRef.current) {
      const controls = globeRef.current.controls();
      if (controls) { controls.autoRotate = true; controls.autoRotateSpeed = 0.4; }
      globeRef.current.pointOfView({ lat: 31, lng: 35, altitude: 2.2 }, 1500);
    }
  }, [GlobeComponent, points]);

  const handlePointClick = useCallback(async (point) => {
    const cc = point.country_code;
    if (!cc) return;
    setRegionPopup({ loading: true, country_code: cc });
    try {
      const res = await fetch(`${API_URL}/api/orientation/globe-region/${cc}`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) setRegionPopup(json);
      }
    } catch (e) { setRegionPopup(null); }
  }, []);

  const dirDist = useMemo(() => {
    const dist = { contribution: 0, recovery: 0, order: 0, exploration: 0 };
    points.forEach(p => { if (dist[p.direction] !== undefined) dist[p.direction]++; });
    return dist;
  }, [points]);

  const cm = useMemo(() => ({ ...dirColors, ...colorMap }), [colorMap]);
  const dominantDir = fieldData?.dominant_direction || todayStats?.dominant_direction || null;
  const dominantColor = cm[dominantDir] || '#6366f1';
  const narrative = fieldData?.field_narrative_he || '';
  const heartbeatDuration = Math.max(2.5, 6 - ((fieldData?.total_actions_today || 0) / 60));

  return (
    <section className="bg-[#0a0a1a] rounded-3xl overflow-hidden border border-gray-800/60" dir="rtl" data-testid="field-globe-section">

      {/* ═══ WORLD STATE HEADER — Calm, symbolic ═══ */}
      <div className="p-4 pb-2" data-testid="world-state-header">
        {/* Title + refresh */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 tracking-wide">מצב השדה</span>
            <span className="relative flex items-center">
              <span className="absolute w-1.5 h-1.5 rounded-full animate-ping opacity-30" style={{ backgroundColor: dominantColor }} />
              <span className="relative w-1.5 h-1.5 rounded-full" style={{ backgroundColor: dominantColor }} />
            </span>
          </div>
          <button onClick={() => { fetchGlobeData(); fetchFieldState(); }} className="p-1 rounded-lg hover:bg-white/5 transition-colors" data-testid="globe-refresh-btn">
            <RefreshCw className={`w-3 h-3 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Narrative — the primary read */}
        {narrative && (
          <p className="text-sm text-gray-300 leading-relaxed mb-3" data-testid="globe-narrative">
            {narrative}
          </p>
        )}

        {/* Dominant direction + minimal direction bar */}
        <div className="flex items-center gap-3 mb-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: dominantColor }} />
            <span className="text-[10px] font-semibold" style={{ color: dominantColor }}>{dirLabels[dominantDir] || '—'}</span>
          </div>
          <div className="flex-1 flex h-[2px] rounded-full overflow-hidden bg-white/[0.04]">
            {Object.entries(fieldData?.direction_counts || dirDist).map(([d, c]) => {
              const total = Object.values(fieldData?.direction_counts || dirDist).reduce((a, b) => a + b, 0) || 1;
              const pct = (c / total) * 100;
              return pct > 0 ? <div key={d} className="h-full transition-all duration-1000" style={{ width: `${pct}%`, backgroundColor: cm[d] }} /> : null;
            })}
          </div>
        </div>
      </div>

      {/* ═══ GLOBE ═══ */}
      <div ref={globeContainerRef} className="relative w-full overflow-hidden" style={{ height: 300 }} data-testid="globe-canvas">
        {/* Heartbeat glow */}
        <div
          className="absolute inset-0 pointer-events-none z-0"
          data-testid="field-heartbeat"
          style={{
            boxShadow: `inset 0 0 60px ${dominantColor}10, inset 0 0 120px ${dominantColor}05`,
            animation: `fieldHeartbeat ${heartbeatDuration}s ease-in-out infinite`,
          }}
        />

        {GlobeComponent && points.length > 0 ? (
          <GlobeComponent
            ref={globeRef}
            width={globeContainerRef.current?.offsetWidth || 360}
            height={300}
            globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
            backgroundColor="rgba(0,0,0,0)"
            pointsData={points}
            pointLat="lat"
            pointLng="lng"
            pointColor="color"
            pointAltitude={d => d.is_user ? 0.07 : 0.03}
            pointRadius={d => d.is_user ? 0.45 : 0.3}
            pointsMerge={false}
            atmosphereColor={dominantColor}
            atmosphereAltitude={0.2}
            animateIn={false}
            onPointClick={handlePointClick}
            ringsData={ringsData}
            ringLat="lat"
            ringLng="lng"
            ringMaxRadius="maxR"
            ringPropagationSpeed="propagationSpeed"
            ringRepeatPeriod="repeatPeriod"
            ringColor={d => { const c = d.color || '#6366f1'; return [`${c}80`, `${c}00`]; }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            {loading ? (
              <div className="flex flex-col items-center gap-2">
                <div className="w-5 h-5 border-2 border-indigo-400/40 border-t-indigo-400 rounded-full animate-spin" />
                <span className="text-[10px] text-gray-600">טוען שדה...</span>
              </div>
            ) : (
              <span className="text-[10px] text-gray-700">אין נתונים זמינים</span>
            )}
          </div>
        )}

        {/* Region Popup */}
        {regionPopup && !regionPopup.loading && (
          <div className="absolute bottom-3 left-3 right-3 bg-[#0e0e1e]/95 backdrop-blur-md rounded-xl p-3 border border-white/[0.06] z-10" data-testid="globe-region-popup">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3 h-3" style={{ color: dominantColor }} />
                <span className="text-sm font-medium text-white">{regionPopup.country_name_he}</span>
              </div>
              <button onClick={() => setRegionPopup(null)} className="text-gray-500 hover:text-white transition-colors"><X className="w-3 h-3" /></button>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs text-gray-400">{regionPopup.total_actions} פעולות</span>
              <span className="text-xs font-medium" style={{ color: cm[regionPopup.dominant_direction] || '#fff' }}>{regionPopup.dominant_direction_he || '—'}</span>
              <span className="text-xs text-gray-500">{regionPopup.trend_he}</span>
            </div>
            <div className="space-y-1">
              {Object.entries(regionPopup.direction_counts || {}).map(([d, c]) => c > 0 && (
                <div key={d} className="flex items-center gap-1.5">
                  <span className="text-[8px] text-gray-500 w-10 text-right">{dirLabels[d]}</span>
                  <div className="flex-1 h-[2px] bg-white/[0.06] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${regionPopup.total_actions > 0 ? (c / regionPopup.total_actions) * 100 : 0}%`, backgroundColor: cm[d] }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ═══ DIRECTION LEGEND — minimal ═══ */}
      <div className="flex gap-3 px-4 py-2.5">
        {Object.entries(dirLabels).map(([dir, label]) => (
          <div key={dir} className="flex items-center gap-1" data-testid={`globe-legend-${dir}`}>
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: cm[dir], opacity: dir === dominantDir ? 1 : 0.4 }} />
            <span className="text-[9px]" style={{ color: dir === dominantDir ? cm[dir] : '#6b7280' }}>{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

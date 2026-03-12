import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Globe as GlobeIcon, RefreshCw, X, TrendingUp, MapPin, Zap, Radio } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

// Known hotspot coordinates for regional glow pulses
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
  const [liveCount, setLiveCount] = useState(0);
  const [lastPulseDir, setLastPulseDir] = useState(null);
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

  // Auto-refresh: globe every 40s, field state every 25s
  useEffect(() => {
    const g = setInterval(fetchGlobeData, 40000);
    const f = setInterval(fetchFieldState, 25000);
    return () => { clearInterval(g); clearInterval(f); };
  }, [fetchGlobeData, fetchFieldState]);

  // Animate live counter
  useEffect(() => {
    const target = fieldData?.total_actions_today || todayStats?.total_actions || 0;
    if (liveCount === target) return;
    const step = Math.max(1, Math.ceil(Math.abs(target - liveCount) / 15));
    const t = setTimeout(() => {
      setLiveCount(prev => prev < target ? Math.min(prev + step, target) : Math.max(prev - step, target));
    }, 50);
    return () => clearTimeout(t);
  }, [fieldData, todayStats, liveCount]);

  // === AMBIENT FIELD PULSES — direction-coded, regional ===
  useEffect(() => {
    const dirs = Object.keys(dirColors);
    const ambientPulse = () => {
      const d = dirs[Math.floor(Math.random() * dirs.length)];
      const hotspot = HOTSPOT_COORDS[Math.floor(Math.random() * HOTSPOT_COORDS.length)];
      const lat = hotspot.lat + (Math.random() - 0.5) * 8;
      const lng = hotspot.lng + (Math.random() - 0.5) * 8;
      const ring = { lat, lng, maxR: 4, propagationSpeed: 1.2, repeatPeriod: 2000, color: dirColors[d] };
      setRingsData(prev => [...prev.slice(-4), ring]);
      setLastPulseDir(d);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 5000);
    };
    const interval = setInterval(ambientPulse, 6000 + Math.random() * 3000);
    return () => clearInterval(interval);
  }, []);

  // === LARGE FIELD SPIKE PULSE — periodic, bigger, slower ===
  useEffect(() => {
    const spikePulse = () => {
      const dominant = fieldData?.dominant_direction || 'contribution';
      const hotspot = HOTSPOT_COORDS[Math.floor(Math.random() * 3)]; // top 3 regions
      const ring = {
        lat: hotspot.lat,
        lng: hotspot.lng,
        maxR: 12,
        propagationSpeed: 0.8,
        repeatPeriod: 3000,
        color: dirColors[dominant]
      };
      setRingsData(prev => [...prev.slice(-3), ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 6000);
    };
    const interval = setInterval(spikePulse, 20000 + Math.random() * 10000);
    return () => clearInterval(interval);
  }, [fieldData]);

  // === REGIONAL HOTSPOT GLOW — soft glow at active regions ===
  useEffect(() => {
    if (!fieldData?.top_regions?.length) return;
    const hotspotGlow = () => {
      const region = fieldData.top_regions[Math.floor(Math.random() * Math.min(3, fieldData.top_regions.length))];
      const coord = HOTSPOT_COORDS.find(h => h.name === region?.name) || HOTSPOT_COORDS[0];
      const ring = {
        lat: coord.lat,
        lng: coord.lng,
        maxR: 6,
        propagationSpeed: 0.6,
        repeatPeriod: 4000,
        color: dirColors[fieldData.dominant_direction] || '#6366f1'
      };
      setRingsData(prev => [...prev.slice(-5), ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 8000);
    };
    const interval = setInterval(hotspotGlow, 15000);
    hotspotGlow(); // initial
    return () => clearInterval(interval);
  }, [fieldData]);

  // Listen for user-triggered field-pulse events
  useEffect(() => {
    const handlePulse = (e) => {
      const { lat, lng, color, direction } = e.detail || {};
      const resolvedColor = color || dirColors[direction] || '#6366f1';
      const resolvedLat = lat ?? (31 + Math.random() * 10 - 5);
      const resolvedLng = lng ?? (35 + Math.random() * 10 - 5);
      const ring = { lat: resolvedLat, lng: resolvedLng, maxR: 10, propagationSpeed: 3, repeatPeriod: 800, color: resolvedColor };
      setRingsData(prev => [...prev, ring]);
      setTimeout(() => setRingsData(prev => prev.filter(r => r !== ring)), 3000);
    };
    window.addEventListener('globe-field-pulse', handlePulse);
    return () => window.removeEventListener('globe-field-pulse', handlePulse);
  }, []);

  // Auto-rotate globe
  useEffect(() => {
    if (globeRef.current) {
      const controls = globeRef.current.controls();
      if (controls) { controls.autoRotate = true; controls.autoRotateSpeed = 0.5; }
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

  const cm = { ...dirColors, ...colorMap };
  const dominantDir = fieldData?.dominant_direction || todayStats?.dominant_direction || null;
  const dominantColor = cm[dominantDir] || '#6366f1';
  const momentum = fieldData?.momentum_he || '';
  const heartbeatDuration = Math.max(2, 6 - ((fieldData?.total_actions_today || 0) / 50));

  return (
    <section className="bg-[#0a0a1a] rounded-3xl overflow-hidden border border-gray-800" dir="rtl" data-testid="field-globe-section">

      {/* ═══ WORLD STATE HEADER ═══ */}
      <div className="p-4 pb-0" data-testid="world-state-header">
        {/* Title row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <GlobeIcon className="w-4 h-4 text-gray-400" />
            <span className="text-xs font-bold text-gray-300 tracking-wide">מצב השדה</span>
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[9px] text-green-400">חי</span>
            </span>
          </div>
          <button onClick={() => { fetchGlobeData(); fetchFieldState(); }} className="p-1 rounded-lg hover:bg-white/5 transition-colors" data-testid="globe-refresh-btn">
            <RefreshCw className={`w-3.5 h-3.5 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* World state metrics */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          {/* Dominant direction */}
          <div className="bg-white/5 rounded-xl p-2.5 text-center" data-testid="world-state-direction">
            <div className="w-5 h-5 mx-auto rounded-full mb-1 flex items-center justify-center" style={{ backgroundColor: `${dominantColor}20` }}>
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: dominantColor }} />
            </div>
            <p className="text-xs font-bold" style={{ color: dominantColor }}>{dirLabels[dominantDir] || '—'}</p>
            <p className="text-[8px] text-gray-500">כיוון מוביל</p>
          </div>

          {/* Live action count */}
          <div className="bg-white/5 rounded-xl p-2.5 text-center" data-testid="world-state-actions">
            <p className="text-xl font-black text-white tabular-nums">{liveCount.toLocaleString()}</p>
            <p className="text-[8px] text-gray-500">פעולות היום</p>
          </div>

          {/* Momentum */}
          <div className="bg-white/5 rounded-xl p-2.5 text-center" data-testid="world-state-momentum">
            <div className="flex items-center justify-center gap-0.5 mb-0.5">
              <Zap className="w-3 h-3" style={{ color: dominantColor }} />
            </div>
            <p className="text-[10px] font-medium text-gray-300">{momentum || 'יציב'}</p>
            <p className="text-[8px] text-gray-500">מומנטום</p>
          </div>
        </div>

        {/* Regional hotspots */}
        {fieldData?.top_regions?.length > 0 && (
          <div className="flex gap-1.5 mb-3 overflow-x-auto pb-0.5" data-testid="world-state-regions">
            {fieldData.top_regions.slice(0, 4).map((r, i) => (
              <div key={r.code || i} className="flex items-center gap-1 px-2 py-1 rounded-full bg-white/5 flex-shrink-0">
                <MapPin className="w-2.5 h-2.5 text-gray-500" />
                <span className="text-[9px] text-gray-400">{r.name}</span>
                <span className="text-[9px] font-medium text-gray-300">{r.count}</span>
              </div>
            ))}
          </div>
        )}

        {/* Direction distribution bar */}
        <div className="flex h-1 rounded-full overflow-hidden mb-1 bg-white/5">
          {Object.entries(fieldData?.direction_counts || dirDist).map(([d, c]) => {
            const total = Object.values(fieldData?.direction_counts || dirDist).reduce((a, b) => a + b, 0) || 1;
            const pct = (c / total) * 100;
            return pct > 0 ? <div key={d} className="h-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: cm[d] }} /> : null;
          })}
        </div>

        {/* Real-time pulse indicator */}
        {lastPulseDir && (
          <div className="flex items-center gap-1.5 py-1.5">
            <Radio className="w-2.5 h-2.5 animate-pulse" style={{ color: dirColors[lastPulseDir] }} />
            <span className="text-[8px] text-gray-500">פעולה אחרונה: <span style={{ color: dirColors[lastPulseDir] }}>{dirLabels[lastPulseDir]}</span></span>
          </div>
        )}
      </div>

      {/* ═══ GLOBE ═══ */}
      <div ref={globeContainerRef} className="relative w-full overflow-hidden" style={{ height: 300 }} data-testid="globe-canvas">
        {/* Heartbeat glow */}
        <div
          className="absolute inset-0 pointer-events-none z-0"
          data-testid="field-heartbeat"
          style={{
            boxShadow: `inset 0 0 80px ${dominantColor}12, inset 0 0 160px ${dominantColor}06`,
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
            pointAltitude={d => d.is_user ? 0.08 : 0.04}
            pointRadius={d => d.is_user ? 0.5 : 0.35}
            pointsMerge={false}
            atmosphereColor={dominantColor}
            atmosphereAltitude={0.18}
            animateIn={false}
            onPointClick={handlePointClick}
            ringsData={ringsData}
            ringLat="lat"
            ringLng="lng"
            ringMaxRadius="maxR"
            ringPropagationSpeed="propagationSpeed"
            ringRepeatPeriod="repeatPeriod"
            ringColor={d => { const c = d.color || '#6366f1'; return [`${c}aa`, `${c}00`]; }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            {loading ? (
              <div className="flex flex-col items-center gap-2">
                <div className="w-6 h-6 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-[10px] text-gray-500">טוען שדה גלובלי...</span>
              </div>
            ) : (
              <span className="text-[10px] text-gray-600">אין נתונים זמינים</span>
            )}
          </div>
        )}

        {/* Region Popup */}
        {regionPopup && !regionPopup.loading && (
          <div className="absolute bottom-3 left-3 right-3 bg-[#1a1a2e]/95 backdrop-blur-md rounded-xl p-3 border border-white/10 z-10" data-testid="globe-region-popup">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3 h-3 text-purple-400" />
                <span className="text-sm font-semibold text-white">{regionPopup.country_name_he}</span>
              </div>
              <button onClick={() => setRegionPopup(null)} className="text-gray-400 hover:text-white"><X className="w-3 h-3" /></button>
            </div>
            <div className="grid grid-cols-3 gap-2 mb-2">
              <div className="text-center">
                <p className="text-base font-bold text-white">{regionPopup.total_actions}</p>
                <p className="text-[8px] text-gray-400">פעולות</p>
              </div>
              <div className="text-center">
                <p className="text-xs font-bold" style={{ color: cm[regionPopup.dominant_direction] || '#fff' }}>{regionPopup.dominant_direction_he || '—'}</p>
                <p className="text-[8px] text-gray-400">כיוון מוביל</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-0.5">
                  <TrendingUp className="w-3 h-3 text-purple-400" />
                  <p className="text-xs font-bold text-white">{regionPopup.trend_he}</p>
                </div>
                <p className="text-[8px] text-gray-400">מגמה</p>
              </div>
            </div>
            <div className="space-y-1">
              {Object.entries(regionPopup.direction_counts || {}).map(([d, c]) => c > 0 && (
                <div key={d} className="flex items-center gap-1.5">
                  <span className="text-[8px] text-gray-400 w-12 text-right">{dirLabels[d]}</span>
                  <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${regionPopup.total_actions > 0 ? (c / regionPopup.total_actions) * 100 : 0}%`, backgroundColor: cm[d] }} />
                  </div>
                  <span className="text-[8px] text-gray-500 w-4">{c}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ═══ DIRECTION LEGEND ═══ */}
      <div className="flex gap-2 p-3 pt-2 flex-wrap justify-start">
        {Object.entries(dirDist).map(([dir, count]) => (
          <div key={dir} className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5" data-testid={`globe-legend-${dir}`}>
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: cm[dir] }} />
            <span className="text-[9px] text-gray-400">{dirLabels[dir]}</span>
            <span className="text-[9px] font-medium text-gray-300">{count}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

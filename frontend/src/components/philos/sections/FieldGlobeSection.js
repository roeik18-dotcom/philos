import { useState, useEffect, useRef, useMemo } from 'react';
import { Globe as GlobeIcon, RefreshCw } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionLabels = {
  contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה'
};

export default function FieldGlobeSection() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [colorMap, setColorMap] = useState({});
  const [totalPoints, setTotalPoints] = useState(0);
  const [GlobeComponent, setGlobeComponent] = useState(null);
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

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/orientation/globe-activity`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          // Limit to 80 points max for performance
          const allPoints = json.points || [];
          setPoints(allPoints.slice(0, 80));
          setColorMap(json.color_map || {});
          setTotalPoints(json.total_points || 0);
        }
      }
    } catch (e) {
      console.log('Could not fetch globe activity:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  // Auto-rotate globe
  useEffect(() => {
    if (globeRef.current) {
      const controls = globeRef.current.controls();
      if (controls) {
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.6;
      }
      // Focus on Israel area initially
      globeRef.current.pointOfView({ lat: 31, lng: 35, altitude: 2.2 }, 1500);
    }
  }, [GlobeComponent, points]);

  // Direction distribution from points
  const dirDist = useMemo(() => {
    const dist = { contribution: 0, recovery: 0, order: 0, exploration: 0 };
    points.forEach(p => { if (dist[p.direction] !== undefined) dist[p.direction]++; });
    return dist;
  }, [points]);

  const defaultColors = {
    contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
  };
  const cm = { ...defaultColors, ...colorMap };

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3 overflow-hidden" dir="rtl" data-testid="field-globe-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
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
            pointAltitude={0.04}
            pointRadius={0.35}
            pointsMerge={true}
            atmosphereColor="#6366f1"
            atmosphereAltitude={0.12}
            animateIn={false}
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

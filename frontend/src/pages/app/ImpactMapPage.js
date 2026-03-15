import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  education: '#3b82f6', environment: '#10b981', health: '#f43f5e',
  community: '#8b5cf6', technology: '#06b6d4', mentorship: '#f59e0b',
  volunteering: '#ec4899', other: '#6b7280',
};

export default function ImpactMapPage() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/actions/map`)
      .then(r => r.json())
      .then(d => { if (d.success) setPoints(d.points); })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="h-screen flex flex-col" data-testid="impact-map-page" style={{ background: '#050510' }}>
      <div className="px-4 pt-4 pb-3 flex items-center justify-between" style={{ background: '#050510' }}>
        <h1 className="text-lg font-semibold text-white">Impact Map</h1>
        <span className="text-[10px] text-white/30">{points.length} actions mapped</span>
      </div>

      <div className="flex-1 relative">
        {loading ? (
          <div className="flex items-center justify-center h-full text-white/30 text-sm">Loading map...</div>
        ) : (
          <MapContainer
            center={[20, 0]}
            zoom={2}
            style={{ height: '100%', width: '100%', background: '#0a0a1a' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; OpenStreetMap'
            />
            {points.map(p => (
              <CircleMarker
                key={p.id}
                center={[p.lat, p.lng]}
                radius={Math.max(5, Math.min(12, p.trust_signal + 5))}
                fillColor={CATEGORY_COLORS[p.category] || '#6b7280'}
                fillOpacity={0.7}
                stroke={true}
                color={CATEGORY_COLORS[p.category] || '#6b7280'}
                weight={1}
                opacity={0.4}
              >
                <Popup>
                  <div style={{ color: '#1a1a2e', fontSize: '12px', lineHeight: 1.4, minWidth: 140 }}>
                    <strong>{p.title}</strong><br/>
                    <span style={{ fontSize: '10px', color: '#666' }}>
                      {p.user_name} &middot; {p.category}<br/>
                      {p.location_name && <>{p.location_name}<br/></>}
                      Trust: +{p.trust_signal.toFixed(1)}
                    </span>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        )}
      </div>

      {/* Legend */}
      <div className="px-4 py-2 flex gap-3 overflow-x-auto" style={{ background: '#050510', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        {Object.entries(CATEGORY_COLORS).slice(0, 6).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1.5 shrink-0">
            <span className="w-2 h-2 rounded-full" style={{ background: color }} />
            <span className="text-[9px] text-white/30 capitalize">{cat}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

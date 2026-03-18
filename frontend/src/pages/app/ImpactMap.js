import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Loader2, Tag, Users, MapPin } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  education: '#7c3aed',
  environment: '#10b981',
  health: '#f43f5e',
  community: '#00d4ff',
  technology: '#f59e0b',
  mentorship: '#ec4899',
  volunteering: '#8b5cf6',
  other: '#6b7280',
};

function createIcon(category) {
  const color = CATEGORY_COLORS[category] || '#6b7280';
  return L.divIcon({
    className: 'map-marker-custom',
    html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 0 8px ${color}80;"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
}

export default function ImpactMap() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    const fetchMap = async () => {
      try {
        const res = await fetch(`${API_URL}/api/actions/map`, { signal: controller.signal });
        const data = await res.json();
        if (data.success) setPoints(data.points);
      } catch (err) {
        if (err.name !== 'AbortError') console.error('Map fetch error:', err);
      }
      if (!controller.signal.aborted) setLoading(false);
    };
    fetchMap();
    return () => controller.abort();
  }, []);

  if (loading) {
    return (
      <div className="map-page" data-testid="impact-map-page">
        <div className="feed-loading">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading map...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="map-page" data-testid="impact-map-page">
      <div className="map-header">
        <h1 className="feed-title" data-testid="map-title">Impact Map</h1>
        <p className="feed-subtitle">{points.length} actions on the map</p>
      </div>

      <div className="map-container" data-testid="map-container">
        <MapContainer
          center={[31.5, 34.8]}
          zoom={3}
          style={{ height: '100%', width: '100%', borderRadius: '12px' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          {points.map(pt => (
            <Marker key={pt.id} position={[pt.lat, pt.lng]} icon={createIcon(pt.category)}>
              <Popup>
                <div className="map-popup" data-testid={`map-popup-${pt.id}`}>
                  <strong>{pt.title}</strong>
                  <div className="map-popup-row">
                    <Tag className="w-3 h-3" /> {pt.category}
                  </div>
                  <div className="map-popup-row">
                    <Users className="w-3 h-3" /> {pt.user_name}
                  </div>
                  {pt.community && (
                    <div className="map-popup-row">
                      <Users className="w-3 h-3" /> {pt.community}
                    </div>
                  )}
                  {pt.location_name && (
                    <div className="map-popup-row">
                      <MapPin className="w-3 h-3" /> {pt.location_name}
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Legend */}
      <div className="map-legend" data-testid="map-legend">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <span key={cat} className="map-legend-item">
            <span className="map-legend-dot" style={{ background: color }} />
            {cat}
          </span>
        ))}
      </div>
    </div>
  );
}

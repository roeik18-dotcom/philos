import { useState } from 'react';
import { Send, MapPin, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { value: 'education', label: 'Education' },
  { value: 'environment', label: 'Environment' },
  { value: 'health', label: 'Health' },
  { value: 'community', label: 'Community' },
  { value: 'technology', label: 'Technology' },
  { value: 'mentorship', label: 'Mentorship' },
  { value: 'volunteering', label: 'Volunteering' },
  { value: 'other', label: 'Other' },
];

export default function PostAction({ user, onPosted }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'community',
    community: '',
    location_name: '',
    location_lat: null,
    location_lng: null,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [detectingLocation, setDetectingLocation] = useState(false);

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const detectLocation = () => {
    if (!navigator.geolocation) return;
    setDetectingLocation(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm(prev => ({
          ...prev,
          location_lat: pos.coords.latitude,
          location_lng: pos.coords.longitude,
          location_name: prev.location_name || 'Current location',
        }));
        setDetectingLocation(false);
      },
      () => setDetectingLocation(false),
      { timeout: 8000 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      setError('Title and description are required.');
      return;
    }
    setError('');
    setSubmitting(true);

    try {
      const token = localStorage.getItem('philos_auth_token');
      const res = await fetch(`${API_URL}/api/actions/post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (data.success) {
        onPosted?.();
      } else {
        setError(data.detail || 'Failed to post action.');
      }
    } catch (err) {
      setError('Network error. Try again.');
    }
    setSubmitting(false);
  };

  return (
    <div className="post-page" data-testid="post-action-page">
      <div className="post-header">
        <h1 className="post-title" data-testid="post-title">Post an Action</h1>
        <p className="post-subtitle">Share what you did. Let the field register your impact.</p>
      </div>

      <form className="post-form" onSubmit={handleSubmit} data-testid="post-form">
        {error && <div className="post-error" data-testid="post-error">{error}</div>}

        <div className="form-group">
          <label className="form-label" htmlFor="title">Title</label>
          <input
            id="title"
            className="form-input"
            type="text"
            placeholder="What did you do?"
            value={form.title}
            onChange={e => handleChange('title', e.target.value)}
            maxLength={120}
            data-testid="input-title"
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="description">Description</label>
          <textarea
            id="description"
            className="form-textarea"
            placeholder="Describe the action and its impact..."
            value={form.description}
            onChange={e => handleChange('description', e.target.value)}
            rows={4}
            maxLength={1000}
            data-testid="input-description"
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="category">Category</label>
          <select
            id="category"
            className="form-select"
            value={form.category}
            onChange={e => handleChange('category', e.target.value)}
            data-testid="input-category"
          >
            {CATEGORIES.map(c => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="community">Community Helped</label>
          <input
            id="community"
            className="form-input"
            type="text"
            placeholder="e.g. Local Volunteers, School Board"
            value={form.community}
            onChange={e => handleChange('community', e.target.value)}
            maxLength={100}
            data-testid="input-community"
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="location_name">Location</label>
          <div className="form-location-row">
            <input
              id="location_name"
              className="form-input"
              type="text"
              placeholder="e.g. Tel Aviv, New York"
              value={form.location_name}
              onChange={e => handleChange('location_name', e.target.value)}
              maxLength={100}
              data-testid="input-location"
            />
            <button
              type="button"
              className="form-detect-btn"
              onClick={detectLocation}
              disabled={detectingLocation}
              data-testid="detect-location-btn"
            >
              {detectingLocation ? <Loader2 className="w-4 h-4 animate-spin" /> : <MapPin className="w-4 h-4" />}
            </button>
          </div>
          {form.location_lat && (
            <span className="form-location-coords" data-testid="location-coords">
              {form.location_lat.toFixed(4)}, {form.location_lng.toFixed(4)}
            </span>
          )}
        </div>

        <button
          type="submit"
          className="form-submit-btn"
          disabled={submitting}
          data-testid="submit-action-btn"
        >
          {submitting ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Posting...</>
          ) : (
            <><Send className="w-4 h-4" /> Post Action</>
          )}
        </button>
      </form>
    </div>
  );
}

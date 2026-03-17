import { useState } from 'react';
import { Send, MapPin, Loader2, Globe, Lock, Check, ArrowRight, Flame, Users, UserCheck } from 'lucide-react';

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

const STEPS = [
  { num: 1, label: 'Create' },
  { num: 2, label: 'Visibility' },
  { num: 3, label: 'Publish' },
];

export default function PostAction({ user, onPosted }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'community',
    community: '',
    location_name: '',
    location_lat: null,
    location_lng: null,
    visibility: 'public',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [posted, setPosted] = useState(false);

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

  const canAdvance = () => {
    if (step === 1) return form.title.trim().length > 0 && form.description.trim().length > 0;
    return true;
  };

  const handleSubmit = async () => {
    setError('');
    setSubmitting(true);
    try {
      const token = localStorage.getItem('philos_auth_token');
      const res = await fetch(`${API_URL}/api/actions/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (data.success) {
        setPosted(true);
      } else {
        setError(data.detail || 'Failed to post action.');
      }
    } catch (err) {
      setError('Network error. Try again.');
    }
    setSubmitting(false);
  };

  // ═══ SUCCESS STATE ═══
  if (posted) {
    return (
      <div className="post-page" data-testid="post-action-page">
        <div className="post-success" data-testid="post-success">
          <div className="post-success-icon"><Check className="w-6 h-6" /></div>
          <h2 className="post-success-title">Action Published</h2>
          <p className="post-success-sub">
            {form.visibility === 'public' ? 'Visible to the network' : 'Stored privately'}
          </p>

          <div className="post-flow-outcome" data-testid="post-flow-outcome">
            <div className="flow-outcome-step">
              <Users className="w-4 h-4" />
              <span>{form.visibility === 'public' ? 'Others can react to your action' : 'Only you can see this action'}</span>
            </div>
            {form.visibility === 'public' && (
              <>
                <div className="flow-outcome-arrow"><ArrowRight className="w-3 h-3" /></div>
                <div className="flow-outcome-step">
                  <Flame className="w-4 h-4" style={{ color: '#f59e0b' }} />
                  <span>Reactions update your trust score</span>
                </div>
                <div className="flow-outcome-arrow"><ArrowRight className="w-3 h-3" /></div>
                <div className="flow-outcome-step">
                  <UserCheck className="w-4 h-4" style={{ color: '#10b981' }} />
                  <span>Trust reflects in your profile</span>
                </div>
              </>
            )}
          </div>

          <button
            className="form-submit-btn"
            onClick={() => onPosted?.()}
            data-testid="go-to-feed-btn"
          >
            View Feed <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="post-page" data-testid="post-action-page">
      {/* ═══ STEP INDICATOR ═══ */}
      <div className="post-steps" data-testid="post-steps">
        {STEPS.map((s, i) => (
          <div key={s.num} className="post-step-wrap">
            {i > 0 && <div className={`post-step-line ${step > s.num - 1 ? 'active' : ''}`} />}
            <button
              className={`post-step ${step === s.num ? 'current' : ''} ${step > s.num ? 'done' : ''}`}
              onClick={() => step > s.num && setStep(s.num)}
              data-testid={`step-${s.num}`}
            >
              {step > s.num ? <Check className="w-3.5 h-3.5" /> : s.num}
            </button>
            <span className={`post-step-label ${step >= s.num ? 'active' : ''}`}>{s.label}</span>
          </div>
        ))}
      </div>

      {error && <div className="post-error" data-testid="post-error">{error}</div>}

      {/* ═══ STEP 1: CREATE ═══ */}
      {step === 1 && (
        <div className="post-step-content" data-testid="step-create">
          <h2 className="post-step-title">What did you do?</h2>

          <div className="form-group">
            <label className="form-label" htmlFor="title">Title</label>
            <input
              id="title" className="form-input" type="text"
              placeholder="What did you do?"
              value={form.title} onChange={e => handleChange('title', e.target.value)}
              maxLength={120} data-testid="input-title"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="description">Description</label>
            <textarea
              id="description" className="form-textarea"
              placeholder="Describe the action and its impact..."
              value={form.description} onChange={e => handleChange('description', e.target.value)}
              rows={4} maxLength={1000} data-testid="input-description"
            />
          </div>

          <div className="form-row">
            <div className="form-group form-half">
              <label className="form-label" htmlFor="category">Category</label>
              <select
                id="category" className="form-select"
                value={form.category} onChange={e => handleChange('category', e.target.value)}
                data-testid="input-category"
              >
                {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
            <div className="form-group form-half">
              <label className="form-label" htmlFor="community">Community</label>
              <input
                id="community" className="form-input" type="text"
                placeholder="e.g. Local Volunteers"
                value={form.community} onChange={e => handleChange('community', e.target.value)}
                maxLength={100} data-testid="input-community"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="location_name">Location</label>
            <div className="form-location-row">
              <input
                id="location_name" className="form-input" type="text"
                placeholder="e.g. Tel Aviv, New York"
                value={form.location_name} onChange={e => handleChange('location_name', e.target.value)}
                maxLength={100} data-testid="input-location"
              />
              <button type="button" className="form-detect-btn" onClick={detectLocation} disabled={detectingLocation} data-testid="detect-location-btn">
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
            className="form-submit-btn"
            disabled={!canAdvance()}
            onClick={() => setStep(2)}
            data-testid="next-to-visibility"
          >
            Next: Choose Visibility <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ═══ STEP 2: VISIBILITY ═══ */}
      {step === 2 && (
        <div className="post-step-content" data-testid="step-visibility">
          <h2 className="post-step-title">Who should see this?</h2>

          <div className="visibility-options" data-testid="visibility-options">
            <button
              className={`visibility-card ${form.visibility === 'public' ? 'selected' : ''}`}
              onClick={() => handleChange('visibility', 'public')}
              data-testid="visibility-public"
            >
              <Globe className="w-5 h-5" />
              <span className="visibility-card-title">Public</span>
              <span className="visibility-card-desc">Visible in the feed. Others can react. Builds trust.</span>
              <div className="visibility-card-flow">
                <span className="vf-tag vf-reactions">Reactions</span>
                <ArrowRight className="w-3 h-3" />
                <span className="vf-tag vf-trust">Trust</span>
                <ArrowRight className="w-3 h-3" />
                <span className="vf-tag vf-profile">Profile</span>
              </div>
            </button>

            <button
              className={`visibility-card ${form.visibility === 'private' ? 'selected' : ''}`}
              onClick={() => handleChange('visibility', 'private')}
              data-testid="visibility-private"
            >
              <Lock className="w-5 h-5" />
              <span className="visibility-card-title">Private</span>
              <span className="visibility-card-desc">Only you can see it. No reactions. No trust change.</span>
              <div className="visibility-card-flow">
                <span className="vf-tag vf-private">Personal record</span>
              </div>
            </button>
          </div>

          <div className="step-nav-row">
            <button className="form-back-btn" onClick={() => setStep(1)} data-testid="back-to-create">Back</button>
            <button className="form-submit-btn" onClick={() => setStep(3)} data-testid="next-to-publish">
              Next: Review <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ═══ STEP 3: PUBLISH ═══ */}
      {step === 3 && (
        <div className="post-step-content" data-testid="step-publish">
          <h2 className="post-step-title">Review & Publish</h2>

          <div className="publish-preview" data-testid="publish-preview">
            <div className="publish-preview-header">
              <span className={`publish-vis-badge vis-${form.visibility}`} data-testid="publish-visibility-badge">
                {form.visibility === 'public' ? <Globe className="w-3 h-3" /> : <Lock className="w-3 h-3" />}
                {form.visibility}
              </span>
              <span className="publish-category">{form.category}</span>
            </div>
            <h3 className="publish-preview-title">{form.title}</h3>
            <p className="publish-preview-desc">{form.description}</p>
            {form.community && <p className="publish-preview-community">Community: {form.community}</p>}
            {form.location_name && <p className="publish-preview-location"><MapPin className="w-3 h-3" /> {form.location_name}</p>}
          </div>

          {form.visibility === 'public' && (
            <div className="publish-trust-flow" data-testid="publish-trust-flow">
              <div className="trust-flow-item"><span className="tf-num">4</span> Receive reactions</div>
              <div className="trust-flow-item"><span className="tf-num">5</span> Update trust score</div>
              <div className="trust-flow-item"><span className="tf-num">6</span> Reflect in profile</div>
            </div>
          )}

          <div className="step-nav-row">
            <button className="form-back-btn" onClick={() => setStep(2)} data-testid="back-to-visibility">Back</button>
            <button
              className="form-submit-btn form-publish-btn"
              disabled={submitting}
              onClick={handleSubmit}
              data-testid="submit-action-btn"
            >
              {submitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Publishing...</>
              ) : (
                <><Send className="w-4 h-4" /> Publish Action</>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

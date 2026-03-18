import { useState } from 'react';
import { ArrowLeft, MapPin, Send } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { id: 'education', label: 'Education' },
  { id: 'environment', label: 'Environment' },
  { id: 'health', label: 'Health' },
  { id: 'community', label: 'Community' },
  { id: 'technology', label: 'Technology' },
  { id: 'mentorship', label: 'Mentorship' },
  { id: 'volunteering', label: 'Volunteering' },
  { id: 'other', label: 'Other' },
];

export default function PostActionPage({ user, onBack }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('community');
  const [community, setCommunity] = useState('');
  const [locationName, setLocationName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !user) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/actions/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${user.token}` },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          category,
          community: community.trim(),
          location_name: locationName.trim(),
        }),
      });
      const data = await res.json();
      if (data.success) {
        setSuccess(true);
        setTimeout(() => { window.location.href = '/app/feed'; }, 1200);
      }
    } finally { setSubmitting(false); }
  };

  if (!user) {
    return (
      <div className="max-w-md mx-auto px-4 pt-12 text-center">
        <p className="text-white/40 text-sm mb-3">You need to sign in to post an action.</p>
        <a href="/" className="text-xs text-cyan-400">Sign in</a>
      </div>
    );
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto px-4 pt-20 text-center" data-testid="post-success">
        <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
          <Send className="w-5 h-5 text-emerald-400" />
        </div>
        <p className="text-sm font-medium mb-1">Action posted</p>
        <p className="text-xs text-white/40">Your impact is now visible in the feed.</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 pb-24" data-testid="post-action-page">
      <div className="pt-4 pb-6">
        <button onClick={onBack || (() => window.history.back())} className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60 transition mb-4">
          <ArrowLeft className="w-3 h-3" /> Back
        </button>
        <h1 className="text-lg font-semibold">Post an Action</h1>
        <p className="text-xs text-white/40 mt-1">Share what you did. Build trust through action.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-[10px] uppercase tracking-wider text-white/30 mb-1.5">What did you do?</label>
          <input
            value={title} onChange={e => setTitle(e.target.value)}
            placeholder="e.g. Organized a community cleanup"
            className="w-full bg-white/[0.03] border border-white/[0.06] rounded-lg px-3 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/30"
            data-testid="post-title"
            required
          />
        </div>

        <div>
          <label className="block text-[10px] uppercase tracking-wider text-white/30 mb-1.5">Description</label>
          <textarea
            value={description} onChange={e => setDescription(e.target.value)}
            placeholder="Tell us more about your action..."
            rows={3}
            className="w-full bg-white/[0.03] border border-white/[0.06] rounded-lg px-3 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/30 resize-none"
            data-testid="post-description"
          />
        </div>

        <div>
          <label className="block text-[10px] uppercase tracking-wider text-white/30 mb-2">Category</label>
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map(c => (
              <button key={c.id} type="button" onClick={() => setCategory(c.id)}
                className={`text-[10px] px-2.5 py-1 rounded-full border transition ${category === c.id ? 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10' : 'border-white/[0.06] text-white/40 hover:text-white/60'}`}>
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-[10px] uppercase tracking-wider text-white/30 mb-1.5">Community (optional)</label>
          <input
            value={community} onChange={e => setCommunity(e.target.value)}
            placeholder="e.g. Local Volunteers"
            className="w-full bg-white/[0.03] border border-white/[0.06] rounded-lg px-3 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/30"
            data-testid="post-community"
          />
        </div>

        <div>
          <label className="block text-[10px] uppercase tracking-wider text-white/30 mb-1.5">
            <MapPin className="w-3 h-3 inline mr-1" />Location (optional)
          </label>
          <input
            value={locationName} onChange={e => setLocationName(e.target.value)}
            placeholder="e.g. Tel Aviv"
            className="w-full bg-white/[0.03] border border-white/[0.06] rounded-lg px-3 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/30"
            data-testid="post-location"
          />
        </div>

        <button
          type="submit" disabled={!title.trim() || submitting}
          className="w-full py-2.5 rounded-lg text-sm font-medium bg-gradient-to-r from-cyan-500 to-cyan-600 text-white transition hover:opacity-90 disabled:opacity-30"
          data-testid="post-submit"
        >
          {submitting ? 'Posting...' : 'Post Action'}
        </button>
      </form>
    </div>
  );
}

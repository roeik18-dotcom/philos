import { useState } from 'react';
import { X, Send } from 'lucide-react';

export default function CreateRequestModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    category: 'body',
    need: '',
    minutes: '',
    distance: ''
  });

  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.name.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!formData.need.trim()) {
      setError('Please describe what help you need');
      return;
    }
    if (!formData.minutes || formData.minutes < 1) {
      setError('Please enter estimated time');
      return;
    }

    // Submit the request
    onSubmit({
      ...formData,
      minutes: parseInt(formData.minutes),
      distance: formData.distance.trim() || 'Not noted'
    });

    // Reset form
    setFormData({
      name: '',
      category: 'body',
      need: '',
      minutes: '',
      distance: ''
    });
    onClose();
  };

  if (!isOpen) return null;

  const getCategoryLabel = (cat) => {
    const labels = {
      body: 'Body',
      emotion: 'Emotion',
      mind: 'Mind'
    };
    return labels[cat];
  };

  return (
    <div 
      className="fixed inset-0 bg-foreground/20 backdrop-blur-sm flex items-end md:items-center justify-center"
      style={{ zIndex: 10000 }}
      onClick={onClose}
      data-testid="create-request-modal"
    >
      <div 
        className="bg-background rounded-t-[2rem] md:rounded-[2rem] w-full max-w-md max-h-[90vh] overflow-y-auto p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-foreground">Need help?</h2>
          <button
            onClick={onClose}
            className="rounded-full hover:bg-muted text-muted-foreground hover:text-foreground h-10 w-10 p-0 flex items-center justify-center transition-all"
            data-testid="close-modal-button"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-base font-medium text-foreground mb-2">
              Your Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
              placeholder="e.g., David"
              data-testid="name-input"
            />
          </div>

          <div>
            <label className="block text-base font-medium text-foreground mb-2">
              Help type
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
              data-testid="category-select"
            >
              <option value="body">Body</option>
              <option value="emotion">Emotion</option>
              <option value="mind">Mind</option>
            </select>
          </div>

          <div>
            <label className="block text-base font-medium text-foreground mb-2">
              Description short
            </label>
            <input
              type="text"
              value={formData.need}
              onChange={(e) => setFormData({ ...formData, need: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
              placeholder="e.g., Help with a walk in the park"
              maxLength="50"
              data-testid="description-input"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-base font-medium text-foreground mb-2">
                Estimated time (minutes)
              </label>
              <input
                type="number"
                value={formData.minutes}
                onChange={(e) => setFormData({ ...formData, minutes: e.target.value })}
                className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
                min="1"
                max="120"
                placeholder="20"
                data-testid="minutes-input"
              />
            </div>

            <div>
              <label className="block text-base font-medium text-foreground mb-2">
                Distance (optional)
              </label>
              <input
                type="text"
                value={formData.distance}
                onChange={(e) => setFormData({ ...formData, distance: e.target.value })}
                className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
                placeholder='0.5 km'
                data-testid="distance-input"
              />
            </div>
          </div>

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-2xl p-4 text-center">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <button
            type="submit"
            className="mt-4 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 h-14 px-10 shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center justify-center gap-3 text-lg font-medium tracking-wide"
            data-testid="submit-request-button"
          >
            <Send className="w-5 h-5" />
            <span>Submit request</span>
          </button>
        </form>
      </div>
    </div>
  );
}

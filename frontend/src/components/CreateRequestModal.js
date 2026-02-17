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
      setError('נא להזין שם פרטי');
      return;
    }
    if (!formData.need.trim()) {
      setError('נא להזין תיאור העזרה');
      return;
    }
    if (!formData.minutes || formData.minutes < 1) {
      setError('נא להזין זמן משוער');
      return;
    }

    // Submit the request
    onSubmit({
      ...formData,
      minutes: parseInt(formData.minutes),
      distance: formData.distance.trim() || 'לא צוין'
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
      body: 'גוף',
      emotion: 'רגש',
      mind: 'מחשבה'
    };
    return labels[cat];
  };

  return (
    <div 
      className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-[100] flex items-end md:items-center justify-center"
      onClick={onClose}
      data-testid="create-request-modal"
    >
      <div 
        className="bg-background rounded-t-[2rem] md:rounded-[2rem] w-full max-w-md max-h-[90vh] overflow-y-auto p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-foreground">צריך עזרה?</h2>
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
              שם פרטי
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
              placeholder="לדוגמה: דוד"
              data-testid="name-input"
            />
          </div>

          <div>
            <label className="block text-base font-medium text-foreground mb-2">
              סוג עזרה
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
              data-testid="category-select"
            >
              <option value="body">גוף</option>
              <option value="emotion">רגש</option>
              <option value="mind">מחשבה</option>
            </select>
          </div>

          <div>
            <label className="block text-base font-medium text-foreground mb-2">
              תיאור קצר
            </label>
            <input
              type="text"
              value={formData.need}
              onChange={(e) => setFormData({ ...formData, need: e.target.value })}
              className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
              placeholder="לדוגמה: ליווי להליכה בפארק"
              maxLength="50"
              data-testid="description-input"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-base font-medium text-foreground mb-2">
                זמן משוער (דקות)
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
                מרחק (אופציונלי)
              </label>
              <input
                type="text"
                value={formData.distance}
                onChange={(e) => setFormData({ ...formData, distance: e.target.value })}
                className="w-full rounded-2xl border border-border bg-white/50 px-4 py-3 text-base focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/50"
                placeholder='0.5 ק"מ'
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
            <span>שלח בקשה</span>
          </button>
        </form>
      </div>
    </div>
  );
}

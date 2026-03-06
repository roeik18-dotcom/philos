import { useState } from 'react';

const GAP_TYPES = ['energy', 'clarity', 'order', 'relation', 'collective_value'];
const SCOPES = ['self', 'one_person', 'small_group', 'community'];

export default function EventZeroForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    current_state: '',
    required_state: '',
    gap_type: 'energy',
    urgency: 50,
    scope: 'self',
    emotion: '',
    context: '',
    desire: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.current_state || !formData.required_state) {
      alert('Current state and required state are required');
      return;
    }

    const eventZero = {
      ...formData,
      urgency: parseInt(formData.urgency),
      event_zero_summary: `Event Zero identified: ${formData.gap_type} gap between current state and required state`
    };

    onSubmit(eventZero);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Current State *
          </label>
          <input
            type="text"
            value={formData.current_state}
            onChange={(e) => setFormData({ ...formData, current_state: e.target.value })}
            className="w-full px-4 py-2 border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-transparent"
            placeholder="e.g., confused and tired"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Required State *
          </label>
          <input
            type="text"
            value={formData.required_state}
            onChange={(e) => setFormData({ ...formData, required_state: e.target.value })}
            className="w-full px-4 py-2 border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-transparent"
            placeholder="e.g., clear and energized"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Gap Type
          </label>
          <select
            value={formData.gap_type}
            onChange={(e) => setFormData({ ...formData, gap_type: e.target.value })}
            className="w-full px-4 py-2 border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-transparent"
          >
            {GAP_TYPES.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Scope
          </label>
          <select
            value={formData.scope}
            onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
            className="w-full px-4 py-2 border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-transparent"
          >
            {SCOPES.map(scope => (
              <option key={scope} value={scope}>{scope}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Urgency: {formData.urgency}
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={formData.urgency}
            onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
            className="w-full"
          />
        </div>
      </div>

      <button
        type="submit"
        className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all"
      >
        Set Event Zero
      </button>
    </form>
  );
}

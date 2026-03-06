import { useState } from 'react';

export default function ActionEvaluationForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    action_harm: 0,
    personal_gain: 0,
    collective_gain: 0
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      action_harm: parseInt(formData.action_harm),
      personal_gain: parseInt(formData.personal_gain),
      collective_gain: parseInt(formData.collective_gain)
    });
  };

  const fields = [
    { key: 'action_harm', label: 'נזק' },
    { key: 'personal_gain', label: 'רווח אישי' },
    { key: 'collective_gain', label: 'רווח קולקטיבי' }
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {fields.map(field => (
        <div key={field.key}>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-foreground">
              {field.label}
            </label>
            <span className="text-sm font-bold text-foreground">
              {formData[field.key]}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={formData[field.key]}
            onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
            className="w-full"
          />
        </div>
      ))}

      <button
        type="submit"
        className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all"
      >
        הגדר הערכה
      </button>
    </form>
  );
}

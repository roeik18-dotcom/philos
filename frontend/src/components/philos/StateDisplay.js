import { useState, useEffect } from 'react';

export default function StateDisplay({ state, onChange }) {
  const [formData, setFormData] = useState({
    emotional_intensity: 50,
    rational_clarity: 50,
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0
  });

  useEffect(() => {
    if (state) {
      setFormData(state);
    }
  }, [state]);

  const handleChange = (field, value) => {
    const newData = { ...formData, [field]: parseInt(value) };
    setFormData(newData);
    onChange(newData);
  };

  const fields = [
    { key: 'emotional_intensity', label: 'Emotional Intensity', min: 0, max: 100 },
    { key: 'rational_clarity', label: 'Rational Clarity', min: 0, max: 100 },
    { key: 'physical_capacity', label: 'Physical Capacity', min: 0, max: 100 },
    { key: 'chaos_order', label: 'Chaos ← → Order', min: -100, max: 100 },
    { key: 'ego_collective', label: 'Ego ← → Collective', min: -100, max: 100 }
  ];

  return (
    <div className="space-y-4">
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
            min={field.min}
            max={field.max}
            value={formData[field.key]}
            onChange={(e) => handleChange(field.key, e.target.value)}
            className="w-full"
          />
          {field.min < 0 && (
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>{field.label.split('←')[0].trim()}</span>
              <span>{field.label.split('→')[1].trim()}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

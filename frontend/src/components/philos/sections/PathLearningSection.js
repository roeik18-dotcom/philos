import { useMemo } from 'react';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance',
  neutral: 'Neutral'
};

// Color mapping for value tags
const valueColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700' },
  harm: { bg: 'bg-red-100', text: 'text-red-700' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-700' }
};

// Calculate match quality between predicted and actual
const calculateMatchQuality = (predicted, actual) => {
  let matchScore = 0;
  let totalChecks = 0;

  // Check value_tag match (most important)
  if (predicted.predicted_value_tag === actual.value_tag) {
    matchScore += 3;
  } else if (
    // Partial match for related tags
    (predicted.predicted_value_tag === 'recovery' && actual.value_tag === 'order') ||
    (predicted.predicted_value_tag === 'order' && actual.value_tag === 'recovery') ||
    (predicted.predicted_value_tag === 'contribution' && actual.value_tag === 'recovery')
  ) {
    matchScore += 1;
  }
  totalChecks += 3;

  // Check order drift direction
  const predictedOrderDir = predicted.predicted_order_drift > 0 ? 1 : predicted.predicted_order_drift < 0 ? -1 : 0;
  const actualOrderDir = actual.orderDrift > 0 ? 1 : actual.orderDrift < 0 ? -1 : 0;
  if (predictedOrderDir === actualOrderDir) matchScore += 2;
  else if (Math.abs(predictedOrderDir - actualOrderDir) === 1) matchScore += 1;
  totalChecks += 2;

  // Check collective drift direction
  const predictedCollDir = predicted.predicted_collective_drift > 0 ? 1 : predicted.predicted_collective_drift < 0 ? -1 : 0;
  const actualCollDir = actual.collectiveDrift > 0 ? 1 : actual.collectiveDrift < 0 ? -1 : 0;
  if (predictedCollDir === actualCollDir) matchScore += 2;
  else if (Math.abs(predictedCollDir - actualCollDir) === 1) matchScore += 1;
  totalChecks += 2;

  // Check harm pressure direction (negative is good)
  const predictedHarmGood = predicted.predicted_harm_pressure < 0;
  const actualHarmGood = actual.harmPressure < 0;
  if (predictedHarmGood === actualHarmGood) matchScore += 1;
  totalChecks += 1;

  // Calculate percentage
  const matchPercentage = (matchScore / totalChecks) * 100;

  if (matchPercentage >= 70) return { quality: 'high', label: 'High', color: 'text-green-600', bg: 'bg-green-100' };
  if (matchPercentage >= 40) return { quality: 'medium', label: 'Moderate', color: 'text-yellow-600', bg: 'bg-yellow-100' };
  return { quality: 'low', label: 'Low', color: 'text-red-600', bg: 'bg-red-100' };
};

// Generate insight text in Hebrew
const generateInsight = (predicted, actual, matchQuality) => {
  const insights = [];
  
  // Value tag insight
  if (predicted.predicted_value_tag === actual.value_tag) {
    insights.push(`The chosen path did lead to ${valueLabels[actual.value_tag]}.`);
  } else {
    insights.push(`The prediction was ${valueLabels[predicted.predicted_value_tag]}, but the result was ${valueLabels[actual.value_tag]}.`);
  }

  // Order drift insight
  if (predicted.predicted_order_drift > 0 && actual.orderDrift > 0) {
    insights.push('Order drift increased as expected.');
  } else if (predicted.predicted_order_drift < 0 && actual.orderDrift < 0) {
    insights.push('Order drift decreased as expected.');
  } else if (Math.sign(predicted.predicted_order_drift) !== Math.sign(actual.orderDrift) && actual.orderDrift !== 0) {
    insights.push('Order drift behaved differently from the prediction.');
  }

  // Collective drift insight
  if (predicted.predicted_collective_drift > 0 && actual.collectiveDrift > 0) {
    insights.push('Social contribution increased as expected.');
  } else if (predicted.predicted_collective_drift !== 0 && actual.collectiveDrift === 0) {
    insights.push('Social impact was not realized.');
  }

  // Harm pressure insight
  if (predicted.predicted_harm_pressure < 0 && actual.harmPressure < 0) {
    insights.push('Harm pressure decreased — positive result!');
  } else if (predicted.predicted_harm_pressure < 0 && actual.harmPressure > 0) {
    insights.push('Harm pressure increased despite the prediction.');
  }

  // Overall summary based on match quality
  if (matchQuality.quality === 'high') {
    insights.push('The prediction was mostly accurate.');
  } else if (matchQuality.quality === 'medium') {
    insights.push('The prediction was only partial.');
  } else {
    insights.push('The prediction did not match the actual result.');
  }

  return insights.slice(0, 3);
};

export default function PathLearningSection({ selectedPath, actualOutcome }) {
  // Calculate actual metrics from outcome (must be before any conditional returns)
  const actualMetrics = useMemo(() => {
    if (!actualOutcome) return null;
    return {
      value_tag: actualOutcome.value_tag,
      orderDrift: actualOutcome.projection?.chaos_order || 0,
      collectiveDrift: actualOutcome.projection?.ego_collective || 0,
      harmPressure: actualOutcome.value_tag === 'harm' ? 20 : actualOutcome.value_tag === 'avoidance' ? 10 : -10,
      recoveryStability: actualOutcome.value_tag === 'recovery' ? 20 : actualOutcome.balance_score > 60 ? 10 : -5
    };
  }, [actualOutcome]);

  // Calculate match quality
  const matchQuality = useMemo(() => {
    if (!selectedPath || !actualMetrics) return null;
    return calculateMatchQuality(selectedPath, actualMetrics);
  }, [selectedPath, actualMetrics]);

  // Generate insights
  const insights = useMemo(() => {
    if (!selectedPath || !actualMetrics || !matchQuality) return [];
    return generateInsight(selectedPath, actualMetrics, matchQuality);
  }, [selectedPath, actualMetrics, matchQuality]);

  // Don't render if no data
  if (!selectedPath || !actualOutcome || !actualMetrics || !matchQuality) {
    return null;
  }

  const predictedColors = valueColors[selectedPath.predicted_value_tag] || valueColors.recovery;
  const actualColors = valueColors[actualMetrics.value_tag] || valueColors.recovery;

  return (
    <section 
      className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-cyan-200"
      data-testid="path-learning-section"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Path Learning</h3>
          <p className="text-xs text-muted-foreground">Comparison between prediction and actual result</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-bold ${matchQuality.bg} ${matchQuality.color}`}>
          Match: {matchQuality.label}
        </div>
      </div>

      {/* Selected Path Info */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-sm font-medium text-muted-foreground mb-2">Chosen path:</p>
        <p className="text-lg font-semibold text-foreground">{selectedPath.suggested_action}</p>
        <p className="text-xs text-muted-foreground mt-1">
          Chosen at {new Date(selectedPath.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Predicted Column */}
        <div className="bg-white/70 rounded-xl p-4">
          <p className="text-sm font-semibold text-foreground mb-3 text-center border-b pb-2">Prediction</p>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">value_tag</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${predictedColors.bg} ${predictedColors.text}`}>
                {valueLabels[selectedPath.predicted_value_tag]}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">order drift</span>
              <span className={`text-sm font-bold ${selectedPath.predicted_order_drift > 0 ? 'text-green-600' : selectedPath.predicted_order_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {selectedPath.predicted_order_drift > 0 ? '+' : ''}{selectedPath.predicted_order_drift}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">collective drift</span>
              <span className={`text-sm font-bold ${selectedPath.predicted_collective_drift > 0 ? 'text-green-600' : selectedPath.predicted_collective_drift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {selectedPath.predicted_collective_drift > 0 ? '+' : ''}{selectedPath.predicted_collective_drift}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">harm pressure</span>
              <span className={`text-sm font-bold ${selectedPath.predicted_harm_pressure < 0 ? 'text-green-600' : 'text-red-600'}`}>
                {selectedPath.predicted_harm_pressure > 0 ? '+' : ''}{selectedPath.predicted_harm_pressure}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">recovery stability</span>
              <span className={`text-sm font-bold ${selectedPath.predicted_recovery_stability > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {selectedPath.predicted_recovery_stability > 0 ? '+' : ''}{selectedPath.predicted_recovery_stability}%
              </span>
            </div>
          </div>
        </div>

        {/* Actual Column */}
        <div className="bg-white/70 rounded-xl p-4">
          <p className="text-sm font-semibold text-foreground mb-3 text-center border-b pb-2">Actual Result</p>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">value_tag</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${actualColors.bg} ${actualColors.text}`}>
                {valueLabels[actualMetrics.value_tag]}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">order drift</span>
              <span className={`text-sm font-bold ${actualMetrics.orderDrift > 0 ? 'text-green-600' : actualMetrics.orderDrift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {actualMetrics.orderDrift > 0 ? '+' : ''}{actualMetrics.orderDrift}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">collective drift</span>
              <span className={`text-sm font-bold ${actualMetrics.collectiveDrift > 0 ? 'text-green-600' : actualMetrics.collectiveDrift < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {actualMetrics.collectiveDrift > 0 ? '+' : ''}{actualMetrics.collectiveDrift}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">harm pressure</span>
              <span className={`text-sm font-bold ${actualMetrics.harmPressure < 0 ? 'text-green-600' : 'text-red-600'}`}>
                {actualMetrics.harmPressure > 0 ? '+' : ''}{actualMetrics.harmPressure}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">recovery stability</span>
              <span className={`text-sm font-bold ${actualMetrics.recoveryStability > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {actualMetrics.recoveryStability > 0 ? '+' : ''}{actualMetrics.recoveryStability}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Match Indicators */}
      <div className="bg-white/70 rounded-xl p-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Match quality:</span>
          <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                matchQuality.quality === 'high' ? 'bg-green-500 w-full' :
                matchQuality.quality === 'medium' ? 'bg-yellow-500 w-2/3' :
                'bg-red-500 w-1/3'
              }`}
            />
          </div>
          <span className={`text-sm font-bold ${matchQuality.color}`}>
            {matchQuality.label}
          </span>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-cyan-100/50 border border-cyan-200 rounded-xl p-4">
        <p className="text-sm font-semibold text-cyan-800 mb-2">Insights:</p>
        <div className="space-y-1">
          {insights.map((insight, idx) => (
            <p key={idx} className="text-sm text-cyan-700">• {insight}</p>
          ))}
        </div>
      </div>
    </section>
  );
}

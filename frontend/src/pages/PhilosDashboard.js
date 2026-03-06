import { useState } from 'react';
import { PhilosEngine, EventZero, State, ActionEvaluation } from '../philos';
import EventZeroForm from '../components/philos/EventZeroForm';
import StateDisplay from '../components/philos/StateDisplay';
import ActionEvaluationForm from '../components/philos/ActionEvaluationForm';
import DecisionDisplay from '../components/philos/DecisionDisplay';
import ActionPathDisplay from '../components/philos/ActionPathDisplay';
import DecisionMap from '../components/philos/DecisionMap';
import HistoryList from '../components/philos/HistoryList';

const engine = new PhilosEngine();

export default function PhilosDashboard() {
  const [eventZero, setEventZero] = useState(null);
  const [state, setState] = useState({
    emotional_intensity: 50,
    rational_clarity: 50,
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0
  });
  const [actionText, setActionText] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [decisionResult, setDecisionResult] = useState(null);
  const [history, setHistory] = useState([]);

  const handleEvaluate = () => {
    if (!eventZero || !state || !evaluation) {
      alert('יש למלא את כל השדות');
      return;
    }

    try {
      const evaluationResult = engine.evaluate(eventZero, state, evaluation);
      setDecisionResult(evaluationResult);
      setHistory(engine.getHistory());
    } catch (error) {
      console.error('Error evaluating:', error);
      alert('שגיאה בהערכה: ' + error.message);
    }
  };

  const handleReset = () => {
    setEventZero(null);
    setState({
      emotional_intensity: 50,
      rational_clarity: 50,
      physical_capacity: 50,
      chaos_order: 0,
      ego_collective: 0
    });
    setActionText("");
    setEvaluation(null);
    setDecisionResult(null);
  };

  const handleClearHistory = () => {
    engine.clearHistory();
    setHistory([]);
  };

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Philos Orientation
          </h1>
          <p className="text-muted-foreground">
            Event Zero → State → Constraints → Decision → Action Path
          </p>
        </div>

        {/* Event Zero */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <h2 className="text-2xl font-semibold text-foreground mb-4">Event Zero</h2>
          <EventZeroForm onSubmit={setEventZero} />
          {eventZero && (
            <div className="mt-4 p-4 bg-muted/30 rounded-2xl">
              <p className="text-sm text-muted-foreground">Summary:</p>
              <p className="text-foreground">{eventZero.event_zero_summary}</p>
            </div>
          )}
        </section>

        {/* State / Forces */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <h2 className="text-2xl font-semibold text-foreground mb-4">State / Forces</h2>
          <StateDisplay state={state} onChange={setState} />
        </section>

        {/* Action Evaluation */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <h2 className="text-2xl font-semibold text-foreground mb-4">הערכת פעולה</h2>
          
          {/* Action Text Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-foreground mb-2">
              פעולה
            </label>
            <input
              type="text"
              value={actionText}
              onChange={(e) => setActionText(e.target.value)}
              className="w-full px-4 py-3 border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-transparent text-lg"
              placeholder="מה אתה רוצה לעשות?"
            />
          </div>
          
          <ActionEvaluationForm onSubmit={setEvaluation} />
        </section>

        {/* Evaluate Button */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={handleEvaluate}
            disabled={!eventZero || !state || !evaluation}
            className="px-8 py-3 bg-primary text-primary-foreground rounded-full font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-all"
          >
            הערך החלטה
          </button>
          <button
            onClick={handleReset}
            className="px-8 py-3 bg-secondary text-secondary-foreground rounded-full font-medium hover:bg-secondary/80 transition-all"
          >
            איפוס
          </button>
        </div>

        {/* Decision Result */}
        {decisionResult && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h2 className="text-2xl font-semibold text-foreground mb-4">תוצאה</h2>
            
            {/* Compact Decision Summary */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">החלטה:</span>
                <span className={`px-4 py-2 rounded-full font-bold ${
                  decisionResult.decision_state.result.status === 'allowed'
                    ? 'bg-green-500/10 text-green-600'
                    : 'bg-red-500/10 text-red-600'
                }`}>
                  {decisionResult.decision_state.result.status === 'allowed' ? '✓ מותר' : '✗ חסום'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">פער:</span>
                <span className="font-medium text-foreground">{eventZero?.gap_type}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">מיקום:</span>
                <span className="font-medium text-foreground">
                  order {state.chaos_order > 0 ? '+' : ''}{state.chaos_order} | collective {state.ego_collective > 0 ? '+' : ''}{state.ego_collective}
                </span>
              </div>

              {actionText && (
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">פעולה:</span>
                  <span className="font-medium text-foreground">{actionText}</span>
                </div>
              )}
            </div>

            {/* Recommendation */}
            <div className="mt-4 p-4 bg-primary/5 border border-primary/20 rounded-2xl">
              <p className="text-foreground font-medium">{decisionResult.decision_state.recommended_action}</p>
            </div>
          </section>
        )}

        {/* Action Path */}
        {decisionResult?.action_path.visible && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h2 className="text-2xl font-semibold text-foreground mb-4">מסלול פעולה</h2>
            <ActionPathDisplay actionPath={decisionResult.action_path} />
          </section>
        )}

        {/* Decision Map */}
        {state && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h2 className="text-2xl font-semibold text-foreground mb-4">מפת ההחלטה</h2>
            <DecisionMap 
              state={state}
              decisionState={decisionResult?.decision_state}
              gapType={eventZero?.gap_type}
            />
          </section>
        )}

        {/* History */}
        {history.length > 0 && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold text-foreground">היסטוריה</h2>
              <button
                onClick={handleClearHistory}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                נקה היסטוריה
              </button>
            </div>
            <HistoryList history={history} />
          </section>
        )}
      </div>
    </div>
  );
}

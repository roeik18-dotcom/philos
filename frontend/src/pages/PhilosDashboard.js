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
  const [evaluation, setEvaluation] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const handleEvaluate = () => {
    if (!eventZero || !state || !evaluation) {
      alert('יש למלא את כל השדות');
      return;
    }

    try {
      const evaluationResult = engine.evaluate(eventZero, state, evaluation);
      setResult(evaluationResult);
      setHistory(engine.getHistory());
    } catch (error) {
      console.error('Error evaluating:', error);
      alert('שגיאה בהערכה: ' + error.message);
    }
  };

  const handleReset = () => {
    setEventZero(null);
    setState(null);
    setEvaluation(null);
    setResult(null);
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
          <h2 className="text-2xl font-semibold text-foreground mb-4">Action Evaluation</h2>
          <ActionEvaluationForm onSubmit={setEvaluation} />
        </section>

        {/* Evaluate Button */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={handleEvaluate}
            disabled={!eventZero || !state || !evaluation}
            className="px-8 py-3 bg-primary text-primary-foreground rounded-full font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-all"
          >
            Evaluate Decision
          </button>
          <button
            onClick={handleReset}
            className="px-8 py-3 bg-secondary text-secondary-foreground rounded-full font-medium hover:bg-secondary/80 transition-all"
          >
            Reset
          </button>
        </div>

        {/* Decision State */}
        {result && (
          <>
            <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
              <h2 className="text-2xl font-semibold text-foreground mb-4">Decision State</h2>
              <DecisionDisplay decision={result.decision_state} />
            </section>

            {/* Action Path */}
            {result.action_path.visible && (
              <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Action Path</h2>
                <ActionPathDisplay actionPath={result.action_path} />
              </section>
            )}
          </>
        )}

        {/* Decision Map */}
        {state && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h2 className="text-2xl font-semibold text-foreground mb-4">מפת ההחלטה</h2>
            <DecisionMap 
              state={state}
              decisionState={result?.decision_state}
              gapType={eventZero?.gap_type}
            />
          </section>
        )}

        {/* History */}
        {history.length > 0 && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold text-foreground">History</h2>
              <button
                onClick={handleClearHistory}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Clear History
              </button>
            </div>
            <HistoryList history={history} />
          </section>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect, useRef } from 'react';
import {
  Eye, GitBranch, Send, Heart, TrendingUp, Award,
  ArrowRight, ArrowLeft, Lock, Globe, Loader2,
  TrendingDown, AlertTriangle, Check,
} from 'lucide-react';
import { useBackendReady } from '../hooks/useBackendReady';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FLOW_STEPS = [
  { key: 'need',     label: 'Need',     icon: Eye },
  { key: 'choice',   label: 'Choice',   icon: GitBranch },
  { key: 'action',   label: 'Action',   icon: Send },
  { key: 'reaction', label: 'Reaction', icon: Heart },
  { key: 'result',   label: 'Result',   icon: TrendingUp },
  { key: 'reward',   label: 'Reward',   icon: Award },
];

const STATUS_ICONS = {
  up: TrendingUp,
  right: ArrowRight,
  down: TrendingDown,
  warning: AlertTriangle,
};

export default function ActionFlow({ user, onExit }) {
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState('forward');
  const { isReady, enqueue } = useBackendReady();

  // Data across steps
  const [baseline, setBaseline] = useState(null);
  const [orientation, setOrientation] = useState(null);
  const [visibility, setVisibility] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', category: 'community' });
  const [submitting, setSubmitting] = useState(false);
  const [postedAction, setPostedAction] = useState(null);
  const [reactionData, setReactionData] = useState(null);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState('');

  const token = localStorage.getItem('philos_auth_token');
  const prevStep = useRef(step);

  useEffect(() => {
    setDirection(step > prevStep.current ? 'forward' : 'backward');
    prevStep.current = step;
  }, [step]);

  // ═══ STEP 0: NEED — fetch baseline ═══
  useEffect(() => {
    if (!user) return;
    Promise.all([
      fetch(`${API_URL}/api/position/${user.id}`).then(r => r.json()),
      fetch(`${API_URL}/api/orientation/${user.id}`).then(r => r.json()),
    ]).then(([pos, ori]) => {
      if (pos.success) setBaseline(pos);
      if (ori.success) setOrientation(ori);
    }).catch(() => {});
  }, [user]);

  // ═══ STEP 4: REACTION — fetch engagement ═══
  useEffect(() => {
    if (step !== 3 || !postedAction) return;
    const fetchReaction = () => {
      fetch(`${API_URL}/api/actions/feed?limit=1&viewer_id=${user.id}`)
        .then(r => r.json())
        .then(d => {
          if (d.success && d.actions?.length) {
            const act = d.actions.find(a => a.id === postedAction.id) || d.actions[0];
            setReactionData(act);
          }
        }).catch(() => {});
    };
    fetchReaction();
    const iv = setInterval(fetchReaction, 5000);
    return () => clearInterval(iv);
  }, [step, postedAction, user]);

  // ═══ STEP 5: RESULT — fetch fresh position and compute deltas ═══
  useEffect(() => {
    if (step !== 4 || !user) return;
    fetch(`${API_URL}/api/position/${user.id}`)
      .then(r => r.json())
      .then(d => {
        if (d.success && baseline) {
          setResultData({
            position: d.position,
            trust: d.total_trust,
            status: d.status,
            posDelta: +(d.position - baseline.position).toFixed(3),
            trustDelta: +(d.total_trust - baseline.total_trust).toFixed(1),
            statusChanged: d.status?.status !== baseline.status?.status,
            prevStatus: baseline.status?.label,
            newStatus: d.status?.label,
            consequence: d.consequence_multiplier,
            panel: d.consequence_panel,
          });
        }
      }).catch(() => {});
  }, [step, user, baseline]);

  const goNext = () => { if (step < 5) setStep(s => s + 1); };
  const goBack = () => { if (step > 0) setStep(s => s - 1); };

  const handlePost = async () => {
    setError('');
    setSubmitting(true);

    const doPost = async () => {
      const res = await fetch(`${API_URL}/api/actions/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ ...form, visibility }),
      });
      const data = await res.json();
      if (data.success) {
        setPostedAction(data);
        goNext();
      } else {
        setError(data.detail || 'Failed to post action.');
      }
      setSubmitting(false);
    };

    if (!isReady) {
      // Queue the action — it will fire when backend wakes
      enqueue(doPost);
    } else {
      try {
        await doPost();
      } catch {
        setError('Connection issue — retrying...');
        enqueue(doPost);
      }
    }
  };

  const StatusIcon = STATUS_ICONS[baseline?.status?.icon] || ArrowRight;

  // ═══ STEP RENDERERS ═══
  const renderNeed = () => {
    const isFirstTime = baseline && baseline.public_actions === 0 && baseline.private_actions === 0;
    const statusColor = baseline?.status?.color || '#f59e0b';
    const insight = orientation?.message || (baseline
      ? `You're at ${baseline.label} with ${baseline.consequence_multiplier}x visibility.`
      : '');

    return (
      <div className="flow-step-content" data-testid="flow-step-need">
        <div className="flow-entry-msg" data-testid="flow-entry-msg">
          {isFirstTime
            ? 'Post one action to see how the system works.'
            : 'One action moves your position.'}
        </div>
        {baseline ? (
          <div className="flow-need-insight" data-testid="flow-need-insight">
            <span
              className="flow-need-status-dot"
              style={{ background: statusColor }}
            />
            <p>{insight}</p>
          </div>
        ) : (
          <div className="flow-loading"><Loader2 className="w-5 h-5 spin" /></div>
        )}
        <button className="flow-cta" onClick={goNext} data-testid="flow-cta-need">
          Take Action <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  };

  const renderChoice = () => (
    <div className="flow-step-content" data-testid="flow-step-choice">
      <div className="flow-step-header">
        <GitBranch className="flow-step-icon" />
        <h2>Choose Visibility</h2>
      </div>
      <p className="flow-step-sub">How should your action appear?</p>
      <div className="flow-choice-options">
        <button
          className={`flow-choice-card ${visibility === 'public' ? 'selected' : ''}`}
          onClick={() => setVisibility('public')}
          data-testid="flow-choice-public"
        >
          <Globe className="w-5 h-5" />
          <span className="flow-choice-title">Public</span>
          <span className="flow-choice-desc">Visible to the network. Earns trust and reactions.</span>
        </button>
        <button
          className={`flow-choice-card ${visibility === 'private' ? 'selected' : ''}`}
          onClick={() => setVisibility('private')}
          data-testid="flow-choice-private"
        >
          <Lock className="w-5 h-5" />
          <span className="flow-choice-title">Private</span>
          <span className="flow-choice-desc">Only you can see it. Builds internal record.</span>
        </button>
      </div>
      <button
        className="flow-cta"
        onClick={goNext}
        disabled={!visibility}
        data-testid="flow-cta-choice"
      >
        Continue <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );

  const renderAction = () => (
    <div className="flow-step-content" data-testid="flow-step-action">
      <div className="flow-step-header">
        <Send className="flow-step-icon" />
        <h2>What did you do?</h2>
      </div>
      <div className="flow-action-form">
        <input
          className="flow-input"
          placeholder="e.g. Helped a neighbor, organized a cleanup..."
          value={form.title}
          onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          autoFocus
          data-testid="flow-input-title"
        />
        <textarea
          className="flow-textarea"
          placeholder="Add details (optional)"
          value={form.description}
          onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          rows={2}
          data-testid="flow-input-description"
        />
        {error && <p className="flow-error">{error}</p>}
      </div>
      <button
        className="flow-cta"
        onClick={handlePost}
        disabled={submitting || !form.title.trim()}
        data-testid="flow-cta-action"
      >
        {submitting ? <Loader2 className="w-4 h-4 spin" /> : <Send className="w-4 h-4" />}
        {submitting ? 'Publishing...' : 'Publish'}
      </button>
    </div>
  );

  const renderReaction = () => {
    const r = reactionData;
    const totalReactions = r
      ? (r.reactions?.support || 0) + (r.reactions?.useful || 0) + (r.reactions?.verified || 0)
      : 0;
    return (
      <div className="flow-step-content" data-testid="flow-step-reaction">
        <div className="flow-step-header">
          <Heart className="flow-step-icon" />
          <h2>Engagement</h2>
        </div>
        {r ? (
          <div className="flow-reaction-grid">
            <div className="flow-reaction-card">
              <span className="flow-reaction-num">{totalReactions}</span>
              <span className="flow-reaction-label">Reactions</span>
            </div>
            <div className="flow-reaction-card">
              <span className="flow-reaction-num">{r.trust_signal || 0}</span>
              <span className="flow-reaction-label">Trust Signal</span>
            </div>
            <div className="flow-reaction-card">
              <span className="flow-reaction-num">{r.visibility_weight || '1.00'}x</span>
              <span className="flow-reaction-label">Visibility</span>
            </div>
          </div>
        ) : (
          <div className="flow-loading"><Loader2 className="w-5 h-5 spin" /></div>
        )}
        <p className="flow-step-sub">
          {visibility === 'public'
            ? 'Your action is live. Reactions are updating in real time.'
            : 'This action is private. Only you can see it.'}
        </p>
        <button className="flow-cta" onClick={goNext} data-testid="flow-cta-reaction">
          See Result <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  };

  const renderResult = () => {
    const d = resultData;
    return (
      <div className="flow-step-content" data-testid="flow-step-result">
        <div className="flow-step-header">
          <TrendingUp className="flow-step-icon" />
          <h2>Your Change</h2>
        </div>
        {d ? (
          <>
            <div className="flow-result-grid">
              <div className="flow-result-card">
                <span className="flow-result-label">Position</span>
                <span className={`flow-result-delta ${d.posDelta > 0 ? 'positive' : d.posDelta < 0 ? 'negative' : ''}`}>
                  {d.posDelta > 0 ? '+' : ''}{(d.posDelta * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flow-result-card">
                <span className="flow-result-label">Trust</span>
                <span className={`flow-result-delta ${d.trustDelta > 0 ? 'positive' : d.trustDelta < 0 ? 'negative' : ''}`}>
                  {d.trustDelta > 0 ? '+' : ''}{d.trustDelta}
                </span>
              </div>
              <div className="flow-result-card">
                <span className="flow-result-label">Status</span>
                <span className="flow-result-delta" style={{ color: d.status?.color }}>
                  {d.statusChanged ? `${d.prevStatus} → ${d.newStatus}` : d.newStatus}
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="flow-loading"><Loader2 className="w-5 h-5 spin" /></div>
        )}
        <button className="flow-cta" onClick={goNext} data-testid="flow-cta-result">
          See Reward <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  };

  const renderReward = () => {
    const d = resultData;
    const mult = d?.consequence || 1.0;
    const isReduced = mult < 1.0;
    const isBoosted = mult > 1.0;
    return (
      <div className="flow-step-content" data-testid="flow-step-reward">
        <div className="flow-step-header">
          <Award className="flow-step-icon" />
          <h2>Consequence</h2>
        </div>
        {d ? (
          <>
            <div className="flow-reward-mult" data-testid="flow-reward-multiplier">
              <span className={`flow-reward-value ${isReduced ? 'reduced' : ''} ${isBoosted ? 'boosted' : ''}`}>
                {mult.toFixed(2)}x
              </span>
              <span className="flow-reward-label">visibility multiplier</span>
            </div>
            <p className="flow-reward-meaning" data-testid="flow-reward-meaning">
              {d.panel?.meaning || 'Your actions have normal visibility.'}
            </p>
            <p className="flow-reward-next" data-testid="flow-reward-next-step">
              {d.panel?.next_step || 'Keep posting to build trust.'}
            </p>
          </>
        ) : (
          <div className="flow-loading"><Loader2 className="w-5 h-5 spin" /></div>
        )}
        <button className="flow-cta flow-cta-finish" onClick={() => {
          setStep(0);
          setVisibility(null);
          setForm({ title: '', description: '', category: 'community' });
          setPostedAction(null);
          setReactionData(null);
          setResultData(null);
          // Refresh baseline
          fetch(`${API_URL}/api/position/${user.id}`).then(r => r.json()).then(d => {
            if (d.success) setBaseline(d);
          }).catch(() => {});
          fetch(`${API_URL}/api/orientation/${user.id}`).then(r => r.json()).then(d => {
            if (d.success) setOrientation(d);
          }).catch(() => {});
          if (onExit) onExit();
        }} data-testid="flow-cta-reward">
          <Check className="w-4 h-4" /> Done
        </button>
      </div>
    );
  };

  const RENDERERS = [renderNeed, renderChoice, renderAction, renderReaction, renderResult, renderReward];

  return (
    <div className="action-flow" data-testid="action-flow">
      <div className={`action-flow-page flow-animate-${direction}`} key={step}>
        {RENDERERS[step]()}
      </div>

      {/* Step indicator bar */}
      <nav className="flow-step-bar" data-testid="flow-step-bar">
        {FLOW_STEPS.map((s, i) => {
          const Icon = s.icon;
          const isActive = i === step;
          const isDone = i < step;
          return (
            <button
              key={s.key}
              className={`flow-step-btn ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
              onClick={() => { if (i <= step) setStep(i); }}
              disabled={i > step}
              data-testid={`flow-step-${s.key}`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{s.label}</span>
            </button>
          );
        })}
        <div
          className="flow-step-progress"
          style={{ width: `${((step) / (FLOW_STEPS.length - 1)) * 100}%` }}
          data-testid="flow-step-progress"
        />
      </nav>

      {/* Back button for non-first steps (except after action post) */}
      {step > 0 && step < 3 && (
        <button className="flow-back-btn" onClick={goBack} data-testid="flow-back-btn">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
      )}
    </div>
  );
}

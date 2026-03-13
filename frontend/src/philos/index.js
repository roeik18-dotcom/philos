// Browser-compatible Philos Engine wrapper
// Adapts the Python backend logic for frontend use

export class PhilosEngine {
  constructor() {
    this.history = [];
  }

  evaluate(eventZero, state, evaluation) {
    // Validate constraints
    const { pass, reasons } = this._validateConstraints(state, evaluation);

    // Compute decision state
    const decisionState = this._computeDecisionState(pass, reasons);

    // Compute action path
    const actionPath = this._computeActionPath(
      eventZero.gap_type,
      decisionState.result.status === 'allowed'
    );

    // Create history item
    const historyItem = {
      timestamp: new Date().toISOString(),
      current_state: eventZero.current_state,
      required_state: eventZero.required_state,
      gap_type: eventZero.gap_type,
      urgency: eventZero.urgency,
      scope: eventZero.scope,
      emotional_intensity: state.emotional_intensity,
      rational_clarity: state.rational_clarity,
      physical_capacity: state.physical_capacity,
      chaos_order: state.chaos_order,
      ego_collective: state.ego_collective,
      action_harm: evaluation.action_harm,
      personal_gain: evaluation.personal_gain,
      collective_gain: evaluation.collective_gain,
      decision_status: decisionState.result.status,
      reasons: reasons,
      recommended_action: decisionState.recommended_action,
      action_path_name: actionPath.visible ? actionPath.path_name : null
    };

    this.history.unshift(historyItem);

    return {
      event_zero: eventZero,
      state,
      evaluation,
      decision_state: decisionState,
      action_path: actionPath,
      history_item: historyItem
    };
  }

  _validateConstraints(state, evaluation) {
    const reasons = [];

    // Moral floor
    if (evaluation.action_harm > 0) {
      reasons.push('Moral floor: Harm too high');
    }

    // Energy floor
    if (state.physical_capacity < 20) {
      reasons.push('Energy collapse: capacity too low');
    }

    // Exploitation
    if (evaluation.personal_gain > evaluation.collective_gain * 2) {
      reasons.push('Exploitation: Personal gain too high relative to Collective');
    }

    return { pass: reasons.length === 0, reasons };
  }

  _computeDecisionState(pass, reasons) {
    const status = pass ? 'allowed' : 'blocked';
    let recommended_action;

    if (pass) {
      recommended_action = 'Allow continuing with measured action';
    } else {
      // Priority: harm > energy > exploitation
      if (reasons.some(r => r.includes('moral'))) {
        recommended_action = 'Stop and check action with less harm';
      } else if (reasons.some(r => r.includes('energy'))) {
        recommended_action = 'Reduce scope and return when there is more capacity';
      } else {
        recommended_action = 'Change the action so it benefits the collective more';
      }
    }

    return {
      constraints: { pass, reason: reasons },
      result: { status },
      recommended_action
    };
  }

  _computeActionPath(gapType, allowed) {
    if (!allowed) {
      return { visible: false, path_name: '', explanation: '', first_action: '' };
    }

    const paths = {
      energy: {
        path_name: 'Path Body',
        explanation: 'The gap requires restoring capacity through physical action',
        first_action: 'Perform a short physical action that restores capacity'
      },
      clarity: {
        path_name: 'Path Mind',
        explanation: 'The gap requires clarity and precise definition',
        first_action: 'Write the problem in one clear sentence'
      },
      order: {
        path_name: 'Order Path',
        explanation: 'The gap requires organizing an existing component in reality',
        first_action: 'Organize one small component in reality'
      },
      relation: {
        path_name: 'Connection Path',
        explanation: 'The gap requires direct contact with a relevant person',
        first_action: 'Reach out directly to one relevant person'
      },
      collective_value: {
        path_name: 'Contribution Path',
        explanation: 'The gap requires action that creates value for more than one person',
        first_action: 'Perform one action that benefits more than one person'
      }
    };

    return { visible: true, ...paths[gapType] };
  }

  getHistory() {
    return this.history;
  }

  clearHistory() {
    this.history = [];
  }
}

// Type placeholders for frontend
export const EventZero = null;
export const State = null;
export const ActionEvaluation = null;

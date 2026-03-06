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
      reasons.push('רצפה מוסרית: נזק גבוה מדי');
    }

    // Energy floor
    if (state.physical_capacity < 20) {
      reasons.push('קריסת אנרגיה: capacity נמוך מדי');
    }

    // Exploitation
    if (evaluation.personal_gain > evaluation.collective_gain * 2) {
      reasons.push('ניצול: רווח אישי גבוה מדי ביחס לקולקטיבי');
    }

    return { pass: reasons.length === 0, reasons };
  }

  _computeDecisionState(pass, reasons) {
    const status = pass ? 'allowed' : 'blocked';
    let recommended_action;

    if (pass) {
      recommended_action = 'אפשר להמשיך לפעולה מדודה';
    } else {
      // Priority: harm > energy > exploitation
      if (reasons.some(r => r.includes('מוסרית'))) {
        recommended_action = 'עצור ובדוק פעולה עם פחות נזק';
      } else if (reasons.some(r => r.includes('אנרגיה'))) {
        recommended_action = 'צמצם היקף וחזור כשיש יותר capacity';
      } else {
        recommended_action = 'שנה את הפעולה כך שתועיל יותר לקולקטיב';
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
        path_name: 'מסלול גוף',
        explanation: 'הפער דורש החזרת קיבולת דרך פעולה גופנית',
        first_action: 'בצע פעולה גופנית קצרה שמחזירה capacity'
      },
      clarity: {
        path_name: 'מסלול מחשבה',
        explanation: 'הפער דורש בהירות והגדרה מדויקת',
        first_action: 'כתוב את הבעיה במשפט אחד ברור'
      },
      order: {
        path_name: 'מסלול סדר',
        explanation: 'הפער דורש ארגון של מרכיב קיים במציאות',
        first_action: 'סדר מרכיב אחד קטן במציאות'
      },
      relation: {
        path_name: 'מסלול קשר',
        explanation: 'הפער דורש מגע ישיר עם גורם אנושי רלוונטי',
        first_action: 'צור קשר ישיר עם אדם אחד רלוונטי'
      },
      collective_value: {
        path_name: 'מסלול תרומה',
        explanation: 'הפער דורש פעולה שיוצרת ערך ליותר מאדם אחד',
        first_action: 'בצע פעולה אחת שמועילה ליותר מאדם אחד'
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

"""Main Philos Orientation engine - orchestrates the entire decision flow."""

from typing import Dict, Any
from .models import (
    EventZero,
    State,
    ActionEvaluation,
    DecisionState,
    ActionPath,
    HistoryItem
)
from .constraints import ConstraintsValidator
from .decision import DecisionEngine
from .history import DecisionHistory


class PhilosEngine:
    """Main orchestrator for Philos Orientation decision system.
    
    Flow:
    EventZero → State → Constraints → Decision → ActionPath → History
    """
    
    def __init__(self):
        self.history = DecisionHistory()
    
    def evaluate(
        self,
        event_zero: EventZero,
        state: State,
        evaluation: ActionEvaluation
    ) -> Dict[str, Any]:
        """Execute complete evaluation flow.
        
        Returns complete computed state including:
        - event_zero_summary
        - decision_state
        - action_path
        - history_item
        """
        
        # Step 1: Validate constraints
        constraints_pass, constraint_reasons = ConstraintsValidator.validate(
            state,
            evaluation
        )
        
        # Step 2: Compute decision state
        decision_state = DecisionEngine.compute_decision_state(
            constraints_pass,
            constraint_reasons
        )
        
        # Step 3: Compute action path
        action_path = DecisionEngine.compute_action_path(
            event_zero.gap_type,
            decision_state.result.status == "allowed"
        )
        
        # Step 4: Add to history
        history_item = self.history.add_decision(
            event_zero,
            state,
            evaluation,
            decision_state,
            action_path
        )
        
        # Return complete result
        return {
            'event_zero': {
                **event_zero.dict(),
                'event_zero_summary': event_zero.event_zero_summary
            },
            'state': state.dict(),
            'evaluation': evaluation.dict(),
            'decision_state': decision_state.dict(by_alias=True),
            'action_path': action_path.dict(),
            'history_item': history_item.dict()
        }
    
    def get_history(self) -> list:
        """Get all decision history (newest first)."""
        return [item.dict() for item in self.history.get_all()]
    
    def get_history_by_status(self, status: str) -> list:
        """Get filtered history by decision status."""
        return [item.dict() for item in self.history.get_by_status(status)]
    
    def get_history_by_gap_type(self, gap_type: str) -> list:
        """Get filtered history by gap type."""
        return [item.dict() for item in self.history.get_by_gap_type(gap_type)]
    
    def clear_history(self):
        """Clear all decision history."""
        self.history.clear()

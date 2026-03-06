"""Decision history storage and retrieval."""

from typing import List, Optional
from datetime import datetime
from .models import (
    HistoryItem,
    EventZero,
    State,
    ActionEvaluation,
    DecisionState,
    ActionPath
)


class DecisionHistory:
    """Manages decision history storage."""
    
    def __init__(self):
        self._history: List[HistoryItem] = []
    
    def add_decision(
        self,
        event_zero: EventZero,
        state: State,
        evaluation: ActionEvaluation,
        decision_state: DecisionState,
        action_path: ActionPath
    ) -> HistoryItem:
        """Add a new decision to history."""
        
        # Create history item
        item = HistoryItem(
            timestamp=datetime.utcnow(),
            
            # EventZero fields
            current_state=event_zero.current_state,
            required_state=event_zero.required_state,
            gap_type=event_zero.gap_type,
            urgency=event_zero.urgency,
            scope=event_zero.scope,
            
            # State fields
            emotional_intensity=state.emotional_intensity,
            rational_clarity=state.rational_clarity,
            physical_capacity=state.physical_capacity,
            chaos_order=state.chaos_order,
            ego_collective=state.ego_collective,
            
            # ActionEvaluation fields
            action_harm=evaluation.action_harm,
            personal_gain=evaluation.personal_gain,
            collective_gain=evaluation.collective_gain,
            
            # Decision fields
            decision_status=decision_state.result.status,
            reasons=decision_state.constraints.reason,
            recommended_action=decision_state.recommended_action,
            action_path_name=action_path.path_name if action_path.visible else None
        )
        
        # Insert at beginning (newest first)
        self._history.insert(0, item)
        
        return item
    
    def get_all(self) -> List[HistoryItem]:
        """Get all history items (newest first)."""
        return self._history.copy()
    
    def get_by_status(self, status: str) -> List[HistoryItem]:
        """Get history items filtered by status."""
        return [
            item for item in self._history
            if item.decision_status == status
        ]
    
    def get_by_gap_type(self, gap_type: str) -> List[HistoryItem]:
        """Get history items filtered by gap type."""
        return [
            item for item in self._history
            if item.gap_type == gap_type
        ]
    
    def clear(self):
        """Clear all history."""
        self._history.clear()
    
    def count(self) -> int:
        """Get total number of history items."""
        return len(self._history)

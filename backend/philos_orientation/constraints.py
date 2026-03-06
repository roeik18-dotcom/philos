"""Constraints validation logic."""

from typing import List, Tuple
from .models import State, ActionEvaluation


class ConstraintsValidator:
    """Validates action against system constraints."""
    
    # Constraint thresholds
    MORAL_FLOOR_THRESHOLD = 0
    ENERGY_FLOOR_THRESHOLD = 20
    EXPLOITATION_RATIO_MAX = 2.0
    
    # Hebrew constraint failure messages
    MESSAGES = {
        'moral_floor': 'רצפה מוסרית: נזק גבוה מדי',
        'energy_floor': 'קריסת אנרגיה: capacity נמוך מדי',
        'exploitation': 'ניצול: רווח אישי גבוה מדי ביחס לקולקטיבי'
    }
    
    @classmethod
    def validate(
        cls,
        state: State,
        evaluation: ActionEvaluation
    ) -> Tuple[bool, List[str]]:
        """Validate all constraints.
        
        Returns:
            (pass: bool, reasons: List[str])
        """
        failures = []
        
        # Check 1: Moral floor (harm must be <= 0)
        if not cls._check_moral_floor(evaluation):
            failures.append(cls.MESSAGES['moral_floor'])
        
        # Check 2: Energy floor (capacity must be >= 20)
        if not cls._check_energy_floor(state):
            failures.append(cls.MESSAGES['energy_floor'])
        
        # Check 3: Exploitation (personal gain <= collective gain * 2)
        if not cls._check_exploitation(evaluation):
            failures.append(cls.MESSAGES['exploitation'])
        
        passed = len(failures) == 0
        return passed, failures
    
    @classmethod
    def _check_moral_floor(cls, evaluation: ActionEvaluation) -> bool:
        """Check if action harm is within acceptable limits."""
        return evaluation.action_harm <= cls.MORAL_FLOOR_THRESHOLD
    
    @classmethod
    def _check_energy_floor(cls, state: State) -> bool:
        """Check if physical capacity is sufficient."""
        return state.physical_capacity >= cls.ENERGY_FLOOR_THRESHOLD
    
    @classmethod
    def _check_exploitation(cls, evaluation: ActionEvaluation) -> bool:
        """Check if personal gain is not exploitative."""
        max_allowed_personal_gain = evaluation.collective_gain * cls.EXPLOITATION_RATIO_MAX
        return evaluation.personal_gain <= max_allowed_personal_gain

"""Decision logic and recommendation engine."""

from typing import List
from .models import GapType, DecisionState, DecisionResult, ConstraintsResult, ActionPath


class DecisionEngine:
    """Core decision logic engine."""
    
    # Priority order for recommendations (highest to lowest)
    CONSTRAINT_PRIORITY = ['moral_floor', 'energy_floor', 'exploitation']
    
    RECOMMENDATIONS = {
        'moral_floor': 'Stop and look for an action with less harm',
        'energy_floor': 'Reduce scope and return when you have more capacity',
        'exploitation': 'Adjust the action to benefit the collective more',
        'allowed': 'You may proceed with a measured action'
    }
    
    # Action paths by gap type
    ACTION_PATHS = {
        'energy': {
            'path_name': 'Body path',
            'explanation': 'The gap requires restoring capacity through physical action',
            'first_action': 'Do a short physical action that restores capacity'
        },
        'clarity': {
            'path_name': 'Thought path',
            'explanation': 'The gap requires clarity and precise definition',
            'first_action': 'Write the problem in one clear sentence'
        },
        'order': {
            'path_name': 'Order path',
            'explanation': 'The gap requires organizing an existing element in reality',
            'first_action': 'Organize one small element in your reality'
        },
        'relation': {
            'path_name': 'Connection path',
            'explanation': 'The gap requires direct contact with a relevant person',
            'first_action': 'Reach out directly to one relevant person'
        },
        'collective_value': {
            'path_name': 'Contribution path',
            'explanation': 'The gap requires an action that creates value for more than one person',
            'first_action': 'Do one action that benefits more than one person'
        }
    }
    
    @classmethod
    def compute_decision_state(
        cls,
        constraints_pass: bool,
        constraint_reasons: List[str]
    ) -> DecisionState:
        """Compute complete decision state with recommendations."""
        
        # Determine status
        status: str = "allowed" if constraints_pass else "blocked"
        
        # Get recommended action
        recommended_action = cls._get_recommendation(
            constraints_pass,
            constraint_reasons
        )
        
        return DecisionState(
            constraints=ConstraintsResult(
                pass_=constraints_pass,
                reason=constraint_reasons
            ),
            result=DecisionResult(status=status),
            recommended_action=recommended_action
        )
    
    @classmethod
    def _get_recommendation(
        cls,
        constraints_pass: bool,
        constraint_reasons: List[str]
    ) -> str:
        """Get recommendation based on highest priority failed constraint."""
        
        if constraints_pass:
            return cls.RECOMMENDATIONS['allowed']
        
        # Map reasons to constraint types
        constraint_map = {
            'Moral floor: harm is too high': 'moral_floor',
            'Energy collapse: capacity is too low': 'energy_floor',
            'Exploitation: personal gain is too high relative to collective': 'exploitation'
        }
        
        # Find highest priority failed constraint
        failed_types = [constraint_map.get(reason) for reason in constraint_reasons]
        
        for priority_type in cls.CONSTRAINT_PRIORITY:
            if priority_type in failed_types:
                return cls.RECOMMENDATIONS[priority_type]
        
        # Fallback (should never reach here)
        return cls.RECOMMENDATIONS['allowed']
    
    @classmethod
    def compute_action_path(
        cls,
        gap_type: GapType,
        decision_allowed: bool
    ) -> ActionPath:
        """Compute action path based on gap type."""
        
        if not decision_allowed:
            return ActionPath(
                visible=False,
                path_name="",
                explanation="",
                first_action=""
            )
        
        path_data = cls.ACTION_PATHS[gap_type]
        
        return ActionPath(
            visible=True,
            path_name=path_data['path_name'],
            explanation=path_data['explanation'],
            first_action=path_data['first_action']
        )

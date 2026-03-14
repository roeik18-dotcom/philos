"""Decision logic and recommendation engine."""

from typing import List
from .models import GapType, DecisionState, DecisionResult, ConstraintsResult, ActionPath


class DecisionEngine:
    """Core decision logic engine."""
    
    # Priority order for recommendations (highest to lowest)
    CONSTRAINT_PRIORITY = ['moral_floor', 'energy_floor', 'exploitation']
    
    # Hebrew recommendations by constraint type
    RECOMMENDATIONS = {
        'moral_floor': 'עצור ובדוק פעולה עם פחות נזק',
        'energy_floor': 'צמצם היקף וחזור כשיש יותר capacity',
        'exploitation': 'שנה את הפעולה כך שתועיל יותר לקולקטיב',
        'allowed': 'אפשר להמשיך לפעולה מדודה'
    }
    
    # Action paths by gap type
    ACTION_PATHS = {
        'energy': {
            'path_name': 'מסלול גוף',
            'explanation': 'הפער דורש החזרת קיבולת דרך פעולה גופנית',
            'first_action': 'בצע פעולה גופנית קצרה שמחזירה capacity'
        },
        'clarity': {
            'path_name': 'מסלול מחשבה',
            'explanation': 'הפער דורש בהירות והגדרה מדויקת',
            'first_action': 'כתוב את הבעיה במשפט אחד ברור'
        },
        'order': {
            'path_name': 'מסלול סדר',
            'explanation': 'הפער דורש ארגון של מרכיב קיים במציאות',
            'first_action': 'סדר מרכיב אחד קטן במציאות'
        },
        'relation': {
            'path_name': 'מסלול קשר',
            'explanation': 'הפער דורש מגע ישיר עם גורם אנושי רלוונטי',
            'first_action': 'צור קשר ישיר עם אדם אחד רלוונטי'
        },
        'collective_value': {
            'path_name': 'מסלול תרומה',
            'explanation': 'הפער דורש פעולה שיוצרת ערך ליותר מאדם אחד',
            'first_action': 'בצע פעולה אחת שמועילה ליותר מאדם אחד'
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
            'רצפה מוסרית: נזק גבוה מדי': 'moral_floor',
            'קריסת אנרגיה: capacity נמוך מדי': 'energy_floor',
            'ניצול: רווח אישי גבוה מדי ביחס לקולקטיבי': 'exploitation'
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

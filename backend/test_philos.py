"""Test examples for Philos Orientation engine."""

import sys
sys.path.append('/app/backend')

from philos_orientation import PhilosEngine, EventZero, State, ActionEvaluation


def test_blocked_by_energy():
    """Test case: Blocked due to low physical capacity."""
    print("\n" + "="*60)
    print("TEST 1: Blocked by Energy Floor")
    print("="*60)
    
    engine = PhilosEngine()
    
    event_zero = EventZero(
        current_state="עייף ומבולבל",
        required_state="בהיר ופעיל",
        gap_type="energy",
        urgency=75,
        scope="self"
    )
    
    state = State(
        emotional_intensity=60,
        rational_clarity=40,
        physical_capacity=15,  # Below 20 threshold!
        chaos_order=-20,
        ego_collective=10
    )
    
    evaluation = ActionEvaluation(
        action_harm=0,
        personal_gain=30,
        collective_gain=20
    )
    
    result = engine.evaluate(event_zero, state, evaluation)
    
    print(f"\nEvent Zero Summary: {result['event_zero']['event_zero_summary']}")
    print(f"\nConstraints Pass: {result['decision_state']['constraints']['pass']}")
    print(f"Reasons: {result['decision_state']['constraints']['reason']}")
    print(f"Status: {result['decision_state']['result']['status']}")
    print(f"Recommended Action: {result['decision_state']['recommended_action']}")
    print(f"\nAction Path Visible: {result['action_path']['visible']}")


def test_blocked_by_harm():
    """Test case: Blocked due to high harm."""
    print("\n" + "="*60)
    print("TEST 2: Blocked by Moral Floor")
    print("="*60)
    
    engine = PhilosEngine()
    
    event_zero = EventZero(
        current_state="מבולגן",
        required_state="מאורגן",
        gap_type="order",
        urgency=50,
        scope="self"
    )
    
    state = State(
        emotional_intensity=40,
        rational_clarity=70,
        physical_capacity=60,
        chaos_order=-30,
        ego_collective=0
    )
    
    evaluation = ActionEvaluation(
        action_harm=50,  # Above 0 threshold!
        personal_gain=20,
        collective_gain=15
    )
    
    result = engine.evaluate(event_zero, state, evaluation)
    
    print(f"\nEvent Zero Summary: {result['event_zero']['event_zero_summary']}")
    print(f"\nConstraints Pass: {result['decision_state']['constraints']['pass']}")
    print(f"Reasons: {result['decision_state']['constraints']['reason']}")
    print(f"Status: {result['decision_state']['result']['status']}")
    print(f"Recommended Action: {result['decision_state']['recommended_action']}")


def test_blocked_by_exploitation():
    """Test case: Blocked due to exploitation ratio."""
    print("\n" + "="*60)
    print("TEST 3: Blocked by Exploitation")
    print("="*60)
    
    engine = PhilosEngine()
    
    event_zero = EventZero(
        current_state="לבד",
        required_state="מחובר",
        gap_type="relation",
        urgency=60,
        scope="one_person"
    )
    
    state = State(
        emotional_intensity=50,
        rational_clarity=60,
        physical_capacity=70,
        chaos_order=10,
        ego_collective=-40  # Ego-focused
    )
    
    evaluation = ActionEvaluation(
        action_harm=0,
        personal_gain=80,  # 80 > 20 * 2 = 40
        collective_gain=20
    )
    
    result = engine.evaluate(event_zero, state, evaluation)
    
    print(f"\nEvent Zero Summary: {result['event_zero']['event_zero_summary']}")
    print(f"\nConstraints Pass: {result['decision_state']['constraints']['pass']}")
    print(f"Reasons: {result['decision_state']['constraints']['reason']}")
    print(f"Status: {result['decision_state']['result']['status']}")
    print(f"Recommended Action: {result['decision_state']['recommended_action']}")


def test_allowed_with_path():
    """Test case: Allowed with action path."""
    print("\n" + "="*60)
    print("TEST 4: Allowed - Action Path Generated")
    print("="*60)
    
    engine = PhilosEngine()
    
    event_zero = EventZero(
        current_state="רוצה לעזור אבל לא יודע איך",
        required_state="תורם לקהילה",
        gap_type="collective_value",
        urgency=65,
        scope="community"
    )
    
    state = State(
        emotional_intensity=40,
        rational_clarity=80,
        physical_capacity=70,
        chaos_order=20,
        ego_collective=60  # Collective-focused
    )
    
    evaluation = ActionEvaluation(
        action_harm=0,
        personal_gain=30,
        collective_gain=80  # High collective gain
    )
    
    result = engine.evaluate(event_zero, state, evaluation)
    
    print(f"\nEvent Zero Summary: {result['event_zero']['event_zero_summary']}")
    print(f"\nConstraints Pass: {result['decision_state']['constraints']['pass']}")
    print(f"Status: {result['decision_state']['result']['status']}")
    print(f"Recommended Action: {result['decision_state']['recommended_action']}")
    print(f"\nAction Path Visible: {result['action_path']['visible']}")
    print(f"Path Name: {result['action_path']['path_name']}")
    print(f"Explanation: {result['action_path']['explanation']}")
    print(f"First Action: {result['action_path']['first_action']}")


def test_multiple_constraints_fail():
    """Test case: Multiple constraints fail - check priority."""
    print("\n" + "="*60)
    print("TEST 5: Multiple Constraints Fail (Priority Check)")
    print("="*60)
    
    engine = PhilosEngine()
    
    event_zero = EventZero(
        current_state="confused and tired",
        required_state="clear and energized",
        gap_type="clarity",
        urgency=80,
        scope="self"
    )
    
    state = State(
        emotional_intensity=70,
        rational_clarity=30,
        physical_capacity=10,  # FAIL: energy
        chaos_order=-50,
        ego_collective=-30
    )
    
    evaluation = ActionEvaluation(
        action_harm=20,  # FAIL: harm
        personal_gain=90,  # FAIL: exploitation (90 > 10 * 2)
        collective_gain=10
    )
    
    result = engine.evaluate(event_zero, state, evaluation)
    
    print(f"\nEvent Zero Summary: {result['event_zero']['event_zero_summary']}")
    print(f"\nConstraints Pass: {result['decision_state']['constraints']['pass']}")
    print(f"Failed Reasons: {result['decision_state']['constraints']['reason']}")
    print(f"Status: {result['decision_state']['result']['status']}")
    print(f"Recommended Action (based on highest priority): {result['decision_state']['recommended_action']}")
    print("\nNote: Should recommend harm fix first (highest priority)")


def test_history():
    """Test case: History tracking."""
    print("\n" + "="*60)
    print("TEST 6: History Tracking")
    print("="*60)
    
    engine = PhilosEngine()
    
    # Run 3 evaluations
    for i in range(3):
        event_zero = EventZero(
            current_state=f"state_{i}",
            required_state=f"target_{i}",
            gap_type=["energy", "clarity", "order"][i],
            urgency=50 + i * 10,
            scope="self"
        )
        
        state = State(
            emotional_intensity=50,
            rational_clarity=50,
            physical_capacity=30 + i * 10,
            chaos_order=0,
            ego_collective=0
        )
        
        evaluation = ActionEvaluation(
            action_harm=0,
            personal_gain=20,
            collective_gain=30
        )
        
        engine.evaluate(event_zero, state, evaluation)
    
    history = engine.get_history()
    
    print(f"\nTotal history items: {len(history)}")
    print("\nHistory (newest first):")
    for i, item in enumerate(history):
        print(f"\n  {i+1}. Gap: {item['gap_type']}, Status: {item['decision_status']}, "
              f"Path: {item['action_path_name'] or 'N/A'}")
    
    # Filter tests
    allowed = engine.get_history_by_status('allowed')
    print(f"\n\nAllowed decisions: {len(allowed)}")
    
    energy_gaps = engine.get_history_by_gap_type('energy')
    print(f"Energy gap decisions: {len(energy_gaps)}")


if __name__ == '__main__':
    test_blocked_by_energy()
    test_blocked_by_harm()
    test_blocked_by_exploitation()
    test_allowed_with_path()
    test_multiple_constraints_fail()
    test_history()
    
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60 + "\n")

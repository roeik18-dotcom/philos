"""
Philos AI Interpretation Layer.
Fallback version WITHOUT external LLM (no emergentintegrations).
Returns simple deterministic sentences so server won't crash.
"""

import logging

logger = logging.getLogger("philos_ai")


async def interpret_action(direction_he, base_he=None):
    """Return simple safe sentence."""
    try:
        base = f" from {base_he}" if base_he else ""
        return f"A movement toward {direction_he}{base} is taking place."
    except Exception as e:
        logger.error(f"interpret_action error: {e}")
        return ""


async def interpret_field(dominant_he, momentum_he, secondary_he=None, region_count=0):
    """Return simple safe sentence."""
    try:
        parts = [f"The field is moving toward {dominant_he}", f"with {momentum_he} momentum"]
        if secondary_he:
            parts.append(f"and a secondary pull toward {secondary_he}")
        if region_count > 3:
            parts.append("across multiple regions")
        return " ".join(parts) + "."
    except Exception as e:
        logger.error(f"interpret_field error: {e}")
        return ""


async def interpret_profile(alias, dominant_he, total_actions, streak, invited_count=0, trust_data=None):
    """Return simple safe sentence."""
    try:
        state = "stable"

        if trust_data:
            vs = trust_data.get("value_score", 0)
            rs = trust_data.get("risk_score", 0)

            if rs > vs:
                state = "restricted"
            elif vs < 5:
                state = "fragile"
            elif vs < 15:
                state = "building"
            else:
                state = "stable"

        return f"{alias} is in a {state} state with {total_actions} actions and direction toward {dominant_he}."
    except Exception as e:
        logger.error(f"interpret_profile error: {e}")
        return ""
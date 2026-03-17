"""
Philos AI Interpretation Layer.
Temporary fallback implementation with no external LLM dependency.
"""
import os
import logging

logger = logging.getLogger("philos_ai")

SYSTEM_PROMPT = """You are a quiet philosopher observing the human field.
You write only one sentence in English.
Your tone: calm, symbolic, observational.
Do not explain. Do not analyze. Do not advise.
Just observe and describe what you see.
One sentence only. Short. Quiet. Meaningful."""

PROFILE_SYSTEM_PROMPT = """You are a quiet observer describing a person's state in the field.
You write only one sentence in English.
Your tone: calm, clear, restrained.
Do not use grand metaphors. Do not sound mystical.
Do not shame. Do not exaggerate. Do not advise.
Prefer grounded description of the state over imagery.
The sentence should help the person understand their state in the field — not embellish it.
One sentence only. Short. Clear. Meaningful.
"""

_api_key = None

def _get_key():
    global _api_key
    if not _api_key:
        _api_key = os.environ.get("EMERGENT_LLM_KEY")
    return _api_key


async def interpret_action(direction_he, base_he=None):
    """Fallback action interpretation."""
    if base_he:
        return f"The movement leans toward {direction_he}, shaped by a base of {base_he}."
    return f"The movement leans toward {direction_he} in the field."


async def interpret_field(dominant_he, momentum_he, secondary_he=None, region_count=0):
    """Fallback field interpretation."""
    parts = [f"The field currently leans toward {dominant_he}"]
    if secondary_he:
        parts.append(f"while {secondary_he} remains present")
    if momentum_he:
        parts.append(f"with a sense of {momentum_he}")
    if region_count and region_count > 3:
        parts.append("across several active regions")
    sentence = " ".join(parts).strip()
    if not sentence.endswith("."):
        sentence += "."
    return sentence


async def interpret_profile(alias, dominant_he, total_actions, streak, invited_count=0, trust_data=None):
    """Fallback profile interpretation."""
    if trust_data:
        vs = trust_data.get("value_score", 0)
        rs = trust_data.get("risk_score", 0)
        if vs > rs:
            state_text = "value is ahead of risk"
        elif vs < rs:
            state_text = "risk is ahead of value"
        else:
            state_text = "value and risk are balanced"
        return f"{alias} is oriented toward {dominant_he}, and {state_text} in the field."
    if streak and streak > 1:
        return f"{alias} is oriented toward {dominant_he} with a steady streak of action."
    return f"{alias} is oriented toward {dominant_he} with {total_actions} actions in the field."

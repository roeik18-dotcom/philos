"""
Philos AI Interpretation Layer.
Generates short, calm, observational English sentences using Claude Sonnet 4.5.
One sentence only. No explanations. No chat. A quiet philosopher observing the field.
"""
import os
import uuid
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

Examples by state:
Stable — "The accumulated value is high relative to risk, and field presence is stable and consistent."
Building — "Value is starting to build, but there isn't enough history yet to establish full trust."
Fragile — "Accumulated value is low and risk is close to it, the field state is not yet solidified."
Restricted — "Risk exceeds value, and field presence is limited until the balance shifts."
"""

_api_key = None

def _get_key():
    global _api_key
    if not _api_key:
        _api_key = os.environ.get("EMERGENT_LLM_KEY")
    return _api_key


async def interpret_action(direction_he, base_he=None):
    """Interpret a user's action as value movement. Returns one English sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"action-{uuid.uuid4().hex[:8]}",
            system_message=SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        base_context = f" Daily base: {base_he}." if base_he else ""
        prompt = f"A user acted in the direction of: {direction_he}.{base_context} Write one short sentence describing this movement in the field."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_action error: {e}")
        return ""


async def interpret_field(dominant_he, momentum_he, secondary_he=None, region_count=0):
    """Interpret the current field state as tension between directions. Returns one English sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"field-{uuid.uuid4().hex[:8]}",
            system_message=SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        parts = [f"Dominant direction in the field: {dominant_he}.", f"Momentum: {momentum_he}."]
        if secondary_he:
            parts.append(f"Secondary direction: {secondary_he}.")
        if region_count > 3:
            parts.append(f"The field is active in several regions.")

        prompt = " ".join(parts) + " Write one short sentence describing the current state of the human field."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_field error: {e}")
        return ""


async def interpret_profile(alias, dominant_he, total_actions, streak, invited_count=0, trust_data=None):
    """Interpret a user's orientation pattern. Returns one grounded English sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"profile-{uuid.uuid4().hex[:8]}",
            system_message=PROFILE_SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        parts = [f"Name: {alias}.", f"Dominant direction: {dominant_he}.", f"Total actions: {total_actions}."]
        if streak > 1:
            parts.append(f"Activity streak: {streak} days.")
        if invited_count > 0:
            parts.append(f"Brought {invited_count} people to the field.")

        if trust_data:
            vs = trust_data.get("value_score", 0)
            rs = trust_data.get("risk_score", 0)
            ts = trust_data.get("trust_score", 0)
            state_map = {
                "stable": "Stable",
                "building": "Building",
                "fragile": "Fragile",
                "restricted": "Restricted"
            }
            if ts <= 0:
                state = "restricted"
            elif ts < 5:
                state = "fragile"
            elif ts < 15:
                state = "building"
            else:
                state = "stable"
            parts.append(f"Field value: {vs}. Field risk: {rs}. Field state: {state_map[state]}.")

        prompt = " ".join(parts) + " Describe in one short, clear sentence this person's state in the field, based on the ratio between value and risk and their action patterns."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_profile error: {e}")
        return ""

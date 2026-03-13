"""
Philos AI Interpretation Layer.
Generates short, calm, observational Hebrew sentences using Claude Sonnet 4.5.
One sentence only. No explanations. No chat. A quiet philosopher observing the field.
"""
import os
import uuid
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger("philos_ai")

SYSTEM_PROMPT = """אתה פילוסוף שקט שצופה בשדה האנושי.
אתה כותב משפט אחד בלבד בעברית.
הטון שלך: רגוע, סמלי, תצפיתי.
אל תסביר. אל תנתח. אל תייעץ.
רק תצפה ותתאר מה אתה רואה.
משפט אחד בלבד. קצר. שקט. משמעותי."""

_api_key = None

def _get_key():
    global _api_key
    if not _api_key:
        _api_key = os.environ.get("EMERGENT_LLM_KEY")
    return _api_key


async def interpret_action(direction_he, base_he=None):
    """Interpret a user's action as value movement. Returns one Hebrew sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"action-{uuid.uuid4().hex[:8]}",
            system_message=SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        base_context = f" הבסיס היומי: {base_he}." if base_he else ""
        prompt = f"משתמש פעל בכיוון: {direction_he}.{base_context} כתוב משפט אחד קצר שמתאר את התנועה הזו בשדה."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_action error: {e}")
        return ""


async def interpret_field(dominant_he, momentum_he, secondary_he=None, region_count=0):
    """Interpret the current field state as tension between directions. Returns one Hebrew sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"field-{uuid.uuid4().hex[:8]}",
            system_message=SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        parts = [f"הכיוון הדומיננטי בשדה: {dominant_he}.", f"המומנטום: {momentum_he}."]
        if secondary_he:
            parts.append(f"כיוון משני: {secondary_he}.")
        if region_count > 3:
            parts.append(f"השדה פעיל במספר אזורים.")

        prompt = " ".join(parts) + " כתוב משפט אחד קצר שמתאר את מצב השדה האנושי כרגע."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_field error: {e}")
        return ""


async def interpret_profile(alias, dominant_he, total_actions, streak, invited_count=0, trust_data=None):
    """Interpret a user's orientation pattern. Returns one Hebrew sentence."""
    key = _get_key()
    if not key:
        return ""
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"profile-{uuid.uuid4().hex[:8]}",
            system_message=SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        parts = [f"שם: {alias}.", f"כיוון דומיננטי: {dominant_he}.", f"מספר פעולות: {total_actions}."]
        if streak > 1:
            parts.append(f"רצף פעילות: {streak} ימים.")
        if invited_count > 0:
            parts.append(f"הביא {invited_count} אנשים לשדה.")

        if trust_data:
            vs = trust_data.get("value_score", 0)
            rs = trust_data.get("risk_score", 0)
            ts = trust_data.get("trust_score", 0)
            state_map = {
                "stable": "יציב",
                "building": "בבנייה",
                "fragile": "שביר",
                "restricted": "מוגבל"
            }
            if ts <= 0:
                state = "restricted"
            elif ts < 5:
                state = "fragile"
            elif ts < 15:
                state = "building"
            else:
                state = "stable"
            parts.append(f"ערך שדה: {vs}. סיכון שדה: {rs}. מצב שדה: {state_map[state]}.")

        prompt = " ".join(parts) + " כתוב משפט אחד קצר שמתאר את דפוס ההתמצאות של האדם הזה ואת מצבו בשדה."

        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip().split('\n')[0] if response else ""
    except Exception as e:
        logger.error(f"AI interpret_profile error: {e}")
        return ""

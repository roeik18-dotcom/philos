"""Position Status Calculator — movement-based status determination.

Status is derived from MOVEMENT, not time alone:
  movement = position_delta + trust_delta + recent_activity_signal

Rules (deterministic, first match wins):
  At Risk  (atRisk)  — enforcement active OR extended inactivity (14+ days, 0 actions)
  Rising   (rising)  — (position increased OR trust increased) AND recent activity
  Decaying (decaying) — no recent activity (7d) OR negative position/trust change
  Stable   (stable)  — default: still active, no significant change

Consequence multipliers (applied to feed ranking / visibility):
  Rising:   1.15x  — modest boost to public action visibility
  Stable:   1.00x  — neutral baseline
  Decaying: 0.85x  — modest reduction
  At Risk:  0.70x  — stronger reduction + warning state
  Enforcement override: if active risk signals exist, multiplier is capped at 0.70x
"""
from datetime import datetime, timezone, timedelta


# ── Thresholds ──
POSITION_DELTA_THRESHOLD = 0.02   # significant position change
TRUST_DELTA_THRESHOLD = 1.0       # significant trust change
RECENT_ACTIVITY_DAYS = 3          # "recently active" window
INACTIVITY_DAYS = 7               # decaying trigger
EXTENDED_INACTIVITY_DAYS = 14     # at-risk trigger

STATUS_META = {
    "rising":   {"icon": "up",      "label": "Rising",   "color": "#10b981"},
    "stable":   {"icon": "right",   "label": "Stable",   "color": "#f59e0b"},
    "decaying": {"icon": "down",    "label": "Decaying", "color": "#ef4444"},
    "atRisk":   {"icon": "warning", "label": "At Risk",  "color": "#dc2626"},
}

# ── Consequence multipliers ──
CONSEQUENCE_MULTIPLIERS = {
    "rising":   1.15,
    "stable":   1.00,
    "decaying": 0.85,
    "atRisk":   0.70,
}
ENFORCEMENT_CAP = 0.70  # max multiplier when enforcement is active


def calculate_status(
    *,
    current_position: float,
    current_trust: float,
    prev_position: float | None,
    prev_trust: float | None,
    recent_action_count: int,
    days_since_last_action: int,
    has_active_risk_signals: bool,
) -> dict:
    """Return {"status", "icon", "label", "color", "reason"}."""

    # ── Deltas (None means no previous snapshot → approximate) ──
    if prev_position is not None:
        pos_delta = current_position - prev_position
    else:
        # No prior snapshot — infer from current position itself
        pos_delta = current_position  # first snapshot treated as positive movement

    if prev_trust is not None:
        trust_delta = current_trust - prev_trust
    else:
        trust_delta = current_trust  # same logic

    pos_increased = pos_delta > POSITION_DELTA_THRESHOLD
    pos_decreased = pos_delta < -POSITION_DELTA_THRESHOLD
    trust_increased = trust_delta > TRUST_DELTA_THRESHOLD
    trust_decreased = trust_delta < -TRUST_DELTA_THRESHOLD

    recently_active = recent_action_count > 0  # any action in last 3 days
    inactive = days_since_last_action >= INACTIVITY_DAYS
    extended_inactive = days_since_last_action >= EXTENDED_INACTIVITY_DAYS

    # ── Rule 1: At Risk — enforcement OR extended inactivity with zero activity ──
    if has_active_risk_signals:
        return _result("atRisk", "Active risk signals detected")
    if extended_inactive and recent_action_count == 0:
        return _result("atRisk", f"No activity for {days_since_last_action} days")

    # ── Rule 2: Rising — positive movement AND recent activity ──
    if recently_active and (pos_increased or trust_increased):
        reasons = []
        if pos_increased:
            reasons.append("position +")
        if trust_increased:
            reasons.append("trust +")
        return _result("rising", ", ".join(reasons))

    # ── Rule 3: Decaying — inactive OR negative movement ──
    if inactive and recent_action_count == 0:
        return _result("decaying", f"Inactive {days_since_last_action} days")
    if pos_decreased or trust_decreased:
        reasons = []
        if pos_decreased:
            reasons.append("position -")
        if trust_decreased:
            reasons.append("trust -")
        return _result("decaying", ", ".join(reasons))

    # ── Rule 4: Stable — still active, no significant change ──
    return _result("stable", "Active, no significant change")


def _result(status: str, reason: str) -> dict:
    meta = STATUS_META[status]
    return {
        "status": status,
        "icon": meta["icon"],
        "label": meta["label"],
        "color": meta["color"],
        "reason": reason,
    }


def get_consequence_multiplier(status: str, has_active_risk_signals: bool = False) -> float:
    """Return the visibility/ranking multiplier for a given status.
    Enforcement override: if risk signals are active, cap at ENFORCEMENT_CAP."""
    base = CONSEQUENCE_MULTIPLIERS.get(status, 1.0)
    if has_active_risk_signals:
        return min(base, ENFORCEMENT_CAP)
    return base


def get_consequence_panel(
    status: str,
    multiplier: float,
    has_active_risk_signals: bool,
    days_since_last_action: int,
    recent_action_count: int,
) -> dict:
    """Return meaning + next_step for the Consequence Transparency Panel."""

    if status == "atRisk":
        if has_active_risk_signals:
            meaning = "Your public actions have significantly reduced visibility due to active risk signals."
            next_step = "Post authentic public actions to begin resolving risk signals."
        else:
            meaning = "Your public actions have significantly reduced visibility due to extended inactivity."
            next_step = "Post 1 public action to start recovering toward Decaying."
    elif status == "decaying":
        meaning = "Your public actions currently receive reduced visibility."
        if days_since_last_action >= INACTIVITY_DAYS:
            next_step = "Post 1 public action to recover toward Stable."
        else:
            next_step = "Continue posting to stabilize your position."
    elif status == "stable":
        meaning = "Your public actions have normal visibility."
        next_step = "Post 1 more public action to move toward Rising."
    elif status == "rising":
        meaning = "Your public actions are getting a visibility boost."
        next_step = "Keep it up — maintain activity to keep your boost."
    else:
        meaning = "Your public actions have normal visibility."
        next_step = "Post a public action to build trust."

    return {"meaning": meaning, "next_step": next_step}


def get_recovery_progress(
    status: str,
    reason: str,
    has_active_risk_signals: bool,
    days_since_last_action: int,
    recent_action_count: int,
    recent_public_count: int,
    unique_reactor_count: int,
) -> dict | None:
    """Return recovery progress for Decaying / At Risk users only.
    Returns None for Rising / Stable (no recovery needed).

    Recovery paths (one per status, first match):
      At Risk (risk signals) → Decaying: need 3 recent public actions
      At Risk (inactivity)   → Stable:   need 1 recent public action
      Decaying (inactivity)  → Stable:   need 1 recent public action
      Decaying (neg change)  → Stable:   need 2 recent public actions + 1 unique reactor
    """
    if status not in ("atRisk", "decaying"):
        return None

    if status == "atRisk":
        if has_active_risk_signals:
            target = 3
            current = min(recent_public_count, target)
            if current >= target:
                req_text = "Actions met — risk signals still active, keep posting authentic actions"
            else:
                remaining = target - current
                req_text = f"{remaining} more public action{'s' if remaining != 1 else ''} to begin recovery"
            return {
                "current_status": "At Risk",
                "target_status": "Decaying",
                "requirement": req_text,
                "progress": round(current / target, 2),
                "current": current,
                "target": target,
            }
        else:
            # Extended inactivity
            target = 1
            current = min(recent_public_count, target)
            return {
                "current_status": "At Risk",
                "target_status": "Stable",
                "requirement": f"{max(0, target - current)} public action{'s' if target - current != 1 else ''} to recover toward Stable",
                "progress": round(current / target, 2),
                "current": current,
                "target": target,
            }

    # Decaying
    if "Inactive" in reason or days_since_last_action >= INACTIVITY_DAYS:
        target = 1
        current = min(recent_public_count, target)
        return {
            "current_status": "Decaying",
            "target_status": "Stable",
            "requirement": f"{max(0, target - current)} public action{'s' if target - current != 1 else ''} to recover toward Stable",
            "progress": round(current / target, 2),
            "current": current,
            "target": target,
        }
    else:
        # Negative position/trust change
        target = 2
        current = min(recent_public_count, target)
        return {
            "current_status": "Decaying",
            "target_status": "Stable",
            "requirement": f"{max(0, target - current)} more public action{'s' if target - current != 1 else ''} to reverse the trend",
            "progress": round(current / target, 2),
            "current": current,
            "target": target,
        }



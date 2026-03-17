"""Position Status Calculator — movement-based status determination.

Status is derived from MOVEMENT, not time alone:
  movement = position_delta + trust_delta + recent_activity_signal

Rules (deterministic, first match wins):
  At Risk  (atRisk)  — enforcement active OR extended inactivity (14+ days, 0 actions)
  Rising   (rising)  — (position increased OR trust increased) AND recent activity
  Decaying (decaying) — no recent activity (7d) OR negative position/trust change
  Stable   (stable)  — default: still active, no significant change
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

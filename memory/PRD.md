# Philos Orientation - Product Requirements Document

## Original Problem Statement
Hebrew (RTL) philosophical orientation app with daily actions, collective "human field" globe, value profiles, AI Interpretation (Claude Sonnet 4.5), Value/Risk/Trust system, Trust Ledger, and Trust Explanation UI.

## Architecture
```
/app/backend/
  server.py, database.py, auth_utils.py, constants.py, philos_ai.py
  models/ (schemas.py, trust.py)
  routes/ (auth.py, philos.py, memory.py, collective.py, orientation.py, social.py, profile.py, admin.py, trust.py, system.py, analytics.py, invites.py)
  services/ (helpers.py, demo.py, trust.py, trust_integration.py, scheduler.py, analytics.py)
```

## Implemented Features
1-9. Core system (globe, orientation, invites, profiles, presence)
10. AI Interpretation Layer (Claude Sonnet 4.5) — calibrated
11. Backend Refactor (modular)
12. Value + Risk + Trust System + daily decay
13. Trust UI on Profile (value/risk bars + state label)
14. Trust-Aware + Calibrated AI Interpretation
15. Trust-to-Product Integration (daily actions, globe, missions, onboarding, invites)
16. Trust Ledger (immutable event log)
17. **Trust Explanation UI** — Completed 2026-03-13
    - TrustHistorySection component on Profile page
    - Hebrew source labels (פעולת כיוון יומית, נקודת שדה, דעיכה יומית, etc.)
    - Deterministic summary line (top source by count)
    - Value/risk deltas with color coding
    - Placed between field-trust-block and direction-bar

18. **Automated Decay Scheduler** — Completed 2026-03-13
    - APScheduler (CronTrigger 03:00 UTC daily)
    - MongoDB lock in `scheduler_locks` — prevents duplicate concurrent runs
    - Execution logging to `decay_log` collection
    - Clean startup/shutdown lifecycle in server.py
    - 23-hour minimum interval between runs
19. **System Health Endpoint** — Completed 2026-03-13
    - GET /api/system/status
    - Reports on: database, trust_engine, trust_ledger, ai_layer, decay_scheduler
    - Flat scheduler fields: scheduler_running, last_decay_run, last_decay_success, decay_runs_last_7_days, next_decay_run, lock_state
20. **MVP Freeze** — Completed 2026-03-13
    - POST /api/system/decay/trigger (admin-only, returns users_processed/total_value_decay/total_risk_decay)
    - Scheduler double-start protection (idempotent start_scheduler)
    - Manual trigger bypasses 23h interval, respects concurrency lock
    - Internal documentation: /app/backend/TRUST_ENGINE.md

21. **Real Usage Loop** — Completed 2026-03-13
    - Lightweight analytics: event logging for daily_actions, missions_joined, globe_points, trust_changes, return_sessions
    - GET /api/analytics/summary (per-day summary, last N days)
    - GET /api/analytics/events (raw event log)
    - Analytics hooks in: auth (session_start), orientation (daily_action, globe_point), social (mission_joined), admin (onboarding_complete), trust_integration (trust_change)
    - Retention nudges (RetentionNudges.js) appear after daily action: invite, join mission, globe point, return tomorrow
    - Error monitoring: system status includes recent_errors ring buffer + total_errors_logged
    - First-session flow: onboarding → first trust event → daily action → AI interpretation → profile trust view

22. **Invite System MVP** — Completed 2026-03-13
    - New `invite_codes` collection: code, owner_user_id, status (active/used/expired), created_at, used_at, used_by_user_id
    - 2 active codes per user (auto-generated on registration)
    - Endpoints: GET /api/invites/me, POST /api/invites/generate, POST /api/invites/redeem, POST /api/invites/share, GET /api/invites/lookup/{code}
    - Invite links: /join?invite=CODE and /invite/CODE both supported
    - Trust integration: redeem fires action_type=contribute, source_flow=invite_used (impact=8, authenticity=0.9)
    - Analytics: invite_generated, invite_viewed, invite_shared, invite_redeemed, invite_accepted
    - Frontend: InviteSection (codes + copy link), InvitePage (landing for invite links), AuthScreen (pre-fill invite code)
    - Legacy invites collection backward-compatible via lookup fallback

## Test Reports
- iteration_58-64: All prior features — 100%
- iteration_65: Trust Explanation UI — 100% (10/10 backend + all frontend elements)
- iteration_67: Decay Scheduler + System Status — 100% (17/17 backend tests)
- iteration_68: MVP Freeze Full Regression — 100% (35/35 backend tests)
- iteration_69: Real Usage Loop — 100% (14/14 backend + frontend rendering)
- iteration_70: Invite System MVP — 100% (14/14 backend + frontend rendering)

## Test Credentials
- newuser@test.com / password123 (stable trust)
- trust_building@test.com / password123 (building)
- trust_fragile@test.com / password123 (fragile)
- trust_restricted@test.com / password123 (restricted)

## Backlog
- Risk signal mapping from product behavior
- Trust visualization dashboard
- Further split routes/orientation.py
- Expand Trust-Aware AI to action/field interpretation layers

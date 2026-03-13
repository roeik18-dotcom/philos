# Philos Orientation - Product Requirements Document

## Original Problem Statement
A Hebrew (RTL) philosophical orientation application where users engage in daily actions, observe a collective "human field" via a 3D globe, and build personal value profiles. Features an AI Interpretation Layer (Claude Sonnet 4.5) and a Value + Risk + Trust scoring system with UI integration and trust-aware AI interpretations.

## Core Architecture (Refactored 2026-03-13)
```
/app/backend/
  server.py           # Slim orchestrator
  database.py         # Shared MongoDB connection
  auth_utils.py       # JWT, password hashing, get_current_user
  constants.py        # All domain constants
  philos_ai.py        # AI Interpretation Layer (Claude Sonnet 4.5) — trust-aware
  models/
    schemas.py        # All existing Pydantic models
    trust.py          # Action, RiskSignal, TrustProfile models
  routes/
    auth.py, philos.py, memory.py, collective.py, orientation.py, social.py
    profile.py        # Human Action Record + field_trust + trust-aware AI
    admin.py, trust.py
  services/
    helpers.py, demo.py, trust.py
```

## Implemented Features
1. World State & Globe UI
2. Opposition Engine
3. Daily Base Allocation System
4. Base-Influenced Daily Questions
5. Invite System + Reward System
6. Human Action Record (public profile)
7. Profile Discovery + Presence Indicator
8. AI Interpretation Layer (Claude Sonnet 4.5)
9. Backend Refactor (modular routes/models/services)
10. Value + Risk + Trust System (3 endpoints + daily decay)
11. Trust UI Integration on Profile (value/risk bars + state label)
12. **Trust-Aware AI Interpretation** — Completed 2026-03-13
    - interpret_profile now receives trust_data (value_score, risk_score, trust_score)
    - Prompt includes Hebrew trust context: ערך שדה, סיכון שדה, מצב שדה
    - Output remains: one Hebrew sentence, calm, symbolic, non-punitive
    - All other AI functions (interpret_action, interpret_field) unchanged

## Test Reports
- `/app/test_reports/iteration_58.json` — AI Interpretation Layer: 100%
- `/app/test_reports/iteration_59.json` — Refactor + Trust System: 100%
- `/app/test_reports/iteration_60.json` — Trust UI: 100%
- `/app/test_reports/iteration_61.json` — Trust-Aware AI: 100%

## Test Credentials
- newuser@test.com / password123 (stable trust, user_id: 05d47b99...)
- trust_building@test.com / password123 (building trust, user_id: 2f49d593...)
- trust_fragile@test.com / password123 (fragile trust, user_id: 0c98a493...)

## Backlog
- Trust visualization dashboard
- Further split routes/orientation.py (~3700 lines)
- Production-grade scheduler for daily decay

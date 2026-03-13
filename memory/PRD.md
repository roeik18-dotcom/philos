# Philos Orientation - Product Requirements Document

## Original Problem Statement
A Hebrew (RTL) philosophical orientation application where users engage in daily actions, observe a collective "human field" via a 3D globe, and build personal value profiles. Features an AI Interpretation Layer (Claude Sonnet 4.5) and a Value + Risk + Trust scoring system.

## Core Architecture (Refactored 2026-03-13)
```
/app/backend/
  server.py           # Slim orchestrator - FastAPI app, CORS, router includes, background tasks
  database.py         # Shared MongoDB connection
  auth_utils.py       # JWT, password hashing, get_current_user
  constants.py        # All domain constants
  philos_ai.py        # AI Interpretation Layer (Claude Sonnet 4.5)
  models/
    schemas.py        # All existing Pydantic models
    trust.py          # NEW: Action, RiskSignal, TrustProfile models
  routes/
    auth.py           # Auth + status routes
    philos.py         # Philos sync + session routes
    memory.py         # Memory + replay + insights + user data routes
    collective.py     # Collective layer + trends routes
    orientation.py    # Orientation system routes (field, daily, identity, globe, invites)
    social.py         # Value engine, subscription, social field, missions, circles
    profile.py        # Human Action Record (public profile)
    admin.py          # Admin analytics + feedback + onboarding
    trust.py          # NEW: Actions, Risk Signals, Trust Profile routes
  services/
    helpers.py        # Shared helper functions
    demo.py           # Demo agents system
    trust.py          # NEW: Value/Risk/Trust calculation + daily decay
```

## Tech Stack
- **Frontend:** React, react-router-dom, react-globe.gl, three.js, Shadcn UI. Hebrew RTL.
- **Backend:** FastAPI (modular), Pydantic, Motor (async MongoDB), passlib, python-jose.
- **Database:** MongoDB
- **AI:** Claude Sonnet 4.5 via emergentintegrations + Emergent LLM Key
- **Other:** html-to-image, Stripe, emergentintegrations

## Implemented Features
1. World State & Globe UI with symbolic narrative
2. Opposition Engine (personal tension mirror)
3. Daily Base Allocation System (Heart, Head, Body)
4. Base-Influenced Daily Questions
5. Invite System (PH-XXXX codes, limits, tracking)
6. Invite Reward System (value credits)
7. Human Action Record (public profile)
8. Profile Discovery (Highlighted Records)
9. Presence Indicator (24h pulse)
10. AI Interpretation Layer (Claude Sonnet 4.5) — Verified 2026-03-12
11. **Backend Refactor** — Completed 2026-03-13
    - Split monolithic server.py (7273 lines) into modular routes/models/services
12. **Value + Risk + Trust System** — Completed 2026-03-13
    - POST /api/actions (auth required) — record action, value = log(1+impact)*authenticity
    - POST /api/risk-signal — record risk signal, risk = confidence*severity
    - GET /api/user/{user_id}/trust — trust_score = value_score - risk_score
    - Daily decay: value *= 0.98, risk *= 0.95 (background job)

## New API Endpoints (Trust System)
- `POST /api/actions` — Record user action (requires auth). Body: {action_type, impact, authenticity}
- `POST /api/risk-signal` — Record risk signal. Body: {user_id, signal_type, confidence, severity}
- `GET /api/user/{user_id}/trust` — Get full trust profile with scores + recent history

## DB Collections (Trust System)
- `actions` — {id, user_id, action_type, impact, authenticity, value, timestamp}
- `risk_signals` — {id, user_id, signal_type, confidence, severity, risk, timestamp}
- `user_state` — {user_id, value_score, risk_score, trust_score, total_actions, total_risk_signals, last_updated}

## Test Reports
- `/app/test_reports/iteration_58.json` — AI Interpretation Layer: 100% pass
- `/app/test_reports/iteration_59.json` — Refactor + Trust System: 100% pass (28/28 backend, all frontend)

## Test Credentials
- Email: newuser@test.com / Password: password123
- User ID: 05d47b99-88f1-44b3-a879-6c995634eaa0

## Backlog
- Integrate trust scores into existing UI
- Connect trust to AI interpretation layer
- Trust visualization dashboard

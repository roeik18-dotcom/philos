# Philos Orientation - Product Requirements Document

## Original Problem Statement
A Hebrew (RTL) philosophical orientation application where users engage in daily actions, observe a collective "human field" via a 3D globe, and build personal value profiles. Features an AI Interpretation Layer (Claude Sonnet 4.5) and a Value + Risk + Trust scoring system with UI integration.

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
    trust.py          # Action, RiskSignal, TrustProfile models
  routes/
    auth.py           # Auth + status routes
    philos.py         # Philos sync + session routes
    memory.py         # Memory + replay + insights + user data routes
    collective.py     # Collective layer + trends routes
    orientation.py    # Orientation system routes (field, daily, identity, globe, invites)
    social.py         # Value engine, subscription, social field, missions, circles
    profile.py        # Human Action Record (public profile) + field_trust data
    admin.py          # Admin analytics + feedback + onboarding
    trust.py          # Actions, Risk Signals, Trust Profile routes
  services/
    helpers.py        # Shared helper functions
    demo.py           # Demo agents system
    trust.py          # Value/Risk/Trust calculation + daily decay
```

## Tech Stack
- **Frontend:** React, react-router-dom, react-globe.gl, three.js, Shadcn UI. Hebrew RTL.
- **Backend:** FastAPI (modular), Pydantic, Motor (async MongoDB), passlib, python-jose.
- **Database:** MongoDB
- **AI:** Claude Sonnet 4.5 via emergentintegrations + Emergent LLM Key

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
10. AI Interpretation Layer (Claude Sonnet 4.5)
11. Backend Refactor (monolithic → modular routes/models/services)
12. Value + Risk + Trust System (3 endpoints + daily decay)
13. **Trust UI Integration on Profile** — Completed 2026-03-13
    - FieldTrustBlock component: value bar, risk bar, trust state label
    - Trust states: יציב (Stable), בבנייה (Building), שביר (Fragile), מוגבל (Restricted)
    - Hebrew tooltip: "אמון שדה משקף את הערך שנצבר ביחס לדפוסי הסיכון לאורך זמן."
    - Integrated into `/api/profile/{user_id}/record` response as `field_trust`

## API Endpoints (Trust System)
- `POST /api/actions` — Record user action (requires auth). Body: {action_type, impact, authenticity}
- `POST /api/risk-signal` — Record risk signal. Body: {user_id, signal_type, confidence, severity}
- `GET /api/user/{user_id}/trust` — Get full trust profile
- `GET /api/profile/{user_id}/record` — Now includes `field_trust` object

## DB Collections (Trust System)
- `actions` — {id, user_id, action_type, impact, authenticity, value, timestamp}
- `risk_signals` — {id, user_id, signal_type, confidence, severity, risk, timestamp}
- `user_state` — {user_id, value_score, risk_score, trust_score, total_actions, total_risk_signals, last_updated}

## Test Reports
- `/app/test_reports/iteration_58.json` — AI Interpretation Layer: 100% pass
- `/app/test_reports/iteration_59.json` — Refactor + Trust System: 100% pass (28/28)
- `/app/test_reports/iteration_60.json` — Trust UI Integration: 100% pass (11/11 backend + all frontend)

## Test Credentials
- Email: newuser@test.com / Password: password123
- User ID: 05d47b99-88f1-44b3-a879-6c995634eaa0

## Next Phase
- Connect trust system to AI interpretation layer (user confirmed)

## Backlog
- Trust visualization dashboard
- Further split `routes/orientation.py` (~3700 lines)
- Production-grade scheduler for daily decay

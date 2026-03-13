# Philos Orientation - Product Requirements Document

## Original Problem Statement
A Hebrew (RTL) philosophical orientation application with daily actions, a collective "human field" globe, value profiles, AI Interpretation Layer (Claude Sonnet 4.5), and a Value + Risk + Trust scoring system.

## Architecture
```
/app/backend/
  server.py, database.py, auth_utils.py, constants.py
  philos_ai.py        # AI Layer: SYSTEM_PROMPT (action/field) + PROFILE_SYSTEM_PROMPT (calibrated, grounded)
  models/  routes/  services/
```

## Implemented Features
1-9. Core system (globe, orientation, invites, profiles, presence)
10. AI Interpretation Layer (Claude Sonnet 4.5)
11. Backend Refactor (modular routes/models/services)
12. Value + Risk + Trust System (POST /api/actions, POST /api/risk-signal, GET /api/user/{id}/trust)
13. Trust UI on Profile (value/risk bars + state label: יציב/בבנייה/שביר/מוגבל)
14. Trust-Aware AI Interpretation (trust data in profile prompt)
15. **AI Calibration Pass** — Completed 2026-03-13
    - New PROFILE_SYSTEM_PROMPT: grounded, anti-poetry rules, reference examples per state
    - Outputs now describe actual value/risk relationship, not abstract imagery
    - Non-punitive for all states including restricted

## Test Reports
- iteration_58: AI Layer 100%
- iteration_59: Refactor + Trust 100%
- iteration_60: Trust UI 100%
- iteration_61: Trust-Aware AI 100%
- iteration_62: AI Calibration 100% (22/22 backend, 4/4 frontend profiles)

## Test Credentials
- newuser@test.com / password123 (stable, trust ~15)
- trust_building@test.com / password123 (building, trust ~4)
- trust_fragile@test.com / password123 (fragile, trust ~0.1)
- trust_restricted@test.com / password123 (restricted, trust ~-2.8)

## Backlog
- Trust visualization dashboard
- Further split routes/orientation.py
- Production-grade scheduler for daily decay

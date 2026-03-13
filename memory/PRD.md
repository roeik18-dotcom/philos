# Philos Orientation - Product Requirements Document

## Original Problem Statement
Hebrew (RTL) philosophical orientation app with daily actions, collective "human field" globe, value profiles, AI Interpretation (Claude Sonnet 4.5), Value/Risk/Trust system, Trust Ledger, and Trust Explanation UI.

## Architecture
```
/app/backend/
  server.py, database.py, auth_utils.py, constants.py, philos_ai.py
  models/ (schemas.py, trust.py)
  routes/ (auth.py, philos.py, memory.py, collective.py, orientation.py, social.py, profile.py, admin.py, trust.py)
  services/ (helpers.py, demo.py, trust.py, trust_integration.py)
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

## Test Reports
- iteration_58-64: All prior features — 100%
- iteration_65: Trust Explanation UI — 100% (10/10 backend + all frontend elements)

## Test Credentials
- newuser@test.com / password123 (stable trust)
- trust_building@test.com / password123 (building)
- trust_fragile@test.com / password123 (fragile)
- trust_restricted@test.com / password123 (restricted)

## Backlog
- Risk signal mapping from product behavior
- Trust visualization dashboard
- Further split routes/orientation.py
- Production-grade scheduler for daily decay

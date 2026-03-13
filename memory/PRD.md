# Philos Orientation - Product Requirements Document

## Original Problem Statement
Hebrew (RTL) philosophical orientation app with daily actions, collective "human field" globe, value profiles, AI Interpretation (Claude Sonnet 4.5), and Value/Risk/Trust system connected to real product flows.

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
12. Value + Risk + Trust System (endpoints + daily decay)
13. Trust UI on Profile (value/risk bars + state label)
14. Trust-Aware AI Interpretation
15. AI Calibration Pass (grounded, non-poetic)
16. **Trust-to-Product Integration** — Completed 2026-03-13

## Trust Integration Mapping
| Product Flow | Trigger | action_type | impact | authenticity |
|---|---|---|---|---|
| Daily action (contribution) | daily-answer action_taken=true | contribute | 3+streak*0.5 (max 15) | 1.0 |
| Daily action (recovery) | daily-answer action_taken=true | help | 3+streak*0.5 (max 15) | 1.0 |
| Daily action (order) | daily-answer action_taken=true | create | 3+streak*0.5 (max 15) | 1.0 |
| Daily action (exploration) | daily-answer action_taken=true | explore | 3+streak*0.5 (max 15) | 1.0 |
| Globe point | globe-point sent | contribute | 3 | 0.8 |
| Mission join | missions/join | contribute | 5 | 0.9 |
| Onboarding first action | onboarding/first-action | direction-mapped | 2 | 0.7 |
| Invite used | register with invite_code | contribute (inviter) | 8 | 0.9 |

## Test Reports
- iteration_58-62: AI + Trust + UI + Calibration — all 100%
- iteration_63: Trust-Product Integration — 100% (16/16 backend + frontend)

## Test Credentials
- newuser@test.com / password123 (stable trust)
- trust_building@test.com / password123 (building)
- trust_fragile@test.com / password123 (fragile)
- trust_restricted@test.com / password123 (restricted)

## Backlog
- Risk signal mapping (no clear product signals yet)
- Trust visualization dashboard
- Further split routes/orientation.py
- Production-grade scheduler for daily decay

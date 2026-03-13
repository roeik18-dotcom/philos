# Philos Orientation - Product Requirements Document

## Original Problem Statement
Build a comprehensive "Value + Risk + Trust" system for the "Philos Orientation" application. The project has evolved through several phases of implementation and refinement. A major milestone was translating the entire application from Hebrew to English to prepare for a public launch to an English-speaking audience.

## Core System
- **V+R+T Engine**: Value, Risk, and Trust scoring system
- **Automated Daily Score Decay**: APScheduler-based background job
- **User Invite System**: Code-based invites with tracking and rewards
- **Lightweight Analytics**: Event tracking and funnel analysis
- **Trust Test Page**: Public `/trust-test` page for measuring trust
- **AI Interpretation Layer**: Claude Sonnet 4.5 powered profile insights

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Pydantic + MongoDB
- **AI**: Claude Sonnet 4.5 via `emergentintegrations`
- **Visualization**: react-globe.gl, three.js
- **Payments**: Stripe
- **Scheduling**: APScheduler

## What's Been Implemented

### Phase 1-4: Core System (Complete)
- Full V+R+T reputation engine
- User registration, login, and auth flow
- Orientation map with daily questions
- Decision path and identity system
- Collective field visualization
- Social features (circles, missions, compass)
- Globe interaction and visualization
- Weekly insights and drift detection
- Invite system with rewards

### Phase 5: Full English Translation (Complete - March 2026)
- **Frontend**: 90+ React component files translated from Hebrew to English
- **Backend Routes**: All 7 route files translated (auth, admin, collective, social, orientation, profile, memory)
- **Backend Services**: helpers.py, constants.py translated
- **Backend Models**: schemas.py comments updated
- **Backend Logic**: philos_orientation/decision.py and constraints.py translated
- **AI Prompts**: philos_ai.py updated to generate English responses
- **CSS/Layout**: Switched from RTL to LTR layout, updated fonts for English
- **Result**: Zero Hebrew characters in all production code

## Key Database Collections
- `users`, `user_state`, `trust_ledger`, `decay_log`
- `analytics_events`, `invite_codes`, `invites`
- `daily_questions`, `user_globe_points`, `feedback`

## Key API Endpoints
- `POST /api/auth/register`, `/api/auth/login`, `/api/auth/logout`
- `GET /api/orientation/field-today`, `/api/orientation/field`
- `GET /api/decision-path/{user_id}`, `/api/orientation/identity/{user_id}`
- `GET /api/orientation/daily-question/{user_id}`
- `POST /api/orientation/daily-answer/{user_id}`
- `GET /api/orientation/weekly-insight/{user_id}`
- `GET /api/orientation/compare/{user_id}`
- `POST /api/onboarding/first-action`
- `GET /api/system/status`

## Prioritized Backlog

### P1: Expand Trust-Aware AI
- Extend trust context to action and field interpretation layers

### P2: Define and Map Risk Signals
- Define risk signals based on user behavior patterns

### P2: ProfilePage Refactoring
- Break down `/app/frontend/src/pages/ProfilePage.js` (809 lines) into smaller components

### P3: Legacy Data Migration
- Optional: migrate existing Hebrew daily questions in database for legacy users

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`
- Email: `trust_fragile@test.com` | Password: `password123`

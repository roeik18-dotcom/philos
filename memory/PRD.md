# Philos Orientation - Product Requirements Document

## Original Problem Statement
Build a comprehensive "Value + Risk + Trust" system for the "Philos Orientation" application. The project has evolved through implementation of the V+R+T engine, full Hebrew-to-English translation, and now an investor-facing visual platform landing page.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Pydantic + MongoDB
- **AI**: Claude Sonnet 4.5 via `emergentintegrations`
- **Visualization**: react-globe.gl, three.js, CSS animations
- **Payments**: Stripe
- **Scheduling**: APScheduler

## Routing
- `/` — Platform landing page (investor-facing, primary entry)
- `/trust-test` — Public trust test flow
- `/dashboard` — Authenticated user dashboard
- `/admin` — Admin panel
- `/profile/{id}` — User profile
- `/invite/{code}` — Invite page

## What's Been Implemented

### Core System (Complete)
- Full V+R+T reputation engine
- User auth, orientation map, daily questions
- Decision path, identity, collective field
- Social features, globe, invite system

### Full English Translation (Complete)
- All frontend and backend translated from Hebrew to English
- LTR layout, English fonts

### Platform Landing Page (Complete - March 2026)
- Dark futuristic design with animated nodes
- 13-node system chain: Cosmos → Space → Matter → Energy → Motion → Life → Human → Forces → Conflict → Orientation → Decision → Action → Impact
- Globe-style layered visualization (Cosmos/Life/Human rings)
- Flow diagrams: Directional Forces, Fundamental Contradictions, Orientation Engine
- Investor sections: Problem → Model → System Engine → Application → Vision
- CTA buttons linking to /trust-test
- Scroll-reveal animations via IntersectionObserver
- Files: PlatformLandingPage.js, platform.css

## Prioritized Backlog
### P1: Expand Trust-Aware AI
### P2: Define and Map Risk Signals
### P2: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`

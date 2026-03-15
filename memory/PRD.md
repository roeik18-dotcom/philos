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

### SEO & Indexing (Complete - March 2026)
- sitemap.xml for all public pages (/, /trust-test)
- robots.txt allowing all crawlers
- Google Analytics GA4 (G-5MNK51HSQ1) active
- Google Search Console verification tag active
- Updated meta title, description, keywords
- Open Graph tags (og:title, og:description, og:type, og:url, og:site_name, og:locale)
- Twitter Card meta tags
- Canonical URL tag
- Files: sitemap.xml, robots.txt, index.html

### Product MVP Backend Scaffolding (Complete - March 2026)
- API endpoints: POST /api/actions/, GET /api/actions/feed, GET /api/actions/{id}, POST /api/actions/{id}/react
- Pydantic models in action_models.py
- Frontend placeholder files for 5 MVP pages under /app routes

## Prioritized Backlog
### P1: Build Product MVP (Feed → Post → Impact Map → Profile → Dashboard)
### P2: Implement Reactions & Trust Score
### P2: Opportunity System
### P2: Expand Trust-Aware AI
### P2: Define and Map Risk Signals
### P3: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`

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

### Product MVP (Complete - March 2026)
- 5 pages built under `/app` routes with shared layout and navigation
- `/app/feed` — Action Feed with category filters, action cards (title, description, category, location, contributor, community, timestamp)
- `/app/post` — Post Action form (auth required) with Title, Description, Category, Community, Location + geolocation detect
- `/app/map` — Impact Map using Leaflet + dark CartoCDN tiles, colored markers by category, popups with action details
- `/app/profile` — User profile with avatar, stats (Actions, Impact Score, Verified), contribution categories, communities
- `/app/dashboard` — Daily dashboard with summary stats, network activity, suggested actions
- Auth gating: Post/Profile/Dashboard require sign-in
- Full E2E flow verified: Post → Feed → Map
- Mobile responsive with bottom tab bar
- OG image (1200x630) for social sharing added
- Files: ProductApp.js, ActionFeed.js, PostAction.js, ImpactMap.js, ProductProfile.js, DailyDashboard.js, app.css

## Prioritized Backlog
### P1: Implement Reactions & Trust Score
### P2: Opportunity System
### P2: Expand Trust-Aware AI
### P2: Define and Map Risk Signals
### P3: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`

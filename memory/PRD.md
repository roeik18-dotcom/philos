# Philos Orientation - Mental Navigation System

## Product Overview
A client-side decision engine and dashboard that provides real-time decision analysis and mental navigation. Features Hebrew RTL interface with tabbed navigation (Home, Insights, System, Theory, History).

## Original Problem Statement
Build a sophisticated single-page tool for decision analysis, behavioral tracking, and self-orientation with cloud sync (MongoDB) and user authentication.

## Core Theoretical Model
The system is based on **four directions** and **two axes**:

### Four Directions
1. **Recovery (התאוששות)** - Returning to balance after stress or harm
2. **Order (סדר)** - Creating structure, organization, and clarity  
3. **Contribution (תרומה)** - Acting for the benefit of others
4. **Exploration (חקירה)** - Openness, flexibility, and forward movement

### Two Tension Axes
1. **Chaos ↔ Order** - Between spontaneity and structure
2. **Ego ↔ Collective** - Between self-focus and focus on others

### Balancing Paths (Theory-Driven)
- **harm → recovery** - Harmful actions require recovery balance
- **avoidance → order** - Avoidance is balanced by creating structure
- **isolation → contribution** - Self-focus is balanced by contributing to others
- **rigidity → exploration** - Stagnation is balanced by openness

---

## Implementation Status (March 2026)

### System Logic Coherence ✅
**Status:** Complete
- **Compass position** now calculated from **last 7 days** of actions (weighted average)
- **Recommendation engine** strictly follows theoretical balancing paths
- **Theory tab, Compass, and Recommendations** all use the **same unified model**

### Key Code Changes:
1. `recommendationService.js` - `calculateCompassPosition()` refactored to use 7-day weighted average
2. `recommendationService.js` - `calculateRecommendation()` simplified to strict theory balancing
3. `OrientationCompassSection.js` - Fixed undefined variable bug (`recommendedDirection` → `recommendedArrow`)
4. `NextBestDirectionSection.js` - Simplified to use only history for theory-based recommendations

### Test Results (March 10, 2026):
- **Frontend:** 100% pass rate (6/6 features verified)
- **Compass 7-day calculation:** ✅ PASS
- **Theory balancing paths:** ✅ PASS
- **Theory tab display:** ✅ PASS
- **Home recommendation labels:** ✅ PASS
- **Compass renders:** ✅ PASS
- **Tab navigation:** ✅ PASS

---

## Core Product Features (December 2025)

**Status:** Complete

### 1. Theory Tab (תיאוריה)
- Created `/app/frontend/src/components/philos/sections/TheorySection.js`
- **Four Directions:** התאוששות (Recovery), סדר (Order), תרומה (Contribution), חקירה (Exploration)
- **Two Tensions:** כאוס ↔ סדר (Chaos ↔ Order), אגו ↔ קולקטיב (Ego ↔ Collective)
- **Decision Logic:** 3-step process (Actions → Patterns → Orientation)
- **Balancing Paths:** Visual mapping of negative → positive transitions
- **Hebrew intro and examples included**

### 2. Orientation Compass
- Created `/app/frontend/src/components/philos/sections/OrientationCompassSection.js`
- **Quadrant grid map** with axes:
  - Vertical: סדר (Order) ↔ כאוס (Chaos)
  - Horizontal: אגו (Ego) ↔ קולקטיב (Collective)
- **Current position indicator** with pulse animation
- **Recommended direction arrow** (dashed line)
- **Trail of recent movements** (last 7 days)
- **Empty state** for new users

### 3. Direction History with Pattern Detection
- Created `/app/frontend/src/components/philos/sections/DirectionHistorySection.js`
- **Timeframe selector:** היום (Today) | 7 ימים (7 days) | הכל (All)
- **Pattern detection** with Hebrew insights:
  - "אתה נוטה לנוע לכיוון התאוששות"
  - "יש חזרתיות בהימנעות ולאחריה סדר"
  - "נראה מעבר מתמשך לכיוון חיובי"
- **Distribution chart** showing direction percentages
- **Movement timeline** showing recent transitions

### 4. Updated Tab Navigation
- **New tab order:** בית | תובנות | מערכת | תיאוריה | היסטוריה
- Theory tab is visible and accessible (not hidden in settings)
- Compass added to Home tab
- Direction History added to Theory tab

---

## Loading Skeletons Enhancement (December 2025)

**Status:** Complete

Added lightweight loading skeletons for async components to improve perceived performance:

### New Component
- `/app/frontend/src/components/philos/LoadingSkeletons.js`
- 8 reusable skeleton components:
  - `SectionSkeleton` - Full section placeholder
  - `CardSkeleton` - Card-like content placeholder
  - `StatsSkeleton` - Statistics display placeholder
  - `ChartSkeleton` - Chart/visualization placeholder
  - `ListSkeleton` - List items placeholder
  - `InlineLoader` - Inline text replacement
  - `CollectiveSkeleton` - Specific for collective sections
  - `ReplaySkeleton` - Specific for replay insights

### Integrated Sections
- `CollectiveMirrorSection` - Uses `CollectiveSkeleton`
- `CollectiveTrajectorySection` - Uses `CollectiveSkeleton`
- `GlobalFieldSection` - Uses `SectionSkeleton`
- `ReplayInsightsSummarySection` - Uses `ReplaySkeleton` (conditional)

### Technical Details
- Consistent `animate-pulse bg-gray-200` styling
- All skeletons include `dir="rtl"` for Hebrew layout
- Minimal placeholders, no UI redesign
- Conditional rendering to prevent skeleton flash for new users

---

## Backlog

### P1 - High Priority
- [ ] Complete system stabilization pass (loading states, error handling)
- [ ] Add consistent error handling for all API requests

### P2 - Medium Priority
- [ ] Further refactor dashboard tab panel content into separate components
- [ ] Add comprehensive unit tests for services

### P3 - Future Enhancements
- [ ] Enhance Decision Path Engine with LLM integration
- [ ] Add more sophisticated collective intelligence features
- [ ] Implement user feedback loop for recommendation improvement

---

## Credentials for Testing
- **Email:** `newuser@test.com`
- **Password:** `password123`
- **Anonymous:** App automatically creates persistent anonymous user ID

---

## Last Updated
December 10, 2025 - All 4 refactoring phases completed

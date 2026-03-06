# Philos Orientation - Product Requirements Document

## Original Problem Statement
Create a mindfulness/decision-making app that evolved into the **Philos Orientation** system - a comprehensive decision engine with a visual dashboard.

## Current State (December 2025)

### What's Implemented ✅

#### Core Decision Engine (`/app/frontend/src/philos/index.js`)
- Event Zero identification (current state → required state gap analysis)
- State/Forces tracking (emotional intensity, rational clarity, physical capacity, chaos/order, ego/collective)
- Action evaluation with constraint validation
- Decision computation (allowed/blocked)
- Action path recommendation based on gap type
- History tracking

#### Dashboard UI (`/app/frontend/src/pages/PhilosDashboard.js`)
- **Event Zero Form**: Input current state, required state, gap type, scope, urgency
- **State Display**: 5 sliders for forces (emotional, rational, physical, chaos-order, ego-collective)
- **Action Evaluation Form**: Harm, personal gain, collective gain sliders
- **Decision Display**: Status (ALLOWED/BLOCKED), constraint results, recommended action
- **Action Path Display**: Path name, explanation, first action (in Hebrew)
- **Decision Map**: 2D visualization with position dot (green=allowed, red=blocked), gap type label, crosshairs
- **History List**: Previous evaluations with timestamps, status, path

#### Technical Stack
- **Frontend**: React 18, Tailwind CSS, RTL Hebrew layout
- **Logic**: Client-side JavaScript (no backend dependency)
- **Previous backend**: FastAPI + MongoDB (vestigial, not in use)
- **Previous DB**: Supabase (for old community feature, not in active use)

### UI Language
- All user-facing text is in **Hebrew (עִבְרִית)**
- RTL layout enabled globally via `index.css`

## Completed Tasks (This Session)
1. ✅ Fixed blank page bug - initialized `state` with default values in PhilosDashboard
2. ✅ Verified DecisionMap component integration and rendering
3. ✅ Tested full evaluation flow (Event Zero → State → Evaluation → Decision → Action Path)
4. ✅ Confirmed History tracking works correctly
5. ✅ Verified green/red dot color based on decision status

## Architecture

```
/app/frontend/src/
├── philos/
│   └── index.js          # PhilosEngine class - core decision logic
├── pages/
│   └── PhilosDashboard.js # Main dashboard page
├── components/
│   └── philos/
│       ├── EventZeroForm.js
│       ├── StateDisplay.js
│       ├── ActionEvaluationForm.js
│       ├── DecisionDisplay.js
│       ├── ActionPathDisplay.js
│       ├── DecisionMap.js
│       └── HistoryList.js
└── App.js                # Renders PhilosDashboard
```

## Backlog / Future Tasks

### P1 - High Priority
- [ ] Persist history to localStorage or Supabase
- [ ] Add data-testid attributes for testing
- [ ] Translate remaining English labels to Hebrew

### P2 - Medium Priority  
- [ ] Mobile responsiveness improvements
- [ ] Slider value tooltips/labels
- [ ] Export history to CSV/JSON
- [ ] Dark mode support

### P3 - Low Priority / Cleanup
- [ ] Remove unused backend code (`/app/backend`)
- [ ] Remove old community help feature code
- [ ] Clean up Supabase configuration if not needed

## Known Issues
None currently - all components rendering correctly.

## Preview URL
https://orientation-map-1.preview.emergentagent.com

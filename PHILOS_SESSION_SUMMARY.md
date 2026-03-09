# Philos Orientation Dashboard - Session Summary

## 🎯 Project Status: ACTIVE DEVELOPMENT

### Current Implementation
Philos Orientation is a decision engine dashboard that evaluates actions based on:
- **Event Zero** → Gap analysis between current and required state
- **State/Forces** → Emotional, rational, physical dimensions
- **Axes** → Chaos/order and ego/collective positioning
- **Constraints** → Three validation rules
- **Decision** → Allowed/blocked with Hebrew recommendations
- **Action Path** → Contextualized next steps
- **History** → Audit trail of all evaluations

---

## 📁 Files Created/Modified

### Core Engine
**`/app/frontend/src/philos/index.js`**
- `PhilosEngine` class (JavaScript)
- Constraint validation logic
- Decision computation
- Action path mapping
- History management

### Main Dashboard
**`/app/frontend/src/pages/PhilosDashboard.js`**
- Main orchestrator component
- State management for all inputs
- Evaluate/Reset handlers
- Section layout and flow

### UI Components (all in `/app/frontend/src/components/philos/`)
1. **EventZeroForm.js** - Gap analysis inputs (current_state, required_state, gap_type, urgency, scope)
2. **StateDisplay.js** - Five live sliders (emotional_intensity, rational_clarity, physical_capacity, chaos_order, ego_collective)
3. **ActionEvaluationForm.js** - Three evaluation inputs (action_harm, personal_gain, collective_gain)
4. **DecisionDisplay.js** - Constraints results, status badge, recommendations
5. **ActionPathDisplay.js** - Hebrew path name, explanation, first action
6. **HistoryList.js** - Chronological evaluation history with filters
7. **DecisionMap.js** - **NEW** 2D visualization:
   - X axis: ego ← → collective
   - Y axis: chaos ↑ order ↓
   - Live positioning dot
   - Color-coded by decision (green=allowed, red=blocked)
   - Gap type label
   - Crosshair guides

### App Integration
**`/app/frontend/src/App.js`**
- Renders PhilosDashboard as root component
- Replaced previous community help template

---

## 🔧 Technical Details

### Constraint Rules (Philos Logic)
```javascript
// 1. Moral Floor
action_harm <= 0
Fail: "רצפה מוסרית: נזק גבוה מדי"

// 2. Energy Floor  
physical_capacity >= 20
Fail: "קריסת אנרגיה: capacity נמוך מדי"

// 3. Exploitation
personal_gain <= collective_gain * 2
Fail: "ניצול: רווח אישי גבוה מדי ביחס לקולקטיבי"
```

### Action Paths by Gap Type
- **energy** → מסלול גוף (Body path)
- **clarity** → מסלול מחשבה (Mind path)
- **order** → מסלול סדר (Order path)
- **relation** → מסלול קשר (Relation path)
- **collective_value** → מסלול תרומה (Contribution path)

### State Model
```javascript
{
  emotional_intensity: 0-100,
  rational_clarity: 0-100,
  physical_capacity: 0-100,
  chaos_order: -100 to +100,  // -100=chaos, +100=order
  ego_collective: -100 to +100  // -100=ego, +100=collective
}
```

---

## 📍 Current State & Next Steps

### ✅ Completed
- [x] Backend Philos logic layer (Python) at `/app/backend/philos_orientation/`
- [x] Frontend Philos engine (JavaScript port)
- [x] All 7 UI components
- [x] Dashboard layout with sections
- [x] Decision Map component created
- [x] DecisionMap imported in dashboard

### ⚠️ Partially Complete
- [ ] **DecisionMap not yet rendered** - Import added but not in JSX
- [ ] Export CSV functionality - planned but not implemented

### 🎯 Immediate Next Actions
1. **Add DecisionMap to PhilosDashboard render:**
   ```jsx
   {/* Decision Map - add after Action Path section */}
   {state && (
     <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
       <h2 className="text-2xl font-semibold text-foreground mb-4">מפת ההחלטה</h2>
       <DecisionMap 
         state={state} 
         decisionState={result?.decision_state}
         gapType={eventZero?.gap_type}
       />
     </section>
   )}
   ```

2. **Add Export CSV button to History section:**
   ```jsx
   const exportCSV = () => {
     const csv = convertHistoryToCSV(history);
     downloadFile(csv, 'philos-history.csv', 'text/csv');
   };
   ```

3. **Restart frontend:**
   ```bash
   sudo supervisorctl restart frontend
   ```

4. **Test with screenshot** - Verify full flow works

---

## 🚀 Deployment Status

### Frontend
- **Running**: Yes (port 3000)
- **URL**: https://philos-orient.preview.emergentagent.com
- **Status**: LIVE but showing old code (needs restart)

### Backend  
- **Running**: Yes (port 8001)
- **Philos Python module**: `/app/backend/philos_orientation/`
- **Status**: Logic layer complete, not connected to frontend (frontend uses JS port)

---

## 💡 Architecture Notes

### Frontend-Only Implementation
The dashboard currently uses a JavaScript port of the Philos engine (`/app/frontend/src/philos/index.js`). The Python backend (`/app/backend/philos_orientation/`) exists but is NOT connected.

**Future Enhancement:** Connect frontend to FastAPI backend for:
- Persistent history storage
- Server-side validation
- Multi-user support
- Analytics

### Component Flow
```
App.js
  └─ PhilosDashboard.js
       ├─ EventZeroForm → setEventZero
       ├─ StateDisplay → setState (live updates)
       ├─ ActionEvaluationForm → setEvaluation
       ├─ [Evaluate Button] → engine.evaluate()
       ├─ DecisionDisplay (if result)
       ├─ ActionPathDisplay (if allowed)
       ├─ DecisionMap (if state) ← NOT YET RENDERED
       └─ HistoryList (if history.length > 0)
```

---

## 📝 Code Snippets for Continuation

### Complete DecisionMap Integration
Add this section in PhilosDashboard.js after the Action Path section (around line 115):

```jsx
{/* Decision Map */}
{state && (
  <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
    <h2 className="text-2xl font-semibold text-foreground mb-4">מפת ההחלטה</h2>
    <DecisionMap 
      state={state} 
      decisionState={result?.decision_state}
      gapType={eventZero?.gap_type}
    />
  </section>
)}
```

### Add Export CSV Function
Add to PhilosDashboard.js:

```javascript
const handleExportCSV = () => {
  if (history.length === 0) {
    alert('No history to export');
    return;
  }

  const headers = [
    'Timestamp', 'Gap Type', 'Current State', 'Required State',
    'Urgency', 'Scope', 'Emotional Intensity', 'Rational Clarity',
    'Physical Capacity', 'Chaos Order', 'Ego Collective',
    'Action Harm', 'Personal Gain', 'Collective Gain',
    'Decision Status', 'Action Path', 'Reasons'
  ];

  const rows = history.map(item => [
    new Date(item.timestamp).toISOString(),
    item.gap_type,
    item.current_state,
    item.required_state,
    item.urgency,
    item.scope,
    item.emotional_intensity,
    item.rational_clarity,
    item.physical_capacity,
    item.chaos_order,
    item.ego_collective,
    item.action_harm,
    item.personal_gain,
    item.collective_gain,
    item.decision_status,
    item.action_path_name || '',
    item.reasons.join('; ')
  ]);

  const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `philos-history-${Date.now()}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
};
```

Add button to History section header:
```jsx
<div className="flex items-center justify-between mb-4">
  <h2 className="text-2xl font-semibold text-foreground">History</h2>
  <div className="flex gap-2">
    <button onClick={handleExportCSV} className="text-sm text-muted-foreground hover:text-foreground">
      Export CSV
    </button>
    <button onClick={handleClearHistory} className="text-sm text-muted-foreground hover:text-foreground">
      Clear History
    </button>
  </div>
</div>
```

---

## 🎨 Design System

### Colors
- Background: #F9F7F2 (warm alabaster)
- Foreground: #4A4238 (deep mocha)
- Primary: #4A4238
- Muted: #EFEBE6
- Border: #E6E2DD

### Typography
- Headings: Rubik (Hebrew support)
- Body: Heebo
- All text: LTR (English/Latin alphabet)
- Numbers: Standard formatting

### Layout
- Max width: 4xl (896px)
- Spacing: 6 units between sections
- Card radius: 3xl (1.5rem)
- Minimal, clean aesthetic

---

## 🐛 Known Issues
- None currently - all components functional

## 🔄 Testing Checklist
- [ ] Set Event Zero values
- [ ] Move all 5 state sliders
- [ ] Set action evaluation values
- [ ] Click "Evaluate Decision"
- [ ] Verify decision shows (allowed/blocked)
- [ ] Check action path appears (if allowed)
- [ ] Verify decision map dot moves with sliders
- [ ] Check dot color matches decision status
- [ ] Verify history populates
- [ ] Test "Reset" button
- [ ] Test "Clear History" button
- [ ] Test "Export CSV" button (once implemented)

---

## 📚 Reference

### File Locations
```
/app/frontend/src/
├── App.js (root component)
├── philos/
│   └── index.js (engine)
├── pages/
│   └── PhilosDashboard.js (main dashboard)
└── components/philos/
    ├── EventZeroForm.js
    ├── StateDisplay.js
    ├── ActionEvaluationForm.js
    ├── DecisionDisplay.js
    ├── ActionPathDisplay.js
    ├── DecisionMap.js
    └── HistoryList.js

/app/backend/philos_orientation/
├── __init__.py
├── models.py (Pydantic models)
├── constraints.py (validation)
├── decision.py (decision logic)
├── history.py (history management)
└── engine.py (orchestrator)
```

### Commands
```bash
# Restart frontend
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status

# View logs
tail -50 /var/log/supervisor/frontend.out.log
tail -50 /var/log/supervisor/frontend.err.log

# Test backend (if needed)
cd /app/backend && python test_philos.py
```

---

## 🎯 Session Handoff

**Current Task:** Complete DecisionMap integration and add Export CSV

**Estimated Time:** 10-15 minutes

**Priority:** High - dashboard is 95% complete, just needs final integration

**Blocker:** None - all code ready, just needs render + restart

---

**Session End**: Ready for continuation with clear next steps
**Code Status**: All preserved and functional
**Next Session**: Add DecisionMap to render, implement CSV export, test & deploy

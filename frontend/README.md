# Frontend — Intake + Comparison Display (Person 1)

React + Vite. Built mock-first so it never blocks on the backend.

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Opens on `http://localhost:5173` by default.

## Mock mode

`VITE_FORCE_MOCK=true` in `.env` always uses `src/mockResponse.js` instead of
calling the real API — useful for demo recording if OpenAI billing/quota is
down.

Even with `VITE_FORCE_MOCK=false`, if the backend at `VITE_API_BASE` is
unreachable, `src/api.js` automatically falls back to mock data and shows a
banner on the comparison screen.

## Structure

```
src/
├── App.jsx                     # top-level state: intake → comparison
├── api.js                      # calls POST /api/reason, mock fallback
├── mockResponse.js             # mirrors backend/mock.py exactly
├── components/
│   ├── IntakeForm.jsx              # plain-language situation input
│   ├── ContextCards.jsx            # dynamic cards from extracted context
│   ├── ComparisonScreen.jsx        # top-level output layout
│   ├── PathColumn.jsx              # one path: timeline + tradeoffs + verify
│   ├── ConfidenceThread.jsx        # signature element — line texture = confidence
│   ├── UncertaintyPanel.jsx        # Person 2 — claims + uncertainty flags
│   ├── WhatIfExplorer.jsx          # Person 2 — assumption challenge + rerun
│   ├── LoadingIndicator.jsx        # rotating messages during long API calls
│   └── DataSourceBanner.jsx        # shows when mock fallback is active
```

## Design notes

- **Confidence thread**: a vertical line beside each timeline entry. Solid =
  high confidence, dashed = medium, sparse-dotted = low. Wired in `PathColumn`.
- Cards and columns render from **whatever the backend extracts** — nothing is
  hardcoded to the Filipino nurse scenario.
- Person 2's Uncertainty Panel and What-If Explorer render inside
  `<ComparisonScreen>{...}</ComparisonScreen>`.

## Known gaps / next steps

- [x] Optional structured intake follow-up (paths, constraints, values) feeding
      `structured_context` — collapsible section on the intake form.
- [x] Streaming progress via `POST /api/reason/stream` — phase updates + early
      extraction preview while the full analysis runs.

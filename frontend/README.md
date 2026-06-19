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
down, or while Person 3's reasoning engine is still being tuned.

Even with `VITE_FORCE_MOCK=false`, if the backend at `VITE_API_BASE` is
unreachable, `src/api.js` automatically falls back to mock data and logs a
warning to the console. The intake form should never feel broken to a user
during demo day.

## Structure

```
src/
├── App.jsx                 # top-level state: intake → comparison
├── api.js                  # calls POST /api/reason, mock fallback
├── mockResponse.js         # mirrors backend/mock.py exactly
├── components/
│   ├── IntakeForm.jsx          # plain-language situation input
│   ├── ContextCards.jsx        # dynamic cards from extracted context
│   ├── ComparisonScreen.jsx    # top-level output layout
│   ├── PathColumn.jsx          # one path: timeline + tradeoffs + verify
│   └── ConfidenceThread.jsx    # signature element — line texture = confidence
```

## Design notes

- **Confidence thread**: a vertical line beside each timeline entry. Solid =
  high confidence, dashed = medium, sparse-dotted = low. This is how
  "honest uncertainty" shows up visually instead of just a text label —
  judges should see it, not just read about it.
- Cards and columns are written to render from **whatever the backend
  extracts** — nothing is hardcoded to the Filipino nurse scenario. Test
  with a different `user_description` (e.g. grad school vs startup) to
  confirm the UI still makes sense.
- Connecting Person 2's What-If Explorer: render it inside
  `<ComparisonScreen>{...}</ComparisonScreen>` — there's already a children
  slot placed after the path columns.

## Known gaps / next steps

- [ ] Loading state during `/api/reason` call is a static label — could add
      a subtle animation once Person 2's uncertainty UI direction is locked.
- [ ] `extractConstraints` / `extractTimelinePressure` in `ContextCards.jsx`
      use simple heuristics over the response — fine for now, revisit if
      Person 4 adds dedicated extraction fields to `structured_context`.
- [ ] No structured_context is sent from intake yet — currently relying on
      the backend's own extraction phase from `user_description` alone.

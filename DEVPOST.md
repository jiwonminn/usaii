# Devpost draft — Life Decision Simulator

Copy sections below into Devpost. Person 4 owns final submission; Person 3 reviewed AI Architecture + AI Reasoning.

---

## Inspiration (short)

Major life decisions — immigration, career pivots, relocation, education vs work — are rarely a simple pros/cons list. People face real constraints (savings runway, dependents, deadlines) and hidden tradeoffs they have not named yet. We built a tool that structures that thinking and models paths over time with honest uncertainty, without telling anyone what to choose.

---

## What it does

Users describe any decision in plain language. The system:

1. Extracts the core decision, binding constraint, and paths being compared
2. Models each path at **3 months, 1 year, and 3 years** with financial, career, and personal impact
3. Surfaces non-obvious tradeoffs, hidden considerations, and what each path closes off
4. Shows confidence per claim and flags what the AI cannot know
5. Lets users challenge assumptions via **what-if** input and reruns reasoning dynamically

Demo scenario: a Filipino RN in Toronto with 3 months savings deciding between PSW work now vs CNO credential recognition. The same engine handles grad school vs startup, relocation, and law school vs bank offer — no code changes per scenario.

---

## How we built it (AI Architecture)

**Stack:** React + Vite frontend, FastAPI backend, OpenAI chat API (`gpt-4o-mini` default), Pydantic schemas.

**End-to-end flow:**

```
Plain-language intake
        ↓
Phase 1 — Extract (LLM call #1)
  → binding constraint, paths, personal constraints, risk signals
        ↓
Phase 2 — Model (LLM call #2)
  → tradeoffs, timed outcomes, verification checklist, claims + confidence
        ↓
Phase 3 — Validate (no LLM)
  → reject generic pros/cons; auto-retry Phase 2 if quality fails
        ↓
Structured comparison UI + optional what-if rerun
```

**API contract:** `POST /api/reason` accepts `user_description`, optional `structured_context`, and optional `what_if_assumption`. Returns `ReasoningResponse` JSON including `extraction` for context cards and `paths[]` for side-by-side comparison.

**Why two LLM calls, not one:** Extraction grounds Phase 2 in the user's actual constraints before tradeoff modeling. A single-shot prompt tended to produce generic advice; splitting extract → model improved path alignment and reduced template drift across domains.

**Quality gate:** `backend/validators.py` programmatically checks for generic phrasing ("income vs career satisfaction"), missing URLs in verification items, overconfident long-horizon claims, and path count mismatches. Failed checks trigger up to 3 auto-retries with targeted fix instructions.

---

## AI Reasoning — why an LLM, not a rules engine (30% rubric)

A keyword filter or curated directory can map "nurse + Toronto" to immigration resources. That fails this problem because:

| What judges care about | Rules / keyword filter | Our LLM chain |
|------------------------|------------------------|---------------|
| Parse messy natural language | Fragile | Extracts structure from free text in any domain |
| Find the **binding constraint** | Manual rules per domain | Identifies what actually limits options now (e.g. "3 months savings + 2 dependents") |
| Surface **non-obvious tradeoffs** | Cannot — only matches categories | Second-order effects (shift work vs study time, career inertia, hybrid feasibility) |
| Model outcomes over time | Static lookup tables | Projects 3mo / 1yr / 3yr per path as one causal story with ranges |
| Infer hybrid paths | Must be pre-defined | Adds realistic third options when user text supports it (e.g. part-time PSW + CNO prep) |
| What-if branching | Not possible | Re-runs Phase 2 when user challenges an assumption |
| Honest uncertainty | Binary yes/no | Per-claim confidence + `unknown_factors` + global flags |

**What the model classifies from (inputs):**

- `user_description` — primary signal; any decision domain
- `structured_context` — optional paths, constraints, timeline, stakes, values from intake follow-up
- `what_if_assumption` — free-text assumption to stress-test (e.g. "CNO completes in 4 months instead of 12")

**What the model produces (outputs):**

- `decision_summary` anchored to binding constraint
- `paths[]` with `outcomes` at three horizons, `tradeoffs`, `hidden_considerations`, `what_you_give_up`
- `verify_before_deciding` with official source URLs (CNO, government sites, employers)
- `claims[]` with mixed confidence levels and `anchored_to` sources
- `global_uncertainty_flags` — explicit limits of AI knowledge
- `extraction` — Phase 1 structured context for UI cards

**Proof of generality:** Four test scenarios (nurse, grad school vs startup, Toronto→Calgary, law school vs bank) run through the same `engine.py` with no template switching. Validation script: `PYTHONPATH=. python scripts/test_reasoning.py all --validate`.

---

## Human in the loop

- The AI **never** tells the user which path to choose — only structures tradeoffs and questions to ask third parties (employers, schools, regulators, partners).
- The AI **never** claims anyone is "safe," "verified," or "licensed."
- Final decision stays with the user; outputs are framed as **decision inputs**, not correct answers.
- `verify_before_deciding` pushes users to confirm facts on official sources before acting.

---

## Responsible AI safeguards

1. **Uncertainty shown explicitly** — confidence on every outcome and claim; medium/low claims require `unknown_factors`.
2. **No false precision** — financial and timeline estimates use ranges (`roughly $X–$Y`, `often 6–18 months`).
3. **No false success** — credentialing, startups, and job searches model failure/delay branches at 1–3 years.
4. **Generic output rejected** — validator blocks pros/cons boilerplate and triggers auto-retry.
5. **Disclaimer on every response** — "projection based on what you shared — not a guarantee."
6. **Mock mode for demo safety** — `USE_MOCK` / `VITE_FORCE_MOCK` avoids live API when billing unavailable; does not present mock as verified fact.

---

## Data disclosure

- **Training data:** We use OpenAI's hosted models (`gpt-4o-mini` / optionally `gpt-4o`). We did not train custom models.
- **User data:** Decision descriptions are sent to OpenAI API at request time for reasoning. No persistent user database in MVP.
- **Synthetic / mock data:** `backend/mock.py` and `frontend/src/mockResponse.js` contain hand-authored sample outputs for offline demo — not presented as live AI reasoning when mock mode is on.
- **No fake review dataset:** We did not claim fake-review detection or a verified professional directory — those were explicitly out of scope after pivoting to Direction A (Life Decision Simulator).

---

## Tools used

- **OpenAI API** — `gpt-4o-mini` for extraction + tradeoff modeling
- **FastAPI** — `POST /api/reason`, `GET /health`
- **Pydantic** — request/response schema validation
- **React + Vite** — intake, context cards, path comparison, confidence UI
- **Python** — engine, prompts, validators, test scripts (`test_reasoning.py`, `preflight.py`)

---

## Challenges we ran into

- **Generic LLM outputs** — early responses sounded like pros/cons lists. Fixed with two-phase chain, few-shot quality examples, and programmatic validator + auto-retry.
- **Latency** — each request is 2–3 LLM calls (~60–90s). Frontend shows loading state; mock fallback if API unreachable.
- **Overconfidence** — model defaulted to `high` confidence with empty `unknown_factors`. Prompt rules + validator now enforce mixed confidence and failure branches on uncertain paths.

---

## Accomplishments that we're proud of

- Same engine handles immigration credentialing, early-career, relocation, and education-vs-job decisions without hardcoded templates.
- Binding-constraint-driven reasoning produces tradeoffs tied to the user's actual numbers and household situation.
- Uncertainty is visible in the UI (confidence labels + flags) and in the JSON contract judges can inspect.

---

## What we learned

- Splitting **extract** from **model** improved coherence more than a longer single prompt.
- Programmatic quality checks catch generic phrasing that humans skim past in demo output.
- Honest uncertainty (ranges, failure branches, verification checklists) is a feature, not a weakness — it matches how real decisions work.

---

## What's next

- Structured intake follow-up questions feeding `structured_context` directly
- Streaming/partial responses to reduce perceived latency
- User-saved decision sessions and exportable verification checklists
- Evaluation harness with human-rated output quality across more domains

---

## Quick reference for judges

| File | Purpose |
|------|---------|
| `backend/engine.py` | 3-phase reasoning chain |
| `backend/prompts.py` | System prompts + test scenarios |
| `backend/validators.py` | Quality gate |
| `backend/schemas.py` | API contract |
| `scripts/test_reasoning.py` | Run + validate all scenarios |
| `scripts/preflight.py` | Pre-submit mock + contract check |

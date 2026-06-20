# Life Decision Simulator

AI-powered MVP for **Direction A — Life Decision Simulator**. Users describe any major life or career decision in plain language. The system structures their thinking, models multiple paths with tradeoffs over time, surfaces hidden considerations, and shows honest uncertainty — without telling them what to choose.

> **Not a pros/cons generator.** The LLM reasons from the user's specific constraints (savings runway, dependents, deadlines) and produces decision inputs, not "correct answers."

## LLM Reasoning Engine (architecture)

The reasoning engine is **fully generic** — the same code handles immigration/career decisions, grad school vs startup, relocation, or any other scenario without hardcoded templates.

### Why an LLM (not a rules engine)?

A simple filter can map keywords to categories. This project needs more:

| Capability | Rules / keyword filter | Our LLM chain |
|------------|------------------------|---------------|
| Parse messy natural language | Fragile | Extracts decision structure from free text |
| Find the **binding constraint** | Needs manual rules per domain | Identifies what actually limits options (e.g. "3 months savings") |
| Surface **non-obvious tradeoffs** | Can't — only matches categories | Second-order effects (e.g. shift work vs study time with dependents) |
| Model outcomes over time | Static lookup tables | Projects 3 months / 1 year / 3 years per path with ranges |
| Hybrid paths | Must be pre-defined | Infers realistic third options (e.g. part-time work + credential prep) |
| What-if branching | Not possible | Re-runs reasoning when user challenges an assumption |
| Honest uncertainty | Binary yes/no | Confidence per claim + explicit "what AI cannot know" |

### Three-phase pipeline

```
User input (any decision)
        │
        ▼
┌─────────────────────────────────────┐
│  Phase 1 — Extract (LLM call #1)  │
│  backend/extraction.py            │
│  • core_decision                  │
│  • binding_constraint             │
│  • personal_constraints           │
│  • paths_to_model (2–3 incl.      │
│    hybrid when realistic)         │
│  • non_obvious_risk_signals       │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Phase 2 — Model (LLM call #2)    │
│  backend/prompts.py + engine.py   │
│  • tradeoffs per path               │
│  • outcomes: 3mo / 1yr / 3yr      │
│  • hidden_considerations            │
│  • verify_before_deciding + URLs    │
│  • claims with confidence           │
│  • what_if_impact (if provided)     │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Phase 3 — Validate (no LLM)      │
│  backend/validators.py            │
│  • flags generic pros/cons language │
│  • checks URLs, unknown_factors     │
│  • auto-retries Phase 2 once        │
└─────────────────────────────────────┘
        │
        ▼
   ReasoningResponse JSON → frontend / API
```

### What the LLM classifies from (inputs)

| Input field | Source | Used for |
|-------------|--------|----------|
| `user_description` | Intake UI — plain language, any language | Primary signal for extraction |
| `structured_context` | Intake follow-up questions | Paths, constraints, values, domain (optional) |
| `what_if_assumption` | What-if explorer | Re-runs Phase 2 with changed assumption |

### What the LLM produces (outputs)

See `backend/schemas.py` for the full contract. Key fields:

- **`decision_summary`** — names the binding constraint and why the decision is hard
- **`paths[]`** — 2–3 modeled options, each with:
  - `outcomes` at `3_months`, `1_year`, `3_years` (financial, career, personal impact)
  - `tradeoffs`, `hidden_considerations`, `what_you_give_up`
  - `verify_before_deciding` with official source URLs
- **`claims[]`** — individual assertions with `confidence` + `unknown_factors` + `anchored_to`
- **`global_uncertainty_flags`** — what the AI explicitly cannot know
- **`disclaimer`** — outputs are projections, not guarantees

### Logical coherence (any scenario, not demo-only)

The engine enforces reasoning that generalizes across domains:

- **Path alignment** — output paths must match Phase 1 extraction (the user's actual options)
- **Timeline coherence** — 3 months → 1 year → 3 years is one causal story per path
- **No false success** — credentialing, startups, and job searches must not assume success at 1–3 years
- **Anchored tradeoffs** — generic pros/cons are rejected; tradeoffs cite user constraints, numbers, or parties
- **Specific questions** — `questions_to_ask` targets employers, schools, partners — not "what are your goals?"
- **4 test scenarios** — nurse, grad school, relocation, law school — same engine, no code changes

```bash
PYTHONPATH=. python scripts/test_reasoning.py all --validate
```

### Responsible AI guardrails (built in)

- Never tells the user which path to choose
- Never claims anyone is "safe" or "verified"
- Uses ranges, not false precision (`roughly $X–$Y`, `often 6–18 months`)
- Medium/low confidence claims must list `unknown_factors`
- Verification checklist points users to official sources (CNO, government sites, etc.)
- Quality validator rejects generic pros/cons phrasing and triggers auto-retry

### Model & configuration

| Env variable | Default | Purpose |
|--------------|---------|---------|
| `OPENAI_API_KEY` | — | Required for live reasoning |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model for both LLM phases |
| `USE_MOCK` | `false` | Return sample JSON without API calls |
| `REASONING_MAX_RETRIES` | `3` | Auto-retry count when validation fails |

---

## Quick start

### 1. Setup

```bash
cd usaii
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your OPENAI_API_KEY
```

### 2. Test with built-in scenarios

Three scenarios ship in `backend/prompts.py` to prove the engine is generic (not demo-only):

| Key | Decision type |
|-----|---------------|
| `filipino_nurse_toronto` | Immigration / credentialing (demo video scenario) |
| `grad_school_vs_startup` | Early career / education |
| `toronto_to_calgary` | Relocation / partner constraints |
| `law_school_vs_bank` | Education vs job offer / debt / family pressure |

```bash
# One scenario
PYTHONPATH=. python scripts/test_reasoning.py filipino_nurse_toronto

# All three — same engine, no code changes
PYTHONPATH=. python scripts/test_reasoning.py all

# With extraction + quality report (recommended for tuning)
PYTHONPATH=. python scripts/test_reasoning.py all --validate

# What-if assumption
PYTHONPATH=. python scripts/test_reasoning.py filipino_nurse_toronto \
  --what-if "CNO process completes in 4 months instead of 12"

# No API key / no billing — mock mode
PYTHONPATH=. python scripts/test_reasoning.py filipino_nurse_toronto --mock
```

### 3. Test with your own decision (any scenario)

The engine accepts **any** decision via the API — you are not limited to the three test keys.

**Option A — curl (server running):**

```bash
uvicorn backend.main:app --reload --port 8000
```

```bash
curl -s -X POST http://localhost:8000/api/reason \
  -H "Content-Type: application/json" \
  -d '{
    "user_description": "I got accepted to law school but I also have a full-time offer at a bank. I have student debt and my parents want me to take the stable job.",
    "structured_context": {},
    "what_if_assumption": null
  }'
```

**Option B — Python one-liner:**

```python
from backend.schemas import ReasoningRequest
from backend.engine import run_reasoning_chain

req = ReasoningRequest(user_description="YOUR DECISION HERE IN PLAIN LANGUAGE")
print(run_reasoning_chain(req).model_dump_json(indent=2))
```

Run from project root with `PYTHONPATH=.` and venv active.

### 4. API contract

**`POST /api/reason`**

Request:

```json
{
  "user_description": "plain language situation — any decision",
  "structured_context": {
    "paths_being_compared": ["optional", "from intake"],
    "constraints": ["optional"],
    "timeline_pressure": "optional",
    "stakes": "optional",
    "values": ["optional"],
    "domain": "optional"
  },
  "what_if_assumption": null
}
```

Response: `ReasoningResponse` (see `backend/schemas.py`), including optional `extraction` from Phase 1 for context cards.

**`GET /health`** — server status check.

---

## Project structure

```
usaii/
├── backend/
│   ├── main.py          # FastAPI server (POST /api/reason)
│   ├── engine.py        # 2-step LLM chain + auto-retry
│   ├── extraction.py    # Phase 1 output schema
│   ├── prompts.py       # System prompts + test scenarios
│   ├── validators.py    # Phase 3 quality gate
│   ├── schemas.py       # API request/response types
│   ├── mock.py          # Offline sample data
│   └── env.py           # .env loading
├── scripts/
│   └── test_reasoning.py
├── requirements.txt
└── .env.example
```

---

## Tuning guide

Use `--validate` after every prompt change:

```bash
PYTHONPATH=. python scripts/test_reasoning.py all --validate
```

| Quality issue | Edit |
|---------------|------|
| Generic tradeoffs ("income vs career") | `backend/prompts.py` → `FEW_SHOT_QUALITY` examples |
| Missing personal constraints in outcomes | `build_user_prompt()` rules |
| Over-optimistic long-term projections | Prompt rules for credential/licensing paths |
| New generic phrase keeps appearing | `backend/validators.py` → `GENERIC_PHRASES` |

For final demo quality, try `OPENAI_MODEL=gpt-4o` in `.env` if budget allows.

---

## Common errors

| Error | Fix |
|-------|-----|
| `Create a .env file` | `cp .env.example .env` and add your key |
| `insufficient_quota` (429) | Add billing at [OpenAI](https://platform.openai.com/settings/organization/billing) or use `--mock` |
| `Incorrect API key` | Regenerate key on OpenAI dashboard |
| `ModuleNotFoundError: backend` | Run from project root with `PYTHONPATH=.` |

**Security:** `.env` is gitignored. Never commit API keys.

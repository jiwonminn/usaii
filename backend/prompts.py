"""System and user prompts for the generic decision reasoning chain."""

from __future__ import annotations

import json

SYSTEM_PROMPT = """You are the reasoning engine for "Life Decision Simulator" — a decision support tool, NOT an advice bot.

You do NOT pick a winner. You help the user think by modeling paths, tradeoffs, and uncertainty from THEIR situation.

REASONING METHOD (apply internally for every path):
1. Restate the binding constraint — what makes this decision urgent or risky for THIS user.
2. For each path: "If the user chooses [path] while [constraint] applies, then at [horizon]..."
3. Surface second-order effects the user may not have named (inertia, closed doors, hybrid feasibility).
4. Mark what you cannot know — use confidence levels honestly.

DOMAIN RULES:
- Works for ANY decision: career, education, relocation, immigration, relationships, health, finances, housing.
- NEVER default to immigration, nursing, or any hackathon demo template unless the user describes it.
- Paths come from the user's text. Match paths_to_model from extraction. Add hybrid path ONLY when realistic.
- Do not invent facts (salaries, timelines, policies) the user did not provide — use ranges and flag uncertainty.
- Never say anyone is "safe", "verified", or "licensed". Point to official sources to check.

OUTPUT QUALITY:
- decision_summary: open with binding_constraint; explain why the decision is hard in 2–3 sentences.
- paths[].outcomes: keys MUST be "3_months", "1_year", "3_years". Each horizon = one paragraph of reasoning.
- Timeline coherence: 3_months → 1_year → 3_years is ONE story per path. No unexplained jumps.
- Uncertain paths (credentialing, startups, job search, admissions): 1_year and 3_years MUST include failure/delay branches.
- Financial estimates: use ranges ("roughly $X–$Y"). Plausible across horizons unless a named event explains a change.
- tradeoffs: 2–3 per path. Second-order and situation-specific. Cite user constraints, numbers, deadlines, people.
- hidden_considerations: 2 per path. Focus on optionality — what doors close permanently vs stay open.
- what_you_give_up: 2 per path. Concrete sacrifices, not vague "opportunities".
- verify_before_deciding: 2 per path. At least one item across all paths must have a https:// URL.
- claims: exactly 3 with mixed confidence (high/medium/low). Each medium/low needs unknown_factors. High-confidence MUST have anchored_to (source name or URL, never null).
- High-confidence claims MUST have anchored_to filled (source name or URL) — never null.
- cross_path_insights: exactly 3. Synthesize interactions between paths through the binding constraint.
- questions_to_ask: 3–4. Directed at a specific party (employer, school, partner, regulator) — not self-reflection.
- Use "may", "could", "often", "roughly" — never "will definitely", "guaranteed", "certain to succeed".

Respond ONLY with valid JSON matching the schema. No markdown fences. Proper spacing in all strings."""

EXTRACTION_SYSTEM_PROMPT = """You extract decision structure from ANY life/career situation.

Your job: identify what decision the user faces, what limits them most, and which paths deserve modeling.

binding_constraint selection:
- Pick the ONE factor that most narrows viable options RIGHT NOW.
- Examples: savings runway, offer deadline, dependents, existing debt, visa status, partner's job, health limit.
- NOT generic ("it's a hard choice") — name the specific limit from their text.

paths_to_model:
- List every option the user named. If they name 3, return 3 — do not merge.
- Add a hybrid path ONLY if realistic (part-time work + study, defer offer + explore, etc.).
- Do NOT inject paths from unrelated domains (e.g. do not add "immigration lawyer" unless user mentions legal help).

non_obvious_risk_signals:
- Pull from user's own details: dollar amounts, dates, named people, stated fears.
- NOT generic ("market conditions", "things might change").

Return filled JSON only. No schema definition. No markdown."""

FEW_SHOT_QUALITY = """
═══ TRADEOFFS ═══
BAD: "Immediate income vs long-term career satisfaction"
BAD: "No income could lead to financial hardship"
GOOD: "PSW evening shifts may leave no study window for CNO exams while caring for two young children"
GOOD: "Deferring law school one year may forfeit scholarship terms tied to fall 2025 enrollment"
GOOD: "Startup cofounder role has no salary — partial master's funding still leaves a tuition gap on top of living costs"

═══ TIMELINE (one path, one story) ═══
BAD: 3_months "no income" → 1_year "earning $80k as licensed nurse" (unexplained leap)
GOOD: 3_months "CNO docs submitted, savings declining" → 1_year "assessment ongoing OR bridging required — income still near zero" → 3_years "if licensed, RN range; if not, may revert to PSW with years lost"

═══ personal_impact ═══
BAD: "Helps family wellbeing"
GOOD: "Three months savings means any credential delay forces spouse into full-time work before childcare is arranged"

═══ hidden_considerations ═══
BAD: "There are pros and cons to consider"
GOOD: "Staying in PSW role 2+ years can create career inertia — clinically active but professionally distanced from RN networks"
GOOD: "Bank offer may include clawback clauses if you leave within 12 months — affects optionality if you reapply to law school later"

═══ cross_path_insights (exactly 3, constraint-driven synthesis) ═══
BAD: "Both paths have tradeoffs between money and career"
BAD: "Staying is stable, moving pays more"
GOOD: "With 3 months runway, hybrid only works if part-time hours are contractually fixed — otherwise savings expire before CNO intake"
GOOD: "Grad school keeps a 2027 campus recruiting pipeline open; startup path forecloses it if the cofounder hires a replacement engineer by December"
GOOD: "Calgary's 20% raise is misleading if partner's job search exceeds 6 months — dual income is the binding constraint, not headline salary"

═══ claims ═══
BAD: {"text": "Nursing pays well", "confidence": "high", "unknown_factors": [], "anchored_to": null}
GOOD: {"text": "Ontario PSW wages often fall in the $18–$22/hr range for new hires", "confidence": "medium", "unknown_factors": ["region", "employer type", "shift premiums"], "anchored_to": "Ontario labour market norms"}

═══ questions_to_ask ═══
BAD: "What do you value most in a career?"
GOOD: "Does this bank offer include a clawback period if I leave within the first year?"
GOOD: "Can the CNO tell me my specific assessment pathway and average timeline for my country of training?"

FORBIDDEN in tradeoffs and cross_path_insights (unless embedded in a long, anchored sentence with user-specific numbers/people):
"financial hardship", "financial stability", "income vs", "career satisfaction", "long-term career goals",
"immediate financial needs", "each option presents", "fulfilling career", "pros and cons", "best of both worlds"
"""

RETRY_INSTRUCTION = """
⚠ QUALITY CHECK FAILED — regenerate the COMPLETE JSON fixing ONLY these issues:
{issues}

Fix rules:
- Replace any flagged generic phrase with a sentence citing the user's binding_constraint or personal_constraints.
- cross_path_insights: rewrite all 3 as constraint-driven synthesis, not path summaries.
- If path count wrong: add missing paths from paths_to_model.
- If optimism flagged: change 1_year/3_years to partial progress or failure branches.
- Keep all other good content; do not shorten or drop paths.
"""

PER_PATH_INSTRUCTIONS = """
For EACH path in paths_to_model, build:

description: 1–2 sentences — what choosing this path means in practice for THIS user.

outcomes.3_months: Immediate effects on money, career, and personal life. confidence usually medium or high only if user gave clear facts.
outcomes.1_year: Intermediate state — include uncertainty. For hard paths, show "in progress" not "succeeded".
outcomes.3_years: Long-term projection as a RANGE of outcomes (success / stall / pivot). confidence medium or low unless path is low-risk.

Each outcome object must populate: summary, financial_estimate, career_impact, personal_impact, confidence, unknown_factors (non-empty unless confidence is high AND horizon is 3_months).

tradeoffs: 2–3 items referencing binding_constraint or personal_constraints by name.
hidden_considerations: 2 items about optionality (doors closing/opening).
what_you_give_up: 2 concrete sacrifices.
verify_before_deciding: 2 items with official_source (URL when possible).
"""


def build_extraction_prompt(
    user_description: str,
    structured_context: dict,
) -> str:
    context_block = ""
    if structured_context:
        context_block = f"\nSTRUCTURED CONTEXT (may be partial):\n{structured_context}\n"

    return f"""USER SITUATION:
{user_description}
{context_block}
Return a JSON object with these keys (filled from THIS user only):

- core_decision (string)
- binding_constraint (string) — the single tightest limit right now
- why_decision_is_hard (string) — 1–2 sentences, specific to user
- personal_constraints (array of strings)
- paths_to_model (array of strings) — every option user named; hybrid if realistic
- values (array of strings)
- domain (string) — e.g. "relocation / career", "education / debt"
- non_obvious_risk_signals (array of strings) — from user's own details

Reference shapes (DO NOT copy unless user describes that situation):

Credentialing: binding_constraint might be "3 months savings with 2 dependents"
Early career: binding_constraint might be "2-month decision deadline with partial funding only"
Relocation: binding_constraint might be "3-week offer expiry with partner needing a new job"
Education/debt: binding_constraint might be "$40k existing debt with 4-week response deadline"

Return filled object only. No JSON schema."""


def build_user_prompt(
    user_description: str,
    structured_context: dict,
    what_if_assumption: str | None,
    response_schema: str,
    extraction: dict | None = None,
    retry_issues: list[str] | None = None,
) -> str:
    context_block = ""
    if structured_context:
        context_block = f"""
STRUCTURED CONTEXT (from intake — may be partial):
{structured_context}
"""

    what_if_block = ""
    if what_if_assumption:
        what_if_block = f"""
WHAT-IF ASSUMPTION:
User challenges: "{what_if_assumption}"
- Rerun ALL path outcomes as if this assumption changed.
- Shift confidence levels where the assumption reduces or increases uncertainty.
- Fill what_if_impact with 2–3 sentences: which paths benefit, which worsen, and why.
"""

    extraction_block = ""
    if extraction:
        binding = extraction.get("binding_constraint", "")
        personal = extraction.get("personal_constraints", [])
        paths = extraction.get("paths_to_model", [])
        risks = extraction.get("non_obvious_risk_signals", [])

        extraction_block = f"""
EXTRACTION (ground truth — do not contradict):
{json.dumps(extraction, indent=2)}

MANDATORY:
- decision_summary opens with: "{binding}"
- Model exactly these paths (names may be shortened but must match): {paths}
- Every personal_impact field must reference at least one of: {personal if personal else ["user's stated constraints"]}
- Weave these risk signals into tradeoffs or hidden_considerations: {risks if risks else ["from user description"]}
"""

    retry_block = ""
    if retry_issues:
        retry_block = RETRY_INSTRUCTION.format(
            issues="\n".join(f"- {i}" for i in retry_issues)
        )

    return f"""{FEW_SHOT_QUALITY}
{PER_PATH_INSTRUCTIONS}
USER SITUATION:
{user_description}
{context_block}
{extraction_block}
{what_if_block}
{retry_block}
Return JSON matching this schema:
{response_schema}

CHECKLIST before responding:
☐ paths[].name aligns with paths_to_model
☐ Each path has outcomes.3_months, outcomes.1_year, outcomes.3_years
☐ 3 cross_path_insights — (1) constraint × path interaction, (2) optionality/door closing, (3) timing or hybrid feasibility
☐ 3 claims — mixed confidence; high-confidence MUST have anchored_to (source name or URL, never null)
☐ 3–4 questions_to_ask — directed at employer/school/partner/regulator
☐ At least one https:// URL in verify_before_deciding
☐ No forbidden generic phrases in tradeoffs or cross_path_insights
☐ No "guaranteed" / "will definitely" / "fully licensed" at 1_year or 3_years on uncertain paths"""


# Test scenarios — prove engine is generic (not demo-only)
TEST_SCENARIOS = {
    "filipino_nurse_toronto": {
        "user_description": (
            "We just arrived in Toronto from the Philippines. I'm a registered nurse back home "
            "but my degree isn't recognized in Ontario yet. We have about 3 months of savings left. "
            "I have two young kids and my spouse can't work full-time yet. I'm torn between taking "
            "a PSW/personal support worker job right away to pay bills, or going through the CNO "
            "credential recognition process which could take 6–18 months with no guarantee I'll pass."
        ),
        "structured_context": {
            "paths_being_compared": [
                "Take PSW/healthcare aide job now",
                "Pursue CNO nursing credential recognition",
            ],
            "constraints": ["3 months savings", "2 dependents", "spouse limited work capacity"],
            "timeline_pressure": "high — savings running out",
            "stakes": "family financial stability and long-term nursing career in Canada",
            "values": ["financial security", "career alignment", "family wellbeing"],
            "domain": "immigration / career credentialing",
        },
    },
    "grad_school_vs_startup": {
        "user_description": (
            "I'm a fourth-year CS student in Canada. I got into a good master's program with partial "
            "funding, I also have a return offer from my summer co-op at a mid-size tech company, "
            "and my friend wants me to join their early-stage startup as a technical co-founder. "
            "I don't know which path gives me the best long-term optionality."
        ),
        "structured_context": {
            "paths_being_compared": [
                "Accept master's program",
                "Take return co-op offer",
                "Join startup as co-founder",
            ],
            "constraints": ["partial funding only for grad school", "startup has no salary initially"],
            "timeline_pressure": "decision needed before graduation in 2 months",
            "stakes": "career trajectory and financial runway",
            "values": ["learning", "optionality", "ownership"],
            "domain": "early career",
        },
    },
    "toronto_to_calgary": {
        "user_description": (
            "I've been in Toronto for 3 years working in marketing. I got a job offer in Calgary "
            "paying 20% more but I don't know anyone there. Rent is cheaper but I'd leave my "
            "professional network and my partner would need to find a new job too."
        ),
        "structured_context": {
            "paths_being_compared": ["Stay in Toronto", "Move to Calgary for higher pay"],
            "constraints": ["partner's job search", "no local network in Calgary"],
            "timeline_pressure": "offer expires in 3 weeks",
            "stakes": "career growth, relationship stability, cost of living",
            "values": ["income", "community", "partner's career"],
            "domain": "relocation / career",
        },
    },
    "law_school_vs_bank": {
        "user_description": (
            "I got accepted to law school but I also have a full-time offer at a bank. "
            "I have $40k in student debt already and my parents want me to take the stable job. "
            "I always wanted to be a lawyer but the bank pays well and I'd start immediately."
        ),
        "structured_context": {
            "paths_being_compared": ["Accept law school", "Take bank job"],
            "constraints": ["$40k existing student debt", "family pressure for stability"],
            "timeline_pressure": "need to respond to both offers within 4 weeks",
            "stakes": "career identity, debt load, family expectations",
            "values": ["professional identity", "financial security", "family approval"],
            "domain": "education / career",
        },
    },
}

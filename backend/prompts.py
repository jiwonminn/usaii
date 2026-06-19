"""System and user prompts for the generic decision reasoning chain."""

from __future__ import annotations

import json

SYSTEM_PROMPT = """You are a life decision reasoning engine for a hackathon MVP called "Life Decision Simulator."

Your job is NOT to tell the user which path to choose. You structure their thinking by:
1. Extracting the core decision and paths being compared from whatever they describe
2. Identifying real constraints and what the user values
3. Surfacing non-obvious tradeoffs per path that the user probably hasn't considered
4. Modeling realistic outcomes at 3 months, 1 year, and 3 years per path
5. Highlighting hidden considerations (e.g., one path closes a door permanently; another enables a future option)
6. Assigning honest uncertainty — never present outputs as correct answers

RULES:
- Work for ANY decision domain (career, immigration, housing, education, relocation, relationships, health, finances) — never assume immigration, nursing, or any demo template.
- Derive paths ONLY from what the user described. If they name 2 options, model those 2; add a hybrid ONLY when it is realistic for their domain — do not invent irrelevant paths.
- Use ranges and qualifiers, not false precision. Say "roughly $X–$Y" or "often takes 6–18 months" when uncertain.
- Anchor claims to publicly available knowledge where possible. Name the source or URL when known.
- Explicitly flag what you CANNOT know from the user's input — do not fill gaps with invented facts.
- Do NOT claim anyone is "safe," "verified," or "licensed." Tell users what to verify on official sources.
- Every path gets tradeoffs — there is no perfect option.
- If a what-if assumption is provided, rerun your reasoning and explain how outcomes shift.

LOGICAL COHERENCE (outputs must read as reasoned, not generated):
- Each path tells ONE coherent story across 3_months → 1_year → 3_years. Later horizons build on earlier ones — do not contradict without explaining what changed.
- Do not assume success at 1_year or 3_years for uncertain paths (credentialing, startups, job searches). Model partial progress, delays, or failure branches.
- Financial estimates must be internally plausible (roughly consistent across horizons unless a major event explains a jump).
- causal reasoning: use "because [user constraint], [likely effect]" — not "you will" or "guaranteed."
- path names in output must match paths_to_model from extraction (same options, clear labels).
- questions_to_ask must be specific to THIS situation — questions the user can ask an employer, school, partner, or agency — not generic "what are your goals?"

QUALITY BAR (judges score AI Reasoning on this — avoid generic pros/cons lists):
- Name the user's BINDING CONSTRAINT first (e.g., "3 months savings" changes everything). Every path analysis must reference it.
- Tradeoffs must be NON-OBVIOUS and second-order (e.g., "PSW shift work reduces CNO study hours with two dependents" — NOT "income vs career satisfaction").
- hidden_considerations must include optionality: what doors close permanently vs stay open, and realistic hybrid paths when they exist.
- If 2 paths are compared, consider whether a 3rd hybrid path is realistic (e.g., part-time PSW + CNO prep) — include it as a path when relevant.
- verify_before_deciding: include full URLs to official sources when you know them (e.g., https://www.cno.org/).
- claims: NEVER leave unknown_factors empty when confidence is "medium" or "low". High-confidence claims should still list what could change the estimate.
- outcomes: personal_impact must reflect the user's stated constraints (dependents, spouse, savings runway) — not generic advice.
- Do not write obvious bullet points. Each insight should teach the user something they likely had not articulated.
- cross_path_insights: exactly 3 items. Each must reference the binding constraint OR a personal constraint OR optionality/inertia (what doors close vs stay open). Never summarize paths — synthesize non-obvious interactions between paths.

Respond ONLY with valid JSON matching the schema provided. No markdown fences. Use proper spacing in all string values."""

EXTRACTION_SYSTEM_PROMPT = """You extract decision structure from ANY life/career situation — immigration, education, job offers, relocation, relationships, health, finances, creative pursuits.

Rules:
- binding_constraint = the ONE factor that most limits options (deadline, runway, dependents, visa, health, offer expiry).
- paths_to_model = options the user actually mentioned or clearly implied. Do NOT default to immigration/nursing templates.
- If user lists 3 options (e.g. grad school, job, startup), model all 3 — do not collapse to 2.
- Hybrid path only when realistic for THIS domain (e.g. part-time work + study, remote job + relocation).
- non_obvious_risk_signals must quote specifics from the user's story (numbers, dates, people) — not generic "market risk."

Respond ONLY with valid JSON. No markdown. No JSON schema — return filled values only."""

FEW_SHOT_QUALITY = """
EXAMPLES OF BAD vs GOOD TRADEOFFS (learn the pattern):

BAD (generic — never write these):
- "Immediate income vs long-term career satisfaction"
- "No immediate income could lead to financial hardship"
- "Both paths involve tradeoffs between financial needs and career goals"

GOOD (situation-specific, second-order):
- "PSW evening shifts may leave no study window for CNO exams while caring for two young children"
- "Starting CNO now preserves bridging-program eligibility windows that close if you delay 12+ months"
- "Accepting the co-op offer now may signal to your startup cofounder that you are not fully committed"
- "Partial master's funding leaves a tuition gap that student loans may not cover if the startup equity is illiquid for 2+ years"
- "Calgary's 20% raise matters less if your partner's marketing role search takes 6+ months in a new city"
- "Law school adds tuition on top of $40k debt — bank income starts now but may close the admissions window if deferred"

LOGICAL TIMELINE (same path, coherent story):
BAD: 3_months says "no income", 1_year says "fully licensed nurse earning $80k" with no explanation.
GOOD: 3_months "submitted CNO docs, still no paycheck", 1_year "assessment in progress OR bridging required — income still uncertain", 3_years "if licensed, RN income; if not, may need to restart PSW path"

EXAMPLES OF BAD vs GOOD personal_impact:
BAD: "Increased financial stability helps family wellbeing."
GOOD: "Three months savings means any CNO delay forces spouse into full-time work before childcare is sorted."

FORBIDDEN PHRASES — never use in tradeoffs OR cross_path_insights:
"financial hardship", "financial stability", "income vs", "career satisfaction", "long-term career goals",
"immediate financial needs", "weighing immediate", "each option presents", "fulfilling career"

EXAMPLES OF BAD vs GOOD cross_path_insights:

BAD (summary — never write these):
- "Both paths involve tradeoffs between financial needs and career goals."
- "Staying offers stability while moving offers higher pay."
- "Each option has pros and cons to consider."

GOOD (non-obvious, constraint-driven):
- "With only 3 months runway, the hybrid path only works if part-time PSW hours are predictable — otherwise savings expire before CNO documents are even submitted."
- "Grad school preserves a 2027 hiring cycle optionality that the startup path forecloses if the cofounder replaces you within 6 months."
- "Calgary's salary bump may not offset partner unemployment — the binding constraint is dual income, not headline pay."
"""

RETRY_INSTRUCTION = """
PREVIOUS OUTPUT FAILED QUALITY CHECK. Fix these specific issues and regenerate the FULL JSON:
{issues}

Do not repeat generic pros/cons language. Ground every personal_impact in the user's stated constraints.
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
Extract decision structure. Return a JSON object with exactly these keys and string/list values from the user's situation:

- core_decision (string)
- binding_constraint (string) — the ONE tightest limit (savings runway, deadline, dependents)
- why_decision_is_hard (string)
- personal_constraints (array of strings) — spouse, kids, language, health, etc.
- paths_to_model (array of strings) — at least 2 paths; add hybrid if realistic
- values (array of strings)
- domain (string)
- non_obvious_risk_signals (array of strings) — specific risks from their story, not generic advice

Example A — credentialing / immigration:
{{
  "core_decision": "PSW job now vs CNO credential recognition",
  "binding_constraint": "3 months savings with 2 dependents",
  "why_decision_is_hard": "Immediate income pressure conflicts with a long uncertain credential path.",
  "personal_constraints": ["two young children", "spouse cannot work full-time yet"],
  "paths_to_model": ["Take PSW job now", "Pursue CNO recognition", "Part-time PSW + CNO prep"],
  "values": ["financial security", "nursing career"],
  "domain": "immigration / career credentialing",
  "non_obvious_risk_signals": ["credential gap may require bridging courses", "savings may not cover rent past month 3"]
}}

Example B — early career (different domain — do NOT copy paths unless user describes this):
{{
  "core_decision": "Master's program vs return co-op offer vs startup co-founder role",
  "binding_constraint": "Decision deadline in 2 months with partial grad funding only",
  "why_decision_is_hard": "Each path closes different doors — grad school delays income, startup has no salary, co-op is safe but caps upside.",
  "personal_constraints": [],
  "paths_to_model": ["Accept master's program", "Take return co-op offer", "Join startup as co-founder"],
  "values": ["learning", "optionality", "ownership"],
  "domain": "early career / education",
  "non_obvious_risk_signals": ["startup equity may be worthless", "partial funding may require debt"]
}}

Extract from THIS user's situation only. Do NOT return a JSON schema. Return only the filled object."""


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
WHAT-IF ASSUMPTION TO MODEL:
The user wants to challenge this assumption: "{what_if_assumption}"
Rerun your reasoning as if this assumption were true or changed. Explain how outcomes and confidence levels shift in what_if_impact.
"""

    extraction_block = ""
    if extraction:
        extraction_block = f"""
DECISION EXTRACTION (step 1 — use as ground truth for modeling):
{json.dumps(extraction, indent=2)}

You MUST:
- Open decision_summary with the binding_constraint
- Model every path in paths_to_model
- Reference personal_constraints in EVERY path's personal_impact fields
- Surface non_obvious_risk_signals in tradeoffs or hidden_considerations
"""

    retry_block = ""
    if retry_issues:
        retry_block = RETRY_INSTRUCTION.format(
            issues="\n".join(f"- {i}" for i in retry_issues)
        )

    return f"""{FEW_SHOT_QUALITY}
USER SITUATION (plain language):
{user_description}
{context_block}
{extraction_block}
{what_if_block}
{retry_block}
Analyze this decision and return JSON matching this schema exactly:
{response_schema}

Requirements for paths[].outcomes: must include keys "3_months", "1_year", "3_years" each as a TimedOutcome object.
Include at least 2 paths (extract from user input; if only one is mentioned, infer a realistic alternative; add a hybrid path when realistic).
Include at least 3 claims with varying confidence levels; every claim must have at least 1 unknown_factor unless confidence is high AND the fact is definitional.
High-confidence claims MUST include anchored_to with a named source or URL.
Include at least 2 global_uncertainty_flags for things you cannot know.
decision_summary must name the binding constraint and why this decision is hard — not restate the obvious.
paths[].name must align with paths_to_model from extraction (same options, readable labels).
For credentialing, licensing, startups, or job searches: 1_year and 3_years outcomes must NOT assume success — model partial progress, delays, or failure branches.
Each path's 3_months → 1_year → 3_years must tell a coherent causal story without unexplained jumps.
cross_path_insights: exactly 3 items — non-obvious, constraint-driven synthesis. No forbidden phrases.
tradeoffs: situation-specific only — cite the user's constraints, numbers, deadlines, or named parties.
questions_to_ask: 3+ specific questions for THIS decision (employer, school, partner, agency) — not generic self-reflection."""


# Test scenarios for Day 1 validation (Person 3 shares raw outputs with team)
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

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
- Work for ANY decision domain (career, immigration, housing, education, relocation, etc.) — never assume a hardcoded template.
- Use ranges and qualifiers, not false precision. Say "roughly $X–$Y" or "often takes 6–18 months" when uncertain.
- Anchor claims to publicly available knowledge where possible (licensing bodies, government programs, industry norms). Name the source.
- Explicitly flag what you CANNOT know from the user's input.
- Do NOT claim anyone is "safe," "verified," or "licensed." Tell users what to verify on official sources.
- Every path gets tradeoffs — there is no perfect option.
- If a what-if assumption is provided, rerun your reasoning and explain how outcomes shift.

QUALITY BAR (judges score AI Reasoning on this — avoid generic pros/cons lists):
- Name the user's BINDING CONSTRAINT first (e.g., "3 months savings" changes everything). Every path analysis must reference it.
- Tradeoffs must be NON-OBVIOUS and second-order (e.g., "PSW shift work reduces CNO study hours with two dependents" — NOT "income vs career satisfaction").
- hidden_considerations must include optionality: what doors close permanently vs stay open, and realistic hybrid paths when they exist.
- If 2 paths are compared, consider whether a 3rd hybrid path is realistic (e.g., part-time PSW + CNO prep) — include it as a path when relevant.
- verify_before_deciding: include full URLs to official sources when you know them (e.g., https://www.cno.org/).
- claims: NEVER leave unknown_factors empty when confidence is "medium" or "low". High-confidence claims should still list what could change the estimate.
- outcomes: personal_impact must reflect the user's stated constraints (dependents, spouse, savings runway) — not generic advice.
- Do not write obvious bullet points. Each insight should teach the user something they likely had not articulated.

Respond ONLY with valid JSON matching the schema provided. No markdown fences. Use proper spacing in all string values."""

EXTRACTION_SYSTEM_PROMPT = """You extract decision structure from ANY life/career situation.
Do not recommend a path. Identify what makes the decision hard and what paths deserve modeling.
If two polar options exist (A vs B), check whether a realistic hybrid path C exists.
Respond ONLY with valid JSON matching the schema. No markdown."""

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

EXAMPLES OF BAD vs GOOD personal_impact:
BAD: "Increased financial stability helps family wellbeing."
GOOD: "Three months savings means any CNO delay forces spouse into full-time work before childcare is sorted."
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

Example (replace with this user's actual details):
{{
  "core_decision": "PSW job now vs CNO credential recognition",
  "binding_constraint": "3 months savings with 2 dependents",
  "why_decision_is_hard": "...",
  "personal_constraints": ["two young children", "spouse cannot work full-time yet"],
  "paths_to_model": ["Take PSW job now", "Pursue CNO recognition", "Part-time PSW + CNO prep"],
  "values": ["financial security", "nursing career"],
  "domain": "immigration / career credentialing",
  "non_obvious_risk_signals": ["credential gap may require bridging courses", "savings may not cover rent past month 3"]
}}

Do NOT return a JSON schema. Return only the filled object."""


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
For credentialing/licensing paths: 1_year outcomes must NOT assume success — model partial progress, bridging, or failure branches."""


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
}

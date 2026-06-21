

"""Context structuring — Person 4 core deliverable.

Takes raw user text and produces a StructuredContext (paths, constraints,
timeline, stakes, values, domain) plus targeted follow-up questions for
information the user did not provide but the reasoning engine needs.

This runs BEFORE Person 3's extraction phase. The structured context it
produces feeds into extraction and modeling, improving output quality
from "generic" to "grounded in the user's real situation."
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI, RateLimitError

from backend.env import get_openai_api_key
from backend.schemas import StructuredContext

STRUCTURING_SYSTEM_PROMPT = """You are the intake structuring layer for a life decision simulator.

Your job: take messy, natural-language descriptions of life decisions and extract clean, structured context that a downstream reasoning engine will use.

You are NOT the reasoning engine. Do NOT model outcomes, give advice, or evaluate paths. Just extract what the user told you and identify what's missing.

EXTRACT these fields from the user's text:
- paths_being_compared: the options the user is weighing (2-4 paths). Use the user's own words.
- constraints: anything that limits their options — money, time, dependents, health, location, legal status, debt.
- timeline_pressure: how urgent is the decision? Quote deadlines if mentioned.
- stakes: what's at risk if they choose wrong?
- values: what matters to them? (security, growth, family, identity, independence, etc.)
- domain: categorize the decision area (e.g. "career / education", "relocation", "immigration / credentialing", "finance / housing", "relationship / family")

FOLLOW-UP QUESTIONS:
Generate 2-4 targeted questions for information the user did NOT provide but that would significantly improve the analysis. Each question must:
- Target a specific gap (not "tell me more")
- Explain WHY this information matters for modeling their paths
- Be answerable in 1-2 sentences

Common gaps to probe:
- Financial runway / savings / debt numbers
- Who else is affected (dependents, partner, family)
- Hard deadlines or offer expiry dates
- What they've already tried or ruled out
- Specific fears vs. hopes

COMPLETENESS SCORE:
Rate 1-5 how much context the user provided:
1 = barely stated the decision
2 = stated decision but missing most constraints
3 = clear decision with some constraints, missing financial/timeline details
4 = good detail, minor gaps
5 = very thorough, follow-ups are nice-to-have only

OUTPUT: JSON with keys: paths_being_compared, constraints, timeline_pressure, stakes, values, domain, follow_up_questions (array of {question, why_it_matters}), completeness_score, intake_summary.

intake_summary: 1-2 sentences restating what the user is deciding, using THEIR details — not generic framing. This confirms back to the user that we understood them.

Return filled JSON only. No markdown fences."""

FOLLOWUP_SYSTEM_PROMPT = """You are updating structured context for a life decision simulator based on the user's answers to follow-up questions.

You will receive:
1. The original user description
2. The current structured context (partially filled)
3. The user's answers to follow-up questions

Your job: merge the new information into the structured context. Update fields that now have better data. Do NOT remove information that was already extracted.

If the answers reveal new constraints, paths, or stakes, add them. If answers clarify timeline or financial details, update those fields.

Also generate 0-2 NEW follow-up questions if critical gaps remain after incorporating answers. If context is now sufficient (completeness >= 4), return empty follow_up_questions.

Return the same JSON structure: paths_being_compared, constraints, timeline_pressure, stakes, values, domain, follow_up_questions, completeness_score, intake_summary."""


def _get_client() -> OpenAI:
    return OpenAI(api_key=get_openai_api_key())


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _chat_json(client: OpenAI, system: str, user: str, *, temperature: float = 0.2) -> dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
    except RateLimitError as exc:
        detail = str(exc)
        if "insufficient_quota" in detail:
            raise RuntimeError(
                "OpenAI returned insufficient_quota (429). "
                "Fix: https://platform.openai.com/settings/organization/billing"
            ) from exc
        raise

    raw = response.choices[0].message.content
    if not raw:
        raise RuntimeError("Empty response from LLM during structuring.")
    return json.loads(raw)


class FollowUpQuestion:
    def __init__(self, question: str, why_it_matters: str):
        self.question = question
        self.why_it_matters = why_it_matters

    def to_dict(self) -> dict[str, str]:
        return {"question": self.question, "why_it_matters": self.why_it_matters}


class StructuringResult:
    def __init__(
        self,
        context: StructuredContext,
        follow_up_questions: list[FollowUpQuestion],
        completeness_score: int,
        intake_summary: str,
    ):
        self.context = context
        self.follow_up_questions = follow_up_questions
        self.completeness_score = completeness_score
        self.intake_summary = intake_summary

    def to_dict(self) -> dict:
        return {
            "structured_context": self.context.model_dump(),
            "follow_up_questions": [q.to_dict() for q in self.follow_up_questions],
            "completeness_score": self.completeness_score,
            "intake_summary": self.intake_summary,
        }


def structure_user_input(user_description: str) -> StructuringResult:
    """Extract structured decision context from raw user text.

    Returns structured context, follow-up questions, and a completeness score.
    """
    if os.environ.get("USE_MOCK", "").lower() in ("1", "true", "yes"):
        return _mock_structuring(user_description)

    client = _get_client()
    prompt = f"USER INPUT:\n{user_description}"
    data = _chat_json(client, STRUCTURING_SYSTEM_PROMPT, prompt)
    return _parse_structuring_response(data)


def incorporate_followup_answers(
    user_description: str,
    current_context: StructuredContext,
    answers: dict[str, str],
) -> StructuringResult:
    """Merge follow-up answers into existing structured context.

    answers: mapping of question text -> user's answer.
    """
    if os.environ.get("USE_MOCK", "").lower() in ("1", "true", "yes"):
        return _mock_followup(current_context, answers)

    client = _get_client()

    answers_text = "\n".join(
        f"Q: {q}\nA: {a}" for q, a in answers.items() if a.strip()
    )

    prompt = f"""ORIGINAL USER DESCRIPTION:
{user_description}

CURRENT STRUCTURED CONTEXT:
{json.dumps(current_context.model_dump(), indent=2)}

USER'S ANSWERS TO FOLLOW-UP QUESTIONS:
{answers_text}"""

    data = _chat_json(client, FOLLOWUP_SYSTEM_PROMPT, prompt)
    return _parse_structuring_response(data)


def _parse_structuring_response(data: dict) -> StructuringResult:
    context = StructuredContext(
        paths_being_compared=data.get("paths_being_compared", []),
        constraints=data.get("constraints", []),
        timeline_pressure=data.get("timeline_pressure"),
        stakes=data.get("stakes"),
        values=data.get("values", []),
        domain=data.get("domain"),
    )

    follow_ups = []
    for fq in data.get("follow_up_questions", []):
        if isinstance(fq, dict) and fq.get("question"):
            follow_ups.append(
                FollowUpQuestion(
                    question=fq["question"],
                    why_it_matters=fq.get("why_it_matters", ""),
                )
            )

    return StructuringResult(
        context=context,
        follow_up_questions=follow_ups,
        completeness_score=data.get("completeness_score", 1),
        intake_summary=data.get("intake_summary", ""),
    )


def _mock_structuring(user_description: str) -> StructuringResult:
    desc = user_description.lower()

    if "nurse" in desc or "cno" in desc:
        return StructuringResult(
            context=StructuredContext(
                paths_being_compared=["Take PSW job now", "Pursue CNO credential recognition"],
                constraints=["3 months savings", "2 dependents", "spouse limited work capacity"],
                timeline_pressure="High — savings running out within 3 months",
                stakes="Family financial stability and long-term nursing career in Canada",
                values=["financial security", "career alignment", "family wellbeing"],
                domain="immigration / career credentialing",
            ),
            follow_up_questions=[
                FollowUpQuestion(
                    question="Have you already started the CNO application process, or is this from scratch?",
                    why_it_matters="Knowing where you are in the process changes the timeline projection significantly.",
                ),
                FollowUpQuestion(
                    question="Can your spouse pick up part-time work, or are there barriers (childcare, legal status)?",
                    why_it_matters="A second income source, even small, changes how long your savings last.",
                ),
            ],
            completeness_score=3,
            intake_summary=(
                "You're a Filipino RN in Toronto weighing immediate PSW work against "
                "pursuing CNO nursing credential recognition, with about 3 months of savings "
                "and two young kids depending on you."
            ),
        )

    return StructuringResult(
        context=StructuredContext(
            paths_being_compared=["Option A (from your description)", "Option B (from your description)"],
            constraints=["Extracted from your input (mock)"],
            timeline_pressure="Unknown — mock mode",
            stakes="Extracted from your input (mock)",
            values=["To be determined from your context"],
            domain="general",
        ),
        follow_up_questions=[
            FollowUpQuestion(
                question="What's the hardest part about this decision for you?",
                why_it_matters="Understanding your main concern helps us model the right tradeoffs.",
            ),
            FollowUpQuestion(
                question="Is there a deadline by which you need to decide?",
                why_it_matters="Timeline pressure changes which paths are even viable.",
            ),
        ],
        completeness_score=2,
        intake_summary="Mock structuring — connect live API for real context extraction.",
    )


def _mock_followup(
    current_context: StructuredContext,
    answers: dict[str, str],
) -> StructuringResult:
    return StructuringResult(
        context=current_context,
        follow_up_questions=[],
        completeness_score=4,
        intake_summary="Context enriched with your follow-up answers (mock).",
    )

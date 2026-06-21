

"""Shared request/response schemas for the Life Decision Simulator API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.extraction import DecisionExtraction


class StructuredContext(BaseModel):
    """Context extracted from intake (Person 1/4). All fields optional for partial intake."""

    paths_being_compared: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    timeline_pressure: str | None = None
    stakes: str | None = None
    values: list[str] = Field(default_factory=list)
    domain: str | None = None


class ReasoningRequest(BaseModel):
    user_description: str = Field(
        ...,
        description="Plain-language description of the decision situation.",
    )
    structured_context: StructuredContext = Field(default_factory=StructuredContext)
    what_if_assumption: str | None = Field(
        default=None,
        description="Optional assumption to challenge; reruns reasoning dynamically.",
    )


# --- Person 4: Context Structuring API schemas ---


class StructureRequest(BaseModel):
    """Step 1 of the intake flow — raw text in, structured context out."""

    user_description: str = Field(
        ...,
        description="Plain-language description of the decision situation.",
    )


class FollowUpQuestionOut(BaseModel):
    question: str
    why_it_matters: str = ""


class StructureResponse(BaseModel):
    """Returned by /api/structure — structured context + follow-up questions."""

    structured_context: StructuredContext
    follow_up_questions: list[FollowUpQuestionOut] = Field(default_factory=list)
    completeness_score: int = Field(
        ge=1, le=5,
        description="1=barely stated, 5=very thorough.",
    )
    intake_summary: str = Field(
        default="",
        description="1-2 sentence restatement confirming we understood the user.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking warnings from input validation.",
    )


class FollowUpRequest(BaseModel):
    """Step 2 (optional) — user answers follow-up questions to enrich context."""

    user_description: str = Field(
        ...,
        description="Original user description (same as step 1).",
    )
    structured_context: StructuredContext = Field(
        ...,
        description="Structured context from step 1.",
    )
    answers: dict[str, str] = Field(
        ...,
        description="Mapping of question text -> user's answer.",
    )


ConfidenceLevel = Literal["high", "medium", "low"]


class VerificationItem(BaseModel):
    item: str
    official_source: str | None = None
    confidence: ConfidenceLevel = "medium"
    reason_uncertain: str | None = None


class TimedOutcome(BaseModel):
    summary: str
    financial_estimate: str | None = None
    career_impact: str | None = None
    personal_impact: str | None = None
    confidence: ConfidenceLevel = "medium"
    unknown_factors: list[str] = Field(default_factory=list)


class PathAnalysis(BaseModel):
    name: str
    description: str
    outcomes: dict[str, TimedOutcome] = Field(
        description="Keys: 3_months, 1_year, 3_years",
    )
    tradeoffs: list[str] = Field(default_factory=list)
    hidden_considerations: list[str] = Field(default_factory=list)
    what_you_give_up: list[str] = Field(default_factory=list)
    verify_before_deciding: list[VerificationItem] = Field(default_factory=list)


class ClaimWithUncertainty(BaseModel):
    text: str
    confidence: ConfidenceLevel
    unknown_factors: list[str] = Field(default_factory=list)
    anchored_to: str | None = Field(
        default=None,
        description="Public source or general knowledge anchor, if any.",
    )


class ReasoningResponse(BaseModel):
    decision_summary: str
    core_decision: str
    paths: list[PathAnalysis]
    cross_path_insights: list[str] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(
        default_factory=list,
        description="Direct questions the user should ask other parties.",
    )
    claims: list[ClaimWithUncertainty] = Field(default_factory=list)
    global_uncertainty_flags: list[str] = Field(
        default_factory=list,
        description="What the AI explicitly cannot know about this situation.",
    )
    what_if_impact: str | None = Field(
        default=None,
        description="How the what-if assumption shifted the analysis, if provided.",
    )
    disclaimer: str = (
        "This is a projection based on what you have shared — not a guarantee. "
        "Your situation may differ. Only you can make the final decision."
    )
    extraction: DecisionExtraction | None = Field(
        default=None,
        description="Phase 1 structured context — attached by engine, not generated in phase 2.",
    )

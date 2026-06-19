"""Step 1 of reasoning chain — extract decision structure before tradeoff modeling."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DecisionExtraction(BaseModel):
    """Structured context extracted from any user decision — feeds step 2."""

    core_decision: str
    binding_constraint: str = Field(
        description="The single tightest constraint that makes this decision hard (e.g. runway, deadline).",
    )
    why_decision_is_hard: str
    personal_constraints: list[str] = Field(
        default_factory=list,
        description="Dependents, partner, health, language, location — anything that changes outcomes.",
    )
    paths_to_model: list[str] = Field(
        min_length=2,
        description="Include explicit paths plus a hybrid path when realistic.",
    )
    values: list[str] = Field(default_factory=list)
    domain: str
    non_obvious_risk_signals: list[str] = Field(
        default_factory=list,
        description="Specific risks from the user's text, not generic advice.",
    )

"""Quality checks on reasoning output — used for auto-retry and Friday polish."""

from __future__ import annotations

import re

from backend.schemas import ReasoningResponse

# Obvious pros/cons phrasing judges flag as "not AI reasoning"
GENERIC_PHRASES = [
    "income vs",
    "vs long-term",
    "financial hardship",
    "financial stability",
    "long-term career goals",
    "immediate financial needs",
    "career satisfaction",
    "fulfilling career",
    "weighing immediate",
    "each option presents",
]

URL_PATTERN = re.compile(r"https?://")


def validate_reasoning(
    response: ReasoningResponse,
    *,
    binding_constraint: str | None = None,
    personal_constraints: list[str] | None = None,
) -> list[str]:
    """Return human-readable quality issues. Empty list = passes."""
    issues: list[str] = []
    personal_constraints = personal_constraints or []

    summary_lower = response.decision_summary.lower()
    if binding_constraint and binding_constraint.lower()[:20] not in summary_lower:
        # Allow partial match on first significant chunk
        key_words = [w for w in binding_constraint.lower().split() if len(w) > 4]
        if key_words and not any(w in summary_lower for w in key_words[:3]):
            issues.append(
                f"decision_summary must name the binding constraint ({binding_constraint!r})."
            )

    all_tradeoffs = " ".join(
        t.lower() for p in response.paths for t in p.tradeoffs
    )
    for phrase in GENERIC_PHRASES:
        if phrase in all_tradeoffs:
            issues.append(
                f"Generic tradeoff detected ({phrase!r}). Use second-order, situation-specific tradeoffs."
            )

    cross = " ".join(response.cross_path_insights).lower()
    for phrase in GENERIC_PHRASES:
        if phrase in cross:
            issues.append(
                "cross_path_insights sound like a summary, not non-obvious reasoning. "
                "Include optionality, inertia, or constraint-driven tradeoffs."
            )
            break

    summary_phrase_hits = sum(1 for phrase in ("both paths", "each option", "each path", "pros and cons") if phrase in cross)
    if summary_phrase_hits >= 1:
        issues.append(
            "cross_path_insights use summary language ('both paths', 'each option'). "
            "Write constraint-specific synthesis instead."
        )

    for claim in response.claims:
        if claim.confidence in ("medium", "low") and not claim.unknown_factors:
            issues.append(
                f"Claim with {claim.confidence} confidence missing unknown_factors: {claim.text[:60]}..."
            )
        if claim.confidence == "high" and not claim.anchored_to:
            issues.append(
                f"High-confidence claim should anchor to a source: {claim.text[:60]}..."
            )

    has_url = any(
        URL_PATTERN.search(v.official_source or "")
        for p in response.paths
        for v in p.verify_before_deciding
    )
    if not has_url:
        issues.append("verify_before_deciding must include at least one https:// URL.")

    if len(response.paths) < 2:
        issues.append("Need at least 2 paths modeled.")

    if personal_constraints:
        combined_personal = " ".join(
            (o.personal_impact or "").lower()
            for p in response.paths
            for o in p.outcomes.values()
        )
        hits = sum(
            1 for c in personal_constraints
            if any(word in combined_personal for word in c.lower().split() if len(word) > 4)
        )
        if hits < min(2, len(personal_constraints)):
            issues.append(
                "personal_impact fields must reference stated household constraints "
                f"(e.g. {personal_constraints[:3]})."
            )

    for path in response.paths:
        for horizon, outcome in path.outcomes.items():
            if outcome.confidence == "high" and horizon in ("1_year", "3_years"):
                if not outcome.unknown_factors and binding_constraint:
                    issues.append(
                        f"{path.name} / {horizon}: high confidence with empty unknown_factors "
                        "— long horizons should acknowledge uncertainty."
                    )

    if len(response.global_uncertainty_flags) < 2:
        issues.append("Need at least 2 global_uncertainty_flags.")

    return issues

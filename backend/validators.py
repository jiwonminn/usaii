"""Quality checks on reasoning output — used for auto-retry and Friday polish."""

from __future__ import annotations

import re

from backend.schemas import ReasoningResponse

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
    "best of both worlds",
    "unique opportunity",
    "great opportunity",
]

OPTIMISTIC_UNEARNED = [
    "fully licensed",
    "guaranteed",
    "will definitely",
    "certain to",
    "sure to succeed",
    "easily pass",
]

GENERIC_QUESTIONS = [
    "what are your goals",
    "what do you value most",
    "what is most important to you",
    "have you considered all options",
]

URL_PATTERN = re.compile(r"https?://")


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _path_aligns_with_model(path_name: str, paths_to_model: list[str]) -> bool:
    path_norm = _normalize(path_name)
    for model_path in paths_to_model:
        model_norm = _normalize(model_path)
        # overlap on significant words
        path_words = {w for w in path_norm.split() if len(w) > 3}
        model_words = {w for w in model_norm.split() if len(w) > 3}
        if path_words & model_words:
            return True
        if path_norm in model_norm or model_norm in path_norm:
            return True
    return False


def _is_specific_tradeoff(text: str) -> bool:
    """Long or anchored tradeoffs may use common words in a specific context."""
    if any(c.isdigit() for c in text):
        return True
    if len(text) > 95:
        return True
    anchors = (
        "parent", "debt", "law", "bank", "spouse", "partner", "child", "kid",
        "cno", "psw", "calgary", "toronto", "startup", "master", "co-op",
        "offer", "deadline", "week", "month", "visa", "rent", "tuition",
    )
    lower = text.lower()
    return any(a in lower for a in anchors)


def validate_reasoning(
    response: ReasoningResponse,
    *,
    binding_constraint: str | None = None,
    personal_constraints: list[str] | None = None,
    paths_to_model: list[str] | None = None,
) -> list[str]:
    """Return human-readable quality issues. Empty list = passes."""
    issues: list[str] = []
    personal_constraints = personal_constraints or []
    paths_to_model = paths_to_model or []

    summary_lower = response.decision_summary.lower()
    if binding_constraint:
        key_words = [w for w in binding_constraint.lower().split() if len(w) > 4]
        if key_words and not any(w in summary_lower for w in key_words[:3]):
            issues.append(
                f"decision_summary must name the binding constraint ({binding_constraint!r})."
            )

    if paths_to_model:
        if len(response.paths) < len(paths_to_model):
            issues.append(
                f"Expected at least {len(paths_to_model)} paths from extraction; got {len(response.paths)}."
            )
        for path in response.paths:
            if not _path_aligns_with_model(path.name, paths_to_model):
                issues.append(
                    f"Path {path.name!r} does not align with extracted paths_to_model."
                )

    all_tradeoffs = " ".join(
        t.lower() for p in response.paths for t in p.tradeoffs
    )
    for phrase in GENERIC_PHRASES:
        if phrase in all_tradeoffs:
            # Only flag if the phrase appears in a short, non-anchored tradeoff
            offending = [
                t for p in response.paths for t in p.tradeoffs
                if phrase in t.lower() and not _is_specific_tradeoff(t)
            ]
            if offending:
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

    if len(response.cross_path_insights) != 3:
        issues.append(
            f"cross_path_insights should have exactly 3 items; got {len(response.cross_path_insights)}."
        )

    summary_phrases = ("both paths", "each option", "each path", "pros and cons")
    if any(phrase in cross for phrase in summary_phrases):
        issues.append(
            "cross_path_insights use summary language. Write constraint-specific synthesis instead."
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

    for q in response.questions_to_ask:
        q_lower = q.lower()
        if any(g in q_lower for g in GENERIC_QUESTIONS):
            issues.append(
                f"questions_to_ask too generic: {q[:70]}... — ask a specific party (employer, school, partner)."
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

    uncertain_domains = ("credential", "startup", "cno", "license", "recognition", "search", "offer")
    for path in response.paths:
        path_lower = path.name.lower() + " " + path.description.lower()
        is_uncertain_path = any(d in path_lower for d in uncertain_domains)

        for horizon, outcome in path.outcomes.items():
            if outcome.confidence == "high" and horizon in ("1_year", "3_years"):
                if not outcome.unknown_factors:
                    issues.append(
                        f"{path.name} / {horizon}: high confidence with empty unknown_factors "
                        "— long horizons should acknowledge uncertainty."
                    )

            combined = (outcome.summary or "").lower() + " " + (outcome.career_impact or "").lower()
            if is_uncertain_path and horizon in ("1_year", "3_years"):
                for phrase in OPTIMISTIC_UNEARNED:
                    if phrase in combined:
                        issues.append(
                            f"{path.name} / {horizon}: overly optimistic language ({phrase!r}) "
                            "for an uncertain path — model partial progress or failure branches."
                        )

    if len(response.global_uncertainty_flags) < 2:
        issues.append("Need at least 2 global_uncertainty_flags.")

    return issues

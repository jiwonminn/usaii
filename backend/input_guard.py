"""Input validation before expensive LLM calls — Person 4 quality gate."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

MIN_WORDS = 12
MAX_WORDS = 2000
MIN_DECISION_SIGNALS = 1

DECISION_SIGNALS = [
    r"\bor\b",
    r"\bvs\.?\b",
    r"\bversus\b",
    r"\bbetween\b",
    r"\btorn\b",
    r"\bdecid",
    r"\bchoose\b",
    r"\bchoice\b",
    r"\bshould i\b",
    r"\bwhether\b",
    r"\boption",
    r"\bpath\b",
    r"\bdilemma\b",
    r"\bstuck\b",
    r"\bnot sure\b",
    r"\bdon'?t know\b",
    r"\bconfused\b",
    r"\baccept\b.*\bor\b",
    r"\btake\b.*\bor\b",
    r"\bstay\b.*\bor\b.*\b(move|leave|go)\b",
]

SENSITIVE_PATTERNS = [
    (r"\b(suicid|self.?harm|kill myself|end my life)\b", "crisis"),
    (r"\b(abuse|domestic violence|assault)\b", "safety"),
    (r"\b(illegal|smuggl|fraud|launder)\b", "legal"),
]

CRISIS_DISCLAIMER = (
    "It sounds like you may be going through something serious. "
    "This tool models decision paths — it is not equipped for crisis support. "
    "Please reach out to a crisis helpline: 988 (US/Canada), or text HOME to 741741."
)


class InputGuardResult(BaseModel):
    ok: bool
    cleaned_text: str = ""
    word_count: int = 0
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    has_decision_signal: bool = False
    sensitive_flags: list[str] = Field(default_factory=list)


def guard_input(raw_text: str) -> InputGuardResult:
    """Validate and clean user input before structuring."""
    issues: list[str] = []
    warnings: list[str] = []
    sensitive_flags: list[str] = []

    if not raw_text or not raw_text.strip():
        return InputGuardResult(ok=False, issues=["Please describe your decision."])

    cleaned = _clean_text(raw_text)
    word_count = len(cleaned.split())

    if word_count < MIN_WORDS:
        issues.append(
            f"Your description is too short ({word_count} words). "
            f"Include what you're deciding between, what's at stake, and what limits your options. "
            f"Aim for at least {MIN_WORDS} words."
        )

    if word_count > MAX_WORDS:
        issues.append(
            f"Your description is very long ({word_count} words). "
            f"Try to focus on one main decision — max {MAX_WORDS} words."
        )

    for pattern, flag in SENSITIVE_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            sensitive_flags.append(flag)

    if "crisis" in sensitive_flags:
        warnings.append(CRISIS_DISCLAIMER)

    has_signal = any(
        re.search(pat, cleaned, re.IGNORECASE) for pat in DECISION_SIGNALS
    )
    if not has_signal and word_count >= MIN_WORDS:
        warnings.append(
            "We couldn't detect a clear decision in your text. "
            "Try phrasing it as 'I'm deciding between X and Y' or 'Should I do X or Y?'"
        )

    multiple = _detect_multiple_decisions(cleaned)
    if multiple:
        warnings.append(
            "It looks like you might be describing more than one decision. "
            "For the best analysis, focus on your most pressing decision first."
        )

    return InputGuardResult(
        ok=len(issues) == 0,
        cleaned_text=cleaned,
        word_count=word_count,
        issues=issues,
        warnings=warnings,
        has_decision_signal=has_signal,
        sensitive_flags=sensitive_flags,
    )


def _clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\S ]+", " ", text)
    return text


def _detect_multiple_decisions(text: str) -> bool:
    separators = [
        r"\balso[,.]?\s+(i'?m|i am|should i|i need to)\s+decid",
        r"\bseparately\b.*\b(decid|choos)",
        r"\banother (decision|question|dilemma)\b",
        r"\bon top of (that|this)\b.*\b(decid|choos)",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in separators)

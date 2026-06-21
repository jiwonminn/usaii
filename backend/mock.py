"""Sample reasoning output for local dev when OpenAI quota/billing is unavailable."""

from __future__ import annotations

import re

from backend.extraction import DecisionExtraction
from backend.schemas import (
    ClaimWithUncertainty,
    PathAnalysis,
    ReasoningRequest,
    ReasoningResponse,
    TimedOutcome,
    VerificationItem,
)


def _outcome(summary: str, financial: str, career: str, personal: str, confidence: str) -> TimedOutcome:
    return TimedOutcome(
        summary=summary,
        financial_estimate=financial,
        career_impact=career,
        personal_impact=personal,
        confidence=confidence,  # type: ignore[arg-type]
        unknown_factors=["Mock data — replace with live LLM output"],
    )


def mock_filipino_nurse_response(request: ReasoningRequest) -> ReasoningResponse:
    what_if_note = None
    if request.what_if_assumption:
        what_if_note = (
            f"If '{request.what_if_assumption}' were true, the credential path becomes more viable "
            "and short-term financial pressure drops, but this is a projection — confirm timelines "
            "with CNO directly."
        )

    return ReasoningResponse(
        decision_summary=(
            "With 3 months savings and two young children, a Filipino RN in Toronto must balance "
            "immediate household income against long-term nursing licensure. Neither path is risk-free."
        ),
        core_decision="Take PSW work now vs pursue CNO nursing credential recognition first",
        paths=[
            PathAnalysis(
                name="Take PSW / healthcare aide job now",
                description="Start earning quickly in a related healthcare role while living costs continue.",
                outcomes={
                    "3_months": _outcome(
                        "Stable paycheck; savings pressure eases; less time for CNO paperwork/study.",
                        "Roughly $2,800–$3,400/month gross (Ontario PSW range, varies by employer)",
                        "Work experience in Canadian healthcare, but not as an RN",
                        "More predictable household stress; spouse still cannot work full-time while you cover childcare",
                        "medium",
                    ),
                    "1_year": _outcome(
                        "Financial runway improved; credential gap may widen if CNO prep stays on hold.",
                        "Household may break even or save modestly",
                        "PSW experience helps clinically but does not substitute for RN license",
                        "Risk of career inertia; two young children still limit study windows after shifts",
                        "medium",
                    ),
                    "3_years": _outcome(
                        "If CNO was deferred, total time-to-RN may be longer than starting now.",
                        "Lower lifetime earnings vs RN if license delayed multiple years",
                        "May need bridging programs later; path is not closed but cost rises",
                        "Family stability improved early; long-term career alignment uncertain",
                        "low",
                    ),
                },
                tradeoffs=[
                    "PSW evening shifts may leave no study window for CNO exams while caring for two young children",
                    "Lower entry barrier than RN roles, but ceiling stays below licensed nursing compensation",
                    "Shift work may conflict with childcare when spouse cannot work full-time yet",
                ],
                hidden_considerations=[
                    "Some employers offer tuition or scheduling support — worth asking before accepting",
                    "PSW hours may count toward experience narratives but not licensure requirements",
                ],
                what_you_give_up=[
                    "Fastest route to RN salary and scope of practice",
                    "Momentum on CNO documentation while credentials are fresh",
                ],
                verify_before_deciding=[
                    VerificationItem(
                        item="Confirm PSW wage, hours, and contract type",
                        official_source="Employer offer letter + Ontario employment standards",
                        confidence="high",
                    ),
                    VerificationItem(
                        item="Check whether current CNO application window deadlines apply to you",
                        official_source="https://www.cno.org/",
                        confidence="medium",
                        reason_uncertain="CNO timelines vary by assessment pathway",
                    ),
                ],
            ),
            PathAnalysis(
                name="Pursue CNO credential recognition first",
                description="Focus on documentation, exams, and bridging while surviving on limited savings.",
                outcomes={
                    "3_months": _outcome(
                        "High financial stress; progress depends on document readiness and assessment speed.",
                        "Savings may drop sharply; possible part-time work still needed",
                        "If assessment starts, clearer path to RN; if delayed, no income progress",
                        "High anxiety period for family with two dependents",
                        "low",
                    ),
                    "1_year": _outcome(
                        "Best case: partial registration or exam eligibility; worst case: still in assessment.",
                        "Short-term income gap; potential bridging program fees",
                        "RN pathway intact; nursing identity preserved",
                        "Stressful if savings exhausted before income restarts; spouse may need full-time work sooner",
                        "low",
                    ),
                    "3_years": _outcome(
                        "If licensed, earnings and career options likely exceed PSW path.",
                        "RN compensation typically higher long-term",
                        "Full scope RN practice in Ontario",
                        "Upfront sacrifice may pay off if licensure succeeds",
                        "medium",
                    ),
                },
                tradeoffs=[
                    "Credential recognition timeline is uncertain — savings may expire before spouse can increase work hours",
                    "Bridging program gaps could add tuition costs on top of zero income",
                    "Spouse's limited work capacity increases household vulnerability during assessment",
                ],
                hidden_considerations=[
                    "Credential recognition is not pass/fail only — gaps may require costly bridging courses",
                    "Starting CNO now preserves option to work PSW part-time in parallel",
                ],
                what_you_give_up=[
                    "Immediate full-time income stability",
                    "Psychological relief of 'any job now'",
                ],
                verify_before_deciding=[
                    VerificationItem(
                        item="Request your specific CNO assessment pathway and estimated timeline",
                        official_source="https://www.cno.org/en/become-a-nurse/apply/",
                        confidence="high",
                    ),
                    VerificationItem(
                        item="Identify bridging program costs and intakes if gaps are likely",
                        official_source="Ontario college/university program pages",
                        confidence="medium",
                    ),
                ],
            ),
            PathAnalysis(
                name="Part-time PSW + CNO prep",
                description="Earn partial income while submitting CNO documents and studying — only viable if hours are predictable.",
                outcomes={
                    "3_months": _outcome(
                        "Partial paycheck plus CNO paperwork underway; household still stretched.",
                        "Roughly $1,400–$1,800/month if part-time PSW hours are secured",
                        "Dual track keeps RN pathway active while maintaining some Canadian work history",
                        "Exhausting with two young children — spouse cannot work full-time yet to share load",
                        "medium",
                    ),
                    "1_year": _outcome(
                        "Best case: CNO assessment progressing with modest income; worst case: hours cut, savings gone.",
                        "Household may break even only if part-time hours stay fixed",
                        "RN pathway preserved if assessments advance; PSW hours do not substitute for licensure",
                        "Caregiver burnout risk if both credential prep and childcare fall on one parent",
                        "low",
                    ),
                    "3_years": _outcome(
                        "If licensed, RN earnings likely exceed PSW-only path; if stalled, years lost with no full RN salary.",
                        "RN range roughly $70k–$90k if successful; otherwise stuck between PSW wages and unfinished credentialing",
                        "Hybrid preserves nursing identity but delays full-scope practice",
                        "Family may have survived the crunch but at high relational and health cost",
                        "low",
                    ),
                },
                tradeoffs=[
                    "Part-time PSW only works if employer guarantees fixed hours — otherwise 3 months savings expires mid-prep",
                    "Studying for CNO exams after shifts is realistic only if spouse can cover two young children some evenings",
                    "Hybrid path avoids full income gap but extends total time-to-RN versus full-time credential focus",
                ],
                hidden_considerations=[
                    "Some employers rescind part-time offers if full-time coverage is needed — check contract language",
                    "Starting CNO now while working part-time preserves option to scale up PSW hours if savings run out",
                ],
                what_you_give_up=[
                    "Full-time income stability that a PSW-only path provides immediately",
                    "Focused study time that full-time CNO prep would allow without shift fatigue",
                ],
                verify_before_deciding=[
                    VerificationItem(
                        item="Confirm whether part-time PSW contract hours are guaranteed for 6+ months",
                        official_source="Employer offer letter + Ontario employment standards",
                        confidence="high",
                    ),
                    VerificationItem(
                        item="Ask CNO whether part-time work affects assessment timeline for your credentials",
                        official_source="https://www.cno.org/en/become-a-nurse/apply/",
                        confidence="medium",
                        reason_uncertain="Assessment speed depends on document completeness, not employment status",
                    ),
                ],
            ),
        ],
        cross_path_insights=[
            "With 3 months savings, a hybrid path only works if part-time hours are contractually fixed — otherwise savings expire before CNO intake",
            "A hybrid path (part-time PSW + CNO prep) is often realistic but exhausting with two young children",
            "Three months savings is the binding constraint — timeline uncertainty matters more than job title",
        ],
        questions_to_ask=[
            "Can this employer offer predictable hours that leave time for CNO study?",
            "What is my exact CNO application stage and next required document?",
            "Are there community programs helping internationally educated nurses in Toronto?",
        ],
        claims=[
            ClaimWithUncertainty(
                text="PSW roles can provide faster cash flow than waiting on CNO assessment alone",
                confidence="medium",
                unknown_factors=["Local job market demand", "Your language scores and references"],
                anchored_to="Ontario healthcare labour market norms",
            ),
            ClaimWithUncertainty(
                text="CNO recognition often takes many months and may require bridging",
                confidence="high",
                unknown_factors=[],
                anchored_to="https://www.cno.org/en/become-a-nurse/registration/registration-requirements/",
            ),
            ClaimWithUncertainty(
                text="Delaying licensure several years can reduce lifetime nursing earnings",
                confidence="low",
                unknown_factors=["Future policy changes", "Your ability to study while working"],
            ),
        ],
        global_uncertainty_flags=[
            "Exact CNO timeline for your credentials without a case review",
            "Whether spouse can increase work hours if savings run out",
        ],
        what_if_impact=what_if_note,
        extraction=DecisionExtraction(
            core_decision="Take PSW work now vs pursue CNO nursing credential recognition first",
            binding_constraint="3 months savings with 2 dependents",
            why_decision_is_hard="Immediate income pressure conflicts with a long uncertain credential path.",
            personal_constraints=["two young children", "spouse cannot work full-time yet"],
            paths_to_model=[
                "Take PSW / healthcare aide job now",
                "Pursue CNO credential recognition first",
                "Part-time PSW + CNO prep",
            ],
            values=["financial security", "career alignment", "family wellbeing"],
            domain="immigration / career credentialing",
            non_obvious_risk_signals=[
                "credential gap may require bridging courses",
                "savings may not cover rent past month 3",
            ],
        ),
    )


def _extract_path_options(text: str) -> list[str] | None:
    patterns = [
        r"(?:torn between|choosing between|decide between|either|between)\s+(.+?)\s+(?:or|and)\s+(.+?)(?:[.!?]|$)",
        r"(.+?)\s+vs\.?\s+(.+?)(?:[.!?]|$)",
        r"(.+?)\s+or\s+(.+?)(?:[.!?]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        a = " ".join(match.group(1).split()).strip()[:100]
        b = " ".join(match.group(2).split()).strip()[:100]
        if len(a) > 8 and len(b) > 8 and a.lower() != b.lower():
            return [a, b]
    return None


def _path_meta(option: str, index: int) -> tuple[str, str]:
    label = option[0].upper() + option[1:] if option else option
    if index == 0:
        return (
            label,
            f"This path means choosing {option.lower()} — usually eases immediate pressure first, "
            "but you may give up momentum on the other option you mentioned.",
        )
    return (
        label,
        f"This path means pursuing {option.lower()} — better long-term fit if it works out, "
        "but the upfront cost in time, money, or uncertainty is higher early on.",
    )


def _generic_mock_response(request: ReasoningRequest) -> ReasoningResponse:
    desc = request.user_description.strip()
    options = _extract_path_options(desc)
    default_names = ["The safer choice for now", "The bolder choice for later"]
    default_descriptions = [
        "Take the lower-risk option you're weighing — more predictable in the next few months, "
        "but you may feel you're postponing what you actually want.",
        "Commit to the higher-upside option you described — harder at the start, "
        "but potentially better aligned with where you want to be in a year or three.",
    ]

    path_specs: list[tuple[str, str]] = []
    if options:
        path_specs = [_path_meta(opt, i) for i, opt in enumerate(options)]
    else:
        path_specs = list(zip(default_names, default_descriptions, strict=True))

    paths: list[PathAnalysis] = []
    for i, (name, description) in enumerate(path_specs):
        option_label = options[i].lower() if options else name.lower()
        paths.append(
            PathAnalysis(
                name=name,
                description=description,
                outcomes={
                    "3_months": _outcome(
                        f"Early weeks on {option_label} — immediate tradeoffs start to show.",
                        "Depends on your specifics — connect live API for estimates",
                        "Varies with how this path plays out over time",
                        "Household and stress levels shift with whichever path you choose",
                        "low",
                    ),
                    "1_year": _outcome(
                        f"One year in on {option_label} — clearer signal, but not everything is settled.",
                        "Depends on your specifics — connect live API for estimates",
                        "Varies with how this path plays out over time",
                        "Household and stress levels shift with whichever path you choose",
                        "low",
                    ),
                    "3_years": _outcome(
                        "Three years on this path — best case looks stronger; worst case may mean pivoting again.",
                        "Depends on your specifics — connect live API for estimates",
                        "Varies with how this path plays out over time",
                        "Household and stress levels shift with whichever path you choose",
                        "low",
                    ),
                },
                tradeoffs=[
                    f"Time and money spent on {name.lower()} can't automatically be recovered if you switch later",
                    "Your household and relationships feel this choice differently at each stage",
                ],
                hidden_considerations=[
                    "Doors you close now may stay closed longer than you expect",
                    "A hybrid version of this path might still be possible — worth asking before committing",
                ],
                what_you_give_up=[
                    "Flexibility to pursue the other option at the same pace",
                    "Some peace of mind while uncertainty resolves",
                ],
                verify_before_deciding=[
                    VerificationItem(
                        item="Confirm timelines, costs, and requirements for this path",
                        official_source="https://www.canada.ca/",
                        confidence="low",
                    )
                ],
            )
        )

    path_names = [p.name for p in paths]
    ctx = request.structured_context
    structured_paths = ctx.paths_being_compared or path_names
    binding = (
        " · ".join(ctx.constraints)
        if ctx.constraints
        else "Your main limiting factor — connect live API for extraction"
    )
    personal = list(ctx.constraints) if ctx.constraints else []

    summary = (
        f"You're weighing {path_names[0]} against {path_names[1]} — neither is risk-free, "
        "and the right call depends on constraints the live engine would extract from your full description."
        if options
        else "You're facing a real tradeoff — connect the live API for path-specific reasoning tailored to your situation."
    )
    if ctx.constraints:
        summary = (
            f"With {binding} in play, you're weighing {path_names[0]} against {path_names[1]} — "
            "neither path removes the tradeoff entirely."
        )

    return ReasoningResponse(
        decision_summary=summary,
        core_decision=f"{path_names[0]} vs {path_names[1]}",
        paths=paths,
        cross_path_insights=[
            "Both paths change what feels urgent vs what feels possible in 3 months vs 3 years",
            "The binding constraint in your description matters more than which option sounds better on paper",
            "A hybrid or sequenced version of these paths may exist — worth checking before you decide",
        ],
        questions_to_ask=[
            "What is the exact deadline or runway I have before I must choose?",
            "What would each path cost me in time and money over the next 12 months?",
            "Who else is affected if I pick one path and it takes longer than expected?",
        ],
        claims=[
            ClaimWithUncertainty(
                text="Major life decisions rarely have a single correct answer — tradeoffs depend on your constraints",
                confidence="medium",
                unknown_factors=["Your exact runway", "Who else is affected by the choice"],
            ),
            ClaimWithUncertainty(
                text="Short-term relief and long-term alignment often pull in opposite directions",
                confidence="medium",
                unknown_factors=["Your risk tolerance", "Support available to you"],
            ),
            ClaimWithUncertainty(
                text="The first few months on either path rarely predict how year three feels",
                confidence="low",
                unknown_factors=["Market changes", "Personal circumstances shifting"],
            ),
        ],
        global_uncertainty_flags=[
            "Exact timelines and costs for your specific situation",
            "How people depending on you would be affected under each path",
        ],
        what_if_impact=(
            f"If '{request.what_if_assumption}' were true, timelines and confidence would shift — "
            "mock preview only; connect live API for real what-if reasoning."
            if request.what_if_assumption
            else None
        ),
        extraction=DecisionExtraction(
            core_decision=f"{path_names[0]} vs {path_names[1]}",
            binding_constraint=binding,
            why_decision_is_hard=(
                ctx.stakes
                or "Both options carry real costs; the tradeoff isn't obvious from a pros/cons list alone."
            ),
            personal_constraints=personal,
            paths_to_model=structured_paths,
            values=list(ctx.values),
            domain=ctx.domain or "decision support",
            non_obvious_risk_signals=[],
        ),
    )


def run_mock_reasoning_chain(request: ReasoningRequest) -> ReasoningResponse:
    """Return plausible structured output without calling OpenAI."""
    desc = request.user_description.lower()
    if "nurse" in desc or "cno" in desc or "psw" in desc:
        return mock_filipino_nurse_response(request)

    # Generic fallback for other scenarios during mock dev
    return _generic_mock_response(request)

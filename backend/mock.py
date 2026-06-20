"""Sample reasoning output for local dev when OpenAI quota/billing is unavailable."""

from __future__ import annotations

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


def run_mock_reasoning_chain(request: ReasoningRequest) -> ReasoningResponse:
    """Return plausible structured output without calling OpenAI."""
    desc = request.user_description.lower()
    if "nurse" in desc or "cno" in desc or "psw" in desc:
        return mock_filipino_nurse_response(request)

    # Generic fallback for other scenarios during mock dev
    return ReasoningResponse(
        decision_summary="Mock response for local development — enable billing for real AI reasoning.",
        core_decision="Paths extracted from user input (mock)",
        paths=[
            PathAnalysis(
                name="Path A",
                description="First option inferred from your description.",
                outcomes={
                    "3_months": _outcome("Short-term projection A", "TBD", "TBD", "TBD", "low"),
                    "1_year": _outcome("Medium-term projection A", "TBD", "TBD", "TBD", "low"),
                    "3_years": _outcome("Long-term projection A", "TBD", "TBD", "TBD", "low"),
                },
                tradeoffs=["Mock tradeoff — run with live API for real analysis"],
                hidden_considerations=["Replace mock mode before demo submission"],
                what_you_give_up=["Unknown in mock mode"],
                verify_before_deciding=[
                    VerificationItem(
                        item="Verify key assumptions with official sources",
                        official_source="Relevant government or institutional site",
                        confidence="low",
                    )
                ],
            ),
            PathAnalysis(
                name="Path B",
                description="Second option inferred from your description.",
                outcomes={
                    "3_months": _outcome("Short-term projection B", "TBD", "TBD", "TBD", "low"),
                    "1_year": _outcome("Medium-term projection B", "TBD", "TBD", "TBD", "low"),
                    "3_years": _outcome("Long-term projection B", "TBD", "TBD", "TBD", "low"),
                },
                tradeoffs=["Mock tradeoff — run with live API for real analysis"],
                hidden_considerations=["Replace mock mode before demo submission"],
                what_you_give_up=["Unknown in mock mode"],
            ),
        ],
        claims=[
            ClaimWithUncertainty(
                text="This output was generated in mock mode without calling OpenAI",
                confidence="high",
                unknown_factors=["All scenario-specific reasoning"],
            )
        ],
        global_uncertainty_flags=["Entire analysis is placeholder mock data"],
        what_if_impact=(
            f"Mock what-if: {request.what_if_assumption}" if request.what_if_assumption else None
        ),
        extraction=DecisionExtraction(
            core_decision="Paths extracted from user input (mock)",
            binding_constraint="Unknown — connect live API",
            why_decision_is_hard="Mock mode cannot extract real constraints from your description.",
            personal_constraints=[],
            paths_to_model=["Path A", "Path B"],
            values=[],
            domain="mock",
            non_obvious_risk_signals=["Replace mock mode before demo submission"],
        ),
    )

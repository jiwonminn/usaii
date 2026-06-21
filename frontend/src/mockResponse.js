// Mirrors backend/mock.py — mock_filipino_nurse_response
// Used so frontend dev/demo doesn't require the live API or OpenAI billing.

import { buildGenericMock } from "./buildGenericMock";

export const mockResponse = {
  decision_summary:
    "With 3 months savings and two young children, a Filipino RN in Toronto must balance immediate household income against long-term nursing licensure. Neither path is risk-free.",
  core_decision: "Take PSW work now vs pursue CNO nursing credential recognition first",
  paths: [
    {
      name: "Take PSW / healthcare aide job now",
      description:
        "Start earning quickly in a related healthcare role while living costs continue.",
      outcomes: {
        "3_months": {
          summary:
            "Stable paycheck; savings pressure eases; less time for CNO paperwork/study.",
          financial_estimate:
            "Roughly $2,800–$3,400/month gross (Ontario PSW range, varies by employer)",
          career_impact: "Work experience in Canadian healthcare, but not as an RN",
          personal_impact:
            "More predictable household stress; spouse still cannot work full-time while you cover childcare",
          confidence: "medium",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "1_year": {
          summary: "Financial runway improved; credential gap may widen if CNO prep stays on hold.",
          financial_estimate: "Household may break even or save modestly",
          career_impact: "PSW experience helps clinically but does not substitute for RN license",
          personal_impact:
            "Risk of career inertia; two young children still limit study windows after shifts",
          confidence: "medium",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "3_years": {
          summary: "If CNO was deferred, total time-to-RN may be longer than starting now.",
          financial_estimate: "Lower lifetime earnings vs RN if license delayed multiple years",
          career_impact: "May need bridging programs later; path is not closed but cost rises",
          personal_impact: "Family stability improved early; long-term career alignment uncertain",
          confidence: "low",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
      },
      tradeoffs: [
        "PSW evening shifts may leave no study window for CNO exams while caring for two young children",
        "Lower entry barrier than RN roles, but ceiling stays below licensed nursing compensation",
        "Shift work may conflict with childcare when spouse cannot work full-time yet",
      ],
      hidden_considerations: [
        "Some employers offer tuition or scheduling support — worth asking before accepting",
        "PSW hours may count toward experience narratives but not licensure requirements",
      ],
      what_you_give_up: [
        "Fastest route to RN salary and scope of practice",
        "Momentum on CNO documentation while credentials are fresh",
      ],
      verify_before_deciding: [
        {
          item: "Confirm PSW wage, hours, and contract type",
          official_source: "Employer offer letter + Ontario employment standards",
          confidence: "high",
        },
        {
          item: "Check whether current CNO application window deadlines apply to you",
          official_source: "https://www.cno.org/",
          confidence: "medium",
          reason_uncertain: "CNO timelines vary by assessment pathway",
        },
      ],
    },
    {
      name: "Pursue CNO credential recognition first",
      description:
        "Focus on documentation, exams, and bridging while surviving on limited savings.",
      outcomes: {
        "3_months": {
          summary:
            "High financial stress; progress depends on document readiness and assessment speed.",
          financial_estimate: "Savings may drop sharply; possible part-time work still needed",
          career_impact: "If assessment starts, clearer path to RN; if delayed, no income progress",
          personal_impact: "High anxiety period for family with two dependents",
          confidence: "low",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "1_year": {
          summary:
            "Best case: partial registration or exam eligibility; worst case: still in assessment.",
          financial_estimate: "Short-term income gap; potential bridging program fees",
          career_impact: "RN pathway intact; nursing identity preserved",
          personal_impact:
            "Stressful if savings exhausted before income restarts; spouse may need full-time work sooner",
          confidence: "low",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "3_years": {
          summary: "If licensed, earnings and career options likely exceed PSW path.",
          financial_estimate: "RN compensation typically higher long-term",
          career_impact: "Full scope RN practice in Ontario",
          personal_impact: "Upfront sacrifice may pay off if licensure succeeds",
          confidence: "medium",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
      },
      tradeoffs: [
        "Credential recognition timeline is uncertain — savings may expire before spouse can increase work hours",
        "Bridging program gaps could add tuition costs on top of zero income",
        "Spouse's limited work capacity increases household vulnerability during assessment",
      ],
      hidden_considerations: [
        "Credential recognition is not pass/fail only — gaps may require costly bridging courses",
        "Starting CNO now preserves option to work PSW part-time in parallel",
      ],
      what_you_give_up: [
        "Immediate full-time income stability",
        "Psychological relief of 'any job now'",
      ],
      verify_before_deciding: [
        {
          item: "Request your specific CNO assessment pathway and estimated timeline",
          official_source: "https://www.cno.org/en/become-a-nurse/apply/",
          confidence: "high",
        },
        {
          item: "Identify bridging program costs and intakes if gaps are likely",
          official_source: "Ontario college/university program pages",
          confidence: "medium",
        },
      ],
    },
    {
      name: "Part-time PSW + CNO prep",
      description:
        "Earn partial income while submitting CNO documents and studying — only viable if hours are predictable.",
      outcomes: {
        "3_months": {
          summary: "Partial paycheck plus CNO paperwork underway; household still stretched.",
          financial_estimate: "Roughly $1,400–$1,800/month if part-time PSW hours are secured",
          career_impact:
            "Dual track keeps RN pathway active while maintaining some Canadian work history",
          personal_impact:
            "Exhausting with two young children — spouse cannot work full-time yet to share load",
          confidence: "medium",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "1_year": {
          summary:
            "Best case: CNO assessment progressing with modest income; worst case: hours cut, savings gone.",
          financial_estimate: "Household may break even only if part-time hours stay fixed",
          career_impact:
            "RN pathway preserved if assessments advance; PSW hours do not substitute for licensure",
          personal_impact:
            "Caregiver burnout risk if both credential prep and childcare fall on one parent",
          confidence: "low",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
        "3_years": {
          summary:
            "If licensed, RN earnings likely exceed PSW-only path; if stalled, years lost with no full RN salary.",
          financial_estimate:
            "RN range roughly $70k–$90k if successful; otherwise stuck between PSW wages and unfinished credentialing",
          career_impact: "Hybrid preserves nursing identity but delays full-scope practice",
          personal_impact:
            "Family may have survived the crunch but at high relational and health cost",
          confidence: "low",
          unknown_factors: ["Mock data — replace with live LLM output"],
        },
      },
      tradeoffs: [
        "Part-time PSW only works if employer guarantees fixed hours — otherwise 3 months savings expires mid-prep",
        "Studying for CNO exams after shifts is realistic only if spouse can cover two young children some evenings",
        "Hybrid path avoids full income gap but extends total time-to-RN versus full-time credential focus",
      ],
      hidden_considerations: [
        "Some employers rescind part-time offers if full-time coverage is needed — check contract language",
        "Starting CNO now while working part-time preserves option to scale up PSW hours if savings run out",
      ],
      what_you_give_up: [
        "Full-time income stability that a PSW-only path provides immediately",
        "Focused study time that full-time CNO prep would allow without shift fatigue",
      ],
      verify_before_deciding: [
        {
          item: "Confirm whether part-time PSW contract hours are guaranteed for 6+ months",
          official_source: "Employer offer letter + Ontario employment standards",
          confidence: "high",
        },
        {
          item: "Ask CNO whether part-time work affects assessment timeline for your credentials",
          official_source: "https://www.cno.org/en/become-a-nurse/apply/",
          confidence: "medium",
          reason_uncertain:
            "Assessment speed depends on document completeness, not employment status",
        },
      ],
    },
  ],
  cross_path_insights: [
    "With 3 months savings, a hybrid path only works if part-time hours are contractually fixed — otherwise savings expire before CNO intake",
    "A hybrid path (part-time PSW + CNO prep) is often realistic but exhausting with two young children",
    "Three months savings is the binding constraint — timeline uncertainty matters more than job title",
  ],
  questions_to_ask: [
    "Can this employer offer predictable hours that leave time for CNO study?",
    "What is my exact CNO application stage and next required document?",
    "Are there community programs helping internationally educated nurses in Toronto?",
  ],
  claims: [
    {
      text: "PSW roles can provide faster cash flow than waiting on CNO assessment alone",
      confidence: "medium",
      unknown_factors: ["Local job market demand", "Your language scores and references"],
      anchored_to: "Ontario healthcare labour market norms",
    },
    {
      text: "CNO recognition often takes many months and may require bridging",
      confidence: "high",
      unknown_factors: [],
      anchored_to: "https://www.cno.org/en/become-a-nurse/registration/registration-requirements/",
    },
    {
      text: "Delaying licensure several years can reduce lifetime nursing earnings",
      confidence: "low",
      unknown_factors: ["Future policy changes", "Your ability to study while working"],
    },
  ],
  global_uncertainty_flags: [
    "Exact CNO timeline for your credentials without a case review",
    "Whether spouse can increase work hours if savings run out",
  ],
  what_if_impact: null,
  disclaimer:
    "This is a projection based on what you have shared — not a guarantee. Your situation may differ. Only you can make the final decision.",
  extraction: {
    core_decision: "Take PSW work now vs pursue CNO nursing credential recognition first",
    binding_constraint: "3 months savings with 2 dependents",
    why_decision_is_hard:
      "Immediate income pressure conflicts with a long uncertain credential path.",
    personal_constraints: ["two young children", "spouse cannot work full-time yet"],
    paths_to_model: [
      "Take PSW / healthcare aide job now",
      "Pursue CNO credential recognition first",
      "Part-time PSW + CNO prep",
    ],
    values: ["financial security", "career alignment", "family wellbeing"],
    domain: "immigration / career credentialing",
    non_obvious_risk_signals: [
      "credential gap may require bridging courses",
      "savings may not cover rent past month 3",
    ],
  },
};

// Legacy export — prefer buildGenericMock(userDescription) with the user's text.
export const genericMockResponse = buildGenericMock("");

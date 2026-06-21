/** Build a plausible mock response from free-text when live API is unavailable. */

const MOCK_OUTCOME = (summary) => ({
  summary,
  financial_estimate: "Depends on your specifics — connect live API for estimates",
  career_impact: "Varies with how this path plays out over time",
  personal_impact: "Household and stress levels shift with whichever path you choose",
  confidence: "low",
  unknown_factors: ["Mock data — run with live API for scenario-specific reasoning"],
});

function cleanOption(text) {
  return text
    .replace(/^["']|["']$/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 100);
}

function titleCaseOption(text) {
  const cleaned = cleanOption(text);
  if (!cleaned) return "";
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

export function extractPathOptions(text) {
  if (!text?.trim()) return null;

  const patterns = [
    /(?:torn between|choosing between|decide between|either|between)\s+(.+?)\s+(?:or|and)\s+(.+?)(?:[.!?]|$)/i,
    /(.+?)\s+vs\.?\s+(.+?)(?:[.!?]|$)/i,
    /(.+?)\s+or\s+(.+?)(?:[.!?]|$)/i,
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      const a = cleanOption(match[1]);
      const b = cleanOption(match[2]);
      if (a.length > 8 && b.length > 8 && a !== b) {
        return [a, b];
      }
    }
  }
  return null;
}

function summarizePath(optionText, index) {
  const label = titleCaseOption(optionText);
  if (index === 0) {
    return {
      name: label,
      description: `This path means choosing ${label.toLowerCase()} — usually eases immediate pressure first, but you may give up momentum on the other option you mentioned.`,
    };
  }
  return {
    name: label,
    description: `This path means pursuing ${label.toLowerCase()} — better long-term fit if it works out, but the upfront cost in time, money, or uncertainty is higher early on.`,
  };
}

const DEFAULT_PATHS = [
  {
    name: "The safer choice for now",
    description:
      "Take the lower-risk option you're weighing — more predictable in the next few months, but you may feel you're postponing what you actually want.",
  },
  {
    name: "The bolder choice for later",
    description:
      "Commit to the higher-upside option you described — harder at the start, but potentially better aligned with where you want to be in a year or three.",
  },
];

export function buildGenericMock(userDescription = "", structuredContext = {}) {
  const options = extractPathOptions(userDescription);
  const paths = (options ?? DEFAULT_PATHS.map((p) => p.name)).map((option, i) => {
    const meta = options
      ? summarizePath(option, i)
      : DEFAULT_PATHS[i];

    return {
      name: meta.name,
      description: meta.description,
      outcomes: {
        "3_months": MOCK_OUTCOME(
          options
            ? `Early weeks on "${titleCaseOption(option).toLowerCase()}" — immediate tradeoffs start to show.`
            : "Near-term effects of the safer path — pressure may ease, but second thoughts are common."
        ),
        "1_year": MOCK_OUTCOME(
          options
            ? `One year in on "${titleCaseOption(option).toLowerCase()}" — you'll know more, but some outcomes still won't be settled.`
            : "A year out — you'll have clearer signal on whether this path was worth the sacrifice."
        ),
        "3_years": MOCK_OUTCOME(
          options
            ? `Three years on this path — best case looks stronger; worst case may mean pivoting again.`
            : "Longer horizon — compounding effects matter more than the first few months felt."
        ),
      },
      tradeoffs: [
        `Time and money spent on ${meta.name.toLowerCase()} can't automatically be recovered if you switch later`,
        "Your household and relationships feel this choice differently at each stage",
      ],
      hidden_considerations: [
        "Doors you close now may stay closed longer than you expect",
        "A hybrid version of this path might still be possible — worth asking before committing",
      ],
      what_you_give_up: [
        "Flexibility to pursue the other option at the same pace",
        "Some peace of mind while uncertainty resolves",
      ],
      verify_before_deciding: [
        {
          item: "Confirm timelines, costs, and requirements for this path",
          official_source: "https://www.canada.ca/",
          confidence: "low",
        },
      ],
    };
  });

  const pathNames = paths.map((p) => p.name);
  const binding =
    structuredContext.constraints?.length > 0
      ? structuredContext.constraints.join(" · ")
      : "Your main limiting factor — extracted with live API";

  return {
    decision_summary: structuredContext.constraints?.length
      ? `With ${binding} in play, you're weighing ${pathNames[0]} against ${pathNames[1]} — neither path removes the tradeoff entirely.`
      : options
      ? `You're weighing ${pathNames[0]} against ${pathNames[1]} — neither is risk-free, and the right call depends on the constraints you described.`
      : "You're facing a meaningful tradeoff between two directions — each path changes what the next 3 months, 1 year, and 3 years could look like.",
    core_decision: options ? `${pathNames[0]} vs ${pathNames[1]}` : "Two paths under consideration",
    paths,
    cross_path_insights: [
      "Both paths change what feels urgent vs what feels possible in 3 months vs 3 years",
      "The binding constraint in your description matters more than which option sounds better on paper",
      "A hybrid or sequenced version of these paths may exist — worth checking before you decide",
    ],
    questions_to_ask: [
      "What is the exact deadline or runway I have before I must choose?",
      "What would each path cost me in time and money over the next 12 months?",
      "Who else is affected if I pick one path and it takes longer than expected?",
    ],
    claims: [
      {
        text: "Major life decisions rarely have a single correct answer — tradeoffs depend on your constraints",
        confidence: "medium",
        unknown_factors: ["Your exact runway", "Who else is affected by the choice"],
        anchored_to: null,
      },
      {
        text: "Short-term relief and long-term alignment often pull in opposite directions",
        confidence: "medium",
        unknown_factors: ["Your risk tolerance", "Support available to you"],
        anchored_to: null,
      },
      {
        text: "The first few months on either path rarely predict how year three feels",
        confidence: "low",
        unknown_factors: ["Market changes", "Personal circumstances shifting"],
        anchored_to: null,
      },
    ],
    global_uncertainty_flags: [
      "Exact timelines and costs for your specific situation",
      "How people depending on you would be affected under each path",
    ],
    what_if_impact: null,
    disclaimer:
      "This is a projection based on what you have shared — not a guarantee. Your situation may differ. Only you can make the final decision.",
    extraction: {
      core_decision: options ? `${pathNames[0]} vs ${pathNames[1]}` : "Two paths under consideration",
      binding_constraint: binding,
      why_decision_is_hard:
        structuredContext.stakes ||
        "Both options carry real costs; the tradeoff isn't obvious from a pros/cons list alone.",
      personal_constraints: structuredContext.constraints ?? [],
      paths_to_model: structuredContext.paths_being_compared?.length
        ? structuredContext.paths_being_compared
        : pathNames,
      values: structuredContext.values ?? [],
      domain: structuredContext.domain || "decision support",
      non_obvious_risk_signals: [],
    },
  };
}

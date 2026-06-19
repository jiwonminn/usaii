/**
 * Renders the extracted decision context as small cards.
 * Uses Phase 1 `extraction` from the API when present; falls back to
 * heuristics over the final response for mock/offline mode.
 */
export default function ContextCards({ response }) {
  if (!response) return null;

  const ext = response.extraction;
  const { core_decision, paths } = response;

  const cards = [
    (ext?.core_decision || core_decision) && {
      label: "The decision",
      value: ext?.core_decision || core_decision,
    },
    (paths?.length || ext?.paths_to_model?.length) && {
      label: "Paths being compared",
      value: (paths || [])
        .map((p) => p.name)
        .join("  vs.  ") || ext?.paths_to_model?.join("  vs.  "),
    },
    ext?.binding_constraint && {
      label: "What's limiting your options",
      value: ext.binding_constraint,
    },
    ext?.personal_constraints?.length > 0 && {
      label: "Personal constraints",
      value: ext.personal_constraints.join(" · "),
    },
    ext?.why_decision_is_hard && {
      label: "Why this is hard",
      value: ext.why_decision_is_hard,
    },
    !ext && extractConstraintsFallback(response) && {
      label: "What's limiting your options",
      value: extractConstraintsFallback(response),
    },
    !ext?.why_decision_is_hard && extractTimelineFallback(response) && {
      label: "Timeline pressure",
      value: extractTimelineFallback(response),
    },
  ].filter(Boolean);

  if (!cards.length) return null;

  return (
    <div className="context-cards" role="list" aria-label="Extracted decision context">
      {cards.map((card, i) => (
        <div className="context-card" role="listitem" key={i}>
          <div className="context-card__label">{card.label}</div>
          <div className="context-card__value">{card.value}</div>
        </div>
      ))}
    </div>
  );
}

function extractConstraintsFallback(response) {
  const flags = response.global_uncertainty_flags || [];
  const lowConfidenceClaim = (response.claims || []).find((c) => c.confidence === "low");
  if (flags.length) return flags[0];
  if (lowConfidenceClaim) return lowConfidenceClaim.text;
  return null;
}

function extractTimelineFallback(response) {
  for (const path of response.paths || []) {
    const item = (path.verify_before_deciding || []).find((v) =>
      /timeline|deadline|window/i.test(v.item)
    );
    if (item) return item.item;
  }
  return null;
}

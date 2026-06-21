/**
 * Renders the extracted decision context as small cards.
 * Uses Phase 1 `extraction` from the API when present; falls back to
 * heuristics over the final response for mock/offline mode.
 */
export default function ContextCards({ response, structuredContext }) {
  if (!response) return null;

  const ext = response.extraction;
  const ctx = structuredContext ?? {};
  const { core_decision, paths } = response;

  const bindingConstraint =
    ext?.binding_constraint ||
    (ctx.constraints?.length ? ctx.constraints.join(" · ") : null);
  const personalConstraints =
    ext?.personal_constraints?.length > 0
      ? ext.personal_constraints
      : ctx.constraints ?? [];
  const pathsCompared =
    (paths || []).map((p) => p.name).join("  vs.  ") ||
    ext?.paths_to_model?.join("  vs.  ") ||
    ctx.paths_being_compared?.join("  vs.  ");

  const cards = [
    (ext?.core_decision || core_decision) && {
      label: "The decision",
      value: ext?.core_decision || core_decision,
    },
    pathsCompared && {
      label: "Paths being compared",
      value: pathsCompared,
    },
    bindingConstraint && {
      label: "What's limiting your options",
      value: bindingConstraint,
    },
    personalConstraints.length > 0 && {
      label: "Personal constraints",
      value: personalConstraints.join(" · "),
    },
    (ext?.why_decision_is_hard || ctx.stakes) && {
      label: ext?.why_decision_is_hard ? "Why this is hard" : "What's at stake",
      value: ext?.why_decision_is_hard || ctx.stakes,
    },
    (ctx.timeline_pressure || extractTimelineFallback(response)) && {
      label: "Timeline pressure",
      value: ctx.timeline_pressure || extractTimelineFallback(response),
    },
    ctx.values?.length > 0 && {
      label: "Values that matter",
      value: ctx.values.join(" · "),
    },
    !ext && !bindingConstraint && extractConstraintsFallback(response) && {
      label: "What's limiting your options",
      value: extractConstraintsFallback(response),
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

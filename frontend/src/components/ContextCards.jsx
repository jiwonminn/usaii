/**
 * Renders the extracted decision context as small cards.
 * Adapts to whatever the backend extracts — never assumes the
 * Filipino nurse scenario specifically. If a field is empty/missing,
 * that card is simply not rendered.
 */
export default function ContextCards({ response }) {
  if (!response) return null;

  const { core_decision, paths, claims } = response;

  const constraints = extractConstraints(response);
  const timelinePressure = extractTimelinePressure(response);

  const cards = [
    core_decision && { label: "The decision", value: core_decision },
    paths?.length && {
      label: "Paths being compared",
      value: paths.map((p) => p.name).join("  vs.  "),
    },
    constraints && { label: "What's limiting your options", value: constraints },
    timelinePressure && { label: "Timeline pressure", value: timelinePressure },
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

function extractConstraints(response) {
  const flags = response.global_uncertainty_flags || [];
  const lowConfidenceClaim = (response.claims || []).find((c) => c.confidence === "low");
  if (flags.length) return flags[0];
  if (lowConfidenceClaim) return lowConfidenceClaim.text;
  return null;
}

function extractTimelinePressure(response) {
  // Look for a verify_before_deciding item across paths that mentions a timeline
  for (const path of response.paths || []) {
    const item = (path.verify_before_deciding || []).find((v) =>
      /timeline|deadline|window/i.test(v.item)
    );
    if (item) return item.item;
  }
  return null;
}

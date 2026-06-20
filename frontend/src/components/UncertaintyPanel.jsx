import { useState } from "react";

const CONFIDENCE_CONFIG = {
  high:   { label: "High confidence",   color: "var(--teal)" },
  medium: { label: "Medium confidence", color: "var(--clay)" },
  low:    { label: "Low confidence",    color: "var(--signal-low)" },
};

export default function UncertaintyPanel({ response }) {
  if (!response) return null;

  const claims = response.claims ?? [];
  const flags  = response.global_uncertainty_flags ?? [];

  if (!claims.length && !flags.length) return null;

  return (
    <section className="uncertainty-panel" aria-label="Analysis confidence and uncertainty">
      {claims.length > 0 && (
        <div className="uncertainty-panel__section">
          <h4 className="uncertainty-panel__heading">How confident is this analysis?</h4>
          <p className="uncertainty-panel__sub">
            Each assertion the AI made — rated by what it can and can't know.
          </p>
          <div className="claim-list">
            {claims.map((claim, i) => (
              <ClaimCard key={i} claim={claim} />
            ))}
          </div>
        </div>
      )}

      {flags.length > 0 && (
        <div className="uncertainty-panel__section">
          <h4 className="uncertainty-panel__heading">What this AI cannot know</h4>
          <ul
            className="uncertainty-flags"
            aria-label="Things the AI cannot determine about your situation"
          >
            {flags.map((flag, i) => (
              <li key={i} className="uncertainty-flag">
                <span className="uncertainty-flag__icon" aria-hidden="true" />
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function ClaimCard({ claim }) {
  const [expanded, setExpanded] = useState(false);
  const config    = CONFIDENCE_CONFIG[claim.confidence] ?? CONFIDENCE_CONFIG.medium;
  const hasFactors = claim.unknown_factors?.length > 0;
  const canExpand  = hasFactors && claim.confidence !== "high";
  const factorCount = claim.unknown_factors?.length ?? 0;

  return (
    <div className={`claim-card claim-card--${claim.confidence}`}>
      <div className="claim-card__row">
        <div
          className="claim-card__bar"
          style={{ backgroundColor: config.color }}
          aria-hidden="true"
        />
        <div className="claim-card__body">
          <p className="claim-card__text">{claim.text}</p>
          {claim.anchored_to && (
            <span className="claim-card__anchor">Source: {claim.anchored_to}</span>
          )}
        </div>
        <span
          className="claim-card__badge"
          style={{ color: config.color, borderColor: config.color }}
        >
          {config.label}
        </span>
      </div>

      {canExpand && (
        <button
          type="button"
          className="claim-card__toggle"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? "Hide" : "What's uncertain"}
          {" "}({factorCount} factor{factorCount !== 1 ? "s" : ""})
        </button>
      )}

      {expanded && hasFactors && (
        <ul className="claim-card__factors">
          {claim.unknown_factors.map((f, i) => (
            <li key={i}>{f}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

const CONFIDENCE_STYLE = {
  high: { dasharray: "none", label: "High confidence" },
  medium: { dasharray: "4 3", label: "Medium confidence" },
  low: { dasharray: "1.5 4", label: "Low confidence" },
};

/**
 * A vertical thread that runs through a path's timeline.
 * Line texture communicates honesty about uncertainty:
 * solid = high confidence, dashed = medium, dotted/sparse = low.
 * This is the signature element — it makes "honest uncertainty"
 * visible rather than just a label on each claim.
 */
export default function ConfidenceThread({ confidence, accentVar }) {
  const style = CONFIDENCE_STYLE[confidence] || CONFIDENCE_STYLE.medium;

  return (
    <div className="confidence-thread" aria-hidden="true">
      <svg width="2" height="100%" style={{ display: "block", height: "100%", minHeight: 64 }}>
        <line
          x1="1"
          y1="0"
          x2="1"
          y2="100%"
          stroke={`var(${accentVar})`}
          strokeWidth="2"
          strokeDasharray={style.dasharray}
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

export { CONFIDENCE_STYLE };

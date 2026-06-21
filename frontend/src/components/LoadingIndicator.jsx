import { useEffect, useState } from "react";

const DEFAULT_MESSAGES = [
  "Reading your situation…",
  "Finding what's limiting your options…",
  "Modeling paths at 3 months, 1 year, and 3 years…",
  "Surfacing non-obvious tradeoffs…",
  "Checking confidence and uncertainty…",
];

export default function LoadingIndicator({
  messages = DEFAULT_MESSAGES,
  message = null,
  extractionPreview = null,
  intervalMs = 8000,
  className = "",
}) {
  const [index, setIndex] = useState(0);
  const useRotation = !message && messages.length > 1;

  useEffect(() => {
    if (!useRotation) return undefined;
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, intervalMs);
    return () => clearInterval(timer);
  }, [messages, intervalMs, useRotation]);

  const displayMessage = message ?? messages[index];

  return (
    <div className={`loading-indicator ${className}`.trim()} role="status" aria-live="polite">
      <span className="loading-indicator__pulse" aria-hidden="true" />
      <p className="loading-indicator__message">{displayMessage}</p>
      {extractionPreview && (
        <div className="loading-indicator__preview">
          {extractionPreview.core_decision && (
            <p>
              <strong>Decision:</strong> {extractionPreview.core_decision}
            </p>
          )}
          {extractionPreview.binding_constraint && (
            <p>
              <strong>Limiting factor:</strong> {extractionPreview.binding_constraint}
            </p>
          )}
          {extractionPreview.paths_to_model?.length > 0 && (
            <p>
              <strong>Paths:</strong> {extractionPreview.paths_to_model.join(" vs. ")}
            </p>
          )}
        </div>
      )}
      <p className="loading-indicator__hint">This usually takes about a minute.</p>
    </div>
  );
}

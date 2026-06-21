import { useState } from "react";
import LoadingIndicator from "./LoadingIndicator";

const PROMPTS = [
  "Type out all your concerns — I'm torn between taking a PSW job now or waiting for my nursing credentials to transfer...",
  "Share the areas where you need help — I got into law school but also have a full-time bank offer and $40k in debt...",
  "Tell us what's weighing on you — my partner wants to move cities for a job but I'd lose my network and they'd need to find work too...",
];

const EMPTY_STRUCTURED = {
  paths: "",
  constraints: "",
  timeline: "",
  stakes: "",
  values: "",
  domain: "",
};

function parseList(text) {
  if (!text?.trim()) return [];
  return text
    .split(/[\n,]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function buildStructuredContext(fields) {
  const paths = parseList(fields.paths);
  const constraints = parseList(fields.constraints);
  const values = parseList(fields.values);

  const context = {};
  if (paths.length) context.paths_being_compared = paths;
  if (constraints.length) context.constraints = constraints;
  if (fields.timeline.trim()) context.timeline_pressure = fields.timeline.trim();
  if (fields.stakes.trim()) context.stakes = fields.stakes.trim();
  if (values.length) context.values = values;
  if (fields.domain.trim()) context.domain = fields.domain.trim();

  return context;
}

export default function IntakeForm({
  onSubmit,
  isLoading,
  loadingMessage = null,
  loadingExtraction = null,
}) {
  const [text, setText] = useState("");
  const [structured, setStructured] = useState(EMPTY_STRUCTURED);
  const [showDetails, setShowDetails] = useState(false);
  const [placeholderIndex] = useState(() => Math.floor(Math.random() * PROMPTS.length));

  function handleStructuredChange(field, value) {
    setStructured((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim() || isLoading) return;
    onSubmit({
      userDescription: text.trim(),
      structuredContext: buildStructuredContext(structured),
    });
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  return (
    <section className="intake">
      <h1 className="intake__title">What are you trying to decide?</h1>
      <p className="intake__sub">
        Type out all your concerns and the areas where you need help — the way you'd
        vent to a friend who actually gets it. What's at stake, what's pulling you
        each way, and what's limiting you (money, time, family, deadlines, fear of
        picking wrong).
      </p>

      <form onSubmit={handleSubmit} className="intake__form">
        {isLoading ? (
          <LoadingIndicator
            className="intake__loading"
            message={loadingMessage}
            extractionPreview={loadingExtraction}
          />
        ) : (
          <>
            <textarea
              className="intake__textarea"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={PROMPTS[placeholderIndex]}
              rows={7}
              disabled={isLoading}
              aria-label="Describe your decision"
            />

            <div className="intake__details">
              <button
                type="button"
                className="intake__details-toggle"
                onClick={() => setShowDetails((v) => !v)}
                aria-expanded={showDetails}
              >
                {showDetails ? "Hide optional details" : "Add optional details (paths, constraints, timeline)"}
              </button>

              {showDetails && (
                <div className="intake__details-fields">
                  <label className="intake__field">
                    <span>Paths you're comparing</span>
                    <textarea
                      value={structured.paths}
                      onChange={(e) => handleStructuredChange("paths", e.target.value)}
                      placeholder="One per line, e.g. Take PSW job now / Wait for nursing credentials"
                      rows={2}
                      disabled={isLoading}
                    />
                  </label>
                  <label className="intake__field">
                    <span>Constraints</span>
                    <textarea
                      value={structured.constraints}
                      onChange={(e) => handleStructuredChange("constraints", e.target.value)}
                      placeholder="3 months savings · two young kids · spouse can't work full-time yet"
                      rows={2}
                      disabled={isLoading}
                    />
                  </label>
                  <div className="intake__field-row">
                    <label className="intake__field">
                      <span>Timeline pressure</span>
                      <input
                        type="text"
                        value={structured.timeline}
                        onChange={(e) => handleStructuredChange("timeline", e.target.value)}
                        placeholder="e.g. Offer expires in 2 weeks"
                        disabled={isLoading}
                      />
                    </label>
                    <label className="intake__field">
                      <span>What's at stake</span>
                      <input
                        type="text"
                        value={structured.stakes}
                        onChange={(e) => handleStructuredChange("stakes", e.target.value)}
                        placeholder="e.g. Family stability, career ceiling"
                        disabled={isLoading}
                      />
                    </label>
                  </div>
                  <label className="intake__field">
                    <span>Values that matter</span>
                    <textarea
                      value={structured.values}
                      onChange={(e) => handleStructuredChange("values", e.target.value)}
                      placeholder="Financial security, being present for kids, long-term career growth"
                      rows={2}
                      disabled={isLoading}
                    />
                  </label>
                </div>
              )}
            </div>

            <div className="intake__footer">
              <span className="intake__count">{wordCount} words</span>
              <button
                type="submit"
                className="intake__submit"
                disabled={!text.trim() || isLoading}
              >
                Map my paths
              </button>
            </div>
          </>
        )}
      </form>
    </section>
  );
}

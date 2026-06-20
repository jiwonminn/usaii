import { useState } from "react";
import { runReasoning } from "../api";

const TIME_LABELS = {
  "3_months": "3 months",
  "1_year":   "1 year",
  "3_years":  "3 years",
};

export default function WhatIfExplorer({ originalResponse, userDescription }) {
  const [inputValue,    setInputValue]    = useState("");
  const [whatIfResult,  setWhatIfResult]  = useState(null);
  const [isLoading,     setIsLoading]     = useState(false);
  const [error,         setError]         = useState(null);

  const claims = originalResponse?.claims ?? [];

  function selectClaim(text) {
    setInputValue(text);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const assumption = inputValue.trim();
    if (!assumption || isLoading) return;

    setIsLoading(true);
    setError(null);
    setWhatIfResult(null);

    try {
      const result = await runReasoning({
        userDescription,
        whatIfAssumption: assumption,
      });
      setWhatIfResult(result);
    } catch (err) {
      const msg = (err?.message ?? "").toLowerCase();
      if (msg.includes("429") || msg.includes("quota")) {
        setError(
          "API quota reached — add billing at platform.openai.com, or set VITE_FORCE_MOCK=true for offline dev."
        );
      } else {
        setError("What-if analysis failed. Check the API connection and try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  function handleClear() {
    setWhatIfResult(null);
    setError(null);
    setInputValue("");
  }

  return (
    <section className="what-if-explorer" aria-label="What-if explorer">
      <header className="what-if-explorer__header">
        <h3 className="what-if-explorer__title">Challenge an assumption</h3>
        <p className="what-if-explorer__sub">
          Pick one of the AI's claims below, or type your own. The engine will re-run
          the analysis with that assumption changed and show you how the paths shift.
        </p>
      </header>

      {claims.length > 0 && (
        <div
          className="what-if-chips"
          role="group"
          aria-label="AI claims you can challenge"
        >
          {claims.map((claim, i) => (
            <button
              key={i}
              type="button"
              className={`what-if-chip${inputValue === claim.text ? " what-if-chip--active" : ""}`}
              onClick={() => selectClaim(claim.text)}
            >
              {claim.text}
            </button>
          ))}
        </div>
      )}

      <form className="what-if-form" onSubmit={handleSubmit}>
        <textarea
          className="what-if-form__textarea"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder='e.g. "CNO process completes in 4 months instead of 12"'
          rows={3}
          disabled={isLoading}
          aria-label="What-if assumption"
        />
        <div className="what-if-form__footer">
          {whatIfResult && (
            <button type="button" className="what-if-form__clear" onClick={handleClear}>
              Clear
            </button>
          )}
          <button
            type="submit"
            className="what-if-form__submit"
            disabled={!inputValue.trim() || isLoading}
          >
            {isLoading ? "Re-running analysis…" : "What if this changed?"}
          </button>
        </div>
      </form>

      {error && (
        <p className="what-if-explorer__error" role="alert">
          {error}
        </p>
      )}

      {whatIfResult && (
        <WhatIfResult
          original={originalResponse}
          result={whatIfResult}
          assumption={inputValue.trim()}
        />
      )}
    </section>
  );
}

function WhatIfResult({ original, result, assumption }) {
  const summaryShifted =
    result.decision_summary && result.decision_summary !== original.decision_summary;

  return (
    <div className="what-if-result">
      <div className="what-if-result__banner">
        <span className="what-if-result__banner-label">What if</span>
        <p className="what-if-result__banner-text">"{assumption}"</p>
      </div>

      {result.what_if_impact && (
        <p className="what-if-result__impact">{result.what_if_impact}</p>
      )}

      {summaryShifted && (
        <div className="what-if-result__framing">
          <span className="what-if-result__framing-label">How the framing shifted</span>
          <p>{result.decision_summary}</p>
        </div>
      )}

      {result.paths?.length > 0 && (
        <>
          <p className="what-if-result__paths-heading">Outcomes under this assumption</p>
          <div className="what-if-result__paths">
            {result.paths.map((path, i) => (
              <div key={i} className="what-if-path-card">
                <h4 className="what-if-path-card__name">{path.name}</h4>
                <div className="what-if-path-card__outcomes">
                  {Object.entries(path.outcomes ?? {}).map(([key, outcome]) => (
                    <div key={key} className="what-if-outcome-row">
                      <span className="what-if-outcome-row__time">
                        {TIME_LABELS[key] ?? key}
                      </span>
                      <p className="what-if-outcome-row__summary">{outcome.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

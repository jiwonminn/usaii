import ConfidenceThread, { CONFIDENCE_STYLE } from "./ConfidenceThread";

const TIME_LABELS = {
  "3_months": "3 months",
  "1_year": "1 year",
  "3_years": "3 years",
};

export default function PathColumn({ path, accentVar, index }) {
  return (
    <article className="path-column" style={{ "--path-accent": `var(${accentVar})` }}>
      <header className="path-column__header">
        <span className="path-column__index">Path {index + 1}</span>
        <h3 className="path-column__name">{path.name}</h3>
        <p className="path-column__desc">{path.description}</p>
      </header>

      <div className="path-column__timeline">
        {Object.entries(path.outcomes || {}).map(([key, outcome]) => (
          <div className="timeline-row" key={key}>
            <ConfidenceThread confidence={outcome.confidence} accentVar={accentVar} />
            <div className="timeline-row__content">
              <div className="timeline-row__time">{TIME_LABELS[key] || key}</div>
              <p className="timeline-row__summary">{outcome.summary}</p>
              <dl className="timeline-row__details">
                {outcome.financial_estimate && (
                  <>
                    <dt>Financial</dt>
                    <dd>{outcome.financial_estimate}</dd>
                  </>
                )}
                {outcome.career_impact && (
                  <>
                    <dt>Career</dt>
                    <dd>{outcome.career_impact}</dd>
                  </>
                )}
                {outcome.personal_impact && (
                  <>
                    <dt>Personal</dt>
                    <dd>{outcome.personal_impact}</dd>
                  </>
                )}
              </dl>
              <span
                className="confidence-label"
                style={{ color: `var(${accentVar})` }}
                title={CONFIDENCE_STYLE[outcome.confidence]?.label}
              >
                {CONFIDENCE_STYLE[outcome.confidence]?.label || "Medium confidence"}
              </span>
              {outcome.confidence !== "high" && outcome.unknown_factors?.length > 0 && (
                <ul className="timeline-row__unknowns" aria-label="What could change this projection">
                  {outcome.unknown_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
      </div>

      {path.tradeoffs?.length > 0 && (
        <section className="path-column__section">
          <h4>Key tradeoffs</h4>
          <ul>
            {path.tradeoffs.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>
      )}

      {path.hidden_considerations?.length > 0 && (
        <section className="path-column__section">
          <h4>What's easy to miss</h4>
          <ul>
            {path.hidden_considerations.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>
      )}

      {path.what_you_give_up?.length > 0 && (
        <section className="path-column__section">
          <h4>What you'd give up</h4>
          <ul>
            {path.what_you_give_up.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>
      )}

      {path.verify_before_deciding?.length > 0 && (
        <section className="path-column__section path-column__verify">
          <h4>Verify before deciding</h4>
          <ul>
            {path.verify_before_deciding.map((v, i) => (
              <li key={i}>
                <span>{v.item}</span>
                {v.official_source &&
                  (v.official_source.startsWith("http") ? (
                    <a
                      href={v.official_source}
                      target="_blank"
                      rel="noreferrer"
                      className="verify-source"
                    >
                      {v.official_source}
                    </a>
                  ) : (
                    <span className="verify-source verify-source--text">{v.official_source}</span>
                  ))}
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}

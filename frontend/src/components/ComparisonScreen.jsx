import ContextCards from "./ContextCards";
import PathColumn from "./PathColumn";

const ACCENTS = ["--clay", "--teal", "--signal-low"];

export default function ComparisonScreen({ response, onReset, structuredContext, children }) {
  if (!response) return null;

  const { decision_summary, paths, cross_path_insights, questions_to_ask, disclaimer, what_if_impact } =
    response;

  return (
    <section className="comparison">
      <button className="comparison__back" onClick={onReset}>
        ← Describe a different decision
      </button>

      <p className="comparison__summary">{decision_summary}</p>

      <ContextCards response={response} structuredContext={structuredContext} />

      {what_if_impact && (
        <div className="what-if-banner">
          <span className="what-if-banner__label">What if</span>
          {what_if_impact}
        </div>
      )}

      <div className="comparison__paths" style={{ "--path-count": paths?.length || 2 }}>
        {paths?.map((path, i) => (
          <PathColumn key={i} path={path} accentVar={ACCENTS[i % ACCENTS.length]} index={i} />
        ))}
      </div>

      {children}

      {cross_path_insights?.length > 0 && (
        <section className="cross-insights">
          <h4>Worth noticing across paths</h4>
          <ul>
            {cross_path_insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>
        </section>
      )}

      {questions_to_ask?.length > 0 && (
        <section className="ask-questions">
          <h4>Questions worth asking before you decide</h4>
          <ul>
            {questions_to_ask.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </section>
      )}

      <p className="disclaimer">{disclaimer}</p>
    </section>
  );
}

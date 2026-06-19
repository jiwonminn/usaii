import { useState } from "react";
import IntakeForm from "./components/IntakeForm";
import ComparisonScreen from "./components/ComparisonScreen";
import { runReasoning } from "./api";
import "./App.css";

export default function App() {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(userDescription) {
    setIsLoading(true);
    setError(null);
    try {
      const result = await runReasoning({ userDescription });
      setResponse(result);
    } catch (err) {
      setError("Something went wrong mapping your decision. Try describing it again.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setResponse(null);
    setError(null);
  }

  return (
    <main className="app">
      <div className="app__inner">
        {!response ? (
          <IntakeForm onSubmit={handleSubmit} isLoading={isLoading} />
        ) : (
          <ComparisonScreen response={response} onReset={handleReset} />
        )}
        {error && <p className="app__error">{error}</p>}
      </div>
    </main>
  );
}

import { useState } from "react";
import IntakeForm from "./components/IntakeForm";
import ComparisonScreen from "./components/ComparisonScreen";
import UncertaintyPanel from "./components/UncertaintyPanel";
import WhatIfExplorer from "./components/WhatIfExplorer";
import { runReasoning } from "./api";
import "./App.css";

export default function App() {
  const [response,        setResponse]        = useState(null);
  const [userDescription, setUserDescription] = useState("");
  const [isLoading,       setIsLoading]       = useState(false);
  const [error,           setError]           = useState(null);

  async function handleSubmit(desc) {
    setIsLoading(true);
    setError(null);
    try {
      const result = await runReasoning({ userDescription: desc });
      setResponse(result);
      setUserDescription(desc);
    } catch (err) {
      setError("Something went wrong mapping your decision. Try describing it again.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setResponse(null);
    setUserDescription("");
    setError(null);
  }

  return (
    <main className="app">
      <div className="app__inner">
        {!response ? (
          <IntakeForm onSubmit={handleSubmit} isLoading={isLoading} />
        ) : (
          <ComparisonScreen response={response} onReset={handleReset}>
            <UncertaintyPanel response={response} />
            <WhatIfExplorer
              originalResponse={response}
              userDescription={userDescription}
            />
          </ComparisonScreen>
        )}
        {error && <p className="app__error">{error}</p>}
      </div>
    </main>
  );
}

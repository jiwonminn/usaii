import { useState } from "react";
import IntakeForm from "./components/IntakeForm";
import ComparisonScreen from "./components/ComparisonScreen";
import UncertaintyPanel from "./components/UncertaintyPanel";
import WhatIfExplorer from "./components/WhatIfExplorer";
import DataSourceBanner from "./components/DataSourceBanner";
import { runReasoning } from "./api";
import "./App.css";

export default function App() {
  const [response, setResponse] = useState(null);
  const [userDescription, setUserDescription] = useState("");
  const [structuredContext, setStructuredContext] = useState({});
  const [dataSource, setDataSource] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(null);
  const [loadingExtraction, setLoadingExtraction] = useState(null);
  const [error, setError] = useState(null);

  const isLive = dataSource === "live";
  const hasUncertaintyData =
    (response?.claims?.length ?? 0) > 0 || (response?.global_uncertainty_flags?.length ?? 0) > 0;

  async function handleSubmit({ userDescription: desc, structuredContext: context = {} }) {
    setIsLoading(true);
    setLoadingMessage(null);
    setLoadingExtraction(null);
    setError(null);
    try {
      const { response: result, source } = await runReasoning({
        userDescription: desc,
        structuredContext: context,
        onProgress(event) {
          if (event.type === "phase" && event.message) {
            setLoadingMessage(event.message);
          }
          if (event.type === "extraction" && event.data) {
            setLoadingExtraction(event.data);
          }
        },
      });
      setResponse(result);
      setUserDescription(desc);
      setStructuredContext(context);
      setDataSource(source);
    } catch (err) {
      const msg = (err?.message ?? "").toLowerCase();
      if (err?.status === 429 || msg.includes("429") || msg.includes("quota")) {
        setError(
          "API quota reached — add billing at platform.openai.com, or set VITE_FORCE_MOCK=true for offline dev."
        );
      } else {
        setError("Something went wrong mapping your decision. Try describing it again.");
      }
    } finally {
      setIsLoading(false);
      setLoadingMessage(null);
      setLoadingExtraction(null);
    }
  }

  function handleReset() {
    setResponse(null);
    setUserDescription("");
    setStructuredContext({});
    setDataSource(null);
    setLoadingMessage(null);
    setLoadingExtraction(null);
    setError(null);
  }

  return (
    <main className="app">
      <div className="app__inner">
        {!response ? (
          <IntakeForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            loadingMessage={loadingMessage}
            loadingExtraction={loadingExtraction}
          />
        ) : (
          <>
            <DataSourceBanner source={dataSource} />
            <ComparisonScreen
              response={response}
              structuredContext={structuredContext}
              onReset={handleReset}
            >
              {hasUncertaintyData && <UncertaintyPanel response={response} />}
              {hasUncertaintyData ? (
                <WhatIfExplorer
                  originalResponse={response}
                  userDescription={userDescription}
                  structuredContext={structuredContext}
                  isLive={isLive}
                />
              ) : (
                <p className="mock-features-note">
                  Confidence ratings and what-if reruns appear here once the analysis includes
                  claims — connect the live backend for full reasoning.
                </p>
              )}
            </ComparisonScreen>
          </>
        )}
        {error && <p className="app__error">{error}</p>}
      </div>
    </main>
  );
}

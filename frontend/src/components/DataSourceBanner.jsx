export default function DataSourceBanner({ source }) {
  if (!source || source === "live") return null;

  const copy =
    source === "mock-forced"
      ? "Sample data only — turn off VITE_FORCE_MOCK for live AI reasoning."
      : "Live AI didn't respond in time — showing a sample layout. Submit again and wait ~2 minutes, or check that the backend is running with a valid OPENAI_API_KEY.";

  return (
    <div className="data-source-banner" role="alert">
      <strong>Sample data, not live analysis</strong>
      <p>{copy}</p>
    </div>
  );
}

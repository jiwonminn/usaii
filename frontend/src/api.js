import { mockResponse, genericMockResponse } from "./mockResponse";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function runReasoning({ userDescription, structuredContext = {}, whatIfAssumption = null }) {
  const forceMock = import.meta.env.VITE_FORCE_MOCK === "true";

  if (forceMock) {
    await delay(900);
    return injectWhatIf(pickMock(userDescription), whatIfAssumption);
  }

  try {
    const res = await fetch(`${API_BASE}/api/reason`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_description: userDescription,
        structured_context: structuredContext,
        what_if_assumption: whatIfAssumption,
      }),
    });

    if (!res.ok) throw new Error(`API responded with ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("[runReasoning] Backend unreachable, using mock data:", err.message);
    await delay(600);
    return injectWhatIf(pickMock(userDescription), whatIfAssumption);
  }
}

function pickMock(userDescription) {
  const desc = (userDescription || "").toLowerCase();
  if (desc.includes("nurse") || desc.includes("cno") || desc.includes("psw")) {
    return mockResponse;
  }
  return genericMockResponse;
}

function injectWhatIf(response, whatIfAssumption) {
  if (!whatIfAssumption) return response;
  return {
    ...response,
    what_if_impact: `If "${whatIfAssumption}" were true, the modeled outcomes above would shift — this is mock data, connect the live API for real what-if reasoning.`,
  };
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
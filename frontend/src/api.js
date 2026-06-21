import { mockResponse } from "./mockResponse";
import { buildGenericMock } from "./buildGenericMock";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/**
 * @param {object} opts
 * @param {string} opts.userDescription
 * @param {object} [opts.structuredContext]
 * @param {string|null} [opts.whatIfAssumption]
 * @param {(event: object) => void} [opts.onProgress]
 * @returns {Promise<{ response: object, source: 'live' | 'mock-fallback' | 'mock-forced' }>}
 */
export async function runReasoning({
  userDescription,
  structuredContext = {},
  whatIfAssumption = null,
  onProgress,
}) {
  const forceMock = import.meta.env.VITE_FORCE_MOCK === "true";

  if (forceMock) {
    return runMockWithProgress({
      userDescription,
      structuredContext,
      whatIfAssumption,
      onProgress,
      source: "mock-forced",
    });
  }

  try {
    return await runReasoningStream({
      userDescription,
      structuredContext,
      whatIfAssumption,
      onProgress,
    });
  } catch (err) {
    if (err?.noFallback) throw err;

    console.warn("[runReasoning] Stream failed, trying blocking API:", err.message);
    try {
      return await runReasoningBlocking({
        userDescription,
        structuredContext,
        whatIfAssumption,
      });
    } catch (blockingErr) {
      console.warn("[runReasoning] Backend unreachable, using mock data:", blockingErr.message);
      return runMockWithProgress({
        userDescription,
        structuredContext,
        whatIfAssumption,
        onProgress,
        source: "mock-fallback",
        delayMs: 600,
      });
    }
  }
}

async function runReasoningStream({
  userDescription,
  structuredContext,
  whatIfAssumption,
  onProgress,
}) {
  const res = await fetch(`${API_BASE}/api/reason/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_description: userDescription,
      structured_context: structuredContext,
      what_if_assumption: whatIfAssumption,
    }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    const err = new Error(`API responded with ${res.status}${detail ? `: ${detail}` : ""}`);
    err.status = res.status;
    err.noFallback = res.status === 429;
    throw err;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    throw new Error("Streaming not supported by this browser");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data: ")) continue;

      const event = JSON.parse(line.slice(6));
      onProgress?.(event);

      if (event.type === "complete") {
        return { response: event.data, source: "live" };
      }

      if (event.type === "error") {
        const err = new Error(event.detail || "Reasoning failed");
        err.status = event.quota ? 429 : 500;
        err.noFallback = Boolean(event.quota);
        throw err;
      }
    }
  }

  throw new Error("Stream ended without a complete response");
}

async function runReasoningBlocking({ userDescription, structuredContext, whatIfAssumption }) {
  const res = await fetch(`${API_BASE}/api/reason`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_description: userDescription,
      structured_context: structuredContext,
      what_if_assumption: whatIfAssumption,
    }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    const err = new Error(`API responded with ${res.status}${detail ? `: ${detail}` : ""}`);
    err.status = res.status;
    err.noFallback = res.status === 429;
    throw err;
  }

  return { response: await res.json(), source: "live" };
}

async function runMockWithProgress({
  userDescription,
  structuredContext,
  whatIfAssumption,
  onProgress,
  source,
  delayMs = 900,
}) {
  const response = injectWhatIf(pickMock(userDescription, structuredContext), whatIfAssumption);
  const stepDelay = Math.max(120, Math.floor(delayMs / 4));

  onProgress?.({ type: "phase", phase: "extracting", message: "Reading your situation…" });
  await delay(stepDelay);

  if (response.extraction) {
    onProgress?.({ type: "extraction", data: response.extraction });
  }

  onProgress?.({
    type: "phase",
    phase: "modeling",
    message: "Modeling paths at 3 months, 1 year, and 3 years…",
  });
  await delay(stepDelay);

  onProgress?.({
    type: "phase",
    phase: "validating",
    message: "Checking confidence and uncertainty…",
  });
  await delay(stepDelay);

  onProgress?.({ type: "complete", data: response });
  return { response, source };
}

function pickMock(userDescription, structuredContext = {}) {
  const desc = (userDescription || "").toLowerCase();
  if (desc.includes("nurse") || desc.includes("cno") || desc.includes("psw")) {
    return mockResponse;
  }
  return buildGenericMock(userDescription, structuredContext);
}

function injectWhatIf(response, whatIfAssumption) {
  if (!whatIfAssumption) return response;

  const shiftedPaths = (response.paths ?? []).map((path) => ({
    ...path,
    outcomes: Object.fromEntries(
      Object.entries(path.outcomes ?? {}).map(([horizon, outcome]) => [
        horizon,
        {
          ...outcome,
          confidence: outcome.confidence === "high" ? "medium" : outcome.confidence,
          summary: `[What-if] ${outcome.summary}`,
        },
      ])
    ),
  }));

  return {
    ...response,
    paths: shiftedPaths,
    decision_summary: response.decision_summary,
    what_if_impact: `If "${whatIfAssumption}" were true, timelines and confidence levels would shift — sample layout only; connect the live API for real what-if reasoning.`,
  };
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

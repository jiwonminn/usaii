"""FastAPI server — Person 4 wires frontend; Person 3 owns /reason endpoint logic."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

from backend.engine import run_reasoning_chain, run_reasoning_chain_events
from backend.schemas import ReasoningRequest, ReasoningResponse

app = FastAPI(
    title="Life Decision Simulator API",
    description="AI reasoning engine for comparing life/career paths with honest uncertainty.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _mock_mode_enabled() -> bool:
    return os.environ.get("USE_MOCK", "").lower() in ("1", "true", "yes")


def _raise_http_from_runtime(exc: RuntimeError) -> None:
    detail = str(exc)
    lowered = detail.lower()
    if "insufficient_quota" in lowered or "429" in lowered:
        raise HTTPException(status_code=429, detail=detail) from exc
    raise HTTPException(status_code=500, detail=detail) from exc


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Quick check for demo day — confirms server, model, and mock mode."""
    return {
        "status": "ok",
        "mock_mode": _mock_mode_enabled(),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    }


@app.post("/api/reason", response_model=ReasoningResponse)
def reason(request: ReasoningRequest) -> ReasoningResponse:
    """Run the full reasoning chain. Supports optional what_if_assumption for Person 2's explorer."""
    try:
        return run_reasoning_chain(request)
    except RuntimeError as exc:
        _raise_http_from_runtime(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reasoning failed: {exc}") from exc


@app.post("/api/reason/stream")
def reason_stream(request: ReasoningRequest) -> StreamingResponse:
    """Stream pipeline progress (SSE) then the final ReasoningResponse."""

    def generate():
        for event in run_reasoning_chain_events(request):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

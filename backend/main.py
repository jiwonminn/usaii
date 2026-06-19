"""FastAPI server — Person 4 wires frontend; Person 3 owns /reason endpoint logic."""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.engine import run_reasoning_chain
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/reason", response_model=ReasoningResponse)
def reason(request: ReasoningRequest) -> ReasoningResponse:
    """Run the full reasoning chain. Supports optional what_if_assumption for Person 2's explorer."""
    try:
        return run_reasoning_chain(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reasoning failed: {exc}") from exc

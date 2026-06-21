"""FastAPI server — Person 4 wires frontend; Person 3 owns /reason endpoint logic."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

from backend.context_structuring import incorporate_followup_answers, structure_user_input
from backend.engine import run_reasoning_chain, run_reasoning_chain_events
from backend.input_guard import guard_input
from backend.schemas import (
    FollowUpQuestionOut,
    FollowUpRequest,
    ReasoningRequest,
    ReasoningResponse,
    StructureRequest,
    StructureResponse,
)

app = FastAPI(
    title="Life Decision Simulator API",
    description="AI reasoning engine for comparing life/career paths with honest uncertainty.",
    version="0.2.0",
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


# --- Person 4: Context Structuring endpoints ---


@app.post("/api/structure", response_model=StructureResponse)
def structure(request: StructureRequest) -> StructureResponse:
    """Step 1: validate input + extract structured context + generate follow-up questions.

    Frontend calls this BEFORE /api/reason. Returns structured context the
    frontend can show in context cards, plus follow-up questions to fill gaps.
    """
    guard = guard_input(request.user_description)
    if not guard.ok:
        raise HTTPException(status_code=422, detail=guard.issues)

    try:
        result = structure_user_input(guard.cleaned_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StructureResponse(
        structured_context=result.context,
        follow_up_questions=[
            FollowUpQuestionOut(question=q.question, why_it_matters=q.why_it_matters)
            for q in result.follow_up_questions
        ],
        completeness_score=result.completeness_score,
        intake_summary=result.intake_summary,
        warnings=guard.warnings,
    )


@app.post("/api/followup", response_model=StructureResponse)
def followup(request: FollowUpRequest) -> StructureResponse:
    """Step 2 (optional): merge user's follow-up answers into structured context.

    Returns updated context + any remaining follow-up questions (usually 0).
    """
    try:
        result = incorporate_followup_answers(
            user_description=request.user_description,
            current_context=request.structured_context,
            answers=request.answers,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StructureResponse(
        structured_context=result.context,
        follow_up_questions=[
            FollowUpQuestionOut(question=q.question, why_it_matters=q.why_it_matters)
            for q in result.follow_up_questions
        ],
        completeness_score=result.completeness_score,
        intake_summary=result.intake_summary,
        warnings=[],
    )


# --- Person 3: Reasoning endpoint (unchanged logic, better error handling) ---


@app.post("/api/reason", response_model=ReasoningResponse)
def reason(request: ReasoningRequest) -> ReasoningResponse:
    """Run the full reasoning chain. Supports optional what_if_assumption for Person 2's explorer."""
    guard = guard_input(request.user_description)
    if not guard.ok:
        raise HTTPException(status_code=422, detail=guard.issues)

    request.user_description = guard.cleaned_text

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

"""LLM reasoning chain — Person 3 core deliverable."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI, RateLimitError

from backend.env import get_openai_api_key
from backend.extraction import DecisionExtraction
from backend.mock import run_mock_reasoning_chain
from backend.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_extraction_prompt,
    build_user_prompt,
)
from backend.schemas import ReasoningRequest, ReasoningResponse
from backend.validators import validate_reasoning

MAX_QUALITY_RETRIES = int(os.environ.get("REASONING_MAX_RETRIES", "2"))


def _use_mock_mode() -> bool:
    return os.environ.get("USE_MOCK", "").lower() in ("1", "true", "yes")


def _get_client() -> OpenAI:
    return OpenAI(api_key=get_openai_api_key())


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _reasoning_llm_schema() -> dict[str, Any]:
    """Schema for phase 2 LLM — excludes extraction (attached by engine after)."""
    schema = ReasoningResponse.model_json_schema()
    props = schema.get("properties", {})
    props.pop("extraction", None)
    if "required" in schema:
        schema["required"] = [f for f in schema["required"] if f != "extraction"]
    return schema


def _attach_extraction(response: ReasoningResponse, extraction: DecisionExtraction) -> ReasoningResponse:
    return response.model_copy(update={"extraction": extraction})


def _chat_json(client: OpenAI, system: str, user: str, *, temperature: float = 0.35) -> dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
    except RateLimitError as exc:
        detail = str(exc)
        if "insufficient_quota" in detail:
            raise RuntimeError(
                "OpenAI returned insufficient_quota (429). Your API key works, but the account "
                "has no billing/credits.\n"
                "Fix: https://platform.openai.com/settings/organization/billing\n"
                "Workaround: run with mock data while you sort billing:\n"
                "  PYTHONPATH=. python scripts/test_reasoning.py filipino_nurse_toronto --mock"
            ) from exc
        raise

    raw = response.choices[0].message.content
    if not raw:
        raise RuntimeError("Empty response from LLM.")
    return json.loads(raw)


def _extract_decision(
    client: OpenAI,
    request: ReasoningRequest,
) -> DecisionExtraction:
    """Step 1: classify situation, binding constraint, paths to model."""
    prompt = build_extraction_prompt(
        user_description=request.user_description,
        structured_context=request.structured_context.model_dump(exclude_none=True),
    )
    data = _chat_json(client, EXTRACTION_SYSTEM_PROMPT, prompt)
    if "properties" in data and "core_decision" not in data:
        raise RuntimeError("LLM returned JSON schema instead of extraction data. Retry the request.")
    return DecisionExtraction.model_validate(data)


def _model_tradeoffs(
    client: OpenAI,
    request: ReasoningRequest,
    extraction: DecisionExtraction,
    retry_issues: list[str] | None = None,
) -> ReasoningResponse:
    """Step 2: tradeoffs, timed outcomes, uncertainty — grounded in extraction."""
    schema = json.dumps(_reasoning_llm_schema(), indent=2)
    prompt = build_user_prompt(
        user_description=request.user_description,
        structured_context=request.structured_context.model_dump(exclude_none=True),
        what_if_assumption=request.what_if_assumption,
        response_schema=schema,
        extraction=extraction.model_dump(),
        retry_issues=retry_issues,
    )
    temp = 0.2 if retry_issues else 0.35
    data = _chat_json(client, SYSTEM_PROMPT, prompt, temperature=temp)
    return _attach_extraction(ReasoningResponse.model_validate(data), extraction)


def run_reasoning_chain(request: ReasoningRequest) -> ReasoningResponse:
    """
    Two-step generic reasoning chain (same code for any decision):

      Step 1 — extract: binding constraint, paths, personal constraints, risk signals
      Step 2 — model: tradeoffs, 3mo/1yr/3yr outcomes, uncertainty, verification
      Step 3 — validate: auto-retry once if output is too generic (quality gate)
    """
    if _use_mock_mode():
        return run_mock_reasoning_chain(request)

    client = _get_client()
    extraction = _extract_decision(client, request)

    issues: list[str] = []
    response: ReasoningResponse | None = None

    for attempt in range(MAX_QUALITY_RETRIES + 1):
        response = _model_tradeoffs(
            client,
            request,
            extraction,
            retry_issues=issues if attempt > 0 else None,
        )
        issues = validate_reasoning(
            response,
            binding_constraint=extraction.binding_constraint,
            personal_constraints=extraction.personal_constraints,
            paths_to_model=extraction.paths_to_model,
        )
        if not issues:
            break

    if response is None:
        raise RuntimeError("Reasoning chain produced no response.")

    return _attach_extraction(response, extraction)


def run_reasoning_chain_with_meta(request: ReasoningRequest) -> tuple[ReasoningResponse, DecisionExtraction, list[str]]:
    """Same as run_reasoning_chain but returns extraction + any remaining quality issues (for tuning)."""
    if _use_mock_mode():
        return run_mock_reasoning_chain(request), DecisionExtraction(
            core_decision="mock",
            binding_constraint="mock",
            why_decision_is_hard="mock",
            paths_to_model=["A", "B"],
            domain="mock",
        ), []

    client = _get_client()
    extraction = _extract_decision(client, request)

    issues: list[str] = []
    response: ReasoningResponse | None = None

    for attempt in range(MAX_QUALITY_RETRIES + 1):
        response = _model_tradeoffs(
            client,
            request,
            extraction,
            retry_issues=issues if attempt > 0 else None,
        )
        issues = validate_reasoning(
            response,
            binding_constraint=extraction.binding_constraint,
            personal_constraints=extraction.personal_constraints,
            paths_to_model=extraction.paths_to_model,
        )
        if not issues:
            break

    if response is None:
        raise RuntimeError("Reasoning chain produced no response.")

    return _attach_extraction(response, extraction), extraction, issues


async def run_reasoning_chain_async(request: ReasoningRequest) -> ReasoningResponse:
    return run_reasoning_chain(request)

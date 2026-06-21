"""Saturday preflight — verify mock data and API contract before demo/submit."""

from __future__ import annotations

import sys

from backend.mock import mock_filipino_nurse_response, run_mock_reasoning_chain
from backend.prompts import TEST_SCENARIOS
from backend.schemas import ReasoningRequest, ReasoningResponse
from backend.validators import validate_reasoning


def check_mock_nurse() -> list[str]:
    request = ReasoningRequest(user_description="nurse cno psw toronto")
    response = mock_filipino_nurse_response(request)
    ext = response.extraction
    if ext is None:
        return ["Nurse mock missing extraction field — ContextCards will fall back to heuristics."]
    return validate_reasoning(
        response,
        binding_constraint=ext.binding_constraint,
        personal_constraints=ext.personal_constraints,
        paths_to_model=ext.paths_to_model,
    )


def check_schema_contract() -> list[str]:
    issues: list[str] = []
    required = {
        "decision_summary",
        "core_decision",
        "paths",
        "cross_path_insights",
        "questions_to_ask",
        "claims",
        "global_uncertainty_flags",
        "disclaimer",
        "extraction",
    }
    sample = mock_filipino_nurse_response(ReasoningRequest(user_description="nurse"))
    payload = sample.model_dump()
    missing = required - set(payload.keys())
    if missing:
        issues.append(f"ReasoningResponse missing frontend-expected fields: {sorted(missing)}")
    if not isinstance(payload.get("extraction"), dict):
        issues.append("extraction must be an object for ContextCards.")
    return issues


def check_test_scenarios() -> list[str]:
    issues: list[str] = []
    if len(TEST_SCENARIOS) < 4:
        issues.append(f"Expected 4 test scenarios; found {len(TEST_SCENARIOS)}.")
    for name in TEST_SCENARIOS:
        req = ReasoningRequest(user_description=TEST_SCENARIOS[name]["user_description"])
        resp = run_mock_reasoning_chain(req)
        if not isinstance(resp, ReasoningResponse):
            issues.append(f"{name}: mock chain did not return ReasoningResponse.")
    return issues


def main() -> None:
    checks = [
        ("Mock nurse passes quality gate", check_mock_nurse),
        ("API response contract for frontend", check_schema_contract),
        ("Test scenario keys load", check_test_scenarios),
    ]

    failed = False
    for label, fn in checks:
        issues = fn()
        if issues:
            failed = True
            print(f"FAIL — {label}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK   — {label}")

    if failed:
        sys.exit(1)
    print("\nPreflight passed — mock demo data is ready.")


if __name__ == "__main__":
    main()

"""Day 1 test script — Person 3 runs this and shares raw outputs with the team."""

from __future__ import annotations

import argparse
import json
import sys
import time

from backend.prompts import TEST_SCENARIOS
from backend.schemas import ReasoningRequest, StructuredContext
from backend.engine import run_reasoning_chain, run_reasoning_chain_with_meta
from backend.mock import run_mock_reasoning_chain


def run_scenario(name: str, what_if: str | None = None, mock: bool = False, validate: bool = False) -> None:
    if name not in TEST_SCENARIOS:
        print(f"Unknown scenario: {name}")
        print(f"Available: {', '.join(TEST_SCENARIOS)}")
        sys.exit(1)

    scenario = TEST_SCENARIOS[name]
    request = ReasoningRequest(
        user_description=scenario["user_description"],
        structured_context=StructuredContext(**scenario["structured_context"]),
        what_if_assumption=what_if,
    )

    print(f"\n{'='*60}\nScenario: {name}\n{'='*60}\n")
    if mock:
        print("[MOCK MODE] No OpenAI call — sample JSON for frontend/integration\n")
        result = run_mock_reasoning_chain(request)
    elif validate:
        result, extraction, issues = run_reasoning_chain_with_meta(request)
        print("[STEP 1 EXTRACTION]")
        print(json.dumps(extraction.model_dump(), indent=2))
        print("\n[QUALITY CHECK]")
        if issues:
            print("Remaining issues after auto-retry:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("  PASSED — no quality issues")
        print()
    else:
        result = run_reasoning_chain(request)
    print(json.dumps(result.model_dump(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Test reasoning engine scenarios")
    parser.add_argument(
        "scenario",
        nargs="?",
        default="all",
        help=f"Scenario key or 'all'. Options: {', '.join(TEST_SCENARIOS)}, all",
    )
    parser.add_argument(
        "--what-if",
        dest="what_if",
        default=None,
        help="Optional what-if assumption to test dynamic reruns",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use sample JSON without calling OpenAI (useful if billing/quota is not set up)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Show step-1 extraction + quality check results (uses 2-3 API calls)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=25,
        help="Seconds between scenarios when running 'all' with live API (rate limit safety)",
    )
    args = parser.parse_args()

    if args.scenario == "all":
        names = list(TEST_SCENARIOS)
        for i, name in enumerate(names):
            if i > 0 and not args.mock:
                print(f"\n[waiting {args.delay}s for rate limit...]\n")
                time.sleep(args.delay)
            run_scenario(name, what_if=args.what_if, mock=args.mock, validate=args.validate)
    else:
        run_scenario(args.scenario, what_if=args.what_if, mock=args.mock, validate=args.validate)


if __name__ == "__main__":
    main()

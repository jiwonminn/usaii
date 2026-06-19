"""Load environment variables from project-root .env."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_openai_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key and api_key != "sk-your-key-here":
        return api_key

    if not ENV_FILE.exists():
        raise RuntimeError(
            "OPENAI_API_KEY not found. Create a .env file in the project root:\n"
            "  cp .env.example .env\n"
            "Then open .env and paste your real key (not .env.example)."
        )

    raise RuntimeError(
        "OPENAI_API_KEY is missing or still the placeholder in .env.\n"
        f"Edit {ENV_FILE} and set OPENAI_API_KEY=sk-... with your real key."
    )

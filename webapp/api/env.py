"""API: read/write API keys via .env."""

from __future__ import annotations

import os
import re

from fastapi import APIRouter
from pydantic import BaseModel

from webapp.paths import ENV_FILE

router = APIRouter(tags=["env"])


class EnvStatus(BaseModel):
    has_anthropic: bool
    has_openai: bool


class EnvUpdate(BaseModel):
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None


class ValidateResult(BaseModel):
    ok: bool
    provider: str
    message: str | None = None


@router.get("/env", response_model=EnvStatus)
async def get_env() -> EnvStatus:
    return EnvStatus(
        has_anthropic=bool(os.environ.get("ANTHROPIC_API_KEY")),
        has_openai=bool(os.environ.get("OPENAI_API_KEY")),
    )


def _upsert_env_line(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", flags=re.MULTILINE)
    line = f'{key}="{value}"'
    if pattern.search(text):
        return pattern.sub(line, text)
    sep = "" if text.endswith("\n") or not text else "\n"
    return text + sep + line + "\n"


@router.post("/env", response_model=EnvStatus)
async def set_env(payload: EnvUpdate) -> EnvStatus:
    """Persist API keys to .env and also set them on the current process."""
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""

    if payload.anthropic_api_key is not None:
        if payload.anthropic_api_key.strip():
            os.environ["ANTHROPIC_API_KEY"] = payload.anthropic_api_key.strip()
            text = _upsert_env_line(text, "ANTHROPIC_API_KEY", payload.anthropic_api_key.strip())
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)
            text = re.sub(r"^ANTHROPIC_API_KEY\s*=.*$\n?", "", text, flags=re.MULTILINE)

    if payload.openai_api_key is not None:
        if payload.openai_api_key.strip():
            os.environ["OPENAI_API_KEY"] = payload.openai_api_key.strip()
            text = _upsert_env_line(text, "OPENAI_API_KEY", payload.openai_api_key.strip())
        else:
            os.environ.pop("OPENAI_API_KEY", None)
            text = re.sub(r"^OPENAI_API_KEY\s*=.*$\n?", "", text, flags=re.MULTILINE)

    ENV_FILE.write_text(text, encoding="utf-8")
    return EnvStatus(
        has_anthropic=bool(os.environ.get("ANTHROPIC_API_KEY")),
        has_openai=bool(os.environ.get("OPENAI_API_KEY")),
    )


@router.post("/env/validate", response_model=ValidateResult)
async def validate_keys() -> ValidateResult:
    """Try a 1-token Anthropic call to confirm the key works."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            # tiny ping — uses cheapest model + 1 token
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1,
                messages=[{"role": "user", "content": "."}],
            )
            return ValidateResult(ok=True, provider="anthropic", message="Key valid.")
        except Exception as exc:  # noqa: BLE001
            return ValidateResult(ok=False, provider="anthropic", message=str(exc)[:200])

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai

            client = openai.OpenAI(api_key=openai_key)
            client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1,
                messages=[{"role": "user", "content": "."}],
            )
            return ValidateResult(ok=True, provider="openai", message="Key valid.")
        except Exception as exc:  # noqa: BLE001
            return ValidateResult(ok=False, provider="openai", message=str(exc)[:200])

    return ValidateResult(ok=False, provider="none", message="No API key set.")

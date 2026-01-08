import json
from pathlib import Path

from .models import NoteRequest, NoteResponse
from .settings import settings
from .llm.mock_client import MockClient
from .llm.openai_client import OpenAIClient

_PROMPT_PATH = Path(__file__).parent / "prompts" / "qa_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def get_client():
    provider = settings.llm_provider.lower()
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for openai provider.")
        return OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    if provider == "mock":
        return MockClient()
    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")


def build_user_prompt(payload: NoteRequest) -> str:
    return (
        "Analyze the clinical note and metadata below.\n\n"
        f"note_type: {payload.note_type}\n"
        f"date_of_service: {payload.date_of_service}\n"
        f"date_of_injury: {payload.date_of_injury}\n\n"
        "note_text:\n"
        f"{payload.note_text}\n"
    )


def parse_response(raw_text: str) -> NoteResponse:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    return NoteResponse.model_validate(data)


def system_prompt() -> str:
    return _SYSTEM_PROMPT

import json
import logging
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException

from .models import NoteRequest, NoteResponse
from .settings import settings
from .llm.mock_client import MockClient
from .llm.openai_client import OpenAIClient

router = APIRouter()
logger = logging.getLogger("app.api")
_PROMPT_PATH = Path(__file__).parent / "prompts" / "qa_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _get_client():
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


def _build_user_prompt(payload: NoteRequest) -> str:
    return (
        "Analyze the clinical note and metadata below.\n\n"
        f"note_type: {payload.note_type}\n"
        f"date_of_service: {payload.date_of_service}\n"
        f"date_of_injury: {payload.date_of_injury}\n\n"
        "note_text:\n"
        f"{payload.note_text}\n"
    )


def _parse_response(raw_text: str) -> NoteResponse:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    return NoteResponse.model_validate(data)


@router.post("/analyze-note", response_model=NoteResponse)
def analyze_note(payload: NoteRequest) -> NoteResponse:
    start_time = time.perf_counter()
    client = _get_client()
    user_prompt = _build_user_prompt(payload)

    last_error: str | None = None
    for attempt in range(settings.max_retries + 1):
        raw_text = client.generate(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt)
        try:
            response = _parse_response(raw_text)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                "analyze_note success latency_ms=%s score=%s grade=%s flags=%s note_chars=%s",
                latency_ms,
                response.score,
                response.grade,
                len(response.flags),
                len(payload.note_text),
            )
            return response
        except ValueError as exc:
            last_error = str(exc)
            logger.warning(
                "analyze_note invalid_response attempt=%s error=%s",
                attempt + 1,
                last_error,
            )
            if attempt >= settings.max_retries:
                break
            user_prompt = (
                f"{user_prompt}\n\n"
                "Your previous response did not match the required JSON schema. "
                "Return only valid JSON that conforms to the schema exactly."
            )

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    logger.error(
        "analyze_note failed latency_ms=%s error=%s",
        latency_ms,
        last_error or "LLM response failed validation.",
    )
    raise HTTPException(
        status_code=502,
        detail={
            "error": "LLM_RESPONSE_INVALID",
            "message": last_error or "LLM response failed validation.",
        },
    )

import logging
import time

from fastapi import APIRouter, HTTPException
from rq.job import Job

from .models import NoteRequest, NoteResponse
from .settings import settings
from .analyzer import build_user_prompt, get_client, parse_response, system_prompt
from .queue import queue
from .queue import redis_conn
from .jobs import analyze_note_job

router = APIRouter()
logger = logging.getLogger("app.api")


@router.post("/analyze-note", response_model=NoteResponse)
def analyze_note(payload: NoteRequest) -> NoteResponse:
    start_time = time.perf_counter()
    client = get_client()
    user_prompt = build_user_prompt(payload)
    system = system_prompt()

    last_error: str | None = None
    for attempt in range(settings.max_retries + 1):
        raw_text = client.generate(system_prompt=system, user_prompt=user_prompt)
        try:
            response = parse_response(raw_text)
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


@router.post("/analyze-note-async")
def analyze_note_async(payload: NoteRequest):
    job = queue.enqueue(analyze_note_job, payload.model_dump(), retry=3)
    return {"job_id": job.id}


@router.get("/analyze-note-status/{job_id}")
def analyze_note_status(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        return {"status": "finished", "result": job.result}
    if job.is_failed:
        return {"status": "failed", "result": job.result}
    return {"status": job.get_status()}

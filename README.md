# Clinical QA FastAPI Backend

Single endpoint FastAPI service that analyzes a clinical note via an LLM and returns structured QA feedback.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

## Endpoint

`POST /analyze-note`

Example:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/analyze-note -ContentType "application/json" -Body '{"note_text":"Patient reports shoulder pain after lifting a box. Exam: ROM limited.","note_type":"initial evaluation","date_of_service":"2024-01-15","date_of_injury":"2024-01-10"}'
```

## LLM Configuration

Defaults to a local mock provider so the API runs without external keys.

To use OpenAI:

```powershell
$env:LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "your_key"
$env:OPENAI_MODEL = "gpt-4o-mini"
```

## How It Works

- The endpoint builds a structured prompt with the note and metadata.
- The LLM must return strict JSON per schema.
- Responses are validated with Pydantic; invalid output triggers a retry.
- The LLM client is swappable via `LLM_PROVIDER`.

## Logging And Metrics

- Each request logs success or failure with `latency_ms`, score, grade, flag count, and note length.
- Logs avoid recording note text to reduce exposure of sensitive content.

## Tradeoffs

- Single endpoint, no persistence or auth.
- Simple retry logic; not a full safety pipeline.
- Prompt-based control rather than fine-tuning.
- No PHI redaction or audit trail.

## Failure Modes

- Invalid input payload returns a 422 validation error from FastAPI.
- If the LLM returns invalid JSON after retries, the API returns 502 with `LLM_RESPONSE_INVALID`.
- Provider errors (network, quota, bad key) surface as 500s unless handled upstream.

from .api import _build_user_prompt, _parse_response, _SYSTEM_PROMPT, _get_client
from .models import NoteRequest

def analyze_note_job(payload_dict: dict) -> dict:
    payload = NoteRequest.model_validate(payload_dict)
    client = _get_client()
    user_prompt = _build_user_prompt(payload)
    raw_text = client.generate(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt)
    return _parse_response(raw_text).model_dump()
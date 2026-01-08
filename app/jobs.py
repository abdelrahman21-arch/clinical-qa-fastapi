from .analyzer import build_user_prompt, get_client, parse_response, system_prompt
from .models import NoteRequest


def analyze_note_job(payload_dict: dict) -> dict:
    payload = NoteRequest.model_validate(payload_dict)
    client = get_client()
    user_prompt = build_user_prompt(payload)
    raw_text = client.generate(system_prompt=system_prompt(), user_prompt=user_prompt)
    return parse_response(raw_text).model_dump()

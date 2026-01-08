import json

from .base import LLMClient


class MockClient(LLMClient):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = {
            "score": 78,
            "grade": "B+",
            "flags": [
                {
                    "severity": "major",
                    "why_it_matters": "The note lacks a clear mechanism of injury, which weakens causality.",
                    "suggested_edit": "Add a brief statement describing how the injury occurred, or state that it is unknown.",
                },
                {
                    "severity": "minor",
                    "why_it_matters": "The assessment does not distinguish patient-reported symptoms from clinician findings.",
                    "suggested_edit": "Separate subjective complaints from objective exam findings in the assessment section.",
                },
                {
                    "severity": "minor",
                    "why_it_matters": "No explicit date of service is referenced in the narrative.",
                    "suggested_edit": "Include the date of service in the opening sentence of the note.",
                },
            ],
        }
        return json.dumps(response)

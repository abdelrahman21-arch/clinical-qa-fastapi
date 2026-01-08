from openai import OpenAI

from .base import LLMClient


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str, timeout_seconds: int) -> None:
        self._client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            return ""
        return content.strip()

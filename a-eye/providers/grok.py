from openai import OpenAI
from .base import AIProvider


class GrokProvider(AIProvider):
    name = "Grok"

    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    def send(self, messages: list[dict], image_b64: str | None) -> str:
        formatted = []
        for msg in messages[:-1]:
            formatted.append({"role": msg["role"], "content": msg["content"]})

        last = messages[-1]
        content: list = [{"type": "text", "text": last["content"]}]
        if image_b64:
            content.insert(0, {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_b64}"},
            })
        formatted.append({"role": last["role"], "content": content})

        response = self._client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=formatted,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def test_connection(self) -> bool:
        try:
            self._client.chat.completions.create(
                model="grok-2-vision-1212",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5,
            )
            return True
        except Exception:
            return False

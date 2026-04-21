import anthropic
from .base import AIProvider


class ClaudeProvider(AIProvider):
    name = "Claude"

    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def send(self, messages: list[dict], image_b64: str | None) -> str:
        formatted = []
        for msg in messages[:-1]:
            formatted.append({"role": msg["role"], "content": msg["content"]})

        last = messages[-1]
        content: list = [{"type": "text", "text": last["content"]}]
        if image_b64:
            content.insert(0, {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": image_b64},
            })
        formatted.append({"role": last["role"], "content": content})

        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=formatted,
        )
        return response.content[0].text

    def test_connection(self) -> bool:
        try:
            self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except Exception:
            return False

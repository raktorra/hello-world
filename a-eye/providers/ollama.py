import httpx
from .base import AIProvider

_BASE = "http://localhost:11434"
_MODEL = "llava"


class OllamaProvider(AIProvider):
    name = "Ollama (local)"

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

        response = httpx.post(
            f"{_BASE}/v1/chat/completions",
            json={"model": _MODEL, "messages": formatted},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def test_connection(self) -> bool:
        try:
            r = httpx.get(f"{_BASE}/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            return any(_MODEL in m for m in models)
        except Exception:
            return False

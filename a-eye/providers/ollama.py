import httpx
from .base import AIProvider

_BASE = "http://localhost:11434"
_MODEL = "llava"


class OllamaProvider(AIProvider):
    name = "Ollama (local)"

    def send(self, messages: list[dict], image_b64: str | None) -> str:
        # Build a simple prompt string from message history
        prompt = ""
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant:"

        payload = {
            "model": _MODEL,
            "prompt": prompt,
            "stream": False,
        }
        if image_b64:
            payload["images"] = [image_b64]

        response = httpx.post(
            f"{_BASE}/api/generate",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    def test_connection(self) -> bool:
        try:
            r = httpx.get(f"{_BASE}/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            return any(_MODEL in m for m in models)
        except Exception:
            return False

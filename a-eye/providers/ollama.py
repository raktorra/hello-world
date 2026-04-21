import httpx
from .base import AIProvider

_BASE = "http://localhost:11434"
_MODEL = "llava"


class OllamaProvider(AIProvider):
    name = "Ollama (local)"

    def send(self, messages: list[dict], image_b64: str | None) -> str:
        ollama_messages = []
        for msg in messages[:-1]:
            ollama_messages.append({"role": msg["role"], "content": msg["content"]})

        last = messages[-1]
        entry = {"role": last["role"], "content": last["content"]}
        if image_b64:
            entry["images"] = [image_b64]
        ollama_messages.append(entry)

        response = httpx.post(
            f"{_BASE}/api/chat",
            json={"model": _MODEL, "messages": ollama_messages, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()["message"]["content"]

        # If the model returns garbled output (contains special tokens), retry without image
        if image_b64 and ("<unk>" in result or result.count("�") > 5):
            entry.pop("images", None)
            response = httpx.post(
                f"{_BASE}/api/chat",
                json={"model": _MODEL, "messages": ollama_messages, "stream": False},
                timeout=180,
            )
            response.raise_for_status()
            result = response.json()["message"]["content"]

        return result

    def test_connection(self) -> bool:
        try:
            r = httpx.get(f"{_BASE}/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            return any(_MODEL in m for m in models)
        except Exception:
            return False

import base64
import google.generativeai as genai
from .base import AIProvider


class GeminiProvider(AIProvider):
    name = "Gemini"

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-pro")

    def send(self, messages: list[dict], image_b64: str | None) -> str:
        parts = []
        if image_b64:
            parts.append({"mime_type": "image/png", "data": base64.b64decode(image_b64)})

        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        last = messages[-1]
        parts.append(last["content"])

        chat = self._model.start_chat(history=history)
        response = chat.send_message(parts)
        return response.text

    def test_connection(self) -> bool:
        try:
            chat = self._model.start_chat()
            chat.send_message("hi")
            return True
        except Exception:
            return False

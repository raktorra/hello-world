from abc import ABC, abstractmethod


class AIProvider(ABC):
    name: str = ""

    @abstractmethod
    def send(self, messages: list[dict], image_b64: str | None) -> str:
        """Send messages (with optional screenshot) and return the AI reply."""
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        """Return True if the API key is valid."""
        ...

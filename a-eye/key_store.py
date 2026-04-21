import keyring

_SERVICE = "a-eye"
_PROVIDERS = ["claude", "chatgpt", "gemini", "grok"]


def save_key(provider: str, key: str):
    keyring.set_password(_SERVICE, provider, key)


def load_key(provider: str) -> str:
    return keyring.get_password(_SERVICE, provider) or ""


def all_keys() -> dict[str, str]:
    return {p: load_key(p) for p in _PROVIDERS}

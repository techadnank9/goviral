import os
from anthropic import Anthropic

_client: Anthropic | None = None

def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

def ask_claude(system: str, user: str, model: str | None = None) -> str:
    m = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    resp = _get_client().messages.create(
        model=m,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text

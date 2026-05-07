import os
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None

def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return _client

async def ask_claude(system: str, user: str, model: str | None = None) -> str:
    m = model or os.getenv("CLAUDE_MODEL", "anthropic/claude-sonnet-4-5")
    resp = await _get_client().chat.completions.create(
        model=m,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content

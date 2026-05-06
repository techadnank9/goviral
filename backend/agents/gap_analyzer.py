import json
from datetime import datetime, timezone, timedelta
from models.post import Post
from models.pattern import Pattern
from models.trend import TrendSnapshot, ContentGap
from services.claude_client import ask_claude

SYSTEM_PROMPT = """You are Gap Analyzer. You compare what an account has posted recently against what is currently trending in their niche, to find the highest-opportunity content gaps.

A "gap" is a topic that:
1. Is trending in the niche right now (velocity > 1.2)
2. Fits the account's voice and historical content
3. The account has NOT covered in the last 30 days

Input:
- Account's last 30 days of post topics and captions
- Trend snapshot from Trend Scout
- The account's identified winning patterns from Pattern Detective

Output STRICTLY as JSON:
{
  "gaps": [
    {
      "topic": "specific content angle, not just a category",
      "rationale": "why this is the right move for THIS account right now",
      "opportunity_score": 0.0 to 1.0
    }
  ]
}

Return exactly 3 gaps, ranked by opportunity_score descending."""

async def run(posts: list[Post], snapshot: TrendSnapshot, patterns: list[Pattern]) -> list[ContentGap]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    recent = [p for p in posts if p.posted_at >= cutoff]
    recent_captions = [p.caption[:150] for p in recent]

    user_msg = (
        f"Account's last 30 days of captions:\n{json.dumps(recent_captions)}\n\n"
        f"Current trend snapshot:\n{json.dumps(snapshot.model_dump(), indent=2)}\n\n"
        f"Account's winning patterns:\n{json.dumps([p.model_dump() for p in patterns], indent=2)}"
    )

    raw = ask_claude(SYSTEM_PROMPT, user_msg)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])

    data = json.loads(cleaned)
    gaps = [ContentGap(**g) for g in data.get("gaps", [])[:3]]
    while len(gaps) < 3:
        gaps.append(ContentGap(topic="General niche content", rationale="Fallback gap", opportunity_score=0.5))
    return gaps[:3]

from agents.utils import extract_json
import json
import statistics
from models.post import Post, Profile
from models.pattern import Pattern
from services.feature_extractor import compute_engagement_rate, extract_features, find_significant_features
from services.claude_client import ask_claude

SYSTEM_PROMPT = """You are Pattern Detective, an expert at finding the structural reasons specific social media posts go viral.

You will receive:
1. A statistical signal report showing which deterministic features (caption length, hook type, post format, hashtag count, posting hour, video duration) differ significantly between the account's TOP 10% of posts and BOTTOM 10% of posts
2. The full text and metadata of the top 10 performing posts
3. The full text and metadata of 5 underperforming posts for contrast

Your job: name 5 to 7 RECURRING winning patterns. Each pattern must be:
- Grounded in at least one statistically significant feature signal
- Backed by concrete examples (post IDs) from the actual top performers
- Absent or weakly present in the underperformers
- Specific enough to be reused on a new post

Bad pattern (vague): "Engaging captions"
Good pattern (specific): "Contrarian hook under 8 words: 4 of the top 5 posts open with a contrarian one-liner less than 8 words long. Bottom-decile posts average 22-word openers."

Output STRICTLY as JSON matching this schema:
{
  "patterns": [
    {
      "name": "string, 2-4 words",
      "description": "one sentence",
      "evidence_post_ids": ["id1", "id2"],
      "why_it_works": "one paragraph grounded in the data",
      "confidence": 0.0 to 1.0,
      "feature_signal": "the deterministic feature that flagged this"
    }
  ]
}

Do not invent post IDs. Only use IDs present in the input."""

async def run(posts: list[Post], profile: Profile) -> list[Pattern]:
    for p in posts:
        p.engagement_rate = compute_engagement_rate(p, profile.followers)

    sorted_posts = sorted(posts, key=lambda p: p.engagement_rate, reverse=True)
    top_posts = sorted_posts[:max(5, len(sorted_posts) // 10)]
    bottom_posts = sorted_posts[-max(3, len(sorted_posts) // 10):]

    signals = find_significant_features(top_posts, bottom_posts)

    top_summaries = [
        {
            "post_id": p.post_id,
            "caption": p.caption[:300],
            "hook_type": extract_features(p)["hook_type"],
            "format": p.post_format,
            "duration_bucket": extract_features(p)["duration_bucket"],
            "hashtag_count": len(p.hashtags),
            "engagement_rate_pct": round(p.engagement_rate, 2),
        }
        for p in top_posts[:10]
    ]
    bottom_summaries = [
        {
            "post_id": p.post_id,
            "caption": p.caption[:200],
            "hook_type": extract_features(p)["hook_type"],
            "format": p.post_format,
            "engagement_rate_pct": round(p.engagement_rate, 2),
        }
        for p in bottom_posts[:5]
    ]

    user_msg = (
        f"Statistical signals:\n{json.dumps(signals, indent=2)}\n\n"
        f"TOP PERFORMING POSTS:\n{json.dumps(top_summaries, indent=2)}\n\n"
        f"UNDERPERFORMING POSTS:\n{json.dumps(bottom_summaries, indent=2)}"
    )

    raw = await ask_claude(SYSTEM_PROMPT, user_msg)
    data = extract_json(raw)
    top_ids = {p.post_id for p in top_posts}
    patterns = []
    for item in data.get("patterns", []):
        item["evidence_post_ids"] = [pid for pid in item.get("evidence_post_ids", []) if pid in top_ids]
        patterns.append(Pattern(**item))

    return patterns

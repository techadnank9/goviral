from agents.utils import extract_json
import json
from models.post import Post, Profile
from models.trend import TrendSnapshot, TrendingTopic, ContentGap
from services.niche_detector import detect_niche
from services.apify_client import fetch_tiktok_trends
from services.claude_client import ask_claude

SYSTEM_PROMPT = """You are Trend Scout. Given an account's recent post topics and hashtags, plus current trending data from the same platform/region, you identify the 3-5 hottest trending angles in this account's niche right now.

Input you receive:
- Niche label (e.g. "business/founder content", "fitness", "AI tools")
- Top trending hashtags this week with velocity scores
- 20 trending posts from creators in the same niche
- (TikTok only) trending audio with velocity scores

Output STRICTLY as JSON:
{
  "niche": "string",
  "trending_topics": [
    {"topic": "string, plain English", "velocity": 1.0+, "source": "string"}
  ],
  "trending_audio": [
    {"audio_id": "string", "name": "string", "author": "string", "velocity": 1.0+}
  ]
}

Velocity > 1.0 means spiking above baseline. Only include topics with velocity > 1.2."""

async def run(posts: list[Post], profile: Profile) -> TrendSnapshot:
    niche = await detect_niche(profile, posts)

    trending_audio = []
    raw_trends = None
    if profile.platform == "tiktok":
        raw_trends = await fetch_tiktok_trends(niche)
        trending_audio = raw_trends.trending_audio

    recent_hashtags = []
    caption_snippets = []
    for p in posts[:30]:
        recent_hashtags.extend(p.hashtags[:5])
        caption_snippets.append(p.caption[:80])

    trend_data_section = ""
    if raw_trends and raw_trends.trending_topics:
        trend_data_section = f"\nTrending hashtags/topics:\n{json.dumps([t.model_dump() for t in raw_trends.trending_topics[:20]], indent=2)}"
    if trending_audio:
        trend_data_section += f"\nTrending audio:\n{json.dumps([a.model_dump() for a in trending_audio[:10]], indent=2)}"

    user_msg = (
        f"Niche: {niche}\n"
        f"Account's recent hashtags: {json.dumps(list(set(recent_hashtags))[:30])}\n"
        f"Account's recent captions (sample): {json.dumps(caption_snippets[:15])}\n"
        f"{trend_data_section}"
    )

    raw = await ask_claude(SYSTEM_PROMPT, user_msg)
    data = extract_json(raw)
    snapshot = TrendSnapshot(
        niche=niche,
        trending_topics=[TrendingTopic(**t) for t in data.get("trending_topics", [])],
        trending_audio=trending_audio,
    )
    return snapshot

import json
import statistics
from collections import Counter
from models.post import Post, Profile
from models.pattern import Pattern
from models.trend import TrendSnapshot, ContentGap
from models.recommendation import Recommendation, CaptionVariant
from services.feature_extractor import compute_engagement_rate, extract_features
from services.scoring import compute_multipliers, compute_virality_pct
from services.claude_client import ask_claude

SYSTEM_PROMPT = """You are Content Engineer. Your job: produce ONE specific recommendation for the next post this account should publish, and write 5 caption variants for it.

You receive:
- Account profile and platform
- 5-7 winning patterns from Pattern Detective
- Trend snapshot from Trend Scout
- 3 ranked content gaps from Gap Analyzer
- The user's optional topic input (if provided, this OVERRIDES gap selection - use the user's topic)
- 5 raw example captions from the account's top performers (for voice matching)

Step 1: Pick ONE recommendation. If user provided a topic, use it. Otherwise use the highest-scoring gap.

Step 2: Decide format (Reel/carousel/image/video) based on which format has highest engagement rate in the account's history.

Step 3: Write 5 caption variants. Each must:
- Apply a DIFFERENT pattern from the winning patterns list
- Match the account's authentic voice (tone, emoji usage, formatting, vocabulary - mimic the example captions)
- Be ready to post (no placeholders, no [insert here])
- Stay within platform character limits (IG: 2200, TikTok: 2200)

Step 4: For each caption, predict virality % using this formula (you'll be given the multipliers):
predicted_virality = round(min(99, base_account_engagement_pct * pattern_multiplier * trend_alignment * format_multiplier * hook_strength))

Output STRICTLY as JSON:
{
  "recommended_format": "Reel (9:16, 18-24s)" or similar specific string,
  "recommended_topic": "specific topic in plain English",
  "why_this": "2-3 sentences citing actual evidence",
  "best_posting_time": "Tomorrow, 7:42 PM EST",
  "captions": [
    {
      "text": "the actual caption, ready to copy-paste",
      "pattern_used": "name of pattern from Pattern Detective output",
      "rationale": "one sentence: why this pattern fits this topic",
      "predicted_virality_pct": 0-99
    }
  ],
  "suggested_hashtags": ["10 hashtags total"],
  "suggested_audio": [],
  "confidence_pct": 0-99
}

Return exactly 5 captions, sorted by predicted_virality_pct descending."""

def _best_format(posts: list[Post]) -> str:
    by_format: dict[str, list[float]] = {}
    for p in posts:
        by_format.setdefault(p.post_format, []).append(p.engagement_rate)
    best = max(by_format, key=lambda f: statistics.mean(by_format[f]))
    mapping = {"reel": "Reel (9:16, 18-24s)", "carousel": "Carousel (5-8 slides)", "image": "Image", "video": "Video"}
    return mapping.get(best, "Reel (9:16, 18-24s)")

def _best_posting_hour(posts: list[Post]) -> str:
    if not posts:
        return "Tomorrow, 7:00 PM EST"
    hours = [p.posted_at.hour for p in sorted(posts, key=lambda p: p.engagement_rate, reverse=True)[:10]]
    best_hour = Counter(hours).most_common(1)[0][0]
    period = "AM" if best_hour < 12 else "PM"
    h12 = best_hour % 12 or 12
    return f"Tomorrow, {h12}:42 {period} EST"

async def run(
    posts: list[Post],
    profile: Profile,
    patterns: list[Pattern],
    snapshot: TrendSnapshot,
    gaps: list[ContentGap],
    user_topic: str | None,
) -> Recommendation:
    ers = [p.engagement_rate for p in posts if p.engagement_rate > 0]
    if not ers:
        ers = [1.0]
    baseline_er = statistics.median(ers)
    top_er = sorted(ers, reverse=True)[max(0, len(ers) // 10)] if len(ers) > 1 else ers[0]
    top_format = _best_format(posts)

    top_posts = sorted(posts, key=lambda p: p.engagement_rate, reverse=True)[:5]
    example_captions = [p.caption[:300] for p in top_posts]

    trending_topics = {t.topic.lower() for t in snapshot.trending_topics}
    pattern_mults = []
    for pat in patterns[:5]:
        pattern_posts = [p for p in posts if p.post_id in pat.evidence_post_ids]
        pattern_er = statistics.mean([p.engagement_rate for p in pattern_posts]) if pattern_posts else baseline_er
        is_trending = bool(user_topic and any(kw in user_topic.lower() for kw in trending_topics)) \
                   or bool(gaps and any(kw in gaps[0].topic.lower() for kw in trending_topics))
        mults = compute_multipliers(
            account_baseline_er=baseline_er,
            account_top_er=top_er,
            pattern=pat,
            pattern_top_posts_er=pattern_er,
            is_trending_topic=is_trending,
            is_top_format=top_format.lower().startswith("reel"),
            hook_type="statement",
            hook_type_top_er=pattern_er,
        )
        pct = compute_virality_pct(mults, top_er)
        pattern_mults.append({"pattern": pat.name, "multipliers": mults, "predicted_pct": pct})

    user_msg = (
        f"Platform: {profile.platform}\n"
        f"Handle: @{profile.handle} | {profile.followers:,} followers\n"
        f"Best format: {top_format}\n"
        f"Best posting time: {_best_posting_hour(posts)}\n\n"
        f"User's topic request: {user_topic or 'None — use top-ranked gap'}\n\n"
        f"Top content gaps:\n{json.dumps([g.model_dump() for g in gaps], indent=2)}\n\n"
        f"Winning patterns with scoring multipliers:\n{json.dumps(pattern_mults, indent=2)}\n\n"
        f"Trend snapshot:\n{json.dumps(snapshot.model_dump(), indent=2)}\n\n"
        f"Voice examples (top 5 captions):\n{json.dumps(example_captions, indent=2)}"
    )

    raw = ask_claude(SYSTEM_PROMPT, user_msg)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])

    data = json.loads(cleaned)

    captions = sorted(
        [CaptionVariant(**c) for c in data["captions"]],
        key=lambda c: c.predicted_virality_pct,
        reverse=True,
    )
    while len(captions) < 5:
        captions.append(CaptionVariant(
            text="[Fallback caption — regenerate for better results]",
            pattern_used="fallback",
            rationale="Generated fewer than 5 captions",
            predicted_virality_pct=50,
        ))

    return Recommendation(
        handle=profile.handle,
        platform=profile.platform,
        posts_analyzed=len(posts),
        recommended_format=data.get("recommended_format", top_format),
        recommended_topic=data.get("recommended_topic", gaps[0].topic if gaps else "trending content"),
        why_this=data.get("why_this", "Based on your account's patterns and current trends."),
        best_posting_time=data.get("best_posting_time", _best_posting_hour(posts)),
        captions=captions[:5],
        suggested_hashtags=data.get("suggested_hashtags", [])[:10],
        suggested_audio=data.get("suggested_audio", []),
        confidence_pct=data.get("confidence_pct", 80),
    )

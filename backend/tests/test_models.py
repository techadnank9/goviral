import pytest
from datetime import datetime, timezone
from models.post import Post, Profile
from models.pattern import Pattern
from models.trend import TrendingTopic, TrendingAudio, ContentGap, TrendSnapshot
from models.recommendation import CaptionVariant, Recommendation


def test_post_model_roundtrip():
    p = Post(
        post_id="abc123",
        platform="instagram",
        url="https://instagram.com/p/abc",
        caption="Nobody talks about this but I cancelled $200/mo in subscriptions.",
        hashtags=["#ai", "#tools"],
        likes=1000,
        comments=50,
        post_format="reel",
        posted_at=datetime(2026, 4, 1, 19, 0, tzinfo=timezone.utc),
    )
    assert p.engagement_rate == 0.0
    assert p.hook_text == p.caption[:80]


def test_recommendation_requires_five_captions():
    with pytest.raises(Exception):
        Recommendation(
            handle="garyvee",
            platform="instagram",
            posts_analyzed=47,
            recommended_format="Reel (9:16, 18-24s)",
            recommended_topic="AI tools for founders",
            why_this="Evidence.",
            best_posting_time="Tomorrow, 7:42 PM EST",
            captions=[],
            suggested_hashtags=[],
            confidence_pct=87,
        )

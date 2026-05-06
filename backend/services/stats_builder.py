import statistics
from collections import defaultdict
from models.post import Post, Profile
from models.stats import AccountStats, FormatStat, HookStat, HourStat, TopPost
from services.feature_extractor import compute_engagement_rate, classify_hook_type

async def build_stats(posts: list[Post], profile: Profile, niche: str) -> AccountStats:
    for p in posts:
        p.engagement_rate = compute_engagement_rate(p, profile.followers)
        p.hook_type = classify_hook_type(p.caption)

    by_format: dict[str, list[float]] = defaultdict(list)
    for p in posts:
        by_format[p.post_format].append(p.engagement_rate)
    format_breakdown = sorted(
        [FormatStat(format=fmt, avg_er=round(statistics.mean(ers), 3), count=len(ers))
         for fmt, ers in by_format.items()],
        key=lambda x: x.avg_er, reverse=True,
    )

    by_hook: dict[str, list[float]] = defaultdict(list)
    for p in posts:
        by_hook[p.hook_type].append(p.engagement_rate)
    hook_breakdown = sorted(
        [HookStat(hook_type=hook, avg_er=round(statistics.mean(ers), 3), count=len(ers))
         for hook, ers in by_hook.items()],
        key=lambda x: x.avg_er, reverse=True,
    )

    by_hour: dict[int, list[float]] = defaultdict(list)
    for p in posts:
        by_hour[p.posted_at.hour].append(p.engagement_rate)
    hourly_engagement = [
        HourStat(hour=h, avg_er=round(statistics.mean(by_hour[h]), 3) if h in by_hour else 0.0)
        for h in range(24)
    ]

    top_posts = [
        TopPost(
            post_id=p.post_id,
            caption=p.caption[:200],
            engagement_rate=round(p.engagement_rate, 3),
            format=p.post_format,
            hook_type=p.hook_type,
        )
        for p in sorted(posts, key=lambda p: p.engagement_rate, reverse=True)[:5]
    ]

    return AccountStats(
        handle=profile.handle,
        platform=profile.platform,
        posts_analyzed=len(posts),
        niche=niche,
        format_breakdown=format_breakdown,
        hook_breakdown=hook_breakdown,
        hourly_engagement=hourly_engagement,
        top_posts=top_posts,
    )

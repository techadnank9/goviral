import os
from typing import Callable, Awaitable
from models.post import Post, Profile
from models.recommendation import Recommendation
from services.apify_client import fetch_instagram, fetch_tiktok
from agents import pattern_detective, trend_scout, gap_analyzer, content_engineer
from streaming.sse import ProgressEvent

Emitter = Callable[[ProgressEvent], Awaitable[None]]

async def _noop_emitter(event: ProgressEvent) -> None:
    pass

async def analyze(
    handle: str,
    platform: str,
    user_topic: str | None = None,
    emit: Emitter = _noop_emitter,
) -> Recommendation:
    await emit(ProgressEvent(stage="fetching", message="Reading your recent posts...", pct=10))

    fetch = fetch_instagram if platform == "instagram" else fetch_tiktok
    posts, profile = await fetch(handle)

    await emit(ProgressEvent(stage="fetching", message=f"Read {len(posts)} posts from @{profile.handle}", pct=25))

    patterns = await pattern_detective.run(posts, profile)
    await emit(ProgressEvent(stage="patterns", message=f"Found {len(patterns)} winning patterns", pct=50))

    snapshot = await trend_scout.run(posts, profile)
    await emit(ProgressEvent(stage="trends", message=f"Scanned trends in {snapshot.niche.replace('_', ' ')} niche", pct=70))

    gaps = await gap_analyzer.run(posts, snapshot, patterns)
    await emit(ProgressEvent(stage="gaps", message="Found top content gaps", pct=80))

    await emit(ProgressEvent(stage="engineering", message="Engineering your next post...", pct=90))
    recommendation = await content_engineer.run(posts, profile, patterns, snapshot, gaps, user_topic)

    await emit(ProgressEvent(stage="done", message="Done!", pct=100))
    return recommendation

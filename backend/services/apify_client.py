import asyncio
import os
from typing import Any
from apify_client import ApifyClient
from models.post import Post, Profile, PostFormat
from models.trend import TrendingTopic, TrendingAudio, TrendSnapshot
from datetime import datetime, timezone

_client: ApifyClient | None = None

def _get_client() -> ApifyClient:
    global _client
    if _client is None:
        token = os.getenv("APIFY_TOKEN")
        if not token:
            raise RuntimeError("APIFY_TOKEN not set")
        _client = ApifyClient(token)
    return _client

async def run_actor(actor_id: str, run_input: dict[str, Any], timeout_secs: int = 180) -> list[dict]:
    def _sync_call() -> list[dict]:
        client = _get_client()
        run = client.actor(actor_id).call(run_input=run_input, timeout_secs=timeout_secs)
        if not run or not run.get("defaultDatasetId"):
            raise RuntimeError(f"Actor {actor_id} returned no dataset")
        return list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return await asyncio.to_thread(_sync_call)

def _parse_ig_format(item: dict) -> PostFormat:
    if item.get("productType") == "clips":
        return "reel"
    t = item.get("type", "").lower()
    if t == "video":
        return "video"
    if t == "sidecar":
        return "carousel"
    return "image"

def _parse_ig_post(item: dict) -> Post | None:
    try:
        ts = item.get("timestamp", "")
        posted_at = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.now(timezone.utc)
        return Post(
            post_id=str(item.get("id", item.get("shortCode", ""))),
            platform="instagram",
            url=item.get("url", ""),
            caption=item.get("caption") or "",
            hashtags=item.get("hashtags") or [],
            likes=item.get("likesCount") or 0,
            comments=item.get("commentsCount") or 0,
            views=item.get("videoViewCount"),
            video_duration_sec=item.get("videoDuration"),
            post_format=_parse_ig_format(item),
            posted_at=posted_at,
        )
    except Exception:
        return None

def _parse_ig_profile(item: dict) -> Profile:
    return Profile(
        handle=item.get("username", ""),
        platform="instagram",
        followers=item.get("followersCount", 0),
        following=item.get("followsCount", 0),
        post_count=item.get("postsCount", 0),
        bio=item.get("biography", ""),
        verified=item.get("verified", False),
    )

async def fetch_instagram(handle: str) -> tuple[list[Post], Profile]:
    clean = handle.lstrip("@")
    limit = int(os.getenv("MAX_POSTS_TO_ANALYZE", "30"))
    print(f"[fetch_instagram] handle={clean} limit={limit}")

    posts_raw, profile_raw = await asyncio.gather(
        run_actor("apify/instagram-scraper", {
            "directUrls": [f"https://www.instagram.com/{clean}/"],
            "resultsType": "posts",
            "resultsLimit": limit,
            "addParentData": False,
        }),
        run_actor("apify/instagram-profile-scraper", {"usernames": [clean]}),
    )

    posts = [p for item in posts_raw if (p := _parse_ig_post(item)) is not None]
    print(f"[fetch_instagram] raw={len(posts_raw)} parsed={len(posts)}")

    profile = _parse_ig_profile(profile_raw[0]) if profile_raw else Profile(
        handle=clean, platform="instagram", followers=1
    )
    print(f"[fetch_instagram] followers={profile.followers}")
    return posts, profile

def _parse_tt_post(item: dict) -> Post | None:
    try:
        music = item.get("musicMeta", {})
        create_ts = item.get("createTime", 0)
        posted_at = datetime.fromtimestamp(create_ts, tz=timezone.utc)
        hashtags = [h["name"] for h in (item.get("hashtags") or []) if isinstance(h, dict)]
        return Post(
            post_id=str(item.get("id", "")),
            platform="tiktok",
            url=item.get("webVideoUrl", ""),
            caption=item.get("text") or "",
            hashtags=hashtags,
            likes=item.get("diggCount", 0),
            comments=item.get("commentCount", 0),
            shares=item.get("shareCount", 0),
            views=item.get("playCount"),
            video_duration_sec=item.get("videoMeta", {}).get("duration"),
            post_format="video",
            posted_at=posted_at,
            audio_id=music.get("musicId"),
            audio_name=music.get("musicName"),
        )
    except Exception:
        return None

async def fetch_tiktok(handle: str) -> tuple[list[Post], Profile]:
    clean = handle.lstrip("@")
    items = await run_actor("clockworks/tiktok-scraper", {
        "profiles": [clean],
        "resultsPerPage": int(os.getenv("MAX_POSTS_TO_ANALYZE", "100")),
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
    })
    posts = [p for item in items if (p := _parse_tt_post(item)) is not None]
    followers = 0
    if items:
        followers = items[0].get("authorMeta", {}).get("fans", 0)
    profile = Profile(handle=clean, platform="tiktok", followers=max(followers, 1))
    return posts, profile

async def fetch_tiktok_trends(niche: str) -> TrendSnapshot:
    try:
        items = await run_actor("clockworks/tiktok-trends-scraper", {
            "countryCode": "US",
            "trendType": ["hashtag", "song"],
            "period": "7",
        }, timeout_secs=120)
    except Exception:
        return TrendSnapshot(niche=niche, trending_topics=[], trending_audio=[])

    topics: list[TrendingTopic] = []
    audio: list[TrendingAudio] = []
    for item in items[:30]:
        if item.get("trendType") == "hashtag":
            topics.append(TrendingTopic(
                topic=item.get("name", ""),
                velocity=float(item.get("rankChange", 1.0)) + 1.0,
                source="tiktok_trends_us",
            ))
        elif item.get("trendType") == "song":
            audio.append(TrendingAudio(
                audio_id=str(item.get("id", "")),
                name=item.get("title", ""),
                author=item.get("artistName", ""),
                velocity=float(item.get("rankChange", 1.0)) + 1.0,
            ))

    return TrendSnapshot(niche=niche, trending_topics=topics, trending_audio=audio)

import asyncio
import json
import os
import pathlib
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Literal, AsyncGenerator
from models.recommendation import Recommendation, CaptionVariant
from models.stats import AccountStats
from streaming.sse import ProgressEvent, format_sse
from services.stats_builder import build_stats
from services.niche_detector import detect_niche
from services.apify_client import fetch_instagram, fetch_tiktok

router = APIRouter()

class AnalyzeRequest(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"] = "instagram"
    user_topic: str | None = None
    stream: bool = True

class StatsRequest(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"] = "instagram"
    stream: bool = True

@router.get("/health")
async def health():
    return {"status": "ok"}

def _load_demo_cache(handle: str, platform: str) -> dict | None:
    path = pathlib.Path(__file__).parent.parent / "cache" / "demo_accounts" / f"{platform}_{handle.lstrip('@')}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None

async def _stream_analysis(req: AnalyzeRequest) -> AsyncGenerator[str, None]:
    from agents.crew import analyze

    events: list[str] = []
    lock = asyncio.Lock()

    async def emit(event: ProgressEvent) -> None:
        async with lock:
            events.append(format_sse("progress", {
                "stage": event.stage,
                "message": event.message,
                "pct": event.pct,
            }))

    async def event_generator() -> AsyncGenerator[str, None]:
        task = asyncio.create_task(
            analyze(req.handle, req.platform, req.user_topic, emit)
        )
        while not task.done():
            async with lock:
                while events:
                    yield events.pop(0)
            await asyncio.sleep(0.1)

        async with lock:
            while events:
                yield events.pop(0)

        try:
            rec: Recommendation = await task
            yield format_sse("complete", rec.model_dump())
        except Exception as exc:
            yield format_sse("error", {"message": str(exc), "code": "analysis_failed"})

    async for chunk in event_generator():
        yield chunk

async def _stream_stats(req: StatsRequest) -> AsyncGenerator[str, None]:
    events: list[str] = []
    lock = asyncio.Lock()

    async def emit(event: ProgressEvent) -> None:
        async with lock:
            events.append(format_sse("progress", {
                "stage": event.stage,
                "message": event.message,
                "pct": event.pct,
            }))

    async def run() -> AccountStats:
        await emit(ProgressEvent(stage="fetching", message="Fetching your posts...", pct=20))
        fetch = fetch_instagram if req.platform == "instagram" else fetch_tiktok
        posts, profile = await fetch(req.handle)
        await emit(ProgressEvent(stage="analyzing", message=f"Analyzing {len(posts)} posts...", pct=60))
        niche = await detect_niche(profile, posts)
        stats = await build_stats(posts, profile, niche)
        return stats

    async def event_generator() -> AsyncGenerator[str, None]:
        task = asyncio.create_task(run())
        while not task.done():
            async with lock:
                while events:
                    yield events.pop(0)
            await asyncio.sleep(0.1)
        async with lock:
            while events:
                yield events.pop(0)
        try:
            stats: AccountStats = await task
            yield format_sse("complete", stats.model_dump())
        except Exception as exc:
            yield format_sse("error", {"message": str(exc), "code": "stats_failed"})

    async for chunk in event_generator():
        yield chunk

@router.post("/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    if demo_mode:
        cached = _load_demo_cache(req.handle, req.platform)
        if cached:
            if req.stream:
                async def demo_stream():
                    for stage, msg, pct in [
                        ("fetching", "Reading your recent posts...", 25),
                        ("patterns", "Found your winning patterns", 50),
                        ("trends", "Scanning trends in your niche...", 70),
                        ("engineering", "Engineering your next post...", 90),
                    ]:
                        yield format_sse("progress", {"stage": stage, "message": msg, "pct": pct})
                        await asyncio.sleep(0.5)
                    yield format_sse("complete", cached)
                return StreamingResponse(demo_stream(), media_type="text/event-stream")
            return JSONResponse(cached)

    if req.stream:
        return StreamingResponse(_stream_analysis(req), media_type="text/event-stream")
    else:
        from agents.crew import analyze
        rec = await analyze(req.handle, req.platform, req.user_topic)
        return rec

@router.post("/stats")
async def stats_endpoint(req: StatsRequest):
    if req.stream:
        return StreamingResponse(_stream_stats(req), media_type="text/event-stream")
    fetch = fetch_instagram if req.platform == "instagram" else fetch_tiktok
    posts, profile = await fetch(req.handle)
    niche = await detect_niche(profile, posts)
    stats = await build_stats(posts, profile, niche)
    return stats

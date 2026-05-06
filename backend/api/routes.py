import asyncio
import json
import os
import pathlib
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Literal, AsyncGenerator
from models.recommendation import Recommendation, CaptionVariant
from streaming.sse import ProgressEvent, format_sse

router = APIRouter()

class AnalyzeRequest(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"] = "instagram"
    user_topic: str | None = None
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

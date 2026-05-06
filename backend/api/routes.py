from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from models.recommendation import Recommendation, CaptionVariant
from typing import Literal
import json

router = APIRouter()

class AnalyzeRequest(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"] = "instagram"
    user_topic: str | None = None
    stream: bool = True

def _stub_recommendation(handle: str, platform: str) -> Recommendation:
    return Recommendation(
        handle=handle,
        platform=platform,
        posts_analyzed=47,
        recommended_format="Reel (9:16, 18-24s)",
        recommended_topic="AI tools that replaced $200/month in subscriptions",
        why_this="Stub response — real agents not yet wired.",
        best_posting_time="Tomorrow, 7:42 PM EST",
        captions=[
            CaptionVariant(text=f"Caption {i}", pattern_used="stub", rationale="stub", predicted_virality_pct=90 - i * 5)
            for i in range(5)
        ],
        suggested_hashtags=["#ai", "#tools"],
        confidence_pct=87,
    )

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    rec = _stub_recommendation(req.handle, req.platform)
    return rec

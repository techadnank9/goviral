from pydantic import BaseModel, Field, field_validator
from typing import Literal

class CaptionVariant(BaseModel):
    text: str
    pattern_used: str
    rationale: str
    predicted_virality_pct: int = Field(ge=0, le=100)

class Recommendation(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"]
    posts_analyzed: int
    recommended_format: str
    recommended_topic: str
    why_this: str
    best_posting_time: str
    captions: list[CaptionVariant]
    suggested_hashtags: list[str]
    suggested_audio: list[str] = Field(default_factory=list)
    confidence_pct: int = Field(ge=0, le=100)

    @field_validator("captions")
    @classmethod
    def must_have_five_captions(cls, v: list) -> list:
        if len(v) != 5:
            raise ValueError(f"Expected exactly 5 captions, got {len(v)}")
        return v

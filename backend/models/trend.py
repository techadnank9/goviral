from pydantic import BaseModel, Field

class TrendingTopic(BaseModel):
    topic: str
    velocity: float
    source: str

class TrendingAudio(BaseModel):
    audio_id: str
    name: str
    author: str
    velocity: float

class ContentGap(BaseModel):
    topic: str
    rationale: str
    opportunity_score: float = Field(ge=0.0, le=1.0)

class TrendSnapshot(BaseModel):
    niche: str
    trending_topics: list[TrendingTopic]
    trending_audio: list[TrendingAudio] = Field(default_factory=list)
    gaps: list[ContentGap] = Field(default_factory=list)

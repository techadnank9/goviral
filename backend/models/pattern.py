from pydantic import BaseModel, Field

class Pattern(BaseModel):
    name: str = Field(description="Short memorable name, e.g. 'Contrarian Hook'")
    description: str = Field(description="One-sentence explanation")
    evidence_post_ids: list[str] = Field(description="Post IDs that exemplify this pattern")
    why_it_works: str
    confidence: float = Field(ge=0.0, le=1.0)
    feature_signal: str = Field(description="Which deterministic feature flagged this")

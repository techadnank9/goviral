from pydantic import BaseModel
from typing import Literal

class FormatStat(BaseModel):
    format: str
    avg_er: float
    count: int

class HookStat(BaseModel):
    hook_type: str
    avg_er: float
    count: int

class HourStat(BaseModel):
    hour: int
    avg_er: float

class TopPost(BaseModel):
    post_id: str
    caption: str
    engagement_rate: float
    format: str
    hook_type: str

class AccountStats(BaseModel):
    handle: str
    platform: Literal["instagram", "tiktok"]
    posts_analyzed: int
    niche: str
    format_breakdown: list[FormatStat]
    hook_breakdown: list[HookStat]
    hourly_engagement: list[HourStat]
    top_posts: list[TopPost]

from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Literal

Platform = Literal["instagram", "tiktok"]
PostFormat = Literal["reel", "image", "carousel", "video"]
HookType = Literal["question", "statement", "pov", "list", "confession", "command", "other"]

class Post(BaseModel):
    post_id: str
    platform: Platform
    url: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int | None = None
    video_duration_sec: float | None = None
    post_format: PostFormat
    posted_at: datetime
    audio_id: str | None = None
    audio_name: str | None = None
    engagement_rate: float = 0.0
    hook_text: str = ""
    hook_type: HookType = "other"

    model_config = {"extra": "ignore"}

    @model_validator(mode="after")
    def set_hook_text(self) -> "Post":
        if not self.hook_text:
            self.hook_text = self.caption[:80]
        return self

class Profile(BaseModel):
    handle: str
    platform: Platform
    followers: int
    following: int = 0
    post_count: int = 0
    bio: str = ""
    verified: bool = False

    model_config = {"extra": "ignore"}

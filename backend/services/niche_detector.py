import json
from models.post import Post, Profile
from services.claude_client import ask_claude

NICHE_TAXONOMY = [
    "business_and_founders", "ai_and_tech", "fitness_and_health",
    "food_and_cooking", "fashion_and_beauty", "travel",
    "education_and_learning", "personal_finance", "comedy_and_entertainment",
    "lifestyle_and_motivation", "parenting", "gaming",
]

SYSTEM = (
    "You are a social media niche classifier. "
    "Pick exactly ONE niche from the provided list. Reply with only the niche string, nothing else."
)

async def detect_niche(profile: Profile, recent_posts: list[Post]) -> str:
    top_hashtags = []
    caption_snippets = []
    for p in recent_posts[:20]:
        top_hashtags.extend(p.hashtags[:3])
        caption_snippets.append(p.caption[:100])

    user_msg = (
        f"Bio: {profile.bio}\n"
        f"Sample captions: {json.dumps(caption_snippets[:10])}\n"
        f"Top hashtags: {json.dumps(list(set(top_hashtags))[:20])}\n"
        f"Niche options: {json.dumps(NICHE_TAXONOMY)}\n"
        "Pick exactly one niche from the list above."
    )
    result = ask_claude(SYSTEM, user_msg)
    cleaned = result.strip().lower().replace(" ", "_").replace("-", "_")
    if cleaned in NICHE_TAXONOMY:
        return cleaned
    for n in NICHE_TAXONOMY:
        if n in cleaned or cleaned in n:
            return n
    return "lifestyle_and_motivation"

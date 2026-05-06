from models.post import Post, HookType
from typing import Any

def compute_engagement_rate(post: Post, followers: int) -> float:
    if followers <= 0:
        return 0.0
    interactions = post.likes + post.comments + post.shares
    return round((interactions / followers) * 100, 4)

def classify_hook_type(caption: str) -> HookType:
    hook = caption[:80].strip().lower()
    if not hook:
        return "other"
    words = hook.split()
    if not words:
        return "other"
    if hook.endswith("?") or words[0] in ("why", "how", "what", "when", "who"):
        return "question"
    if hook.startswith("pov"):
        return "pov"
    if any(hook.startswith(f"{n} ") for n in ["1","2","3","4","5","6","7","8","9","10"]):
        return "list"
    if any(phrase in hook for phrase in [
        "i was", "i used to", "i thought", "nobody talks", "i'll be honest",
        "nobody talks about"
    ]):
        return "confession"
    if words[0] in {"stop", "start", "do", "don't", "never", "always"}:
        return "command"
    return "statement"

def bucket_duration(secs: float | None) -> str:
    if secs is None:
        return "unknown"
    if secs < 16:
        return "short"
    if secs < 30:
        return "medium"
    return "long"

def extract_features(post: Post) -> dict[str, Any]:
    return {
        "caption_length": len(post.caption),
        "hashtag_count": len(post.hashtags),
        "hook_type": classify_hook_type(post.caption),
        "format": post.post_format,
        "duration_bucket": bucket_duration(post.video_duration_sec),
        "posting_hour": post.posted_at.hour,
        "posting_dow": post.posted_at.weekday(),
        "has_emoji": any(ord(c) > 0x2600 for c in post.caption[:80]),
    }

def _modal(values: list) -> Any:
    if not values:
        return None
    return max(set(values), key=values.count)

def find_significant_features(top_posts: list[Post], bottom_posts: list[Post]) -> list[dict]:
    if not top_posts or not bottom_posts:
        return []

    top_feats = [extract_features(p) for p in top_posts]
    bot_feats = [extract_features(p) for p in bottom_posts]
    categorical = ["hook_type", "format", "duration_bucket"]
    numeric = ["caption_length", "hashtag_count", "posting_hour"]
    results = []

    for feat in categorical:
        top_vals = [f[feat] for f in top_feats]
        bot_vals = [f[feat] for f in bot_feats]
        top_modal = _modal(top_vals)
        bot_modal = _modal(bot_vals)
        if top_modal != bot_modal:
            top_rate = top_vals.count(top_modal) / len(top_vals)
            bot_rate = bot_vals.count(top_modal) / len(bot_vals)
            delta = abs(top_rate - bot_rate)
            if delta >= 0.25:
                results.append({
                    "feature": feat,
                    "top_modal": top_modal,
                    "bottom_modal": bot_modal,
                    "delta": round(delta, 2),
                })

    for feat in numeric:
        top_avg = sum(f[feat] for f in top_feats) / len(top_feats)
        bot_avg = sum(f[feat] for f in bot_feats) / len(bot_feats)
        denom = max(bot_avg, 0.1)
        rel_delta = abs(top_avg - bot_avg) / denom
        if rel_delta >= 0.25:
            results.append({
                "feature": feat,
                "top_avg": round(top_avg, 1),
                "bottom_avg": round(bot_avg, 1),
                "relative_delta": round(rel_delta, 2),
            })

    return results

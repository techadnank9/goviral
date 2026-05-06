from models.pattern import Pattern
from models.post import HookType

def compute_multipliers(
    account_baseline_er: float,
    account_top_er: float,
    pattern: Pattern,
    pattern_top_posts_er: float,
    is_trending_topic: bool,
    is_top_format: bool,
    hook_type: HookType,
    hook_type_top_er: float,
) -> dict:
    pattern_multiplier = max(1.0, pattern_top_posts_er / max(account_baseline_er, 0.1))
    trend_alignment = 1.4 if is_trending_topic else 1.0
    format_multiplier = 1.3 if is_top_format else 0.85
    hook_strength = max(1.0, hook_type_top_er / max(account_baseline_er, 0.1))
    return {
        "base": account_baseline_er,
        "pattern_multiplier": round(pattern_multiplier, 2),
        "trend_alignment": trend_alignment,
        "format_multiplier": format_multiplier,
        "hook_strength": round(hook_strength, 2),
    }

def compute_virality_pct(multipliers: dict, account_top_er: float) -> int:
    raw = (
        multipliers["base"]
        * multipliers["pattern_multiplier"]
        * multipliers["trend_alignment"]
        * multipliers["format_multiplier"]
        * multipliers["hook_strength"]
    )
    pct = min(99, int(round((raw / max(account_top_er, 0.1)) * 100)))
    return max(50, pct)

export type Platform = "instagram" | "tiktok";

export interface CaptionVariant {
  text: string;
  pattern_used: string;
  rationale: string;
  predicted_virality_pct: number;
}

export interface Recommendation {
  handle: string;
  platform: Platform;
  posts_analyzed: number;
  recommended_format: string;
  recommended_topic: string;
  why_this: string;
  best_posting_time: string;
  captions: CaptionVariant[];
  suggested_hashtags: string[];
  suggested_audio: string[];
  confidence_pct: number;
}

export interface ProgressEvent {
  stage: string;
  message: string;
  pct: number;
}

export type AppState =
  | { phase: "input" }
  | { phase: "loading"; stages: ProgressEvent[] }
  | { phase: "result"; recommendation: Recommendation }
  | { phase: "error"; message: string };

export interface FormatStat {
  format: string;
  avg_er: number;
  count: number;
}

export interface HookStat {
  hook_type: string;
  avg_er: number;
  count: number;
}

export interface HourStat {
  hour: number;
  avg_er: number;
}

export interface TopPost {
  post_id: string;
  caption: string;
  engagement_rate: number;
  format: string;
  hook_type: string;
}

export interface AccountStats {
  handle: string;
  platform: Platform;
  posts_analyzed: number;
  niche: string;
  followers: number;
  following: number;
  avg_likes: number;
  avg_comments: number;
  avg_er: number;
  format_breakdown: FormatStat[];
  hook_breakdown: HookStat[];
  hourly_engagement: HourStat[];
  top_posts: TopPost[];
}

export type AppMode = "recommendation" | "dashboard";

export type DashboardState =
  | { phase: "input" }
  | { phase: "loading"; stages: ProgressEvent[] }
  | { phase: "result"; stats: AccountStats }
  | { phase: "error"; message: string };

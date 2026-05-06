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

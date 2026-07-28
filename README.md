# GoViral

Analyzes an Instagram or TikTok account's recent posts and generates a data-backed recommendation for what to post next.

## What it does

Given a handle and platform, a pipeline of Claude-powered agents (`backend/agents/`) does the following, streamed to the client over SSE as it progresses:

1. **Fetch** — pulls recent posts and profile data via Apify (`services/apify_client.py`) for Instagram or TikTok.
2. **Pattern Detective** — runs statistical significance tests over post features (caption length, hook type, format, hashtag count, posting hour, video duration) to find which features separate the account's top 10% of posts from the bottom 10%, then asks Claude to name 5-7 recurring winning patterns backed by concrete examples.
3. **Trend Scout** — detects the account's niche and cross-references currently trending hashtags/topics/audio in that niche (via Apify) to surface 3-5 hot angles.
4. **Gap Analyzer** — runs in parallel with Trend Scout, then identifies content gaps once both finish.
5. **Content Engineer** — synthesizes patterns, trends, and gaps (plus an optional user-supplied topic) into a concrete next-post recommendation with caption variants.

The FastAPI backend exposes `/analyze` (streams progress + final recommendation) and `/stats` endpoints; a demo cache (`backend/cache/demo_accounts/`) lets specific handles return canned data without hitting Apify. The Next.js frontend renders a dashboard with account stats, engagement heatmaps, pattern/trend views, and caption cards.

## Tech stack

**Backend:** Python 3.11+, FastAPI, Pydantic, Anthropic Claude API, Apify client, Server-Sent Events for streaming progress. Tests via pytest.

**Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui (base-ui, class-variance-authority, lucide-react).

## Project structure

```
backend/
  main.py              FastAPI app entry point
  api/routes.py        /analyze, /stats, /health endpoints
  agents/              crew orchestration + Pattern Detective, Trend Scout, Gap Analyzer, Content Engineer
  services/            Apify client, Claude client, feature extraction, scoring, niche detection
  models/               Pydantic models: Post, Profile, Pattern, Trend, Recommendation, Stats
  streaming/sse.py      SSE event formatting
  tests/

frontend/
  app/                 Next.js App Router pages
  components/           DashboardView, RecommendationView, CaptionCard, HourHeatmap, InputForm, etc.
  lib/                 API client, shared types
```

## Getting started

Requires `ANTHROPIC_API_KEY` and Apify credentials (see `.env.example`).

**Backend:**
```bash
cd backend
pip install -e .
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Frontend expects the backend on the URL configured via `lib/api.ts`; backend CORS is controlled by `ALLOWED_ORIGINS` (defaults to `http://localhost:3000`).

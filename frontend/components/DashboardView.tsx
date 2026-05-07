"use client";
import { AccountStats } from "@/lib/types";
import { HourHeatmap } from "./HourHeatmap";
import { HorizontalBar } from "./HorizontalBar";

interface Props {
  stats: AccountStats;
  onReset: () => void;
}

function fmt(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

function nicheLabel(n: string) {
  return n.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

export function DashboardView({ stats, onReset }: Props) {
  const statCards = [
    { icon: "⚡", label: "Engagement Rate", value: `${(stats.avg_er * 100).toFixed(2)}%`, color: "text-amber-500" },
    { icon: "❤️", label: "Average Likes", value: fmt(Math.round(stats.avg_likes)), color: "text-red-400" },
    { icon: "💬", label: "Average Comments", value: fmt(Math.round(stats.avg_comments)), color: "text-blue-400" },
    { icon: "📊", label: "Posts Analyzed", value: String(stats.posts_analyzed), color: "text-violet-500" },
    { icon: "👥", label: "Followers", value: fmt(stats.followers), color: "text-green-500" },
    { icon: "➡️", label: "Following", value: fmt(stats.following), color: "text-indigo-400" },
  ];

  return (
    <div className="w-full max-w-3xl space-y-5">

      {/* Profile header */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-400 to-indigo-500 flex items-center justify-center text-white text-2xl font-black">
              {stats.handle[0].toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">@{stats.handle}</h2>
              <p className="text-sm text-gray-500">{nicheLabel(stats.niche)}</p>
              <p className="text-xs text-gray-400 mt-0.5">{stats.platform === "instagram" ? "Instagram" : "TikTok"}</p>
            </div>
          </div>
          <button onClick={onReset} className="text-xs text-gray-400 hover:text-gray-600 transition-colors">
            Analyze another →
          </button>
        </div>

        {/* Follower row */}
        <div className="mt-5 flex gap-10">
          {[
            { label: "Followers", value: fmt(stats.followers) },
            { label: "Following", value: fmt(stats.following) },
            { label: "Posts", value: String(stats.posts_analyzed) },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-2xl font-black text-gray-900">{value}</p>
              <p className="text-xs text-gray-400">{label}</p>
            </div>
          ))}
        </div>

        {/* ER progress bar */}
        <div className="mt-5">
          <div className="flex justify-between text-xs text-gray-400 mb-1.5">
            <span>Engagement Score</span>
            <span className="font-semibold text-violet-600">{(stats.avg_er * 100).toFixed(2)}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 to-indigo-500"
              style={{ width: `${Math.min(100, stats.avg_er * 500)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-3">
        {statCards.map(({ icon, label, value, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-gray-100 p-5 text-center">
            <div className="text-2xl mb-2">{icon}</div>
            <p className={`text-2xl font-black ${color}`}>{value}</p>
            <p className="text-xs text-gray-400 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Format performance */}
      {stats.format_breakdown.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-sm font-bold text-gray-800 mb-4">Format Performance</p>
          <div className="space-y-2">
            {stats.format_breakdown.map(f => (
              <HorizontalBar
                key={f.format}
                label={f.format.charAt(0).toUpperCase() + f.format.slice(1)}
                value={f.avg_er}
                max={stats.format_breakdown[0].avg_er}
                count={f.count}
              />
            ))}
          </div>
        </div>
      )}

      {/* Hook type performance */}
      {stats.hook_breakdown.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-sm font-bold text-gray-800 mb-4">Hook Type Performance</p>
          <div className="space-y-2">
            {stats.hook_breakdown.map(h => (
              <HorizontalBar
                key={h.hook_type}
                label={h.hook_type.charAt(0).toUpperCase() + h.hook_type.slice(1)}
                value={h.avg_er}
                max={stats.hook_breakdown[0].avg_er}
                count={h.count}
              />
            ))}
          </div>
        </div>
      )}

      {/* Best posting hours */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <p className="text-sm font-bold text-gray-800 mb-4">Best Posting Hours</p>
        <HourHeatmap data={stats.hourly_engagement} />
      </div>

      {/* Top posts */}
      {stats.top_posts.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-sm font-bold text-gray-800 mb-4">Top Performing Posts</p>
          <div className="divide-y divide-gray-50">
            {stats.top_posts.map((post, i) => (
              <div key={post.post_id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                <span className="text-xl font-black text-gray-200 w-6 shrink-0 mt-0.5">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 line-clamp-2">{post.caption || "(no caption)"}</p>
                  <div className="flex gap-3 mt-1.5">
                    <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{post.format}</span>
                    <span className="text-xs font-semibold text-violet-600">{(post.engagement_rate * 100).toFixed(2)}% ER</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

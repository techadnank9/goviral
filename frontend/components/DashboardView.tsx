"use client";
import { AccountStats } from "@/lib/types";
import { HorizontalBar } from "./HorizontalBar";
import { HourHeatmap } from "./HourHeatmap";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface Props {
  stats: AccountStats;
  onReset: () => void;
}

const FORMAT_COLORS: Record<string, string> = {
  reel: "bg-violet-500",
  video: "bg-indigo-500",
  carousel: "bg-blue-500",
  image: "bg-sky-400",
};

const HOOK_COLORS: Record<string, string> = {
  list: "bg-emerald-500",
  pov: "bg-teal-500",
  confession: "bg-amber-500",
  question: "bg-orange-400",
  command: "bg-red-400",
  statement: "bg-gray-400",
  other: "bg-gray-300",
};

export function DashboardView({ stats, onReset }: Props) {
  const maxFormatEr = Math.max(...stats.format_breakdown.map((f) => f.avg_er), 0.01);
  const maxHookEr = Math.max(...stats.hook_breakdown.map((h) => h.avg_er), 0.01);

  return (
    <div className="w-full max-w-2xl space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">@{stats.handle}</h2>
          <p className="text-sm text-gray-500">
            {stats.posts_analyzed} posts · {stats.niche.replace(/_/g, " ")}
          </p>
        </div>
        <button onClick={onReset} className="text-sm text-gray-400 hover:text-gray-600 underline">
          Analyze another
        </button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Format Performance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 pt-3">
          {stats.format_breakdown.length === 0 ? (
            <p className="text-sm text-gray-400">Not enough data</p>
          ) : (
            stats.format_breakdown.map((f) => (
              <HorizontalBar
                key={f.format}
                label={f.format}
                value={f.avg_er}
                maxValue={maxFormatEr}
                count={f.count}
                color={FORMAT_COLORS[f.format] ?? "bg-violet-500"}
              />
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Hook Type Performance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 pt-3">
          {stats.hook_breakdown.length === 0 ? (
            <p className="text-sm text-gray-400">Not enough data</p>
          ) : (
            stats.hook_breakdown.map((h) => (
              <HorizontalBar
                key={h.hook_type}
                label={h.hook_type}
                value={h.avg_er}
                maxValue={maxHookEr}
                count={h.count}
                color={HOOK_COLORS[h.hook_type] ?? "bg-gray-400"}
              />
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Best Posting Hours</CardTitle>
        </CardHeader>
        <CardContent className="pt-3">
          <HourHeatmap data={stats.hourly_engagement} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Performing Posts</CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-gray-50 pt-2">
          {stats.top_posts.map((p, i) => (
            <div key={p.post_id} className="py-3 flex gap-3">
              <span className="text-2xl font-black text-gray-200 w-6 shrink-0">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800 line-clamp-2">{p.caption}</p>
                <div className="flex gap-2 mt-1">
                  <span className="text-xs text-gray-400 capitalize">{p.format}</span>
                  <span className="text-xs text-gray-300">·</span>
                  <span className="text-xs text-gray-400 capitalize">{p.hook_type.replace(/_/g, " ")} hook</span>
                  <span className="text-xs text-gray-300">·</span>
                  <span className="text-xs font-medium text-violet-600">{p.engagement_rate.toFixed(2)}% ER</span>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

"use client";
import { ProgressEvent } from "@/lib/types";
import { Progress } from "@/components/ui/progress";

interface Props {
  stages: ProgressEvent[];
}

export function LoadingProgress({ stages }: Props) {
  const latest = stages[stages.length - 1];
  const pct = latest?.pct ?? 0;

  return (
    <div className="w-full max-w-md space-y-4">
      <Progress value={pct} className="h-2" />
      <div className="space-y-2">
        {stages.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            <span className={i === stages.length - 1 ? "animate-pulse" : ""}>
              {i === stages.length - 1 ? "⏳" : "✓"}
            </span>
            <span className={i === stages.length - 1 ? "text-gray-900 font-medium" : "text-gray-400"}>
              {s.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

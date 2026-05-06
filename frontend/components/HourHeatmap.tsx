import { HourStat } from "@/lib/types";

interface Props {
  data: HourStat[];
}

function formatHour(h: number): string {
  if (h === 0) return "12a";
  if (h === 12) return "12p";
  return h < 12 ? `${h}a` : `${h - 12}p`;
}

export function HourHeatmap({ data }: Props) {
  const maxEr = Math.max(...data.map((d) => d.avg_er), 0.01);
  return (
    <div className="space-y-2">
      <div className="flex gap-0.5">
        {data.map((d) => {
          const intensity = maxEr > 0 ? d.avg_er / maxEr : 0;
          return (
            <div key={d.hour} className="flex-1 flex flex-col items-center gap-0.5 group relative">
              <div
                className="w-full h-8 rounded-sm bg-violet-600 transition-all"
                style={{ opacity: Math.max(0.05, intensity) }}
              />
              <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                {formatHour(d.hour)}: {d.avg_er.toFixed(2)}%
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>12am</span>
        <span>6am</span>
        <span>12pm</span>
        <span>6pm</span>
        <span>11pm</span>
      </div>
    </div>
  );
}

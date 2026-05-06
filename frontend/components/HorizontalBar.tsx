interface Props {
  label: string;
  value: number;
  maxValue: number;
  count: number;
  color?: string;
}

export function HorizontalBar({ label, value, maxValue, count, color = "bg-violet-500" }: Props) {
  const pct = maxValue > 0 ? (value / maxValue) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-24 shrink-0 capitalize">
        {label.replace(/_/g, " ")}
      </span>
      <div className="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-900 w-16 text-right shrink-0">
        {value.toFixed(2)}% <span className="text-gray-400 font-normal text-xs">({count})</span>
      </span>
    </div>
  );
}

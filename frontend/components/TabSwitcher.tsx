"use client";
import { AppMode } from "@/lib/types";

interface Props {
  mode: AppMode;
  onSwitch: (mode: AppMode) => void;
}

export function TabSwitcher({ mode, onSwitch }: Props) {
  return (
    <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-full max-w-md mb-8">
      <button
        onClick={() => onSwitch("recommendation")}
        className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
          mode === "recommendation"
            ? "bg-white text-gray-900 shadow-sm"
            : "text-gray-500 hover:text-gray-700"
        }`}
      >
        Get Recommendation
      </button>
      <button
        onClick={() => onSwitch("dashboard")}
        className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
          mode === "dashboard"
            ? "bg-white text-gray-900 shadow-sm"
            : "text-gray-500 hover:text-gray-700"
        }`}
      >
        Analyze Account
      </button>
    </div>
  );
}

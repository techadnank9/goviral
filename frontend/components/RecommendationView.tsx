"use client";
import { useState } from "react";
import { Recommendation } from "@/lib/types";

interface Props {
  recommendation: Recommendation;
  onRegenerate: () => void;
}

export function RecommendationView({ recommendation: rec, onRegenerate }: Props) {
  const [copied, setCopied] = useState(false);

  const top = rec.captions[0];

  const copy = async () => {
    await navigator.clipboard.writeText(top.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-xl space-y-4">

      {/* What to post */}
      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-6 text-white">
        <p className="text-xs uppercase tracking-widest opacity-60 mb-2">Post this next</p>
        <h2 className="text-2xl font-black leading-tight">{rec.recommended_format}</h2>
        <p className="text-lg font-medium mt-1 opacity-90">{rec.recommended_topic}</p>
        <p className="text-sm opacity-60 mt-3">🕐 {rec.best_posting_time}</p>
      </div>

      {/* Why */}
      <p className="text-sm text-gray-600 leading-relaxed px-1">{rec.why_this}</p>

      {/* Caption */}
      <div className="bg-white border border-gray-100 rounded-2xl p-5 space-y-4">
        <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{top.text}</p>

        {rec.suggested_hashtags.length > 0 && (
          <p className="text-xs text-gray-400">
            {rec.suggested_hashtags.slice(0, 6).map(h => h.startsWith("#") ? h : `#${h}`).join(" ")}
          </p>
        )}

        <div className="flex items-center gap-3 pt-1">
          <button
            onClick={copy}
            className="text-xs bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {copied ? "Copied!" : "Copy caption"}
          </button>
          <button
            onClick={onRegenerate}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            Try another angle →
          </button>
        </div>
      </div>

    </div>
  );
}

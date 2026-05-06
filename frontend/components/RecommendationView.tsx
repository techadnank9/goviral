"use client";
import { useState } from "react";
import { Recommendation } from "@/lib/types";
import { CaptionCard } from "./CaptionCard";
import { Button } from "@/components/ui/button";

interface Props {
  recommendation: Recommendation;
  onRegenerate: () => void;
}

export function RecommendationView({ recommendation: rec, onRegenerate }: Props) {
  const [showWhy, setShowWhy] = useState(false);

  return (
    <div className="w-full max-w-2xl space-y-6">
      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-6 text-white space-y-1">
        <p className="text-xs uppercase tracking-widest opacity-75">Post This</p>
        <h2 className="text-2xl font-bold">{rec.recommended_format.toUpperCase()}</h2>
        <p className="text-lg font-medium opacity-90">{rec.recommended_topic}</p>
        <p className="text-sm opacity-75">{rec.best_posting_time}</p>
      </div>

      <div className="flex gap-4 text-center">
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-2xl font-bold text-violet-600">{rec.posts_analyzed}</p>
          <p className="text-xs text-gray-500">posts analyzed</p>
        </div>
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-2xl font-bold text-violet-600">{rec.confidence_pct}%</p>
          <p className="text-xs text-gray-500">confidence</p>
        </div>
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-2xl font-bold text-violet-600">{rec.captions.length}</p>
          <p className="text-xs text-gray-500">caption options</p>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold text-gray-700">Pick your caption</h3>
        {rec.captions.map((c, i) => (
          <CaptionCard key={i} caption={c} rank={i} />
        ))}
      </div>

      {rec.suggested_hashtags.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-700 mb-2">Hashtags</h3>
          <div className="flex flex-wrap gap-2">
            {rec.suggested_hashtags.map((h, i) => (
              <span key={i} className="text-sm bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                {h.startsWith("#") ? h : `#${h}`}
              </span>
            ))}
          </div>
        </div>
      )}

      <div>
        <button
          onClick={() => setShowWhy(!showWhy)}
          className="text-sm text-gray-500 hover:text-gray-800 underline"
        >
          {showWhy ? "Hide" : "Why will this work?"}
        </button>
        {showWhy && (
          <p className="mt-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{rec.why_this}</p>
        )}
      </div>

      <Button variant="outline" onClick={onRegenerate} className="w-full">
        Generate different angle →
      </Button>
    </div>
  );
}

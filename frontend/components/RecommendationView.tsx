"use client";
import { useState } from "react";
import { Recommendation } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface Props {
  recommendation: Recommendation;
  onRegenerate: () => void;
}

function cleanPattern(raw: string): string {
  // Strip "Insufficient Data - " prefix if present
  return raw.replace(/^Insufficient Data\s*[-–]\s*/i, "").trim();
}

function viralityColor(pct: number): string {
  if (pct >= 85) return "text-green-600";
  if (pct >= 70) return "text-amber-600";
  return "text-orange-500";
}

export function RecommendationView({ recommendation: rec, onRegenerate }: Props) {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(0);

  const copy = async (text: string, idx: number) => {
    await navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const top = rec.captions[0];

  return (
    <div className="w-full max-w-2xl space-y-5">

      {/* Step 1: What to post */}
      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-6 text-white">
        <p className="text-xs uppercase tracking-widest opacity-60 mb-1">Step 1 — What to post</p>
        <h2 className="text-2xl font-black leading-tight">{rec.recommended_format}</h2>
        <p className="text-lg font-medium mt-1 opacity-95">{rec.recommended_topic}</p>
        <p className="text-sm opacity-60 mt-2">🕐 {rec.best_posting_time}</p>
      </div>

      {/* Step 2: Why this */}
      <Card>
        <CardContent className="p-4">
          <p className="text-xs uppercase tracking-widest text-violet-500 font-semibold mb-2">Step 2 — Why this will work</p>
          <p className="text-sm text-gray-700 leading-relaxed">{rec.why_this}</p>
          {rec.posts_analyzed > 0 && (
            <p className="text-xs text-gray-400 mt-2">Based on {rec.posts_analyzed} posts · {rec.confidence_pct}% confidence</p>
          )}
        </CardContent>
      </Card>

      {/* Step 3: Content angles */}
      <div>
        <p className="text-xs uppercase tracking-widest text-violet-500 font-semibold mb-3">Step 3 — Pick a content angle + caption</p>
        <div className="space-y-2">
          {rec.captions.map((c, i) => {
            const isOpen = expandedIdx === i;
            const pattern = cleanPattern(c.pattern_used);
            return (
              <Card
                key={i}
                className={`border transition-all cursor-pointer ${i === 0 ? "border-violet-300" : "border-gray-100"}`}
                onClick={() => setExpandedIdx(isOpen ? null : i)}
              >
                <CardContent className="p-4">
                  {/* Header row */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {i === 0 && <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full font-medium">Best angle</span>}
                        <span className={`text-xs font-semibold ${viralityColor(c.predicted_virality_pct)}`}>
                          {c.predicted_virality_pct}% virality
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-800">{pattern}</p>
                    </div>
                    <span className="text-gray-300 text-lg shrink-0">{isOpen ? "−" : "+"}</span>
                  </div>

                  {/* Expanded: caption + copy */}
                  {isOpen && (
                    <div className="mt-3 pt-3 border-t border-gray-100 space-y-3">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed font-mono">
                        {c.text}
                      </p>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={(e) => { e.stopPropagation(); copy(c.text, i); }}
                          className="text-xs bg-violet-600 hover:bg-violet-700 text-white px-3 py-1.5 rounded-lg font-medium transition-colors"
                        >
                          {copiedIdx === i ? "Copied!" : "Copy caption"}
                        </button>
                        {c.rationale && (
                          <p className="text-xs text-gray-400 italic">{c.rationale}</p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Hashtags */}
      {rec.suggested_hashtags.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <p className="text-xs uppercase tracking-widest text-violet-500 font-semibold mb-3">Hashtags</p>
            <div className="flex flex-wrap gap-2">
              {rec.suggested_hashtags.map((h, i) => (
                <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">
                  {h.startsWith("#") ? h : `#${h}`}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Button variant="outline" onClick={onRegenerate} className="w-full text-gray-600">
        Try a different angle →
      </Button>
    </div>
  );
}

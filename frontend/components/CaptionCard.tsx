"use client";
import { useState } from "react";
import { CaptionVariant } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface Props {
  caption: CaptionVariant;
  rank: number;
}

function viralityColor(pct: number): string {
  if (pct >= 85) return "bg-green-100 text-green-800 border-green-200";
  if (pct >= 70) return "bg-yellow-100 text-yellow-800 border-yellow-200";
  return "bg-orange-100 text-orange-800 border-orange-200";
}

export function CaptionCard({ caption, rank }: Props) {
  const [copied, setCopied] = useState(false);
  const [showRationale, setShowRationale] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(caption.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className={`border ${rank === 0 ? "border-violet-300 shadow-md" : "border-gray-200"}`}>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {rank === 0 && <span className="text-yellow-500">⭐</span>}
            <Badge className={viralityColor(caption.predicted_virality_pct)}>
              {caption.predicted_virality_pct}% predicted virality
            </Badge>
          </div>
          <span className="text-xs text-gray-400 italic">{caption.pattern_used}</span>
        </div>

        <p className="font-mono text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
          {caption.text}
        </p>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={copy}>
            {copied ? "Copied!" : "Copy"}
          </Button>
          <button
            onClick={() => setShowRationale(!showRationale)}
            className="text-xs text-gray-400 hover:text-gray-600 underline"
          >
            {showRationale ? "Hide why" : "Why this?"}
          </button>
        </div>

        {showRationale && (
          <p className="text-xs text-gray-500 italic border-t pt-2">{caption.rationale}</p>
        )}
      </CardContent>
    </Card>
  );
}

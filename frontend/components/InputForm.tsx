"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Platform } from "@/lib/types";

interface Props {
  onSubmit: (handle: string, platform: Platform, topic: string) => void;
  loading: boolean;
}

export function InputForm({ onSubmit, loading }: Props) {
  const [handle, setHandle] = useState("");
  const [platform, setPlatform] = useState<Platform>("instagram");
  const [topic, setTopic] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!handle.trim()) return;
    onSubmit(handle.trim(), platform, topic.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-md">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setPlatform("instagram")}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            platform === "instagram"
              ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Instagram
        </button>
        <button
          type="button"
          onClick={() => setPlatform("tiktok")}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            platform === "tiktok"
              ? "bg-black text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          TikTok
        </button>
      </div>

      <Input
        placeholder="@yourhandle"
        value={handle}
        onChange={(e) => setHandle(e.target.value)}
        className="text-lg"
        disabled={loading}
      />

      <Input
        placeholder="Optional: what's on your mind today?"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        disabled={loading}
      />

      <Button
        type="submit"
        disabled={loading || !handle.trim()}
        className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-semibold py-3 text-base"
      >
        {loading ? "Analyzing..." : "Engineer my next post →"}
      </Button>
    </form>
  );
}

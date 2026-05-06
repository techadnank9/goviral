"use client";
import { useState, useCallback } from "react";
import { AppState, Platform, ProgressEvent, Recommendation } from "@/lib/types";
import { streamAnalysis } from "@/lib/api";
import { InputForm } from "@/components/InputForm";
import { LoadingProgress } from "@/components/LoadingProgress";
import { RecommendationView } from "@/components/RecommendationView";

export default function Home() {
  const [state, setState] = useState<AppState>({ phase: "input" });
  const [lastInput, setLastInput] = useState<{ handle: string; platform: Platform; topic: string } | null>(null);

  const run = useCallback(async (handle: string, platform: Platform, topic: string) => {
    setLastInput({ handle, platform, topic });
    setState({ phase: "loading", stages: [] });

    await streamAnalysis(
      handle,
      platform,
      topic || undefined,
      (event: ProgressEvent) => {
        setState((prev) =>
          prev.phase === "loading"
            ? { phase: "loading", stages: [...prev.stages, event] }
            : prev
        );
      },
      (rec: Recommendation) => {
        setState({ phase: "result", recommendation: rec });
      },
      (msg: string) => {
        setState({ phase: "error", message: msg });
      }
    );
  }, []);

  const regenerate = useCallback(() => {
    if (lastInput) run(lastInput.handle, lastInput.platform, lastInput.topic);
  }, [lastInput, run]);

  const reset = () => setState({ phase: "input" });

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-violet-50 flex flex-col items-center justify-start pt-16 px-4 pb-16">
      <header className="text-center mb-10 space-y-2">
        <h1 className="text-4xl font-black tracking-tight text-gray-900">
          🚀 GoViral
        </h1>
        <p className="text-gray-500 text-lg">Your next post, engineered to win.</p>
      </header>

      {state.phase === "input" && (
        <InputForm onSubmit={run} loading={false} />
      )}

      {state.phase === "loading" && (
        <LoadingProgress stages={state.stages} />
      )}

      {state.phase === "result" && (
        <RecommendationView recommendation={state.recommendation} onRegenerate={regenerate} />
      )}

      {state.phase === "error" && (
        <div className="max-w-md w-full text-center space-y-4">
          <p className="text-red-600 font-medium">{state.message}</p>
          <button onClick={reset} className="text-sm text-gray-500 underline">
            Try again
          </button>
        </div>
      )}
    </main>
  );
}

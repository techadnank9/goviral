"use client";
import { useState, useCallback } from "react";
import {
  AppMode,
  AppState,
  DashboardState,
  Platform,
  ProgressEvent,
  Recommendation,
  AccountStats,
} from "@/lib/types";
import { streamAnalysis, streamStats } from "@/lib/api";
import { InputForm } from "@/components/InputForm";
import { LoadingProgress } from "@/components/LoadingProgress";
import { RecommendationView } from "@/components/RecommendationView";
import { DashboardView } from "@/components/DashboardView";
import { TabSwitcher } from "@/components/TabSwitcher";

export default function Home() {
  const [mode, setMode] = useState<AppMode>("recommendation");
  const [state, setState] = useState<AppState>({ phase: "input" });
  const [lastInput, setLastInput] = useState<{ handle: string; platform: Platform; topic: string } | null>(null);
  const [dashState, setDashState] = useState<DashboardState>({ phase: "input" });

  const runRecommendation = useCallback(async (handle: string, platform: Platform, topic: string) => {
    setLastInput({ handle, platform, topic });
    setState({ phase: "loading", stages: [] });
    await streamAnalysis(
      handle, platform, topic || undefined,
      (event: ProgressEvent) => {
        setState((prev) =>
          prev.phase === "loading" ? { phase: "loading", stages: [...prev.stages, event] } : prev
        );
      },
      (rec: Recommendation) => setState({ phase: "result", recommendation: rec }),
      (msg: string) => setState({ phase: "error", message: msg })
    );
  }, []);

  const runDashboard = useCallback(async (handle: string, platform: Platform, _topic: string) => {
    setDashState({ phase: "loading", stages: [] });
    await streamStats(
      handle, platform,
      (event: ProgressEvent) => {
        setDashState((prev) =>
          prev.phase === "loading" ? { phase: "loading", stages: [...prev.stages, event] } : prev
        );
      },
      (stats: AccountStats) => setDashState({ phase: "result", stats }),
      (msg: string) => setDashState({ phase: "error", message: msg })
    );
  }, []);

  const regenerate = useCallback(() => {
    if (lastInput) runRecommendation(lastInput.handle, lastInput.platform, lastInput.topic);
  }, [lastInput, runRecommendation]);

  const isLoading =
    (mode === "recommendation" && state.phase === "loading") ||
    (mode === "dashboard" && dashState.phase === "loading");

  const showInput =
    (mode === "recommendation" && state.phase === "input") ||
    (mode === "dashboard" && dashState.phase === "input");

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-violet-50 flex flex-col items-center justify-start pt-12 px-4 pb-16">
      <header className="text-center mb-6 space-y-1">
        <h1 className="text-4xl font-black tracking-tight text-gray-900">🚀 GoViral</h1>
        <p className="text-gray-500 text-lg">Your next post, engineered to win.</p>
      </header>

      <TabSwitcher mode={mode} onSwitch={setMode} />

      {showInput && (
        <InputForm
          onSubmit={mode === "recommendation" ? runRecommendation : runDashboard}
          loading={isLoading}
        />
      )}

      {mode === "recommendation" && state.phase === "loading" && <LoadingProgress stages={state.stages} />}
      {mode === "recommendation" && state.phase === "result" && (
        <RecommendationView recommendation={state.recommendation} onRegenerate={regenerate} />
      )}
      {mode === "recommendation" && state.phase === "error" && (
        <div className="max-w-md w-full text-center space-y-4">
          <p className="text-red-600 font-medium">{state.message}</p>
          <button onClick={() => setState({ phase: "input" })} className="text-sm text-gray-500 underline">Try again</button>
        </div>
      )}

      {mode === "dashboard" && dashState.phase === "loading" && <LoadingProgress stages={dashState.stages} />}
      {mode === "dashboard" && dashState.phase === "result" && (
        <DashboardView stats={dashState.stats} onReset={() => setDashState({ phase: "input" })} />
      )}
      {mode === "dashboard" && dashState.phase === "error" && (
        <div className="max-w-md w-full text-center space-y-4">
          <p className="text-red-600 font-medium">{dashState.message}</p>
          <button onClick={() => setDashState({ phase: "input" })} className="text-sm text-gray-500 underline">Try again</button>
        </div>
      )}
    </main>
  );
}

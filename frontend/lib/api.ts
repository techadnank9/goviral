import { AccountStats, ProgressEvent, Recommendation } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function streamAnalysis(
  handle: string,
  platform: string,
  userTopic: string | undefined,
  onProgress: (event: ProgressEvent) => void,
  onComplete: (rec: Recommendation) => void,
  onError: (msg: string) => void
): Promise<void> {
  console.log("[analyze] POST", { handle, platform, userTopic });
  const resp = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ handle, platform, user_topic: userTopic || null, stream: true }),
  });

  console.log("[analyze] response status", resp.status);
  if (!resp.ok || !resp.body) {
    onError(`Server error: ${resp.status}`);
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";

    for (const block of blocks) {
      const lines = block.split("\n");
      let eventType = "";
      let dataLine = "";
      for (const line of lines) {
        if (line.startsWith("event: ")) eventType = line.slice(7).trim();
        if (line.startsWith("data: ")) dataLine = line.slice(6);
      }
      if (!dataLine) continue;

      try {
        const parsed = JSON.parse(dataLine);
        console.log("[analyze] SSE", eventType, parsed);
        if (eventType === "progress") onProgress(parsed as ProgressEvent);
        else if (eventType === "complete") onComplete(parsed as Recommendation);
        else if (eventType === "error") onError(parsed.message ?? "Unknown error");
      } catch {
        console.warn("[analyze] bad SSE frame", block);
      }
    }
  }
}

export async function streamStats(
  handle: string,
  platform: string,
  onProgress: (event: ProgressEvent) => void,
  onComplete: (stats: AccountStats) => void,
  onError: (msg: string) => void
): Promise<void> {
  console.log("[stats] POST", { handle, platform });
  const resp = await fetch(`${API_BASE}/stats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ handle, platform, stream: true }),
  });

  console.log("[stats] response status", resp.status);
  if (!resp.ok || !resp.body) {
    onError(`Server error: ${resp.status}`);
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";
    for (const block of blocks) {
      const lines = block.split("\n");
      let eventType = "";
      let dataLine = "";
      for (const line of lines) {
        if (line.startsWith("event: ")) eventType = line.slice(7).trim();
        if (line.startsWith("data: ")) dataLine = line.slice(6);
      }
      if (!dataLine) continue;
      try {
        const parsed = JSON.parse(dataLine);
        console.log("[stats] SSE", eventType, parsed);
        if (eventType === "progress") onProgress(parsed as ProgressEvent);
        else if (eventType === "complete") onComplete(parsed as AccountStats);
        else if (eventType === "error") onError(parsed.message ?? "Unknown error");
      } catch {
        console.warn("[stats] bad SSE frame", block);
      }
    }
  }
}

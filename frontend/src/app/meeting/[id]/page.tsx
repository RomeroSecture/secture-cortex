"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AudioControls } from "@/components/dashboard/audio-controls";
import { MeetingHeader } from "@/components/dashboard/meeting-header";
import { ConversationTracker } from "@/components/insights/conversation-tracker";
import { InsightPanel } from "@/components/insights/insight-panel";
import type { InsightData } from "@/components/insights/insight-card";
import { MeetingKPIsBar } from "@/components/insights/meeting-kpis";
import { LiveTranscript } from "@/components/transcription/live-transcript";
import type { MeetingKPIs } from "@/types/agent";
import { Button } from "@/components/ui/button";
import { useAudio } from "@/hooks/use-audio";
import { useWebSocket } from "@/hooks/use-websocket";
import { apiFetch, wsUrl } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { TranscriptionSegment } from "@/types/meeting";
import type { WsMessage } from "@/types/websocket";

export default function MeetingDashboard({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: meetingId } = use(params);
  const router = useRouter();

  const [segments, setSegments] = useState<TranscriptionSegment[]>([]);
  const [previewText, setPreviewText] = useState("");
  const [insights, setInsights] = useState<InsightData[]>([]);
  const [meetingStatus, setMeetingStatus] = useState<"recording" | "ended">("recording");
  const [meetingTitle, setMeetingTitle] = useState("Untitled Meeting");
  const [activeTab, setActiveTab] = useState<"insights" | "intelligence">("insights");
  const [trackedEvents, setTrackedEvents] = useState<Array<{
    id: string; type: string; summary: string; detail: string; timestamp: string;
  }>>([]);
  const [kpis, setKpis] = useState<MeetingKPIs>({
    total_insights: 0, insights_by_type: {}, total_transcription_segments: 0,
    total_decisions: 0, total_action_items: 0, total_questions_pending: 0,
    total_commitments: 0, speaker_counts: {},
  });
  const segmentCounter = useRef(0);
  const insightCounter = useRef(0);
  const eventCounter = useRef(0);

  const token = typeof window !== "undefined" ? getToken() : null;
  const searchParams = typeof window !== "undefined"
    ? new URLSearchParams(window.location.search)
    : null;
  const projectId = searchParams?.get("project_id") || "";

  const handleWsMessage = useCallback((msg: WsMessage) => {
    if (msg.type === "transcription") {
      const payload = msg.payload as {
        speaker: string;
        text: string;
        is_final: boolean;
      };
      if (payload.is_final) {
        segmentCounter.current += 1;
        const segment: TranscriptionSegment = {
          id: `seg-${segmentCounter.current}`,
          speaker: payload.speaker,
          text: payload.text,
          is_final: true,
          timestamp: msg.timestamp || new Date().toISOString(),
        };
        setSegments((prev) => [...prev, segment]);
        setPreviewText("");
      } else {
        setPreviewText(payload.text);
      }
    } else if (msg.type === "insight") {
      const payload = msg.payload as {
        type: "alert" | "scope" | "suggestion";
        summary?: string;
        content: string;
        confidence: number;
        sources: string[];
        agent_source?: string;
        subtype?: string;
      };
      insightCounter.current += 1;
      const insight: InsightData = {
        id: `insight-${insightCounter.current}`,
        type: payload.type,
        summary: payload.summary,
        content: payload.content,
        confidence: payload.confidence,
        sources: payload.sources || [],
        agent_source: payload.agent_source,
        subtype: payload.subtype,
      };
      setInsights((prev) => [insight, ...prev]);
    } else if (msg.type === "meeting_status") {
      const status = (msg.payload as { status: string }).status;
      if (status === "ended") setMeetingStatus("ended");
    }

    // Track conversation intelligence events from insight subtypes
    const payload = msg.payload as Record<string, unknown> | undefined;
    const subtype = payload?.subtype as string | undefined;
    if (
      msg.type === "insight" &&
      subtype &&
      ["decision_detected", "action_item", "question_pending",
       "commitment_detected", "jargon_translation", "momentum_alert"
      ].includes(subtype)
    ) {
      eventCounter.current += 1;
      setTrackedEvents((prev) => [{
        id: `evt-${eventCounter.current}`,
        type: subtype,
        summary: (payload?.summary as string) || "",
        detail: (payload?.content as string) || "",
        timestamp: (msg.timestamp as string) || new Date().toISOString(),
      }, ...prev]);

      // Update KPI counters
      setKpis((prev) => {
        const next = { ...prev };
        if (subtype === "decision_detected") next.total_decisions += 1;
        if (subtype === "action_item") next.total_action_items += 1;
        if (subtype === "question_pending") next.total_questions_pending += 1;
        if (subtype === "commitment_detected") next.total_commitments += 1;
        return next;
      });
    }

    // Track insight count for KPIs
    if (msg.type === "insight") {
      setKpis((prev) => ({
        ...prev,
        total_insights: prev.total_insights + 1,
      }));
    }
  }, []);

  // Build WS URL — only include project_id if present
  const wsParams = new URLSearchParams();
  if (token) wsParams.set("token", token);
  if (projectId) wsParams.set("project_id", projectId);

  const { isConnected, send } = useWebSocket({
    url: wsUrl(`/ws/meeting/${meetingId}?${wsParams.toString()}`),
    onMessage: handleWsMessage,
  });

  const handleAudioChunk = useCallback(
    (channel: "mic" | "tab", audioBase64: string) => {
      send({
        type: "audio_chunk",
        payload: { channel, audio: audioBase64 },
      });
    },
    [send]
  );

  const handleFeedback = useCallback(
    async (insightId: string, rating: "useful" | "not_useful" | "dismissed") => {
      if (rating === "dismissed") {
        setInsights((prev) => prev.filter((i) => i.id !== insightId));
      }
      try {
        await apiFetch(`/api/v1/insights/${insightId}/feedback`, {
          method: "POST",
          token: token ?? undefined,
          body: JSON.stringify({ rating }),
        });
      } catch {
        /* silent */
      }
    },
    [token]
  );

  const { isCapturing, hasMic, hasTab, startCapture, stopCapture, error } = useAudio({
    onAudioChunk: handleAudioChunk,
  });

  const handleEndMeeting = useCallback(async () => {
    // Stop audio capture
    stopCapture();
    // Tell backend to end meeting via WS
    send({ type: "end_meeting", payload: {} });
    // Also end via REST API
    if (token && projectId) {
      await apiFetch(`/api/v1/projects/${projectId}/meetings/${meetingId}/end`, {
        method: "POST",
        token,
      }).catch(() => {});
    }
    setMeetingStatus("ended");
  }, [stopCapture, send, token, projectId, meetingId]);

  const handleRename = useCallback(
    async (newTitle: string) => {
      if (!token || !projectId) return;
      try {
        await apiFetch(`/api/v1/projects/${projectId}/meetings/${meetingId}`, {
          method: "PATCH",
          token,
          body: JSON.stringify({ title: newTitle }),
        });
        setMeetingTitle(newTitle);
      } catch {
        /* silent */
      }
    },
    [token, projectId, meetingId]
  );

  // Auto-redirect after meeting ends
  useEffect(() => {
    if (meetingStatus === "ended" && projectId) {
      const timer = setTimeout(() => router.push(`/projects/${projectId}`), 4000);
      return () => clearTimeout(timer);
    }
  }, [meetingStatus, projectId, router]);

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Top: Meeting header */}
      <MeetingHeader
        title={meetingTitle}
        status={meetingStatus}
        startedAt={new Date().toISOString()}
        isWsConnected={isConnected}
        onRename={handleRename}
        projectId={projectId}
      />

      {/* Ended overlay */}
      {meetingStatus === "ended" && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-background/90 backdrop-blur-sm">
          <div className="animate-fade-in-up text-center">
            <h2 className="text-lg font-medium text-foreground">Reunion finalizada</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Guardando transcripcion e insights...
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Redirigiendo en unos segundos
            </p>
          </div>
        </div>
      )}

      {/* KPIs bar */}
      {meetingStatus === "recording" && kpis.total_insights > 0 && (
        <MeetingKPIsBar kpis={kpis} />
      )}

      {/* Main: Transcript + Insights */}
      <div className="flex flex-1 gap-1 overflow-hidden p-1">
        {/* Left — Transcript */}
        <div className="flex flex-1 flex-col rounded-lg bg-surface/50">
          <div className="px-4 py-2">
            <h2 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Transcripcion en vivo
            </h2>
          </div>
          <LiveTranscript segments={segments} preview={previewText} />
        </div>

        {/* Right — Insights + Intelligence tabs */}
        <div className="flex w-[380px] flex-col rounded-lg bg-surface/30">
          {/* Tab switcher */}
          <div className="flex border-b border-border/30 px-3 pt-1">
            <button
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                activeTab === "insights"
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
              onClick={() => setActiveTab("insights")}
            >
              Copiloto IA
              {insights.length > 0 && (
                <span className="ml-1.5 text-[10px] text-muted-foreground">
                  {insights.length}
                </span>
              )}
            </button>
            <button
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                activeTab === "intelligence"
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
              onClick={() => setActiveTab("intelligence")}
            >
              Inteligencia
              {trackedEvents.length > 0 && (
                <span className="ml-1.5 text-[10px] text-muted-foreground">
                  {trackedEvents.length}
                </span>
              )}
            </button>
          </div>

          {/* Tab content */}
          {activeTab === "insights" ? (
            <InsightPanel
              insights={insights}
              isRecording={meetingStatus === "recording"}
              onFeedback={handleFeedback}
            />
          ) : (
            <ConversationTracker events={trackedEvents} />
          )}
        </div>
      </div>

      {/* Bottom: Audio controls + End Meeting */}
      <div className="flex h-12 items-center justify-between rounded-t-lg bg-surface/50 px-4">
        <AudioControls
          isCapturing={isCapturing}
          hasMic={hasMic}
          hasTab={hasTab}
          onStart={startCapture}
          onStop={stopCapture}
          error={error}
        />
        {meetingStatus === "recording" && (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-xs text-destructive hover:bg-destructive/10 hover:text-destructive"
            onClick={handleEndMeeting}
          >
            Finalizar reunion
          </Button>
        )}
      </div>
    </div>
  );
}

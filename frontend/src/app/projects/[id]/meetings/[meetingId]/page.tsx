"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { InsightCard } from "@/components/insights/insight-card";
import { MeetingOutputsPanel } from "@/components/insights/meeting-outputs";
import type { MeetingFull, InsightItem, TranscriptionSegment } from "@/types/project";

const SPEAKER_COLORS: Record<string, string> = {
  "Speaker 0": "text-foreground",
  "Speaker 1": "text-cortex-suggestion",
  "Speaker 2": "text-cortex-alert",
  "Speaker 3": "text-cortex-scope",
  "Speaker 4": "text-destructive",
};

const SPEAKER_BG: Record<string, string> = {
  "Speaker 0": "bg-foreground/5 border-foreground/10",
  "Speaker 1": "bg-cortex-suggestion/5 border-cortex-suggestion/10",
  "Speaker 2": "bg-cortex-alert/5 border-cortex-alert/10",
  "Speaker 3": "bg-cortex-scope/5 border-cortex-scope/10",
  "Speaker 4": "bg-destructive/5 border-destructive/10",
};

function getSpeakerColor(speaker: string): string {
  return SPEAKER_COLORS[speaker] || "text-muted-foreground";
}

function getSpeakerBg(speaker: string): string {
  return SPEAKER_BG[speaker] || "bg-muted/50 border-border";
}

function formatDuration(startedAt: string, endedAt: string | null): string {
  if (!endedAt) return "En curso";
  const start = new Date(startedAt).getTime();
  const end = new Date(endedAt).getTime();
  const diffMs = end - start;
  const minutes = Math.floor(diffMs / 60000);
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (hours > 0) {
    return `${hours}h ${remainingMinutes}min`;
  }
  return `${minutes}min`;
}

export default function MeetingDetailPage({
  params,
}: {
  params: Promise<{ id: string; meetingId: string }>;
}) {
  const { id, meetingId } = use(params);
  const router = useRouter();

  const [meeting, setMeeting] = useState<MeetingFull | null>(null);
  const [insights, setInsights] = useState<InsightItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = getToken();

  const loadData = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const [meetingRes, insightsRes] = await Promise.all([
        apiFetch<MeetingFull>(
          `/api/v1/projects/${id}/meetings/${meetingId}/full`,
          { token }
        ),
        apiFetch<{ data: InsightItem[] }>(
          `/api/v1/projects/${id}/meetings/${meetingId}/insights`,
          { token }
        ).catch(() => ({ data: [] as InsightItem[] })),
      ]);

      setMeeting(meetingRes);
      setInsights(insightsRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar reunion");
    } finally {
      setLoading(false);
    }
  }, [id, meetingId, token, router]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleFeedback(insightId: string, rating: "useful" | "not_useful" | "dismissed") {
    if (!token) return;
    try {
      await apiFetch(
        `/api/v1/projects/${id}/meetings/${meetingId}/insights/${insightId}/feedback`,
        {
          method: "POST",
          token,
          body: JSON.stringify({ rating }),
        }
      );
    } catch {
      // Silently fail feedback — non-critical
    }
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando reunion...</p>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-destructive">{error || "Reunion no encontrada"}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <Link
          href={`/projects/${id}/meetings`}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          &larr; Volver a reuniones
        </Link>
        <div className="mt-3 flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {meeting.title || `Reunion ${meeting.meeting_id.slice(0, 8)}`}
          </h1>
          {meeting.status === "recording" ? (
            <span className="inline-flex items-center gap-1.5 rounded-md bg-destructive/10 px-2.5 py-0.5 text-xs font-medium text-destructive">
              <span className="h-1.5 w-1.5 animate-pulse-recording rounded-full bg-destructive" />
              En curso
            </span>
          ) : (
            <span className="rounded-md bg-muted px-2.5 py-0.5 text-xs text-muted-foreground">
              Finalizada
            </span>
          )}
        </div>
        <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
          <span>{new Date(meeting.started_at).toLocaleString()}</span>
          <span className="text-border">&middot;</span>
          <span>{formatDuration(meeting.started_at, meeting.ended_at)}</span>
          <span className="text-border">&middot;</span>
          <span>
            {meeting.insight_count} insight{meeting.insight_count !== 1 ? "s" : ""}
          </span>
        </div>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      <div className="h-px bg-border" />

      {/* Two-column layout: transcription (2/3) + insights (1/3) */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Transcription */}
        <div className="lg:col-span-2">
          <h2 className="mb-3 text-base font-semibold text-foreground">Transcripcion</h2>
          <div className="rounded-xl border border-border bg-card">
            <div className="max-h-[600px] overflow-y-auto p-4">
              {meeting.transcription.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Sin segmentos de transcripcion registrados.
                </p>
              ) : (
                <div className="space-y-2">
                  {meeting.transcription.map((seg: TranscriptionSegment) => (
                    <div
                      key={seg.id}
                      className={`rounded-lg border px-3 py-2 transition-opacity ${getSpeakerBg(seg.speaker)} ${
                        seg.is_final ? "opacity-100" : "opacity-50"
                      }`}
                    >
                      <span
                        className={`text-xs font-semibold ${getSpeakerColor(seg.speaker)}`}
                      >
                        {seg.speaker}
                      </span>
                      <p className="mt-0.5 text-sm leading-relaxed text-foreground">
                        {seg.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Insights */}
        <div>
          <h2 className="mb-3 text-base font-semibold text-foreground">
            Insights ({insights.length})
          </h2>
          {insights.length === 0 ? (
            <div className="rounded-xl border border-border bg-card p-6 text-center">
              <p className="text-sm text-muted-foreground">
                Sin insights generados para esta reunion.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {insights.map((insight) => (
                <InsightCard
                  key={insight.id}
                  insight={{
                    id: insight.id,
                    type: insight.type,
                    content: insight.content,
                    confidence: insight.confidence,
                    sources: insight.sources,
                    agent_source: insight.agent_source,
                    subtype: insight.insight_subtype,
                  }}
                  onFeedback={handleFeedback}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Post-meeting outputs section */}
      {meeting.status === "ended" && token && (
        <>
          <div className="mt-8 h-px bg-border" />
          <div className="mt-6">
            <h2 className="mb-3 text-base font-semibold text-foreground">
              Outputs Post-Reunion
            </h2>
            <div className="rounded-xl border border-border bg-card">
              <MeetingOutputsPanel
                projectId={id}
                meetingId={meetingId}
                token={token}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

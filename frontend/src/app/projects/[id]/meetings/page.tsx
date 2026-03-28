"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { MeetingItem } from "@/types/project";

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

export default function MeetingHistoryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingMeeting, setStartingMeeting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = getToken();

  const loadMeetings = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const res = await apiFetch<{ data: MeetingItem[] }>(
        `/api/v1/projects/${id}/meetings`,
        { token }
      );
      setMeetings(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar reuniones");
    } finally {
      setLoading(false);
    }
  }, [id, token, router]);

  useEffect(() => {
    loadMeetings();
  }, [loadMeetings]);

  async function handleStartMeeting() {
    if (!token) return;
    setStartingMeeting(true);
    setError(null);

    try {
      const res = await apiFetch<{ data: { id: string } }>(
        `/api/v1/projects/${id}/meetings`,
        { method: "POST", token, body: JSON.stringify({}) }
      );
      router.push(`/meeting/${res.data.id}?project_id=${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar reunion");
      setStartingMeeting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando reuniones...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-12">
      <div className="mb-8">
        <Link
          href={`/projects/${id}`}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          &larr; Volver al proyecto
        </Link>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-foreground">
          Reuniones
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Historial de reuniones y transcripciones de este proyecto.
        </p>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      <div className="mb-6 flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {meetings.length} reunion{meetings.length !== 1 ? "es" : ""}
        </p>
        <Button
          className="bg-primary text-primary-foreground hover:bg-primary/90"
          onClick={handleStartMeeting}
          disabled={startingMeeting}
        >
          {startingMeeting ? "Iniciando..." : "Nueva reunion"}
        </Button>
      </div>

      {meetings.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <p className="text-muted-foreground">
            Sin reuniones aun. Inicia una reunion para comenzar la transcripcion.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {meetings.map((meeting) => (
            <div
              key={meeting.id}
              className="group cursor-pointer rounded-xl border border-border bg-card px-5 py-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
              onClick={() =>
                router.push(`/projects/${id}/meetings/${meeting.id}`)
              }
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {meeting.title || `Reunion ${meeting.id.slice(0, 8)}`}
                  </p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {new Date(meeting.started_at).toLocaleString()}
                    <span className="mx-1.5 text-border">&middot;</span>
                    {formatDuration(meeting.started_at, meeting.ended_at)}
                  </p>
                </div>
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

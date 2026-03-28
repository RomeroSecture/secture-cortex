"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { fetchProjectAnalytics } from "@/lib/api";
import { getToken } from "@/lib/auth";

interface HealthData {
  score: number;
  trend: string;
  factors: Record<string, number>;
}

interface FreshnessData {
  file_id: string;
  filename: string;
  age_days: number;
  status: string;
}

interface GapData {
  type: string;
  message: string;
  severity: string;
}

interface KBData {
  total_chunks: number;
  file_chunks: number;
  meeting_chunks: number;
  coverage_ratio: number;
}

interface Analytics {
  health: HealthData;
  freshness: FreshnessData[];
  gaps: GapData[];
  kb_report: KBData;
}

const TREND_LABELS: Record<string, { label: string; color: string }> = {
  improving: { label: "Mejorando", color: "text-green-400" },
  stable: { label: "Estable", color: "text-yellow-400" },
  declining: { label: "Declinando", color: "text-red-400" },
};

const FRESHNESS_COLORS: Record<string, string> = {
  green: "bg-green-500",
  yellow: "bg-yellow-500",
  red: "bg-red-500",
};

export default function ProjectAnalyticsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  const token = typeof window !== "undefined" ? getToken() : null;

  const loadData = useCallback(async () => {
    if (!token) { router.replace("/login"); return; }
    try {
      const res = await fetchProjectAnalytics(id, token);
      setData(res as unknown as Analytics);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [id, token, router]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center py-20">
        <p className="text-sm text-muted-foreground">Cargando analytics...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-1 items-center justify-center py-20">
        <p className="text-sm text-muted-foreground">No se pudieron cargar los analytics.</p>
      </div>
    );
  }

  const trend = TREND_LABELS[data.health.trend] || TREND_LABELS.stable;

  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-12">
      <div className="mb-8">
        <Link
          href={`/projects/${id}`}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          &larr; Volver al proyecto
        </Link>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-foreground">
          Analytics del Proyecto
        </h1>
      </div>

      {/* Health Score */}
      <div className="mb-8 rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Salud de la Relacion
        </h2>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <span className="text-4xl font-bold tabular-nums text-foreground">
              {Math.round(data.health.score)}
            </span>
            <span className="text-lg text-muted-foreground">/100</span>
          </div>
          <div>
            <span className={`text-sm font-medium ${trend.color}`}>
              {trend.label}
            </span>
            <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
              {Object.entries(data.health.factors).map(([k, v]) => (
                <span key={k} className="rounded bg-muted px-2 py-0.5">
                  {k}: {typeof v === "number" ? Math.round(v) : v}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Gaps */}
      {data.gaps.length > 0 && (
        <div className="mb-8 space-y-2">
          <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Gaps de Conocimiento
          </h2>
          {data.gaps.map((gap, i) => (
            <div
              key={i}
              className={`rounded-lg border px-4 py-3 ${
                gap.severity === "critical"
                  ? "border-red-500/30 bg-red-500/5"
                  : "border-yellow-500/30 bg-yellow-500/5"
              }`}
            >
              <p className="text-sm text-foreground">{gap.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* KB Report */}
      <div className="mb-8 rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Base de Conocimiento
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="text-center">
            <p className="text-2xl font-semibold text-foreground">{data.kb_report.total_chunks}</p>
            <p className="text-xs text-muted-foreground">Chunks Total</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-semibold text-foreground">{data.kb_report.file_chunks}</p>
            <p className="text-xs text-muted-foreground">De Archivos</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-semibold text-foreground">{data.kb_report.meeting_chunks}</p>
            <p className="text-xs text-muted-foreground">De Reuniones</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-semibold text-foreground">{data.kb_report.coverage_ratio}</p>
            <p className="text-xs text-muted-foreground">Ratio Cobertura</p>
          </div>
        </div>
      </div>

      {/* Context Freshness */}
      {data.freshness.length > 0 && (
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Frescura del Contexto
          </h2>
          <div className="space-y-2">
            {data.freshness.map((f) => (
              <div
                key={f.file_id}
                className="flex items-center gap-3 rounded-lg bg-surface/30 px-3 py-2"
              >
                <span
                  className={`h-2 w-2 shrink-0 rounded-full ${
                    FRESHNESS_COLORS[f.status] || "bg-muted"
                  }`}
                />
                <span className="flex-1 truncate text-sm text-foreground">
                  {f.filename}
                </span>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {f.age_days}d
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiFetch, apiUrl } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { ContextFile } from "@/types/project";

const STATUS_STYLES: Record<ContextFile["status"], { label: string; className: string }> = {
  pending: { label: "Pendiente", className: "bg-cortex-alert/10 text-cortex-alert border-cortex-alert/20" },
  indexing: { label: "Indexando", className: "bg-cortex-scope/10 text-cortex-scope border-cortex-scope/20" },
  indexed: { label: "Indexado", className: "bg-cortex-suggestion/10 text-cortex-suggestion border-cortex-suggestion/20" },
  error: { label: "Error", className: "bg-destructive/10 text-destructive border-destructive/20" },
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ContextFilesPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [files, setFiles] = useState<ContextFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [reindexingId, setReindexingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const token = getToken();

  const loadFiles = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const res = await apiFetch<{ data: ContextFile[] }>(
        `/api/v1/projects/${id}/context-files`,
        { token }
      );
      setFiles(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar archivos");
    } finally {
      setLoading(false);
    }
  }, [id, token, router]);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(apiUrl(`/api/v1/projects/${id}/context-files`), {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.error?.message || body?.detail || `HTTP ${res.status}`);
      }

      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir archivo");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(fileId: string) {
    if (!token) return;

    setDeletingId(fileId);
    setError(null);
    try {
      await apiFetch(`/api/v1/projects/${id}/context-files/${fileId}`, {
        method: "DELETE",
        token,
      });
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar archivo");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleReindex(fileId: string) {
    if (!token) return;

    setReindexingId(fileId);
    setError(null);
    try {
      const res = await apiFetch<{ data: ContextFile }>(
        `/api/v1/projects/${id}/context-files/${fileId}/reindex`,
        { method: "POST", token }
      );
      setFiles((prev) =>
        prev.map((f) => (f.id === fileId ? res.data : f))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al reindexar archivo");
    } finally {
      setReindexingId(null);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando archivos...</p>
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
          Archivos de contexto
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Gestiona los documentos del proyecto usados como contexto IA en las reuniones.
        </p>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      {/* Upload area */}
      <div className="mb-6 rounded-xl border border-dashed border-border bg-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-foreground">
              {files.length} archivo{files.length !== 1 ? "s" : ""}
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, TXT, MD, DOCX soportados
            </p>
          </div>
          <div className="relative">
            <Input
              type="file"
              className="absolute inset-0 cursor-pointer opacity-0"
              onChange={handleUpload}
              disabled={uploading}
            />
            <Button
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              size="sm"
              disabled={uploading}
            >
              {uploading ? "Subiendo..." : "Subir archivo"}
            </Button>
          </div>
        </div>
      </div>

      {/* File list */}
      {files.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <p className="text-muted-foreground">
            Sin archivos aun. Sube documentos del proyecto para contexto IA.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {files.map((file) => {
            const statusConfig = STATUS_STYLES[file.status];
            return (
              <div
                key={file.id}
                className="group rounded-xl border border-border bg-card px-5 py-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">{file.filename}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {file.content_type} &middot; {formatBytes(file.file_size)} &middot;{" "}
                      {new Date(file.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={statusConfig.className}>
                      {statusConfig.label}
                    </Badge>
                    {file.status === "error" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="border-border opacity-0 transition-opacity group-hover:opacity-100"
                        disabled={reindexingId === file.id}
                        onClick={() => handleReindex(file.id)}
                      >
                        {reindexingId === file.id ? "Reintentando..." : "Reintentar"}
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
                      disabled={deletingId === file.id}
                      onClick={() => handleDelete(file.id)}
                    >
                      {deletingId === file.id ? "..." : "X"}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiFetch, apiUrl } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type {
  Project,
  ContextFile,
  Member,
  MeetingItem,
} from "@/types/project";

const STATUS_STYLES: Record<ContextFile["status"], { label: string; className: string }> = {
  pending: { label: "Pendiente", className: "bg-cortex-alert/10 text-cortex-alert border-cortex-alert/20" },
  indexing: { label: "Indexando", className: "bg-cortex-scope/10 text-cortex-scope border-cortex-scope/20" },
  indexed: { label: "Indexado", className: "bg-cortex-suggestion/10 text-cortex-suggestion border-cortex-suggestion/20" },
  error: { label: "Error", className: "bg-destructive/10 text-destructive border-destructive/20" },
};

const MEMBER_ROLE_LABELS: Record<string, string> = {
  admin: "Admin",
  tech_lead: "Tech Lead",
  developer: "Desarrollador",
  pm: "PM",
  commercial: "Comercial",
};

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [project, setProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<ContextFile[]>([]);
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [startingMeeting, setStartingMeeting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [saving, setSaving] = useState(false);

  // Add member state
  const [newMemberEmail, setNewMemberEmail] = useState("");
  const [newMemberRole, setNewMemberRole] = useState("developer");
  const [addingMember, setAddingMember] = useState(false);

  // Delete file state
  const [deletingFileId, setDeletingFileId] = useState<string | null>(null);

  const token = getToken();

  const loadData = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const [projectRes, filesRes, meetingsRes, membersRes] = await Promise.all([
        apiFetch<{ data: Project }>(`/api/v1/projects/${id}`, { token }),
        apiFetch<{ data: ContextFile[] }>(`/api/v1/projects/${id}/context-files`, {
          token,
        }).catch(() => ({ data: [] as ContextFile[] })),
        apiFetch<{ data: MeetingItem[] }>(`/api/v1/projects/${id}/meetings`, {
          token,
        }).catch(() => ({ data: [] as MeetingItem[] })),
        apiFetch<{ data: Member[] }>(`/api/v1/projects/${id}/members`, {
          token,
        }).catch(() => ({ data: [] as Member[] })),
      ]);

      setProject(projectRes.data);
      setFiles(filesRes.data);
      setMeetings(meetingsRes.data);
      setMembers(membersRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar el proyecto");
    } finally {
      setLoading(false);
    }
  }, [id, token, router]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    setUploading(true);
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

      const filesRes = await apiFetch<{ data: ContextFile[] }>(
        `/api/v1/projects/${id}/context-files`,
        { token }
      );
      setFiles(filesRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir archivo");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleStartMeeting() {
    if (!token) return;
    setStartingMeeting(true);

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

  function startEditing() {
    if (!project) return;
    setEditName(project.name);
    setEditDescription(project.description || "");
    setEditing(true);
  }

  async function handleSaveEdit() {
    if (!token || !project) return;
    setSaving(true);
    setError(null);

    try {
      const res = await apiFetch<{ data: Project }>(`/api/v1/projects/${id}`, {
        method: "PATCH",
        token,
        body: JSON.stringify({ name: editName, description: editDescription }),
      });
      setProject(res.data);
      setEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar proyecto");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteProject() {
    if (!token) return;
    const confirmed = window.confirm(
      "Seguro que deseas eliminar este proyecto? Esta accion no se puede deshacer."
    );
    if (!confirmed) return;

    try {
      await apiFetch(`/api/v1/projects/${id}`, { method: "DELETE", token });
      router.replace("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar proyecto");
    }
  }

  async function handleDeleteFile(fileId: string) {
    if (!token) return;
    setDeletingFileId(fileId);
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
      setDeletingFileId(null);
    }
  }

  async function handleAddMember() {
    if (!token || !newMemberEmail.trim()) return;
    setAddingMember(true);
    setError(null);

    try {
      await apiFetch(`/api/v1/projects/${id}/members`, {
        method: "POST",
        token,
        body: JSON.stringify({
          email: newMemberEmail.trim(),
          role: newMemberRole,
        }),
      });
      setNewMemberEmail("");
      setNewMemberRole("developer");
      // Reload members
      const membersRes = await apiFetch<{ data: Member[] }>(
        `/api/v1/projects/${id}/members`,
        { token }
      );
      setMembers(membersRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al agregar miembro");
    } finally {
      setAddingMember(false);
    }
  }

  function formatBytes(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando proyecto...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-destructive">{error || "Proyecto no encontrado"}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-12">
      {/* Back link */}
      <Link
        href="/projects"
        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        &larr; Proyectos
      </Link>

      {/* Header */}
      <div className="mt-6 mb-8">
        {editing ? (
          <div className="space-y-3">
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Nombre del proyecto"
              className="border-border bg-transparent text-lg font-semibold"
            />
            <Input
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              placeholder="Descripcion (opcional)"
              className="border-border bg-transparent"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                className="bg-primary text-primary-foreground hover:bg-primary/90"
                onClick={handleSaveEdit}
                disabled={saving || !editName.trim()}
              >
                {saving ? "Guardando..." : "Guardar"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="border-border"
                onClick={() => setEditing(false)}
                disabled={saving}
              >
                Cancelar
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-foreground">
                {project.name}
              </h1>
              {project.description && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {project.description}
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="border-border"
                onClick={startEditing}
              >
                Editar
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="border-border text-destructive hover:bg-destructive/10 hover:text-destructive"
                onClick={handleDeleteProject}
              >
                Eliminar
              </Button>
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      <div className="space-y-8">
        {/* Analytics link */}
        <Link
          href={`/projects/${id}/analytics`}
          className="flex items-center justify-between rounded-xl border border-border bg-card p-4 transition-colors hover:bg-surface-hover"
        >
          <div>
            <h3 className="text-sm font-medium text-foreground">Analytics del Proyecto</h3>
            <p className="text-xs text-muted-foreground">
              Salud de la relacion, cobertura KB, gaps de conocimiento
            </p>
          </div>
          <span className="text-muted-foreground">&rarr;</span>
        </Link>

        {/* Context Files */}
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold text-foreground">Archivos de contexto</h2>
            <div className="flex items-center gap-2">
              <Link
                href={`/projects/${id}/context`}
                className="text-sm text-muted-foreground transition-colors hover:text-primary"
              >
                Gestionar &rarr;
              </Link>
              <div className="relative">
                <Input
                  type="file"
                  className="absolute inset-0 cursor-pointer opacity-0"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
                <Button variant="outline" size="sm" className="border-border" disabled={uploading}>
                  {uploading ? "Subiendo..." : "Subir archivo"}
                </Button>
              </div>
            </div>
          </div>
          {files.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Sin archivos aun. Sube documentos del proyecto para contexto IA.
            </p>
          ) : (
            <div className="space-y-2">
              {files.map((file) => {
                const statusConfig = STATUS_STYLES[file.status];
                return (
                  <div
                    key={file.id}
                    className="group flex items-center justify-between gap-4 rounded-lg border border-border bg-background/50 px-4 py-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-foreground">{file.filename}</p>
                      <p className="text-xs text-muted-foreground">
                        {file.file_type} &middot; {formatBytes(file.file_size)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={statusConfig.className}>
                        {statusConfig.label}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(file.created_at).toLocaleDateString()}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
                        disabled={deletingFileId === file.id}
                        onClick={() => handleDeleteFile(file.id)}
                      >
                        {deletingFileId === file.id ? "..." : "X"}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Meetings */}
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold text-foreground">Reuniones</h2>
            <div className="flex items-center gap-2">
              <Link
                href={`/projects/${id}/meetings`}
                className="text-sm text-muted-foreground transition-colors hover:text-primary"
              >
                Ver todas &rarr;
              </Link>
              <Button
                size="sm"
                className="bg-primary text-primary-foreground hover:bg-primary/90"
                onClick={handleStartMeeting}
                disabled={startingMeeting}
              >
                {startingMeeting ? "Iniciando..." : "Nueva reunion"}
              </Button>
            </div>
          </div>
          {meetings.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Sin reuniones aun. Inicia una reunion para comenzar la transcripcion.
            </p>
          ) : (
            <div className="space-y-2">
              {meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className="group flex cursor-pointer items-center justify-between rounded-lg border border-border bg-background/50 px-4 py-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
                  onClick={() =>
                    router.push(`/meeting/${meeting.id}?project_id=${id}`)
                  }
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {meeting.title || `Reunion ${meeting.id.slice(0, 8)}`}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(meeting.started_at).toLocaleString()}
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
              ))}
            </div>
          )}
        </section>

        {/* Members */}
        <section className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-base font-semibold text-foreground">Miembros</h2>

          {/* Add member form — compact inline */}
          <div className="mb-4 flex items-end gap-2 rounded-lg border border-border bg-background/50 p-3">
            <div className="flex-1">
              <label className="mb-1 block text-xs text-muted-foreground">
                Email del usuario
              </label>
              <Input
                type="email"
                value={newMemberEmail}
                onChange={(e) => setNewMemberEmail(e.target.value)}
                placeholder="usuario@ejemplo.com"
                className="border-border bg-transparent"
              />
            </div>
            <div className="w-40">
              <label className="mb-1 block text-xs text-muted-foreground">
                Rol
              </label>
              <select
                value={newMemberRole}
                onChange={(e) => setNewMemberRole(e.target.value)}
                className="h-9 w-full rounded-md border border-border bg-transparent px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="admin">Admin</option>
                <option value="tech_lead">Tech Lead</option>
                <option value="developer">Desarrollador</option>
                <option value="pm">PM</option>
                <option value="commercial">Comercial</option>
              </select>
            </div>
            <Button
              size="sm"
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={handleAddMember}
              disabled={addingMember || !newMemberEmail.trim()}
            >
              {addingMember ? "Agregando..." : "Agregar"}
            </Button>
          </div>

          {members.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sin miembros asignados.</p>
          ) : (
            <div className="space-y-2">
              {members.map((member) => (
                <div
                  key={member.user_id}
                  className="group flex items-center justify-between rounded-lg border border-border bg-background/50 px-4 py-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">{member.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {member.email}
                      </p>
                    </div>
                  </div>
                  <span className="rounded-md border border-border bg-muted px-2.5 py-0.5 text-xs text-muted-foreground">
                    {MEMBER_ROLE_LABELS[member.role_in_project] || member.role_in_project}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

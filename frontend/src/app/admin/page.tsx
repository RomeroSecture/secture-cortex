"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, Users, FolderOpen, MessageSquare, Lightbulb, FileText } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";

interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: string;
  projects_count: number;
}

interface SystemStats {
  total_users: number;
  total_projects: number;
  total_meetings: number;
  total_insights: number;
  total_context_files: number;
  users_by_role: Record<string, number>;
}

interface AdminProject {
  id: string;
  name: string;
  description: string | null;
  member_count: number;
  meeting_count: number;
  created_at: string;
}

const ROLES = ["admin", "tech_lead", "developer", "pm", "commercial"] as const;

const ROLE_LABELS: Record<string, string> = {
  admin: "Admin",
  tech_lead: "Tech Lead",
  developer: "Dev",
  pm: "PM",
  commercial: "Comercial",
};

const ROLE_BADGE: Record<string, string> = {
  admin: "bg-primary/10 text-primary border-primary/20",
  tech_lead: "bg-cortex-alert/10 text-cortex-alert border-cortex-alert/20",
  developer: "bg-cortex-suggestion/10 text-cortex-suggestion border-cortex-suggestion/20",
  pm: "bg-cortex-scope/10 text-cortex-scope border-cortex-scope/20",
  commercial: "bg-muted text-muted-foreground border-border",
};

type Tab = "users" | "projects";

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("users");
  const [changingRole, setChangingRole] = useState<string | null>(null);
  const [deletingUser, setDeletingUser] = useState<string | null>(null);

  const token = getToken();

  const loadData = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const [statsRes, usersRes, projectsRes] = await Promise.all([
        apiFetch<{ data: SystemStats }>("/api/v1/admin/stats", { token }),
        apiFetch<{ data: AdminUser[] }>("/api/v1/admin/users", { token }),
        apiFetch<{ data: AdminProject[] }>("/api/v1/admin/projects", { token }),
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setProjects(projectsRes.data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudieron cargar los datos de admin."
      );
    } finally {
      setLoading(false);
    }
  }, [token, router]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRoleChange = async (userId: string, newRole: string) => {
    if (!token) return;
    setChangingRole(userId);
    try {
      await apiFetch(`/api/v1/admin/users/${userId}/role`, {
        token,
        method: "PATCH",
        body: JSON.stringify({ role: newRole }),
      });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cambiar rol");
    } finally {
      setChangingRole(null);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!token) return;
    setDeletingUser(userId);
    try {
      await apiFetch(`/api/v1/admin/users/${userId}`, {
        token,
        method: "DELETE",
      });
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      if (stats) {
        setStats({ ...stats, total_users: stats.total_users - 1 });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar usuario");
    } finally {
      setDeletingUser(null);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando panel de admin...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Panel de administracion
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Vista global del sistema
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3">
          <p className="text-sm text-destructive">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-1 text-xs text-destructive/70 underline"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <StatCard icon={<Users className="h-4 w-4" />} label="Usuarios" value={stats.total_users} />
          <StatCard icon={<FolderOpen className="h-4 w-4" />} label="Proyectos" value={stats.total_projects} />
          <StatCard icon={<MessageSquare className="h-4 w-4" />} label="Reuniones" value={stats.total_meetings} />
          <StatCard icon={<Lightbulb className="h-4 w-4" />} label="Insights" value={stats.total_insights} />
          <StatCard icon={<FileText className="h-4 w-4" />} label="Archivos" value={stats.total_context_files} />
        </div>
      )}

      {/* Roles breakdown */}
      {stats && Object.keys(stats.users_by_role).length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2">
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <span
              key={role}
              className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium ${ROLE_BADGE[role] || ROLE_BADGE.commercial}`}
            >
              {ROLE_LABELS[role] || role}
              <span className="opacity-60">{count}</span>
            </span>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-surface p-1">
        <button
          onClick={() => setTab("users")}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "users"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Usuarios ({users.length})
        </button>
        <button
          onClick={() => setTab("projects")}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "projects"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Proyectos ({projects.length})
        </button>
      </div>

      {/* Users Tab */}
      {tab === "users" && (
        <div className="space-y-2">
          {users.map((user) => (
            <div
              key={user.id}
              className="flex items-center gap-4 rounded-xl border border-border bg-card px-5 py-4 transition-all hover:border-primary/20"
            >
              {/* Avatar */}
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                {user.name.charAt(0).toUpperCase()}
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">{user.name}</p>
                <p className="truncate text-xs text-muted-foreground">{user.email}</p>
              </div>

              {/* Project count */}
              <span className="hidden text-xs text-muted-foreground sm:block">
                {user.projects_count} proyecto{user.projects_count !== 1 ? "s" : ""}
              </span>

              {/* Role selector */}
              <select
                value={user.role}
                onChange={(e) => handleRoleChange(user.id, e.target.value)}
                disabled={changingRole === user.id}
                className={`rounded-md border px-2.5 py-1.5 text-xs font-medium outline-none transition-colors ${ROLE_BADGE[user.role] || ROLE_BADGE.commercial} ${
                  changingRole === user.id ? "opacity-50" : "cursor-pointer hover:opacity-80"
                }`}
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {ROLE_LABELS[r]}
                  </option>
                ))}
              </select>

              {/* Delete button */}
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                onClick={() => {
                  if (confirm(`Eliminar a ${user.name} (${user.email})?`)) {
                    handleDeleteUser(user.id);
                  }
                }}
                disabled={deletingUser === user.id}
                title="Eliminar usuario"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Projects Tab */}
      {tab === "projects" && (
        <div className="space-y-2">
          {projects.length === 0 ? (
            <div className="rounded-xl border border-border bg-card p-12 text-center">
              <p className="text-muted-foreground">No hay proyectos en el sistema.</p>
            </div>
          ) : (
            projects.map((project) => (
              <div
                key={project.id}
                className="flex items-center gap-4 rounded-xl border border-border bg-card px-5 py-4 transition-all hover:border-primary/20 cursor-pointer"
                onClick={() => router.push(`/projects/${project.id}`)}
              >
                {/* Icon */}
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-cortex-scope/10 text-cortex-scope">
                  <FolderOpen className="h-4 w-4" />
                </div>

                {/* Info */}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">{project.name}</p>
                  {project.description && (
                    <p className="truncate text-xs text-muted-foreground">{project.description}</p>
                  )}
                </div>

                {/* Counters */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {project.member_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {project.meeting_count}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-xl border border-border bg-card px-4 py-3">
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="mt-1 text-2xl font-semibold tracking-tight text-foreground">{value}</p>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { AdminUser } from "@/types/project";

const ROLE_BADGE: Record<string, string> = {
  admin: "bg-primary/10 text-primary border-primary/20",
  tech_lead: "bg-cortex-alert/10 text-cortex-alert border-cortex-alert/20",
  developer: "bg-cortex-suggestion/10 text-cortex-suggestion border-cortex-suggestion/20",
  pm: "bg-cortex-scope/10 text-cortex-scope border-cortex-scope/20",
  commercial: "bg-muted text-muted-foreground border-border",
};

const ROLE_LABELS: Record<string, string> = {
  admin: "Admin",
  tech_lead: "Tech Lead",
  developer: "Desarrollador",
  pm: "Product Manager",
  commercial: "Comercial",
};

function getRoleBadge(role: string): string {
  return ROLE_BADGE[role] || ROLE_BADGE.commercial;
}

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = getToken();

  const loadUsers = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const res = await apiFetch<{ data: AdminUser[] }>("/api/v1/auth/users", {
        token,
      });
      setUsers(res.data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudieron cargar los usuarios. El endpoint de admin puede no estar disponible."
      );
    } finally {
      setLoading(false);
    }
  }, [token, router]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando usuarios...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Panel de administracion
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {users.length} usuario{users.length !== 1 ? "s" : ""} en el sistema
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-border bg-card p-8 text-center">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {!error && users.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <p className="text-muted-foreground">No se encontraron usuarios.</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {users.map((user) => (
            <div
              key={user.id}
              className="group rounded-xl border border-border bg-card p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30"
            >
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  {/* Avatar + Name */}
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">
                        {user.name}
                      </p>
                      <p className="truncate text-xs text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom row: role badge + project count */}
              <div className="mt-4 flex items-center justify-between">
                <span
                  className={`inline-flex rounded-md border px-2.5 py-0.5 text-xs font-medium ${getRoleBadge(user.role)}`}
                >
                  {ROLE_LABELS[user.role] || user.role}
                </span>
                <span className="text-xs text-muted-foreground">
                  {user.projects_count} proyecto{user.projects_count !== 1 ? "s" : ""}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

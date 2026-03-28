"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";
import type { UserProfile, UserRole } from "@/types/project";

const ROLES: UserRole[] = ["admin", "tech_lead", "developer", "pm", "commercial"];

const ROLE_LABELS: Record<UserRole, string> = {
  admin: "Admin",
  tech_lead: "Tech Lead",
  developer: "Desarrollador",
  pm: "Product Manager",
  commercial: "Comercial",
};

const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  admin: "Acceso total al sistema",
  tech_lead: "Liderazgo tecnico del equipo",
  developer: "Desarrollo e implementacion",
  pm: "Gestion de producto y roadmap",
  commercial: "Relacion con clientes",
};

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [selectedRole, setSelectedRole] = useState<UserRole>("developer");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [canEdit, setCanEdit] = useState(false);

  const token = getToken();

  const loadProfile = useCallback(async () => {
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const res = await apiFetch<{ data: UserProfile }>("/api/v1/auth/me", {
        token,
      });
      setProfile(res.data);
      setSelectedRole(res.data.role);
      setCanEdit(true);
    } catch {
      // Endpoint may not exist -- fall back to local user
      const localUser = getUser();
      if (localUser) {
        setProfile({
          id: localUser.id,
          email: localUser.email,
          name: localUser.name,
          role: "developer",
        });
      }
      setCanEdit(false);
    } finally {
      setLoading(false);
    }
  }, [token, router]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  async function handleSave() {
    if (!token || !canEdit) return;
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await apiFetch<{ data: UserProfile }>("/api/v1/auth/me", {
        method: "PATCH",
        token,
        body: JSON.stringify({ role: selectedRole }),
      });
      setProfile(res.data);
      setSuccess("Perfil actualizado correctamente");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando perfil...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-destructive">No se pudo cargar el perfil</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-6 py-12">
      <Link
        href="/projects"
        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        &larr; Proyectos
      </Link>

      <div className="mt-6 rounded-xl border border-border bg-card p-8">
        {/* User info header */}
        <div className="mb-8">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary text-xl font-semibold">
            {profile.name.charAt(0).toUpperCase()}
          </div>
          <h1 className="mt-4 text-2xl font-semibold tracking-tight text-foreground">
            {profile.name}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{profile.email}</p>
        </div>

        <div className="h-px bg-border" />

        {/* Role selector */}
        {canEdit ? (
          <div className="mt-6 space-y-4">
            <p className="text-sm font-medium text-muted-foreground">
              Rol en el equipo
            </p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {ROLES.map((role) => (
                <button
                  key={role}
                  type="button"
                  onClick={() => setSelectedRole(role)}
                  className={`group rounded-lg border px-4 py-3 text-left transition-all duration-200 hover:-translate-y-0.5 ${
                    selectedRole === role
                      ? "border-primary bg-primary/10 shadow-sm"
                      : "border-border bg-transparent hover:border-primary/30"
                  }`}
                >
                  <p
                    className={`text-sm font-medium ${
                      selectedRole === role
                        ? "text-primary"
                        : "text-foreground"
                    }`}
                  >
                    {ROLE_LABELS[role]}
                  </p>
                  <p className="mt-0.5 text-[11px] text-muted-foreground">
                    {ROLE_DESCRIPTIONS[role]}
                  </p>
                </button>
              ))}
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
            {success && (
              <p className="text-sm text-cortex-suggestion">{success}</p>
            )}

            <Button
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={handleSave}
              disabled={saving || selectedRole === profile.role}
            >
              {saving ? "Guardando..." : "Guardar cambios"}
            </Button>
          </div>
        ) : (
          <div className="mt-6">
            <p className="text-sm text-muted-foreground">
              Rol actual:{" "}
              <span className="font-medium text-foreground">
                {ROLE_LABELS[profile.role] || profile.role}
              </span>
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              El rol no puede editarse desde aqui (endpoint no disponible).
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

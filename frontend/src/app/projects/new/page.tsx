"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

interface CreateProjectResponse {
  data: {
    id: string;
    name: string;
  };
}

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const res = await apiFetch<CreateProjectResponse>("/api/v1/projects", {
        method: "POST",
        token,
        body: JSON.stringify({
          name,
          description: description || undefined,
        }),
      });

      router.push(`/projects/${res.data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el proyecto");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-6">
      <div className="w-full max-w-lg">
        <Link
          href="/projects"
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          &larr; Volver a proyectos
        </Link>

        <div className="mt-4 rounded-xl border border-border bg-card p-8">
          <h1 className="text-xl font-semibold tracking-tight text-foreground">
            Nuevo proyecto
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Crea un proyecto para organizar reuniones y contexto.
          </p>

          <form onSubmit={handleSubmit} className="mt-6">
            <FieldGroup>
              <Field>
                <FieldLabel>Nombre</FieldLabel>
                <Input
                  placeholder="Nombre del proyecto"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="border-border bg-transparent"
                />
              </Field>

              <Field>
                <FieldLabel>Descripcion</FieldLabel>
                <Input
                  placeholder="Breve descripcion (opcional)"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="border-border bg-transparent"
                />
              </Field>

              {error && <FieldError>{error}</FieldError>}

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  className="border-border"
                  onClick={() => router.back()}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  {loading ? "Creando..." : "Crear proyecto"}
                </Button>
              </div>
            </FieldGroup>
          </form>
        </div>
      </div>
    </div>
  );
}

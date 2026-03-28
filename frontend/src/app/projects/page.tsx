"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

interface ProjectsResponse {
  data: Project[];
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    apiFetch<ProjectsResponse>("/api/v1/projects", { token })
      .then((res) => setProjects(res.data))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load projects")
      )
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">Cargando proyectos...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight text-foreground">
          Proyectos
        </h1>
        <Link href="/projects/new">
          <Button className="bg-primary text-primary-foreground text-sm h-9 px-4">
            Nuevo Proyecto
          </Button>
        </Link>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      {projects.length === 0 && !error ? (
        <div className="rounded-xl border border-border bg-card py-16 text-center">
          <p className="text-sm text-muted-foreground">
            Sin proyectos todavia. Crea tu primer proyecto para comenzar.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {projects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`}>
              <div className="group rounded-xl border border-border bg-card p-5 transition-all hover:border-primary/30 hover:-translate-y-0.5">
                <h3 className="font-medium text-foreground group-hover:text-primary transition-colors">
                  {project.name}
                </h3>
                {project.description && (
                  <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {project.description}
                  </p>
                )}
                <p className="mt-3 text-xs text-muted-foreground">
                  {new Date(project.created_at).toLocaleDateString()}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

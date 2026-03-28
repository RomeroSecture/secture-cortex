"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field";
import { apiFetch } from "@/lib/api";
import { setToken } from "@/lib/auth";

type Mode = "login" | "register";

interface AuthResponse {
  data: {
    access_token: string;
    token_type: string;
  };
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    emailRef.current?.focus();
  }, [mode]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const path = mode === "login" ? "/api/v1/auth/login" : "/api/v1/auth/register";
      const body =
        mode === "login"
          ? { email, password }
          : { email, name, password };

      const res = await apiFetch<AuthResponse>(path, {
        method: "POST",
        body: JSON.stringify(body),
      });

      setToken(res.data.access_token, {
        id: res.user.id,
        email: res.user.email,
        name: res.user.name,
        role: res.user.role,
      });
      window.dispatchEvent(new Event("storage"));
      router.push("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        {/* Branding */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl tracking-tight">
            <span className="text-foreground">Secture</span>{" "}
            <span className="font-semibold text-primary">Cortex</span>
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Tu copiloto IA para reuniones con clientes
          </p>
        </div>

        {/* Card */}
        <div className="rounded-xl border border-border bg-surface p-6">
          {/* Tabs — underline style */}
          <div className="mb-6 flex border-b border-border">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError(null);
              }}
              className={`flex-1 pb-2.5 text-sm font-medium transition-colors ${
                mode === "login"
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Iniciar sesión
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setError(null);
              }}
              className={`flex-1 pb-2.5 text-sm font-medium transition-colors ${
                mode === "register"
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Registro
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <FieldGroup>
              {mode === "register" && (
                <Field>
                  <FieldLabel>Nombre</FieldLabel>
                  <Input
                    placeholder="Tu nombre"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="bg-transparent border-border focus:ring-primary"
                  />
                </Field>
              )}

              <Field>
                <FieldLabel>Email</FieldLabel>
                <Input
                  ref={emailRef}
                  type="email"
                  placeholder="tu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="bg-transparent border-border focus:ring-primary"
                />
              </Field>

              <Field>
                <FieldLabel>Contraseña</FieldLabel>
                <Input
                  type="password"
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="bg-transparent border-border focus:ring-primary"
                />
              </Field>

              {error && <FieldError>{error}</FieldError>}

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-primary text-primary-foreground"
              >
                {loading
                  ? "Cargando..."
                  : mode === "login"
                    ? "Iniciar sesion"
                    : "Crear cuenta"}
              </Button>
            </FieldGroup>
          </form>
        </div>
      </div>
    </div>
  );
}

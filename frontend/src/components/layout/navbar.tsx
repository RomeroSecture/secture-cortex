"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useSyncExternalStore } from "react";
import { Button } from "@/components/ui/button";
import { clearToken } from "@/lib/auth";

function subscribeToStorage(callback: () => void) {
  window.addEventListener("storage", callback);
  return () => window.removeEventListener("storage", callback);
}

// useSyncExternalStore compares by reference — return a string to avoid infinite loop
function getSnapshot(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("secture_user");
}

function getServerSnapshot(): string | null {
  return null;
}

function parseUser(raw: string | null): { name: string; role: string } | null {
  if (!raw) return null;
  try {
    const u = JSON.parse(raw);
    return { name: u.name || "", role: u.role || "" };
  } catch {
    return null;
  }
}

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  const rawUser = useSyncExternalStore(subscribeToStorage, getSnapshot, getServerSnapshot);
  const user = parseUser(rawUser);

  const handleLogout = useCallback(() => {
    clearToken();
    window.dispatchEvent(new Event("storage"));
    router.push("/login");
  }, [router]);

  const navLink = (href: string, label: string) => (
    <Link
      href={href}
      className={`px-3 py-1.5 text-sm transition-colors ${
        pathname.startsWith(href)
          ? "text-foreground font-medium"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <header className="flex h-12 items-center justify-between border-b border-border bg-background/80 backdrop-blur-md px-6">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-1 text-sm tracking-tight">
          <span className="text-foreground">Secture</span>
          <span className="font-semibold text-primary">Cortex</span>
        </Link>
        <div className="h-4 w-px bg-border" />
        <nav className="flex items-center gap-1">
          {navLink("/projects", "Proyectos")}
          {user?.role === "admin" && navLink("/admin", "Admin")}
        </nav>
      </div>

      <div className="flex items-center gap-3">
        {user ? (
          <>
            <Link
              href="/profile"
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {user.name}
              {user.role && (
                <span className="rounded-full bg-surface px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  {user.role}
                </span>
              )}
            </Link>
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground h-8 px-2 text-xs" onClick={handleLogout}>
              Salir
            </Button>
          </>
        ) : (
          <Link href="/login">
            <Button variant="ghost" size="sm" className="h-8 px-3 text-xs">
              Iniciar sesión
            </Button>
          </Link>
        )}
      </div>
    </header>
  );
}

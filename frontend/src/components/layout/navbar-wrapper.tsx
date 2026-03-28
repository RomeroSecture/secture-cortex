"use client";

import { usePathname } from "next/navigation";
import { Navbar } from "@/components/layout/navbar";

export function NavbarWrapper() {
  const pathname = usePathname();

  // Hide navbar on meeting pages (full-screen experience)
  if (pathname.startsWith("/meeting")) {
    return null;
  }

  return <Navbar />;
}

"use client";

import { useRouter } from "next/navigation";
import { type ReactNode, useEffect } from "react";

import { MockBanner } from "@/components/mock-banner";
import { Skeleton } from "@/components/ui/skeleton";
import { useSession } from "@/lib/session";

import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

/**
 * Client-side auth guard plus layout. The real security boundary is the API:
 * every endpoint checks the session itself. This guard only avoids showing an
 * empty shell to a logged-out visitor.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const session = useSession();

  useEffect(() => {
    if (session.isSuccess && session.data === null) router.replace("/login");
  }, [session.isSuccess, session.data, router]);

  if (session.isError) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6 text-sm text-muted-foreground">
        Can&apos;t reach the SafeOps API. Check that the backend is running, then refresh.
      </div>
    );
  }

  if (!session.data) {
    return (
      <div className="flex min-h-screen" aria-busy="true" aria-label="Loading">
        <div className="hidden w-60 border-r bg-sidebar p-4 md:block">
          <Skeleton className="mb-6 h-7 w-40" />
          {Array.from({ length: 8 }, (_, i) => (
            <Skeleton key={i} className="mb-2 h-8 w-full" />
          ))}
        </div>
        <div className="flex-1 p-8">
          <Skeleton className="mb-4 h-8 w-64" />
          <Skeleton className="h-40 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <MockBanner />
      <div className="flex flex-1">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar session={session.data} />
          <main className="flex-1 px-4 py-6 md:px-8">{children}</main>
        </div>
      </div>
    </div>
  );
}

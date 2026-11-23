"use client";

import { LogOut, Menu, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Brand } from "@/components/brand";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Session } from "@/lib/api/client";
import { useLogout } from "@/lib/session";

import { NavLinks } from "./nav-links";

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter((part) => /^[A-Za-z]/.test(part))
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function Topbar({ session }: { session: Session }) {
  const router = useRouter();
  const logout = useLogout();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, organization } = session;

  function onLogout() {
    logout.mutate(undefined, {
      onSuccess: () => router.replace("/login"),
      onError: () => toast.error("Couldn't sign out. Please try again."),
    });
  }

  return (
    <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur-sm">
      <div className="flex h-12 items-center gap-3 px-4 md:px-8">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((open) => !open)}
        >
          {mobileOpen ? <X className="size-4" /> : <Menu className="size-4" />}
        </Button>
        <div className="md:hidden">
          <Brand />
        </div>

        <span className="hidden truncate text-sm text-muted-foreground md:inline">
          {organization.name}
        </span>

        <div className="ml-auto">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="gap-2" aria-label="Account menu">
                <span className="flex size-6 items-center justify-center rounded-full bg-primary text-[10px] font-semibold text-primary-foreground">
                  {initials(user.full_name) || "?"}
                </span>
                <span className="hidden text-sm sm:inline">{user.full_name}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-60">
              <DropdownMenuLabel className="flex flex-col gap-1">
                <span className="truncate text-sm font-medium">{user.email}</span>
                <span className="flex items-center gap-2 text-xs font-normal text-muted-foreground">
                  <Badge variant="secondary" className="capitalize">
                    {user.role}
                  </Badge>
                  <span className="truncate">{organization.name}</span>
                </span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={onLogout} disabled={logout.isPending}>
                <LogOut className="size-4" aria-hidden />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {mobileOpen && (
        <div className="border-t bg-sidebar px-3 py-3 md:hidden">
          <NavLinks onNavigate={() => setMobileOpen(false)} />
        </div>
      )}
    </header>
  );
}

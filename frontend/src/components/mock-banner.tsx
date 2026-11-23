"use client";

import { FlaskConical } from "lucide-react";

import { useSystemInfo } from "@/lib/session";

/** Shown on every screen while the clearly-labelled mock LLM provider is active. */
export function MockBanner() {
  const { data } = useSystemInfo();
  if (!data?.mock_mode) return null;

  return (
    <div
      role="status"
      className="flex items-center justify-center gap-2 border-b border-warning-foreground/20 bg-warning px-4 py-1.5 text-xs font-medium text-warning-foreground"
    >
      <FlaskConical className="size-3.5" aria-hidden />
      Mock AI provider active: AI output is placeholder text labelled [MOCK], not real model
      responses.
    </div>
  );
}

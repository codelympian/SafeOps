import type { LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";

/**
 * An honest placeholder for a section that isn't built yet. No buttons:
 * the spec forbids controls that do nothing.
 */
export function EmptyState({
  icon: Icon,
  title,
  description,
  phase,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  phase: number;
}) {
  return (
    <section
      aria-label={title}
      className="flex flex-col items-center gap-3 rounded-lg border border-dashed px-6 py-16 text-center"
    >
      <span className="flex size-10 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <Icon className="size-5" aria-hidden />
      </span>
      <h2 className="text-base font-medium">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      <Badge variant="outline" className="font-mono text-[11px]">
        Arrives in Phase {phase}
      </Badge>
    </section>
  );
}

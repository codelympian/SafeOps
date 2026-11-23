import { ShieldCheck } from "lucide-react";

export function Brand() {
  return (
    <div className="flex items-center gap-2">
      <span className="flex size-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <ShieldCheck className="size-4" aria-hidden />
      </span>
      <span className="text-sm font-semibold tracking-tight">
        SafeOps <span className="font-normal text-muted-foreground">Intelligence</span>
      </span>
    </div>
  );
}

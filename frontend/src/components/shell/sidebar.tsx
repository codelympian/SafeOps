import { Brand } from "@/components/brand";

import { NavLinks } from "./nav-links";

export function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col gap-6 border-r bg-sidebar px-3 py-4 md:flex">
      <div className="px-1.5">
        <Brand />
      </div>
      <NavLinks />
      <p className="mt-auto px-1.5 text-[11px] leading-snug text-muted-foreground">
        Advisory decision support. Findings require review by qualified HSE personnel.
      </p>
    </aside>
  );
}

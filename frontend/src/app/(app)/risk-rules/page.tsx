import { ShieldAlert } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { RiskDisclaimer } from "@/components/risk-disclaimer";

export const metadata: Metadata = { title: "Risk Rules" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Risk Rules"
        description="The activity and hazard taxonomy, interaction rules and the 5×5 risk matrix that drive job analysis."
      />
      <RiskDisclaimer />
      <EmptyState
        icon={ShieldAlert}
        title="Rules not loaded yet"
        description="Rules are stored as data, not prompt text, so changing a rule never needs a code change. Engineers can read them; admins can edit them."
        phase={6}
      />
    </>
  );
}

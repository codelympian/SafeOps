import { ClipboardCheck } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { RiskDisclaimer } from "@/components/risk-disclaimer";

export const metadata: Metadata = { title: "Job Risk Analysis" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Job Risk Analysis"
        description="Describe a planned job and get a risk briefing: flagged activity interactions, why they were flagged, and similar past incidents."
      />
      <RiskDisclaimer />
      <EmptyState
        icon={ClipboardCheck}
        title="No assessments yet"
        description="Deterministic rules detect dangerous combinations of activities by zone and time. AI only explains findings and suggests candidates for a reviewer to accept or reject."
        phase={7}
      />
    </>
  );
}

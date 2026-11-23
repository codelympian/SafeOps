import { LayoutDashboard } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Overview" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Overview"
        description="Document processing status, recent incidents and recent assessments with high or critical findings."
      />
      <EmptyState
        icon={LayoutDashboard}
        title="Nothing to summarize yet"
        description="Once documents are ingested, this page shows processing status, recent incidents and assessments that need attention."
        phase={8}
      />
    </>
  );
}

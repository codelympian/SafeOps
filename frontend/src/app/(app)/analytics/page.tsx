import { BarChart3 } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Analytics" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Analytics"
        description="Trends computed directly from your ingested incident data."
      />
      <EmptyState
        icon={BarChart3}
        title="No data to chart yet"
        description="Incidents over time, by category and severity, and top contributing factors. Every number is computed from the database, never written by AI."
        phase={8}
      />
    </>
  );
}

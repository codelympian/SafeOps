import { TriangleAlert } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Incident Library" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Incident Library"
        description="Incidents extracted from your reports, with evidence for every field and human review."
      />
      <EmptyState
        icon={TriangleAlert}
        title="No incidents extracted yet"
        description="Each extracted field will show its source passage and a computed confidence level. Reviewers can verify or correct every value."
        phase={5}
      />
    </>
  );
}

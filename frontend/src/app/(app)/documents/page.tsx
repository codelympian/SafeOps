import { FileText } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Documents" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="Documents"
        description="Upload incident reports, procedures, permits and JSAs (PDF, DOCX, TXT, CSV) for processing."
      />
      <EmptyState
        icon={FileText}
        title="No documents yet"
        description="Uploaded files are validated, split into sections, indexed for search and tracked through uploaded, processing and ready or failed states."
        phase={2}
      />
    </>
  );
}

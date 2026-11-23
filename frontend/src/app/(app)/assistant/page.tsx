import { MessageSquareText } from "lucide-react";
import type { Metadata } from "next";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "HSE Assistant" };

export default function Page() {
  return (
    <>
      <PageHeader
        title="HSE Assistant"
        description="Ask questions about your safety documents and get answers grounded in, and cited from, those documents."
      />
      <EmptyState
        icon={MessageSquareText}
        title="No conversations yet"
        description="Ask about past incidents, procedures and controls. Answers will cite the exact passages they rely on, and say plainly when the evidence is insufficient."
        phase={4}
      />
    </>
  );
}

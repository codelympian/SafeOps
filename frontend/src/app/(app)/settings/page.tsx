import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { SettingsPanels } from "@/components/settings/settings-panels";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" description="Your profile and this deployment's AI provider status." />
      <SettingsPanels />
    </>
  );
}

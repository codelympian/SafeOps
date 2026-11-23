"use client";

import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useSession, useSystemInfo } from "@/lib/session";

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid grid-cols-[9rem_1fr] items-baseline gap-4 py-2 text-sm">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="min-w-0 break-words">{children}</dd>
    </div>
  );
}

export function SettingsPanels() {
  const session = useSession();
  const info = useSystemInfo();

  return (
    <div className="grid max-w-4xl gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
          <CardDescription>Your account in this organization.</CardDescription>
        </CardHeader>
        <CardContent>
          {session.data ? (
            <dl className="divide-y">
              <Row label="Name">{session.data.user.full_name}</Row>
              <Row label="Email">{session.data.user.email}</Row>
              <Row label="Role">
                <Badge variant="secondary" className="capitalize">
                  {session.data.user.role}
                </Badge>
              </Row>
              <Row label="Organization">{session.data.organization.name}</Row>
            </dl>
          ) : (
            <Skeleton className="h-32 w-full" />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">AI provider</CardTitle>
          <CardDescription>Configured on the server via environment variables.</CardDescription>
        </CardHeader>
        <CardContent>
          {info.isError && (
            <p className="text-sm text-destructive">Couldn&apos;t load provider status.</p>
          )}
          {info.isPending && <Skeleton className="h-32 w-full" />}
          {info.data && (
            <dl className="divide-y">
              <Row label="LLM provider">
                <span className="font-mono">{info.data.llm_provider}</span>
                {info.data.mock_mode && (
                  <Badge variant="outline" className="ml-2 border-warning-foreground/30 bg-warning text-warning-foreground">
                    Mock mode
                  </Badge>
                )}
              </Row>
              <Row label="Embedding model">
                <span className="font-mono">{info.data.embedding_model}</span>
              </Row>
              <Row label="Environment">
                <span className="font-mono">{info.data.app_env}</span>
              </Row>
              {info.data.mock_mode && (
                <p className="pt-3 text-xs text-muted-foreground">
                  The mock provider returns deterministic placeholder text prefixed with [MOCK], so
                  the app runs without an API key. Set LLM_PROVIDER to anthropic or openai, plus
                  the matching API key, to use a real model.
                </p>
              )}
            </dl>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

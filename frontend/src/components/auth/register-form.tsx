"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "@/lib/session";

const MIN_PASSWORD = 10;

export function RegisterForm() {
  const router = useRouter();
  const register = useRegister();
  const [form, setForm] = useState({ org_name: "", full_name: "", email: "", password: "" });

  function update(field: keyof typeof form) {
    return (event: React.ChangeEvent<HTMLInputElement>) =>
      setForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    register.mutate(form, { onSuccess: () => router.replace("/overview") });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create an organization</CardTitle>
        <CardDescription>You&apos;ll be its admin and can add colleagues later.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          {register.error && (
            <Alert variant="destructive">
              <AlertDescription>{register.error.message}</AlertDescription>
            </Alert>
          )}
          <div className="flex flex-col gap-2">
            <Label htmlFor="org_name">Organization name</Label>
            <Input id="org_name" required maxLength={200} value={form.org_name} onChange={update("org_name")} />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="full_name">Your name</Label>
            <Input
              id="full_name"
              autoComplete="name"
              required
              maxLength={200}
              value={form.full_name}
              onChange={update("full_name")}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="email">Work email</Label>
            <Input id="email" type="email" autoComplete="email" required value={form.email} onChange={update("email")} />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              required
              minLength={MIN_PASSWORD}
              aria-describedby="password-hint"
              value={form.password}
              onChange={update("password")}
            />
            <p id="password-hint" className="text-xs text-muted-foreground">
              At least {MIN_PASSWORD} characters.
            </p>
          </div>
          <Button type="submit" disabled={register.isPending}>
            {register.isPending ? "Creating…" : "Create organization"}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-foreground underline-offset-4 hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}

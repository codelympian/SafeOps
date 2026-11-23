import { Brand } from "@/components/brand";
import { MockBanner } from "@/components/mock-banner";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <MockBanner />
      <main className="flex flex-1 flex-col items-center justify-center gap-8 px-4 py-12">
        <Brand />
        <div className="w-full max-w-sm">{children}</div>
        <p className="max-w-sm text-center text-xs text-muted-foreground">
          Decision support only. SafeOps never declares a job safe and does not replace
          competent HSE personnel, permit-to-work systems or approved risk assessments.
        </p>
      </main>
    </div>
  );
}

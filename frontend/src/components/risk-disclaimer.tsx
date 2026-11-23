import { TriangleAlert } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

/** Required on every risk-analysis screen (spec §1 and §10). */
export function RiskDisclaimer() {
  return (
    <Alert className="mb-6 border-warning-foreground/25 bg-warning text-warning-foreground">
      <TriangleAlert aria-hidden />
      <AlertTitle>Decision support only</AlertTitle>
      <AlertDescription className="text-warning-foreground/90">
        SafeOps never states that a job is safe. Findings are advisory and must be reviewed by
        competent HSE personnel. It does not replace permit-to-work systems or approved risk
        assessments.
      </AlertDescription>
    </Alert>
  );
}

# SafeOps frontend

Next.js (App Router) + TypeScript + Tailwind + shadcn/ui. Talks directly to the FastAPI
backend with credentials (CORS allowlist). See the repo root README and `docs/`.

```bash
pnpm install
pnpm dev          # http://localhost:3000 (backend must be running on :8000)
pnpm test         # Vitest + React Testing Library
pnpm lint && pnpm typecheck
pnpm api-types    # regenerate src/lib/api/schema.d.ts from openapi.json
```

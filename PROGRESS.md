# PROGRESS

_Last updated: 2026-11-24_

## Current phase
**Phase 1 complete** (approved 2026-11-24). Next: **Phase 2, Synthetic data and ingestion**. It opens with the 🔶 embedding model decision.

## Phase status
| Phase | Status |
|---|---|
| 0 Inspect & plan | ✅ Approved 2026-11-22 (commit 492019c, pushed) |
| 1 Foundation | ✅ Approved 2026-11-24 |
| 2 Synthetic data & ingestion | Not started. Starts with 🔶 embedding model decision, then 🔶 ERD sign-off |
| 3 Retrieval & eval harness | Not started |
| 4 HSE Assistant | Not started |
| 5 Incident intelligence | Not started |
| 6 Risk engine | Not started |
| 7 Pre-job analysis | Not started |
| 8 Overview & analytics | Not started |
| 9 Final eval & packaging | Not started |

## What works (Phase 1)
- **Stack:** `make up` starts Postgres 16 + pgvector (host port 5433), Redis 7, the API (:8000, with healthcheck) and the Arq worker. `make dev` also starts Next.js on :3000.
- **API:** `/health` (checks DB and Redis, 503 if either fails), `/system/info` (provider and mock flag), `/auth/register|login|logout|me`, `/users` (admin only, org-scoped).
- **Auth:** argon2id passwords. JWT in an httpOnly SameSite=Lax cookie. CSRF token bound to the session, checked on every authenticated write. Three roles.
- **Tenancy:** `OrgScopedRepository` scopes every query by `org_id` in SQL. Cross-org reads return 404.
- **Logging:** structlog JSON with a request ID on every line, including uvicorn and arq. A generic 500 is returned with the request ID and no stack trace.
- **Seed:** `make seed` creates two fictional orgs (Kestrel Energy = A, Harrow Petrochem = B) and 5 demo logins. It's idempotent.
- **Frontend:** login/register, client auth guard, sidebar with the 8 sections, empty states (no dead buttons), mock banner, risk disclaimer on Jobs and Risk Rules, Settings with live profile and provider status. Typed API client generated from OpenAPI.
- **Tests:** backend 38 passing (auth, CSRF, roles, tenant isolation, security units, health/logging, worker). Frontend 12 passing.
- **Tooling:** ruff, mypy --strict, eslint, tsc strict, `alembic check`, and the Makefile all pass locally. GitHub Actions CI is written. **Its first run happens on push.**

## Known issues / shortcuts
- CI has not run yet (needs the push). Confirm it's green after approval.
- No server-side session revocation (logout clears the cookie; the token stays valid until expiry, 8h). Future work: a denylist.
- `POST /auth/register` reveals whether an email exists (409). Accepted for the demo.
- Dark-mode tokens exist, but there's no theme toggle.
- The frontend auth guard is client-side (the API enforces auth on every endpoint). It shows a skeleton before redirecting.
- The backend test suite needs the Docker stack running (real Postgres on :5433).
- A "Flow Test Org" was created in the local dev DB during manual verification (dev data only).
- The VS Code Python linter flags E501 at 79 columns. The project's ruff config uses 100. This is editor-only.

## Next
Phase 2: Synthetic data and ingestion. It begins with two decisions: the embedding model (bge-small vs bge-base, etc.), then the ERD.

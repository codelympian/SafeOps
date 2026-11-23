# Decision Log (ADR style)

Each entry: **Context → Decision → Consequences.** Status is `Accepted`, `Proposed` (waiting for approval), or `Superseded by ADR-NNN`.

---

## ADR-001 — Pin Python 3.12 for the backend
**Status:** Accepted (spec default) · Phase 0
**Context:** The machine's default interpreter is 3.14.3. 3.12 is also installed. The spec says 3.12. Native-extension packages (PyMuPDF, asyncpg, onnxruntime) publish wheels for new Python versions later than pure-Python packages.
**Decision:** Pin 3.12 with `uv` (`.python-version` + `requires-python = ">=3.12,<3.13"`). Docker images use `python:3.12-slim`.
**Consequences:** Reliable wheels and the same version locally, in CI and in containers. We don't get 3.13/3.14 language features, which this project doesn't need.

## ADR-002 — fastembed (ONNX) for local embeddings and reranking
**Status:** Accepted 2026-11-22 · Phase 0 (library choice). The *model* choice is a separate 🔶 decision in Phase 2.
**Context:** The spec allows `fastembed` or `sentence-transformers`. sentence-transformers depends on PyTorch, which adds ~1–2 GB to every image and a slow install. fastembed runs ONNX models on CPU, supports `query_embed` vs `embed` (the correct BGE query/passage handling), and also ships cross-encoder rerankers.
**Decision:** Use fastembed for both the embedder and the reranker.
**Alternatives:** sentence-transformers (largest model catalogue, heavier); a hosted embedding API (rejected: costs money, needs a key, not offline).
**Consequences:** Small images and fast cold starts. Risk: some models (possibly bge-m3) or Hub revision pinning may not be supported. Verified in Phase 2/3. If needed, an optional eval-only dependency group is added, not a runtime one.

## ADR-003 — Hand-written magic-byte validation instead of python-magic
**Status:** Accepted · Phase 0
**Context:** The spec requires checking file type by content. `python-magic` needs the native libmagic library, which is awkward on Windows. We accept only four types.
**Decision:** A small validator: PDF = `%PDF-` header; DOCX = ZIP signature **and** `word/document.xml` in the archive; TXT/CSV = decodes as text (charset-normalizer) with no NUL bytes, and CSV additionally parses with a consistent column count.
**Consequences:** No native dependency, fully unit-testable. It only covers our allowlist, which is the intent.

## ADR-004 — Standard library `csv` instead of pandas
**Status:** Accepted · Phase 0
**Context:** CSV ingestion is "one row = one record". pandas is ~50 MB and brings type-inference surprises (dates, NaN).
**Decision:** Use `csv.DictReader` with explicit typing via Pydantic.
**Consequences:** Lighter and more predictable. If heavy analytics ever happen in Python, that's done in SQL anyway.

## ADR-005 — Generate synthetic PDF/DOCX with PyMuPDF and python-docx
**Status:** Accepted · Phase 0
**Context:** The synthetic generator must write PDFs and DOCX files. We already depend on PyMuPDF and python-docx for reading.
**Decision:** Use the same libraries to write. No reportlab or fpdf.
**Consequences:** One fewer dependency. The generator can deliberately vary font sizes to exercise the PDF heading heuristic.

## ADR-006 — pnpm for the frontend
**Status:** Accepted · Phase 0
**Context:** npm 11.9 and pnpm 12.21 are installed. The spec doesn't specify.
**Decision:** pnpm. It's faster, uses a content-addressed store, and has strict dependency resolution (no phantom deps).
**Consequences:** Reviewers need pnpm (`corepack enable` gives it with Node). Documented in the README.

## ADR-007 — Running the Makefile on Windows
**Status:** Accepted 2026-11-22: option 1 · Phase 0
**Context:** The spec requires a Makefile. GNU make isn't installed. CI (Linux) has make.
**Options:**
1. **Install GNU make** (`winget install ezwinports.make`) and run targets from Git Bash. *(Recommended: keeps the spec's Makefile as the single source of truth.)*
2. Develop inside **WSL2**, where make, uv and Docker all work natively, and the environment matches CI most closely. More setup, better long-term.
3. Replace make with a cross-platform runner (`just`/Taskfile). This changes the spec, and reviewers on Linux/macOS expect make.
**Decision:** Option 1. GNU make 4.4.1 installed via `winget install ezwinports.make`.
**Consequences:** Makefile recipes must run under Git Bash (POSIX shell) on Windows and under bash in CI, so no PowerShell-only syntax goes in recipes.

## ADR-008 — Force LF line endings via `.gitattributes`
**Status:** Accepted · Phase 0
**Context:** On Windows, Git may check files out with CRLF. Shell scripts and entrypoints with CRLF fail inside Linux containers (`/bin/sh^M: not found`), and Makefile recipes can break.
**Decision:** `* text=auto eol=lf`, with `.bat`/`.ps1` kept as CRLF and PDFs/DOCX marked binary.
**Consequences:** Same bytes on every platform. Editors on Windows handle LF fine.

## ADR-009 — `mock` is the default LLM provider in `.env.example`
**Status:** Accepted · Phase 0
**Context:** A reviewer should be able to run the app in two minutes without an API key. The spec defines a clearly labelled mock provider.
**Decision:** `LLM_PROVIDER=mock`. Model ID variables are blank by default, with example values in comments.
**Consequences:** The app boots keyless and shows a mock banner. Real-provider features are exercised once keys are set.

## ADR-010 — Map the compose Postgres to host port 5433
**Status:** Accepted · Phase 0
**Context:** A native Windows PostgreSQL is already listening on `localhost:5432`. If compose also published 5432, the bind would fail, or tools on the host would quietly connect to the wrong server. Another project's Supabase stack uses 54321/54322 (no conflict).
**Decision:** Publish the compose Postgres on host port **5433** (configurable via `POSTGRES_PORT`). Containers keep talking to `db:5432` on the compose network.
**Consequences:** No interference with the existing install. Host-side tools (psql, pytest run outside Docker) use 5433. The README quickstart will mention it.

---

# Phase 1 — Foundation

## ADR-011 — Frontend calls the API directly, with a CORS allowlist
**Status:** Accepted (user choice) · Phase 1
**Context:** The browser app (`:3000`) and the API (`:8000`) are different origins. Options were direct calls with CORS, or a Next.js rewrite proxy making them same-origin.
**Decision:** Direct calls with `credentials: "include"`. FastAPI's `CORSMiddleware` allows only `CORS_ORIGINS`, with credentials. Production refuses a `*` origin.
**Consequences:** SSE in Phase 4 streams straight from FastAPI, with no proxy that could buffer or compress it. This matches how a split deployment works. Cookie and CORS settings must be kept consistent.

## ADR-012 — Registration creates a new organization and makes the caller its admin
**Status:** Accepted (user choice) · Phase 1
**Context:** The spec requires register/login but doesn't say how users join orgs.
**Decision:** `POST /auth/register` creates an org plus an admin user. Admins add reviewers and engineers with `POST /users`, always into their own org.
**Consequences:** Nobody can register into someone else's tenant. Invites and email verification are out of scope. Registering with an existing email returns 409, which reveals that the email exists. That's acceptable for a portfolio demo and noted as a limitation.

## ADR-013 — Session cookie + CSRF token bound to the session
**Status:** Accepted · Phase 1
**Context:** The spec requires a JWT in an httpOnly, SameSite cookie, with CSRF protection.
**Decision:**
- The JWT (HS256, pinned algorithm) holds `sub`, `csrf`, `iat` and `exp`. It lives in an `HttpOnly; SameSite=Lax` cookie (`Secure` via `COOKIE_SECURE`).
- The random CSRF token is returned in the login, register and `/auth/me` response bodies. The frontend keeps it in memory and sends it as `X-CSRF-Token` on every POST, PUT, PATCH and DELETE. The server compares it in constant time with the token's claim.
- The check lives in the shared `get_auth` dependency, so no write endpoint can forget it.
- The user is reloaded from the database on every request.
**Alternatives:** A double-submit cookie (needs JS-readable cookies, which breaks across domains). SameSite alone (no defence in depth).
**Consequences:** Deactivation and role changes apply immediately, at the cost of one indexed lookup per request. Logout clears the cookie but doesn't revoke the token server-side; a denylist is future work. Login timing is equalised with a dummy argon2 hash, so it doesn't reveal which emails exist.

## ADR-014 — The Phase 1 migration contains only the auth tables
**Status:** Accepted · Phase 1
**Context:** The spec asks for ERD sign-off "before the first migration", but also schedules auth (which needs `organizations` and `users`) in Phase 1 and the ERD in Phase 2.
**Decision:** Migration `0001` creates only `organizations` and `users`, which the spec fully defines, and enables `pgvector`. No domain table is created before the Phase 2 ERD is approved.
**Consequences:** The ERD review still governs every domain table. If the ERD changes `users`, a normal follow-up migration handles it.

## ADR-015 — Keys and constraints in the auth tables
**Status:** Accepted · Phase 1
**Decision:**
- UUID primary keys, so IDs don't reveal row counts and can't be enumerated across tenants.
- `role` is a `VARCHAR` with a `CHECK`, not a Postgres `ENUM`: adding a role later is a constraint swap, not an `ALTER TYPE`.
- Email is globally unique and stored lowercase, enforced by a `CHECK`, because login happens before the org is known.
- Deterministic constraint names via a SQLAlchemy naming convention.
**Consequences:** `alembic check` verifies the hand-written migration matches the models, both locally and in CI.

## ADR-016 — Backend in Docker, frontend and tests on the host, tests on real Postgres
**Status:** Accepted · Phase 1
**Context:** On Windows, Next.js file-watching inside a container over a bind mount is slow.
**Decision:**
- Compose runs Postgres, Redis, the API and the worker, with hot reload via polling. The Next.js dev server runs on the host.
- pytest runs on the host against a **separate `safeops_test` database** on the compose Postgres (CI uses a service container). It never uses SQLite or the dev database.
- Migrations go down to base and back up once per test session, and tables are truncated before each test.
**Consequences:** Tests exercise real Postgres SQL. That matters now for isolation, and later for pgvector and tsvector. The backend suite needs the Docker stack running.

## ADR-017 — Next.js `cacheComponents` off; client-side data with TanStack Query
**Status:** Accepted · Phase 1
**Context:** `create-next-app` 16.4 enables `cacheComponents` and `partialPrefetching`. Those prerender client components and require every initial query to sit behind Suspense. All our data comes from FastAPI with an httpOnly session cookie.
**Decision:** Turn both off. Pages are static shells, and data is fetched in the browser with TanStack Query through a typed `openapi-fetch` client generated from the backend's OpenAPI spec.
**Consequences:** It's simple and easy to defend, and there's one source of truth for API types. CI fails if the generated types drift from the backend. We give up server-rendered data, which an authenticated dashboard doesn't need.

## ADR-018 — Tenant scoping in one repository base class; cross-tenant reads return 404
**Status:** Accepted · Phase 1
**Decision:** `OrgScopedRepository` adds `WHERE org_id = :ctx_org` inside every query, and sets `org_id` from the authenticated context on insert, ignoring any client-supplied value. Endpoints get an `OrgContext` only from the session. A row in another org returns **404, not 403**, so the API never confirms another tenant's IDs. The one unscoped lookup (by email at login) is named and documented.
**Consequences:** The scoping rule is written once and covered by tests at both the repository and API level. Postgres row-level security remains future work.

## ADR-019 — Pure ASGI middleware for request IDs and error handling
**Status:** Accepted · Phase 1
**Context:** Starlette's `BaseHTTPMiddleware` can interfere with streaming responses (Phase 4 SSE) and context propagation.
**Decision:**
- A small pure-ASGI middleware accepts a safe incoming `X-Request-ID` or generates one, and binds it to structlog contextvars.
- It writes one JSON access line per request and returns the ID in a response header.
- It converts unhandled exceptions into `{"detail": "Internal server error", "request_id": ...}`. The stack trace is logged server-side only.
**Consequences:** Every log line, including from uvicorn and arq, carries the request ID, and clients never see stack traces.

## ADR-020 — UI foundation: shadcn/ui (Radix), IBM Plex, semantic colour tokens
**Status:** Accepted · Phase 1
**Decision:**
- shadcn/ui on Radix primitives: accessible components we own as source.
- IBM Plex Sans and Mono, a technical and legible family.
- Cool neutral surfaces with a steel-blue primary. Colour is used only through semantic tokens (`risk-low|medium|high|critical`, `warning`, `success`, `info`).
- No gradients or decorative effects.
- Empty sections show an honest empty state with no buttons, because the spec forbids controls that do nothing.
**Consequences:** Phases 2–8 use the tokens for risk levels and statuses. Dark mode tokens exist, but there is no theme toggle yet.

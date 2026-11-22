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

# SafeOps Intelligence

AI-assisted HSE (Health, Safety and Environment) document intelligence and pre-job risk decision support.

> **Status:** in progress (portfolio project). See [PROGRESS.md](PROGRESS.md). The full README, with evaluation results, is written in Phase 9.
>
> **Decision support only.** SafeOps never states that a job is safe. It does not replace competent HSE personnel, permit-to-work systems or approved risk assessments. All data in this repo is **synthetic** and all organizations are fictional.

## Quickstart (local)

Requirements: Docker, [uv](https://docs.astral.sh/uv/), Node 24 + pnpm, GNU make. On Windows, run `make` from Git Bash.

```bash
make env       # create .env from .env.example (edit JWT_SECRET for any shared use)
make install   # backend + frontend dependencies
make up        # Postgres (pgvector), Redis, API and worker in Docker
make seed      # two fictional demo orgs and demo logins
make dev       # also starts the frontend at http://localhost:3000
```

- App: http://localhost:3000. API docs: http://localhost:8000/docs.
- Postgres is published on host port **5433** (not 5432), to avoid clashing with a local install.
- The default `LLM_PROVIDER=mock` needs no API key. AI output is labelled `[MOCK]` and a banner is shown.

### Demo logins (local demo only)

The password for all of these is the `DEMO_PASSWORD` value in `.env` (default `SafeOpsDemo!2026`).

| Org | Email | Role |
|---|---|---|
| Kestrel Energy (fictional, org A) | `admin@kestrel.example` | admin |
| | `reviewer@kestrel.example` | reviewer |
| | `engineer@kestrel.example` | engineer |
| Harrow Petrochem (fictional, org B) | `admin@harrow.example` | admin |
| | `engineer@harrow.example` | engineer |

## Development

```bash
make test      # backend (pytest, needs `make up`) + frontend (Vitest)
make lint      # ruff, mypy --strict, eslint, tsc --strict
make api-types # regenerate the typed frontend client after changing the API
make help      # all commands
```

## Docs

- [docs/MASTER_PROMPT.md](docs/MASTER_PROMPT.md): full specification
- [docs/PLAN.md](docs/PLAN.md): architecture, dependencies, phase plan, risks
- [docs/DECISIONS.md](docs/DECISIONS.md): architecture decision records

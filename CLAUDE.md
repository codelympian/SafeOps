# SafeOps Intelligence

- The full project spec is in docs/MASTER_PROMPT.md. Read it before doing any work.
- Read PROGRESS.md first to see which phase we're in and what's done.
- Work on one phase only. Stop at the end of the phase, give the phase report, and wait for my approval.
- I'm a student learning AI engineering: explain decisions and follow the teaching rules in the spec.

## Git
- Commit small logical steps within a phase when it makes sense.
- Push to origin main only after I approve the phase report. Phase commits: "Phase N: <summary>".
- Never commit .env or any secrets. Check what's staged before every commit.
- Never force-push, rewrite history, or change the remote without asking.

## Environment notes (Windows host)
- Python 3.12 is pinned for the backend (system default is 3.14). Use `uv`.
- Postgres, Redis, API and worker run in Docker Compose; CI runs on Linux.

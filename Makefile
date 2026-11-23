# SafeOps Intelligence: developer commands.
# On Windows, run from Git Bash (recipes use POSIX shell syntax, ADR-007).

SHELL := bash
.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help env install dev up down logs ps migrate seed test test-backend test-frontend \
        lint lint-backend lint-frontend format api-types

help: ## List available commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

env: ## Create .env from .env.example if it doesn't exist
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example. Review it, and set JWT_SECRET before any shared use."; fi

install: ## Install backend (uv) and frontend (pnpm) dependencies
	cd backend && uv sync
	cd frontend && pnpm install

dev: env up ## Start Postgres, Redis, API and worker in Docker, then the frontend dev server
	@echo "API: http://localhost:8000/docs   App: http://localhost:3000"
	cd frontend && pnpm dev

up: env ## Start the Docker stack in the background (rebuilds images if needed)
	$(COMPOSE) up -d --build --wait

down: ## Stop the Docker stack (data volumes are kept)
	$(COMPOSE) down

logs: ## Follow API and worker logs
	$(COMPOSE) logs -f api worker

ps: ## Show container status
	$(COMPOSE) ps

migrate: ## Apply database migrations
	$(COMPOSE) exec api alembic upgrade head

seed: ## Create the two fictional demo orgs and their demo logins
	$(COMPOSE) exec api python -m app.seed

test: test-backend test-frontend ## Run all tests

test-backend: ## Backend tests (needs the Docker stack: Postgres on :5433, Redis on :6379)
	cd backend && uv run pytest

test-frontend: ## Frontend unit/component tests
	cd frontend && pnpm test

lint: lint-backend lint-frontend ## Lint, format-check and type-check everything

lint-backend:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app tests

lint-frontend:
	cd frontend && pnpm lint && pnpm typecheck

format: ## Auto-format backend code
	cd backend && uv run ruff format . && uv run ruff check --fix .

api-types: ## Regenerate the typed frontend API client from the backend's OpenAPI spec
	cd backend && uv run python -m app.export_openapi > ../frontend/openapi.json
	cd frontend && pnpm api-types

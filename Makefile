.PHONY: help dev up down ingest test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Docker ---
up: ## Start all services with Docker Compose
	docker compose up --build -d

down: ## Stop all services
	docker compose down

logs: ## Tail all logs
	docker compose logs -f

# --- Development (local) ---
dev-backend: ## Run backend locally (requires venv)
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

# --- Database ---
migrate: ## Run database migrations
	cd backend && python -m alembic upgrade head

# --- Ingestion ---
ingest: ## Run transcript ingestion
	curl -s -X POST http://localhost:8000/api/ingestion/run | python -m json.tool

# --- Testing ---
test-backend: ## Run backend tests
	cd backend && python -m pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-backend test-frontend ## Run all tests

# --- Cleanup ---
clean: ## Remove containers, volumes, and build artifacts
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

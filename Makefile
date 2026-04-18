.PHONY: help dev-backend dev-frontend install-backend install-frontend \
        docker-build docker-up docker-down docker-logs \
        lint-backend type-check-frontend clean

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Foundry AI — Available commands"
	@echo "────────────────────────────────────────────────────────"
	@echo "  make install-backend      Install Python dependencies"
	@echo "  make install-frontend     Install Node dependencies"
	@echo "  make dev-backend          Run backend in dev mode"
	@echo "  make dev-frontend         Run frontend in dev mode"
	@echo "  make docker-build         Build Docker images"
	@echo "  make docker-up            Start all services (detached)"
	@echo "  make docker-down          Stop all services"
	@echo "  make docker-logs          Tail logs from all containers"
	@echo "  make lint-backend         Run Python syntax check"
	@echo "  make type-check-frontend  Run TypeScript type check"
	@echo "  make clean                Remove build artifacts"
	@echo ""

# ── Local development ─────────────────────────────────────────────────────────
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm ci

dev-backend:
	cd backend && python main.py

dev-frontend:
	cd frontend && npm run dev

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose down && docker compose up -d

# ── Quality ───────────────────────────────────────────────────────────────────
lint-backend:
	python3 -c "\
import ast, sys, os; \
errors = []; \
[errors.append(f'{os.path.join(r,f)}: {e}') \
  for r,d,files in os.walk('backend') \
  for f in files if f.endswith('.py') \
  for e in [None] \
  if (lambda src: (ast.parse(src), None)[1] \
      if not (lambda: (_ for _ in ()).throw(SyntaxError()))() else None)( \
      open(os.path.join(r,f)).read()) is None]; \
print('Lint OK' if not errors else '\n'.join(errors))"
	@echo "Backend syntax OK"

type-check-frontend:
	cd frontend && npm run type-check

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next frontend/out frontend/node_modules/.cache

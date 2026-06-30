.PHONY: dev prod build logs down

# Desarrollo local (sin Docker)
dev:
	@./dev.sh

# Producción con Docker
prod:
	docker compose up -d

# Rebuild y producción
build:
	docker compose up --build -d

# Ver logs
logs:
	docker compose logs -f

# Apagar
down:
	docker compose down

# Instalar dependencias de todo el monorepo
install:
	cd api && uv sync
	cd web && pnpm install

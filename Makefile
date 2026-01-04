COMPOSE=docker compose

.PHONY: init build up down ps logs logs-be logs-fe logs-evo shell-be shell-fe

init:
	@echo "[init] Creating volumes and databases on first run"
	$(COMPOSE) up -d postgres redis minio
	@sleep 5
	@echo "[init] Postgres/Redis/MinIO up."

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

 down:
	$(COMPOSE) down

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f

logs-be:
	$(COMPOSE) logs -f evoai-backend

logs-fe:
	$(COMPOSE) logs -f evoai-frontend

logs-evo:
	$(COMPOSE) logs -f evolution-api

shell-be:
	$(COMPOSE) exec evoai-backend /bin/sh

shell-fe:
	$(COMPOSE) exec evoai-frontend /bin/sh

.PHONY: docs
docs:
	@echo "📝 Gerando documentação Evolution API..."
	@bash evo-ai_tmp_clone/scripts/convert-postman-docs.sh

# 28HubConect — Orquestração evo-ai + Evolution-API

Este repositório integra o evo-ai (backend FastAPI + frontend Next.js) com a Evolution-API e serviços de infraestrutura (Postgres, Redis, MinIO e Nginx), permitindo criar e conectar instâncias WhatsApp e vincular o chatbot EvoAI diretamente pela UI do evo-ai.

## Requisitos
- Docker 24+
- Docker Compose v2+

## Primeiros passos
1. Copie `.env.example` para `.env` e ajuste valores conforme seu ambiente.
2. Execute a inicialização básica:
```bash
make init
```
3. Construa e suba todos os serviços:
```bash
make build
make up
```
4. Acesse:
- Frontend: http://localhost/
- Backend evo-ai (docs): http://localhost/api/docs
- Evolution-API (exposto via Nginx em /evolution/): http://localhost/evolution/
- MinIO Console: http://localhost/minio/

## Serviços
- Postgres 15 — bancos `evo_ai` (evo-ai) e `evolution_db` (evolution-api)
- Redis 7 — cache/filas
- MinIO — storage S3-compatível (versão fixa licenciada: RELEASE.2022-10-05T14-58-27Z)
- evo-ai backend — FastAPI
- evo-ai frontend — Next.js
- Evolution-API — provedor de integrações WhatsApp
- Nginx — reverse proxy

## Configuração de integração
- No `.env`, configure:
  - `POSTGRES_CONNECTION_STRING` do evo-ai
  - `EVOLUTION_API_BASE_URL` e `EVOLUTION_API_APIKEY` (chamadas do evo-ai → Evolution-API)
  - `EVOAI_AGENT_URL` e `EVOAI_AGENT_APIKEY` (Evolution-API → evo-ai para processamento do chatbot)

## Fluxo básico
- Em `/channels`, crie a instância e clique em “Conectar” para exibir o QR. Após conectar, o bot EvoAI é vinculado automaticamente.

## Comandos úteis
```bash
make ps          # status
make logs        # logs gerais
make logs-be     # logs backend evo-ai
make logs-fe     # logs frontend evo-ai
make logs-evo    # logs evolution-api
make down        # derrubar stack
```

## Observações
- Ajuste os endpoints no frontend via `NEXT_PUBLIC_API_BASE_URL` se publicar atrás de diferentes caminhos.
- Para multi-tenant, mova as variáveis da Evolution-API e do agente para tabela de Settings por tenant.

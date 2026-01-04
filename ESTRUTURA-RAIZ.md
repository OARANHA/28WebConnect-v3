# 📦 ESTRUTURA RAIZ - 28HubConect

## 📁 Estrutura de Pastas (Raiz do Projeto)

```
28HubConect/
├── evo-ai/                          # ✅ JÁ EXISTE (com suas páginas)
│   ├── frontend/
│   │   ├── app/(protected)/
│   │   ├── app/(public)/login/
│   │   └── ...
│   ├── src/
│   │   ├── api/
│   │   │   ├── auth_routes.py       ✅ JÁ EXISTE
│   │   │   ├── dashboard_routes.py  ✅ SUAS ROTAS
│   │   │   └── ... (8 endpoints)
│   │   └── ...
│   └── Dockerfile
│
├── evolution-api/                   # ✅ JÁ EXISTE (clonado)
│   ├── ...
│   └── Dockerfile
│
├── docker-compose.yml               # 🆕 CRIAR (orquestração)
├── init.sql                         # 🆕 CRIAR (inicialização DB)
├── nginx.conf                       # 🆕 CRIAR (reverse proxy)
├── .env.example                     # 🆕 CRIAR (template variáveis)
├── .env                             # 🆕 CRIAR (suas credenciais)
├── Makefile                         # 🆕 CRIAR (comandos úteis)
├── README.md                        # 🆕 CRIAR (documentação raiz)
└── docs/
    ├── SETUP.md                     # 🆕 CRIAR (guia setup)
    ├── DEPLOYMENT.md                # 🆕 CRIAR (deploy produção)
    └── API.md                       # 🆕 CRIAR (documentação API)
```

---

## 📄 Arquivo 1: `docker-compose.yml` (RAIZ)

**Localização:** `/28HubConect/docker-compose.yml`

```yaml
version: '3.9'

services:
  # ==========================================
  # DATABASE - PostgreSQL
  # ==========================================
  postgres:
    image: postgres:15-alpine
    container_name: hubconect_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_INITDB_ARGS: --encoding=UTF8
      TZ: America/Sao_Paulo
    ports:
      - \"5432:5432\"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - hubconect_network
    healthcheck:
      test: [\"CMD-SHELL\", \"pg_isready -U postgres\"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ==========================================
  # CACHE - Redis
  # ==========================================
  redis:
    image: redis:7-alpine
    container_name: hubconect_redis
    ports:
      - \"6379:6379\"
    volumes:
      - redis_data:/data
    networks:
      - hubconect_network
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ==========================================
  # STORAGE - MinIO (S3-compatible) -smepre esse por questão de licença minio:RELEASE.2022-10-05T14-58-27Z
  # ==========================================
  minio:
    image: minio/minio:RELEASE.2022-10-05T14-58-27Z  # ✅ LICENÇA OK
    container_name: hubconect_minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - \"9000:9000\"
      - \"9001:9001\"
    volumes:
      - minio_data:/minio_data
    command: server /minio_data --console-address \":9001\"
    networks:
      - hubconect_network
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:9000/minio/health/live\"]
      interval: 30s
      timeout: 20s
      retries: 3
    restart: unless-stopped

  # ==========================================
  # EVO-AI BACKEND - FastAPI
  # ==========================================
  evo-ai-backend:
    build:
      context: ./evo-ai
      dockerfile: Dockerfile
      target: backend
    container_name: hubconect_evo_ai_backend
    environment:
      # Database
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/28hubconect_db
      # Redis
      REDIS_URL: redis://redis:6379/0
      # JWT
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-sua-chave-secreta-super-segura-aqui}
      # MinIO
      MINIO_URL: http://minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
      # App settings
      ENVIRONMENT: development
      LOG_LEVEL: info
      TZ: America/Sao_Paulo
    ports:
      - \"8000:8000\"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    volumes:
      - ./evo-ai/src:/app/src
      - ./evo-ai/scripts:/app/scripts
    networks:
      - hubconect_network
    restart: unless-stopped
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  # ==========================================
  # EVO-AI FRONTEND - Next.js
  # ==========================================
  evo-ai-frontend:
    build:
      context: ./evo-ai/frontend
      dockerfile: Dockerfile
    container_name: hubconect_evo_ai_frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NODE_ENV: development
      TZ: America/Sao_Paulo
    ports:
      - \"3000:3000\"
    depends_on:
      - evo-ai-backend
    volumes:
      - ./evo-ai/frontend:/app
      - /app/node_modules
    networks:
      - hubconect_network
    restart: unless-stopped

  # ==========================================
  # EVOLUTION-API - WhatsApp/Integrations
  # ==========================================
  evolution-api:
    image: evolutionapi/evolution-api:latest
    container_name: hubconect_evolution_api
    environment:
      EVOLUTION_INSTANCE_NAME: 28hubconect
      SERVER_URL: http://localhost:8080
      API_KEY: ${EVOLUTION_API_KEY:-evolution-api-key}
      DATABASE_CONNECTION_URI: postgresql://postgres:postgres@postgres:5432/evolution_db
      REDIS_URL: redis://redis:6379/1
      LOG_LEVEL: info
      TZ: America/Sao_Paulo
    ports:
      - \"8080:8080\"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - hubconect_network
    restart: unless-stopped

  # ==========================================
  # NGINX - Reverse Proxy
  # ==========================================
  nginx:
    image: nginx:alpine
    container_name: hubconect_nginx
    ports:
      - \"80:80\"
      - \"443:443\"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - evo-ai-frontend
      - evo-ai-backend
      - evolution-api
      - minio
    networks:
      - hubconect_network
    restart: unless-stopped

# ==========================================
# VOLUMES
# ==========================================
volumes:
  postgres_data:
  redis_data:
  minio_data:

# ==========================================
# NETWORKS
# ==========================================
networks:
  hubconect_network:
    driver: bridge
```

---

## 📄 Arquivo 2: `init.sql` (RAIZ)

**Localização:** `/28HubConect/init.sql`

```sql
-- ==========================================
-- CREATE DATABASES
-- ==========================================
CREATE DATABASE 28hubconect_db;
CREATE DATABASE evolution_db;

-- Connect to 28hubconect_db
\\c 28hubconect_db;

-- ==========================================
-- USER TABLES (JÁ EXISTEM NO EVO-AI)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    last_login TIMESTAMP,
    login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    granted_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(user_id, resource, action)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    status VARCHAR(20),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_action ON audit_logs(action);

-- ==========================================
-- ADMIN USER (PADRÃO)
-- ==========================================
INSERT INTO users (
    email,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    created_at
) VALUES (
    'admin@28hubconect.local',
    '\\$2b\\$12\\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUVj2uDO', -- Senha: Admin@12345 (bcrypt)
    'Admin',
    'User',
    'admin',
    'active',
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- ==========================================
-- CREATE INDEXES
-- ==========================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

---

## 📄 Arquivo 3: `.env.example` (RAIZ)

**Localização:** `/28HubConect/.env.example`

```bash
# ==========================================
# POSTGRES
# ==========================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/28hubconect_db

# ==========================================
# REDIS
# ==========================================
REDIS_URL=redis://redis:6379/0

# ==========================================
# JWT
# ==========================================
JWT_SECRET_KEY=sua-chave-secreta-super-segura-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# ==========================================
# MINIO (S3)
# ==========================================
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=28hubconect

# ==========================================
# EVO-AI BACKEND
# ==========================================
ENVIRONMENT=development
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000

# ==========================================
# EVO-AI FRONTEND
# ==========================================
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development

# ==========================================
# EVOLUTION-API
# ==========================================
EVOLUTION_API_KEY=evolution-api-key
EVOLUTION_INSTANCE_NAME=28hubconect
EVOLUTION_SERVER_URL=http://localhost:8080

# ==========================================
# EMAIL (SendGrid)
# ==========================================
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=

# ==========================================
# GENERAL
# ==========================================
TZ=America/Sao_Paulo
```

---

## 📄 Arquivo 4: `nginx.conf` (RAIZ)

**Localização:** `/28HubConect/nginx.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] \"$request\" '
                    '$status $body_bytes_sent \"$http_referer\" '
                    '\"$http_user_agent\" \"$http_x_forwarded_for\"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # ==========================================
    # FRONTEND (Next.js)
    # ==========================================
    upstream frontend {
        server evo-ai-frontend:3000;
    }

    # ==========================================
    # BACKEND (FastAPI)
    # ==========================================
    upstream backend {
        server evo-ai-backend:8000;
    }

    # ==========================================
    # EVOLUTION-API
    # ==========================================
    upstream evolution {
        server evolution-api:8080;
    }

    # ==========================================
    # MINIO
    # ==========================================
    upstream minio {
        server minio:9000;
    }

    # ==========================================
    # HTTP → HTTPS (Production only)
    # ==========================================
    # server {
    #     listen 80;
    #     server_name _;
    #     return 301 https://\$host\$request_uri;
    # }

    # ==========================================
    # MAIN SERVER
    # ==========================================
    server {
        listen 80 default_server;
        server_name _;

        # ==========================================
        # FRONTEND ROUTES
        # ==========================================
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
        }

        # ==========================================
        # BACKEND API ROUTES
        # ==========================================
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_read_timeout 60s;
        }

        # ==========================================
        # EVOLUTION-API ROUTES
        # ==========================================
        location /evolution/ {
            proxy_pass http://evolution/;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # ==========================================
        # MINIO ROUTES
        # ==========================================
        location /storage/ {
            proxy_pass http://minio/;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }

        # ==========================================
        # HEALTH CHECK
        # ==========================================
        location /health {
            access_log off;
            return 200 \"healthy\\n\";
            add_header Content-Type text/plain;
        }
    }

    # ==========================================
    # HTTPS (Production)
    # ==========================================
    # server {
    #     listen 443 ssl http2 default_server;
    #     server_name 28hubconect.com.br;
    #
    #     ssl_certificate /etc/nginx/certs/cert.pem;
    #     ssl_certificate_key /etc/nginx/certs/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # ... rest da config igual ao acima
    # }
}
```

---

## 📄 Arquivo 5: `Makefile` (RAIZ)

**Localização:** `/28HubConect/Makefile`

```makefile
.PHONY: help init build up down logs ps shell-postgres shell-redis clean restart rebuild

# Colors
CYAN=\\033[0;36m
GREEN=\\033[0;32m
YELLOW=\\033[1;33m
RED=\\033[0;31m
NC=\\033[0m

help:
	@echo \"$(CYAN)28HubConect - Docker Management$(NC)\"
	@echo \"$(YELLOW)Available commands:$(NC)\"
	@echo \"  $(GREEN)make init$(NC)          - Initialize .env from .env.example\"
	@echo \"  $(GREEN)make build$(NC)         - Build all Docker images\"
	@echo \"  $(GREEN)make up$(NC)            - Start all services (docker-compose up -d)\"
	@echo \"  $(GREEN)make down$(NC)          - Stop all services\"
	@echo \"  $(GREEN)make logs$(NC)          - View all logs (docker-compose logs -f)\"
	@echo \"  $(GREEN)make logs-backend$(NC)  - View backend logs\"
	@echo \"  $(GREEN)make logs-frontend$(NC) - View frontend logs\"
	@echo \"  $(GREEN)make ps$(NC)            - List all running containers\"
	@echo \"  $(GREEN)make shell-postgres$(NC) - Connect to PostgreSQL CLI\"
	@echo \"  $(GREEN)make shell-redis$(NC)   - Connect to Redis CLI\"
	@echo \"  $(GREEN)make clean$(NC)         - Remove all containers and volumes\"
	@echo \"  $(GREEN)make restart$(NC)       - Restart all services\"
	@echo \"  $(GREEN)make rebuild$(NC)       - Rebuild and restart all services\"
	@echo \"  $(GREEN)make test$(NC)          - Run tests\"

init:
	@if [ ! -f .env ]; then \\
		cp .env.example .env; \\
		echo \"$(GREEN)✓ .env created from .env.example$(NC)\"; \\
	else \\
		echo \"$(YELLOW)⚠ .env already exists$(NC)\"; \\
	fi

build:
	@echo \"$(CYAN)Building Docker images...$(NC)\"
	docker-compose build --no-cache

up:
	@echo \"$(CYAN)Starting services...$(NC)\"
	docker-compose up -d
	@echo \"$(GREEN)✓ Services started$(NC)\"
	@echo \"\"
	@echo \"$(CYAN)Available at:$(NC)\"
	@echo \"  Frontend:     http://localhost:3000\"
	@echo \"  Backend API:  http://localhost:8000/docs\"
	@echo \"  Evolution API: http://localhost:8080\"
	@echo \"  MinIO:        http://localhost:9001\"
	@echo \"  PostgreSQL:   localhost:5432\"

down:
	@echo \"$(CYAN)Stopping services...$(NC)\"
	docker-compose down
	@echo \"$(GREEN)✓ Services stopped$(NC)\"

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f evo-ai-backend

logs-frontend:
	docker-compose logs -f evo-ai-frontend

ps:
	@echo \"$(CYAN)Running containers:$(NC)\"
	docker-compose ps

shell-postgres:
	docker-compose exec postgres psql -U postgres -d 28hubconect_db

shell-redis:
	docker-compose exec redis redis-cli

clean:
	@echo \"$(RED)Removing all containers and volumes...$(NC)\"
	docker-compose down -v
	@echo \"$(GREEN)✓ Cleaned$(NC)\"

restart: down up

rebuild: clean build up

test:
	@echo \"$(CYAN)Running tests...$(NC)\"
	docker-compose exec evo-ai-backend pytest
	docker-compose exec evo-ai-frontend npm test
```

---

## 📄 Arquivo 6: `README.md` (RAIZ)

**Localização:** `/28HubConect/README.md`

```markdown
# 📱 28HubConect - Plataforma Omnichannel

Plataforma completa de automação omnichannel com WhatsApp, email, Instagram, pipelines, CRM e muito mais.

## 🚀 Características

- ✅ Dashboard completo com analytics
- ✅ Gerenciamento de Pipelines
- ✅ Integração com WhatsApp (Evolution API)
- ✅ Canais de comunicação (Email, Instagram, etc)
- ✅ CRM integrado
- ✅ Campanhas de marketing
- ✅ Ferramentas e integrações
- ✅ Auditoria completa
- ✅ Autenticação JWT
- ✅ Storage S3 (MinIO)

## 📋 Pré-requisitos

- Docker >= 20.10
- Docker Compose >= 1.29
- 4GB RAM mínimo
- 10GB espaço em disco

## 🔧 Instalação Rápida

### 1. Clone o repositório

\`\`\`bash
git clone https://github.com/seu-usuario/28HubConect.git
cd 28HubConect
\`\`\`

### 2. Inicialize as variáveis de ambiente

\`\`\`bash
make init
\`\`\`

### 3. Construa as imagens

\`\`\`bash
make build
\`\`\`

### 4. Inicie os serviços

\`\`\`bash
make up
\`\`\`

## 🌐 Acessos

Após iniciar, acesse:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Evolution API | http://localhost:8080 | - |
| PostgreSQL | localhost:5432 | postgres / postgres |
| Redis | localhost:6379 | - |

## 🔐 Login Padrão

\`\`\`
Email: admin@28hubconect.local
Senha: Admin@12345
\`\`\`

## 📚 Documentação

- [Setup Detalhado](./docs/SETUP.md)
- [Deployment em Produção](./docs/DEPLOYMENT.md)
- [Documentação da API](./docs/API.md)

## 🛠️ Comandos Úteis

\`\`\`bash
# Ver logs
make logs

# Parar serviços
make down

# Reiniciar
make restart

# Acessar PostgreSQL
make shell-postgres

# Acessar Redis
make shell-redis

# Limpar tudo
make clean
\`\`\`

## 📁 Estrutura do Projeto

\`\`\`
28HubConect/
├── evo-ai/              # Frontend + Backend (Next.js + FastAPI)
├── evolution-api/       # WhatsApp Integration
├── docker-compose.yml   # Orquestração dos serviços
├── nginx.conf          # Configuração do proxy reverso
├── init.sql            # Inicialização do banco
├── .env                # Variáveis de ambiente
└── docs/               # Documentação
\`\`\`

## 🚀 Deploy em Produção

Veja [DEPLOYMENT.md](./docs/DEPLOYMENT.md) para instruções completas.

\`\`\`bash
# Build para produção
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

## 🐛 Troubleshooting

### Serviço não inicia
\`\`\`bash
# Verificar logs
make logs

# Reiniciar serviço específico
docker-compose restart nome-servico
\`\`\`

### Banco de dados não conecta
\`\`\`bash
# Verificar status
docker-compose ps

# Reiniciar postgres
docker-compose restart postgres

# Conectar ao psql
make shell-postgres
\`\`\`min

### Frontend não carrega
\`\`\`bash
# Limpar node_modules e reinstalar
docker-compose exec evo-ai-frontend npm install

# Reiniciar frontend
docker-compose restart evo-ai-frontend
\`\`\`

## 📞 Suporte

- Issues: GitHub Issues
- Documentação: [Wiki](https://github.com/OARANHAO/28HubConect/wiki)
- Email: suporte@28hubconect.local

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👥 Contribuidores

- Você (Intermediário)
- Rovo (Desenvolvedor)
- Plex (Arquiteto)

---

**Última atualização:** Janeiro 2026
```

---

## 📋 Quick Start - Passo a Passo

```bash
# 1. Clone repositories
cd 28HubConect
git clone https://github.com/EvolutionAPI/evo-ai.git
git clone https://github.com/EvolutionAPI/evolution-api.git

# 2. Copiar seus endpoints para evo-ai/src/api/
cp seus_endpoints/*.py evo-ai/src/api/

# 3. Copiar suas páginas para evo-ai/frontend/
mkdir -p evo-ai/frontend/app/(protected)/{dashboard,pipelines,channels,contacts,campaigns,settings,tools,audit}
cp suas_paginas/*.tsx evo-ai/frontend/app/(protected)/

# 4. Iniciar tudo
make init
make build
make up

# 5. Testar
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

---

## ✅ Checklist para Rovo

- [X] Criar repositório 28HubConect
- [X] Clonar evo-ai e evolution-api
- [X] Criar arquivos de raiz (docker-compose.yml, init.sql, etc)
- [X] Executar `make init && make build && make up`
- [X] Testar login em http://localhost:8002/login
- [X] Verificar endpoints em http://localhost:8000/docs
- [ ] Confirmar que todas as 9 páginas carregam
- [ ] Fazer backup das variáveis .env

---

**Pronto para começar! 🚀**

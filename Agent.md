# 🤖 Agent.md - Guia de Continuidade do Projeto Evo AI

Este documento contém todas as informações necessárias para que outra IA possa dar continuidade ao projeto **Evo AI Enhanced**, transformando-o em uma plataforma completa de automação omnichannel.

---

## 📋 Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [O Que Foi Implementado](#2-o-que-foi-implementado)
3. [Estrutura do Projeto](#3-estrutura-do-projeto)
4. [Como Dar Continuidade](#4-como-dar-continuidade)
5. [Próximos Passos Sugeridos](#5-próximos-passos-sugeridos)
6. [Tecnologias Utilizadas](#6-tecnologias-utilizadas)
7. [APIs Disponíveis](#7-apis-disponíveis)
8. [Como Rodar o Projeto](#8-como-rodar-o-projeto)
9. [Variáveis de Ambiente](#9-variáveis-de-ambiente)
10. [Arquitetura do Sistema](#10-arquitetura-do-sistema)
11. [Integrações Existentes](#11-integrações-existentes)
12. [Bugs Conhecidos e Melhorias](#12-bugs-conhecidos-e-melhorias)

---

## 1. Visão Geral do Projeto

### Nome do Projeto
**Evo AI Enhanced** - Plataforma de Inteligência Artificial com integração omnichannel

### Descrição
O Evo AI é uma plataforma para criar e gerenciar agentes AI, integrada com o **Evolution API** para múltiplos canais de comunicação (WhatsApp, Instagram, Email, SMS). A versão enhanced adiciona funcionalidades de CRM, automação de campanhas, pipelines de workflows, e sistema de auditoria.

### Objetivo
Transformar o Evo AI de uma simples plataforma de agentes AI em uma **solução completa de automação omnichannel**, similar a plataformas como Typebot, Dify AI e Chatwoot.

### Repositórios de Origem
- **Evo AI:** `https://github.com/EvolutionAPI/evo-ai` (frontend Next.js + backend Python/FastAPI)
- **Evolution API:** `https://github.com/EvolutionAPI/evolution-api` (backend Node.js para integração WhatsApp/canais)

### Caminho do Projeto
```
/home/z/my-project/evo-ai/
```

---

## 2. O Que Foi Implementado

### ✅ Frontend (Next.js)

#### 2.1 Sidebar Aprimorado
**Arquivo:** `evo-ai/frontend/components/sidebar.tsx`

**Funcionalidades:**
- 9 novos menus principais adicionados
- 2 novos menus de admin adicionados
- Sistema de badges "New" nos menus novos
- Suporte a collapse/expand do sidebar
- Persistência do estado do sidebar no localStorage
- Seções visuais (Main, Administration)
- Menu de usuário (My Account) com Profile, Security e Logout

**Menus Principais (Todos os Usuários):**
1. 📊 **Dashboard** - Visão geral com métricas (NOVO)
2. 🤖 **Agents** - Gerenciamento de agentes AI
3. 🔀 **Pipelines** - Workflows de automação visual (NOVO)
4. 💬 **Chat** - Interface de chat com agentes
5. 📱 **Channels** - Integração com canais de comunicação (NOVO)
6. 👥 **Contacts** - CRM integrado (NOVO)
7. 🎯 **Campaigns** - Envio em massa de mensagens (NOVO)
8. 🔧 **Tools** - Ferramentas customizadas (NOVO)
9. 🌐 **Shared Chat** - Showcase de agentes públicos
10. 📚 **Documentation** - Documentação técnica

**Menus de Admin:**
1. 🖥️ **MCP Servers** - Gerenciamento de servidores MCP
2. 💼 **Clients** - Gerenciamento de clientes
3. ⚙️ **Settings** - Configurações globais (NOVO)
4. 📜 **Audit** - Logs de auditoria (NOVO)

#### 2.2 Novas Páginas Criadas

Todas as páginas seguem o mesmo padrão:
- Usam `shadcn/ui` para componentes UI
- Estilizadas com Tailwind CSS
- Tema escuro (`bg-[#121212]`)
- Cards com fundo `bg-neutral-900`
- Texto branco/neutral

**Arquivos Criados:**

1. **`evo-ai/frontend/app/dashboard/page.tsx`**
   - Cards de métricas principais
   - Seção de gráficos (placeholders)
   - Lista de atividade recente
   - Ações rápidas

2. **`evo-ai/frontend/app/pipelines/page.tsx`**
   - Grid de cards de pipelines
   - Status de pipeline (Ativo/Pausado)
   - Estatísticas de execuções
   - Botões para editar e executar pipelines

3. **`evo-ai/frontend/app/channels/page.tsx`**
   - Grid de cards de canais
   - Suporte para múltiplos tipos (WhatsApp, Instagram, Email, SMS)
   - Status de conexão (Conectado/Desconectado)
   - Estatísticas de mensagens por canal
   - Ícones específicos por tipo de canal

4. **`evo-ai/frontend/app/contacts/page.tsx`**
   - Lista completa de contatos
   - Barra de busca avançada
   - Sistema de tags para segmentação
   - Informações de contato (nome, email, telefone)
   - Histórico de mensagens por contato

5. **`evo-ai/frontend/app/campaigns/page.tsx`**
   - Grid de cards de campanhas
   - Status de campanha (Em andamento/Agendada/Concluída/Pausada)
   - Estatísticas detalhadas (Enviados, Entregues, Abertos)
   - Suporte para diferentes canais (WhatsApp, Email)
   - Sistema de agendamento
   - Botões para iniciar/pausar/duplicar campanhas

6. **`evo-ai/frontend/app/settings/page.tsx`**
   - Configurações gerais (Modo Escuro, Notificações, Sons)
   - Webhooks e integrações (Typebot, Dify AI)
   - Armazenamento (S3, Minio)
   - Notificações (Email, Push, Resumo Diário)
   - Segurança (API Keys, Domínios Permitidos)

7. **`evo-ai/frontend/app/tools/page.tsx`**
   - Lista de ferramentas customizadas
   - Barra de busca
   - Suporte para ferramentas customizadas e integrações
   - Estatísticas de uso (último uso, execuções)
   - Status de ferramenta (Ativa/Inativa)
   - Botão para testar ferramentas

8. **`evo-ai/frontend/app/audit/page.tsx`** (Admin Only)
   - Lista completa de logs de auditoria
   - Sistema de busca e filtros
   - Classificação por tipo de ação (create, update, delete, execute, security)
   - Ícones coloridos por tipo de ação
   - Sistema de paginação
   - Botão para exportar logs

#### 2.3 Página Principal Atualizada

**Arquivo:** `evo-ai/frontend/app/page.tsx`

**Alteração:**
- Redireciona de `/` para `/dashboard` em vez de `/agents`

---

### ✅ Backend (Python/FastAPI)

#### 2.4 Novos Endpoints API Criados

Todos os endpoints seguem o padrão RESTful e retornam dados simulados para desenvolvimento. Use `pydantic` para validação e `SQLAlchemy` para persistência em produção.

**Arquivos Criados:**

1. **`evo-ai/src/api/dashboard_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/dashboard/stats` - Estatísticas principais
     ```json
     {
       "totalAgents": 24,
       "chatSessions": 1234,
       "activeContacts": 5678,
       "activePipelines": 12,
       "agentGrowth": 2,
       "chatGrowth": 18,
       "contactGrowth": 201,
       "pipelineGrowth": 3
     }
     ```
   
   - `GET /api/v1/dashboard/activity` - Atividade recente
     ```json
     [
       {"action": "Novo agente criado", "time": "Há 2 horas", "user": "João Silva"},
       {"action": "Pipeline 'Vendas' atualizado", "time": "Há 4 horas", "user": "Maria Santos"},
       {"action": "Canal WhatsApp conectado", "time": "Há 6 horas", "user": "Pedro Costa"}
     ]
     ```
   
   - `GET /api/v1/dashboard/charts/chat` - Dados do gráfico de chat
     ```json
     [
       {"date": "2025-01-09", "sessions": 145},
       {"date": "2025-01-10", "sessions": 189},
       {"date": "2025-01-11", "sessions": 167}
     ]
     ```
   
   - `GET /api/v1/dashboard/charts/contacts` - Dados do gráfico de contatos
     ```json
     [
       {"month": "2024-08", "contacts": 4100},
       {"month": "2024-09", "contacts": 4350},
       {"month": "2024-10", "contacts": 4620}
     ]
     ```

2. **`evo-ai/src/api/pipelines_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/pipelines/` - Listar todos os pipelines
     ```json
     [
       {
         "id": 1,
         "name": "Pipeline de Vendas",
         "description": "Fluxo de atendimento automatizado para vendas",
         "status": "active",
         "lastRun": "Há 2 horas",
         "executions": 156
       }
     ]
     ```
   
   - `POST /api/v1/pipelines/` - Criar novo pipeline
     ```json
     {
       "name": "Novo Pipeline",
       "description": "Descrição do pipeline",
       "type": "workflow"
     }
     ```

3. **`evo-ai/src/api/channels_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/channels/` - Listar todos os canais
     ```json
     [
       {
         "id": 1,
         "name": "WhatsApp Business",
         "type": "whatsapp",
         "description": "WhatsApp Cloud API para atendimento",
         "status": "connected",
         "phoneNumber": "+55 11 98765-4321",
         "messagesToday": 234
       }
     ]
     ```
   
   - `POST /api/v1/channels/` - Criar novo canal
     ```json
     {
       "name": "Novo Canal",
       "type": "whatsapp",
       "description": "Descrição do canal",
       "phoneNumber": "+55 11 12345-6789"
     }
     ```

4. **`evo-ai/src/api/contacts_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/contacts/?search=termo` - Listar contatos com busca
     ```json
     [
       {
         "id": 1,
         "name": "João Silva",
         "phone": "+55 11 98765-4321",
         "email": "joao.silva@email.com",
         "tags": ["cliente-vip", "recorrente"],
         "lastContact": "Há 2 horas",
         "messages": 45
       }
     ]
     ```
   
   - `POST /api/v1/contacts/` - Criar novo contato
     ```json
     {
       "name": "Novo Contato",
       "phone": "+55 11 12345-6789",
       "email": "novo@email.com",
       "tags": ["lead"]
     }
     ```

5. **`evo-ai/src/api/campaigns_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/campaigns/` - Listar todas as campanhas
     ```json
     [
       {
         "id": 1,
         "name": "Promoção de Natal",
         "description": "Campanha de promoções de fim de ano",
         "status": "running",
         "type": "whatsapp",
         "recipients": 1250,
         "sent": 875,
         "delivered": 820,
         "opened": 645,
         "scheduled": "2025-01-15 10:00"
       }
     ]
     ```
   
   - `POST /api/v1/campaigns/` - Criar nova campanha
     ```json
     {
       "name": "Nova Campanha",
       "description": "Descrição da campanha",
       "type": "whatsapp",
       "recipients": 1000,
       "message": "Mensagem da campanha",
       "scheduled": "2025-01-20 09:00"
     }
     ```

6. **`evo-ai/src/api/tools_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/tools/?search=termo` - Listar ferramentas com busca
     ```json
     [
       {
         "id": 1,
         "name": "Calculadora de Preços",
         "description": "Calcula preços baseado em parâmetros personalizados",
         "type": "custom",
         "lastUsed": "Há 2 horas",
         "executions": 156,
         "status": "active",
         "code": "function calculatePrice(basePrice, discount) { return basePrice - (basePrice * discount / 100); }"
       }
     ]
     ```
   
   - `POST /api/v1/tools/` - Criar nova ferramenta
     ```json
     {
       "name": "Nova Ferramenta",
       "description": "Descrição da ferramenta",
       "type": "custom",
       "code": "function myTool() { // código da ferramenta }"
     }
     ```

7. **`evo-ai/src/api/audit_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/audit/?search=termo&type=tipo` - Listar logs com filtros
     ```json
     {
       "logs": [
         {
           "id": 1,
           "action": "Criou novo agente",
           "entity": "Agent: Assistente de Vendas",
           "user": "João Silva",
           "timestamp": "2025-01-15 14:32:15",
           "type": "create",
           "ip": "192.168.1.100"
         }
       ],
       "total": 1234
     }
     ```
   
   - `POST /api/v1/audit/` - Criar novo log de auditoria
     ```json
     {
       "action": "Criou novo agente",
       "entity": "Agent: Novo Agente",
       "type": "create",
       "ip": "192.168.1.100"
     }
     ```

8. **`evo-ai/src/api/settings_routes.py`**
   
   **Endpoints:**
   - `GET /api/v1/settings/` - Obter configurações do sistema
     ```json
     {
       "general": {
         "darkMode": true,
         "realTimeNotifications": true,
         "notificationSounds": true
       },
       "notifications": {
         "emailNotifications": false,
         "pushNotifications": true,
         "dailySummary": false
       },
       "webhooks": [
         {
           "id": 1,
           "name": "Webhook de Mensagens",
           "description": "Receba eventos de novas mensagens",
           "status": "Ativo",
           "url": "https://example.com/webhook/messages"
         }
       ],
       "integrations": [
         {
           "id": 1,
           "name": "Typebot",
           "description": "Conectar com Typebot para workflows",
           "status": "Não configurado"
         },
         {
           "id": 2,
           "name": "Dify AI",
           "description": "Integração com Dify para agentes",
           "status": "Conectado"
         }
       ]
     }
     ```
   
   - `PUT /api/v1/settings/` - Atualizar configurações do sistema
     ```json
     {
       "general": {
         "darkMode": true,
         "realTimeNotifications": true
       },
       "notifications": {
         "emailNotifications": false,
         "pushNotifications": true
       }
     }
     ```

---

### ✅ Docker (Containerização)

#### 2.5 Dockerfile Multi-Stage

**Arquivo:** `evo-ai/Dockerfile`

**Estágios de Build:**
1. **frontend-builder** - Build do frontend Next.js
2. **backend** - Ambiente Python com dependências
3. **final** - Imagem final com tudo otimizado

**Características:**
- Usa Node.js 18 Alpine para o frontend
- Usa Python 3.11 Slim para o backend
- Multi-stage build para otimizar tamanho da imagem
- Non-root user por segurança
- Health checks configurados
- Exposição das portas 8000 (backend) e 3000 (frontend)

#### 2.6 Docker Compose

**Arquivo:** `evo-ai/docker-compose.yml`

**Serviços Configurados:**

1. **evoai (aplicação principal)**
   - Frontend (Next.js): porta 3000
   - Backend (FastAPI): porta 8000
   - Health check configurado
   - Variáveis de ambiente do frontend e backend

2. **postgres**
   - PostgreSQL 15 Alpine
   - Database: `evoai`
   - User: `evoai`
   - Password: `evoai_password`
   - Volume persistente
   - Health check configurado

3. **redis**
   - Redis 7 Alpine
   - Comando: `redis-server --appendonly yes`
   - Volume persistente
   - Health check configurado

4. **minio**
   - MinIO (S3 compatível)
   - API: porta 9000
   - Console: porta 9001
   - Credenciais padrão (minioadmin/minioadmin)
   - Volume persistente

5. **evolution-api**
   - Evolution API (integração WhatsApp)
   - Porta: 8080
   - Database: SQLite
   - Autenticação: API Key
   - Volume persistente para store

6. **nginx**
   - Nginx Alpine
   - Portas: 80 (HTTP), 443 (HTTPS)
   - Reverse proxy para evoai e evolution-api
   - Suporte a SSL/TLS

---

## 3. Estrutura do Projeto

### 3.1 Estrutura de Diretórios

```
evo-ai/
├── frontend/                    # Frontend Next.js
│   ├── app/                  # Páginas Next.js (App Router)
│   │   ├── page.tsx         # Página principal (redirect para /dashboard)
│   │   ├── dashboard/       # Página Dashboard
│   │   │   └── page.tsx
│   │   ├── pipelines/       # Página Pipelines
│   │   │   └── page.tsx
│   │   ├── channels/        # Página Channels
│   │   │   └── page.tsx
│   │   ├── contacts/        # Página Contacts
│   │   │   └── page.tsx
│   │   ├── campaigns/       # Página Campaigns
│   │   │   └── page.tsx
│   │   ├── settings/        # Página Settings
│   │   │   └── page.tsx
│   │   ├── tools/           # Página Tools
│   │   │   └── page.tsx
│   │   ├── audit/           # Página Audit (Admin)
│   │   │   └── page.tsx
│   │   ├── agents/          # Página Agents (existente)
│   │   ├── chat/            # Página Chat (existente)
│   │   ├── mcp-servers/     # Página MCP Servers (existente)
│   │   ├── clients/         # Página Clients (existente)
│   │   ├── documentation/   # Página Documentation (existente)
│   │   └── shared-chat/     # Página Shared Chat (existente)
│   │
│   ├── components/          # Componentes React
│   │   ├── sidebar.tsx     # Sidebar principal (ATUALIZADO)
│   │   ├── main-layout.tsx # Layout com sidebar (existente em outro projeto)
│   │   └── ui/             # Componentes shadcn/ui
│   │
│   ├── lib/               # Utilitários
│   │   └── utils.ts      # Funções utilitárias
│   │
│   ├── services/          # Serviços de API (axios)
│   │   ├── agentService.ts
│   │   ├── mcpServerService.ts
│   │   └── authServices.ts
│   │
│   ├── types/             # TypeScript types
│   │   ├── agent.ts
│   │   └── mcpServer.ts
│   │
│   ├── hooks/             # React hooks
│   │   ├── use-toast.ts
│   │   └── use-mobile.ts
│   │
│   ├── public/            # Arquivos estáticos
│   │   ├── images/         # Imagens de canais (WhatsApp, Instagram, etc.)
│   │   ├── favicon.svg
│   │   └── logo.svg
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.mjs
│   └── Dockerfile
│
├── src/                         # Backend Python/FastAPI
│   ├── api/                     # Rotas da API
│   │   ├── agent_routes.py      # Rotas de agentes (existente)
│   │   ├── mcp_server_routes.py # Rotas de MCP Servers (existente)
│   │   ├── auth_routes.py       # Rotas de autenticação (existente)
│   │   ├── session_routes.py    # Rotas de sessões (existente)
│   │   ├── tool_routes.py       # Rotas de ferramentas (existente)
│   │   ├── admin_routes.py      # Rotas de admin (existente)
│   │   ├── client_routes.py     # Rotas de clientes (existente)
│   │   ├── a2a_routes.py        # Rotas de A2A (existente)
│   │   ├── chat_routes.py       # Rotas de chat (existente)
│   │   ├── dashboard_routes.py # NOVO - Dashboard
│   │   ├── pipelines_routes.py # NOVO - Pipelines
│   │   ├── channels_routes.py  # NOVO - Channels
│   │   ├── contacts_routes.py  # NOVO - Contacts
│   │   ├── campaigns_routes.py # NOVO - Campaigns
│   │   ├── tools_routes.py      # NOVO - Tools
│   │   ├── audit_routes.py     # NOVO - Audit
│   │   └── settings_routes.py  # NOVO - Settings
│   │
│   ├── config/                  # Configurações
│   │   ├── database.py        # Conexão com banco de dados
│   │   ├── settings.py        # Variáveis de ambiente
│   │   └── redis.py           # Conexão com Redis
│   │
│   ├── core/                    # Lógica central
│   │   ├── jwt_middleware.py   # Middleware JWT
│   │   └── exceptions.py       # Exceções customizadas
│   │
│   ├── models/                  # Modelos SQLAlchemy (existente)
│   ├── schemas/                 # Schemas Pydantic (existente)
│   │
│   ├── services/                # Serviços de negócio
│   │   ├── agent_service.py
│   │   ├── mcp_server_service.py
│   │   ├── auth_service.py
│   │   ├── session_service.py
│   │   ├── audit_service.py    # (existente)
│   │   ├── tool_service.py
│   │   └── apikey_service.py
│   │
│   ├── main.py                 # Entry point FastAPI
│   ├── requirements.txt         # Dependências Python
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml           # Configuração Docker Compose (NOVO)
├── Dockerfile                 # Configuração Docker (NOVO)
└── .dockerignore              # Arquivos ignorados no build Docker (NOVO)
```

---

## 4. Como Dar Continuidade

### 4.1 Pré-requisitos

Para continuar o desenvolvimento, você precisa ter instalado:

**Frontend:**
- Node.js 18+
- npm, yarn ou pnpm
- Editor de código (VS Code, WebStorm, etc.)

**Backend:**
- Python 3.11+
- pip ou poetry
- PostgreSQL 15+ (para produção)
- Redis 7+ (para produção)

**Docker (Opcional):**
- Docker 20+
- Docker Compose 2.20+

---

### 4.2 Passo a Passo para Continuar

#### Passo 1: Clone e Configuração

```bash
# Clone o repositório (se não estiver clonado)
cd /home/z/my-project/evo-ai

# Frontend - Instalar dependências
cd frontend
npm install

# Backend - Criar ambiente virtual
cd ..
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências Python
pip install -r requirements.txt
```

#### Passo 2: Executar em Desenvolvimento

**Frontend:**
```bash
cd /home/z/my-project/evo-ai/frontend
npm run dev
# Acesse: http://localhost:3000
```

**Backend:**
```bash
cd /home/z/my-project/evo-ai
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# API disponível em: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

#### Passo 3: Continuar Desenvolvendo

**Escolha uma das funcionalidades abaixo para implementar:**

1. **Implementar Banco de Dados Real**
   - Criar modelos SQLAlchemy para as novas tabelas
   - Criar migrations com Alembic
   - Substituir dados simulados por queries reais

2. **Criar Formulários de Criação**
   - Criar formulários para adicionar pipelines, canais, contatos, campanhas, ferramentas
   - Implementar validação de formulários
   - Adicionar tratamento de erros

3. **Conectar com Evolution API**
   - Implementar integração real com WhatsApp via Evolution API
   - Configurar webhooks para eventos de mensagens
   - Testar envio e recebimento de mensagens

4. **Adicionar Gráficos Reais**
   - Integrar Recharts ou Chart.js para visualizações
   - Implementar gráficos de atividade e crescimento
   - Adicionar filtros por período

5. **Implementar CRUD Completo**
   - Adicionar endpoints PUT e DELETE para todas as novas APIs
   - Implementar paginação
   - Adicionar filtros avançados

---

## 5. Próximos Passos Sugeridos

### Fase 1: Banco de Dados e Persistência (1-2 semanas)

1. ✅ **Criar Models SQLAlchemy**
   - Criar `models/dashboard.py` - Modelos de dashboard
   - Criar `models/channel.py` - Modelos de canais
   - Criar `models/contact.py` - Modelos de contatos
   - Criar `models/campaign.py` - Modelos de campanhas
   - Criar `models/tool.py` - Modelos de ferramentas
   - Criar `models/pipeline.py` - Modelos de pipelines
   - Criar `models/audit_log.py` - Modelos de auditoria

2. ✅ **Criar Schemas Pydantic**
   - Criar schemas para validação de entrada e saída
   - Usar `BaseModel` do pydantic
   - Adicionar validadores customizados

3. ✅ **Criar Migrations com Alembic**
   - Inicializar Alembic: `alembic init migrations`
   - Criar migrations: `alembic revision --autogenerate -m "Initial migration"`
   - Aplicar migrations: `alembic upgrade head`

4. ✅ **Atualizar Services**
   - Implementar queries SQL reais nos services
   - Usar SQLAlchemy ORM para todas as operações
   - Implementar paginação nos serviços

### Fase 2: Formulários de Criação (1 semana)

5. ✅ **Criar Componentes de Formulários**
   - `PipelineForm.tsx` - Formulário para criar/editar pipelines
   - `ChannelForm.tsx` - Formulário para adicionar canais
   - `ContactForm.tsx` - Formulário para criar/editar contatos
   - `CampaignForm.tsx` - Formulário para criar campanhas
   - `ToolForm.tsx` - Formulário para criar ferramentas
   - Usar `react-hook-form` para gerenciamento de formulários
   - Usar `zod` para validação

6. ✅ **Criar Dialogs Modais**
   - `CreatePipelineDialog.tsx`
   - `AddChannelDialog.tsx`
   - `CreateContactDialog.tsx`
   - `CreateCampaignDialog.tsx`
   - `CreateToolDialog.tsx`

### Fase 3: Integração com Evolution API (1-2 semanas)

7. ✅ **Implementar Conexão com Canais**
   - Configurar Evolution API como serviço externo
   - Implementar endpoints para conectar canais
   - Armazenar credenciais de forma segura

8. ✅ **Implementar Webhooks**
   - Criar endpoint para receber webhooks do Evolution API
   - Processar eventos de mensagem, status, etc.
   - Atualizar banco de dados em tempo real

9. ✅ **Implementar Envio de Mensagens**
   - Criar endpoints para enviar mensagens via canais
   - Suportar diferentes tipos de mensagem (texto, mídia, localização)
   - Implementar fila de envio com Redis

### Fase 4: Gráficos e Analytics (1 semana)

10. ✅ **Integrar Recharts ou Chart.js**
    - Instalar: `npm install recharts`
    - Criar componentes de gráficos
    - Implementar gráfico de sessões de chat
    - Implementar gráfico de crescimento de contatos
    - Adicionar filtros por período

11. ✅ **Criar Página de Analytics**
    - Métricas avançadas
    - Relatórios personalizados
    - Exportação de relatórios (PDF, Excel)

### Fase 5: Testes e Deploy (1 semana)

12. ✅ **Implementar Testes**
    - Testes unitários para componentes React
    - Testes de integração para APIs FastAPI
    - Testes end-to-end com Playwright

13. ✅ **Configurar Deploy**
    - Configurar CI/CD com GitHub Actions
    - Deploy em produção (Vercel, AWS, GCP, etc.)
    - Configurar monitoramento (Sentry, Langfuse)

---

## 6. Tecnologias Utilizadas

### 6.1 Frontend

| Tecnologia | Versão | Uso |
|------------|---------|-----|
| Next.js | 15.2.4 | Framework React com App Router |
| React | 18+ | Biblioteca UI |
| TypeScript | 5+ | Tipagem estática |
| Tailwind CSS | 3.4.17 | Estilização |
| shadcn/ui | latest | Componentes UI (Radix UI) |
| Lucide React | latest | Ícones |
| Recharts | (sugerido) | Gráficos |
| React Hook Form | 7.54.1+ | Gerenciamento de formulários |
| Zod | 3.24.1+ | Validação de formulários |

### 6.2 Backend

| Tecnologia | Versão | Uso |
|------------|---------|-----|
| Python | 3.11+ | Linguagem principal |
| FastAPI | latest | Framework web |
| SQLAlchemy | latest | ORM para banco de dados |
| Pydantic | latest | Validação de dados |
| Alembic | latest | Migrations de banco |
| PostgreSQL | 15+ | Banco de dados principal |
| Redis | 7+ | Cache e filas |
| uvicorn | latest | Servidor ASGI |
| python-jose | latest | Autenticação JWT |

### 6.3 DevOps

| Tecnologia | Versão | Uso |
|------------|---------|-----|
| Docker | 20+ | Containerização |
| Docker Compose | 2.20+ | Orquestração |
| Nginx | latest | Reverse proxy |
| MinIO | latest | Storage S3 compatível |

### 6.4 Integrações

| Serviço | Uso |
|----------|-----|
| Evolution API | Integração WhatsApp/canais |
| Typebot | Workflows de chatbot |
| Dify AI | Agentes especializados |
| Chatwoot | Suporte ao cliente |
| Langfuse | Tracing e observabilidade |

---

## 7. APIs Disponíveis

### 7.1 Novas APIs Criadas

#### Dashboard API
```python
GET /api/v1/dashboard/stats          # Estatísticas principais
GET /api/v1/dashboard/activity       # Atividade recente
GET /api/v1/dashboard/charts/chat    # Dados do gráfico de chat
GET /api/v1/dashboard/charts/contacts # Dados do gráfico de contatos
```

#### Channels API
```python
GET /api/v1/channels/               # Listar canais
POST /api/v1/channels/              # Criar novo canal
PUT /api/v1/channels/{id}          # Atualizar canal (para implementar)
DELETE /api/v1/channels/{id}       # Deletar canal (para implementar)
```

#### Contacts API
```python
GET /api/v1/contacts/?search=termo   # Listar contatos com busca
POST /api/v1/contacts/              # Criar novo contato
PUT /api/v1/contacts/{id}          # Atualizar contato (para implementar)
DELETE /api/v1/contacts/{id}       # Deletar contato (para implementar)
GET /api/v1/contacts/{id}          # Obter contato específico (para implementar)
```

#### Campaigns API
```python
GET /api/v1/campaigns/               # Listar campanhas
POST /api/v1/campaigns/              # Criar nova campanha
PUT /api/v1/campaigns/{id}          # Atualizar campanha (para implementar)
DELETE /api/v1/campaigns/{id}       # Deletar campanha (para implementar)
POST /api/v1/campaigns/{id}/start   # Iniciar campanha (para implementar)
POST /api/v1/campaigns/{id}/pause   # Pausar campanha (para implementar)
```

#### Pipelines API
```python
GET /api/v1/pipelines/               # Listar pipelines
POST /api/v1/pipelines/              # Criar novo pipeline
PUT /api/v1/pipelines/{id}          # Atualizar pipeline (para implementar)
DELETE /api/v1/pipelines/{id}       # Deletar pipeline (para implementar)
POST /api/v1/pipelines/{id}/execute # Executar pipeline (para implementar)
```

#### Tools API
```python
GET /api/v1/tools/?search=termo      # Listar ferramentas com busca
POST /api/v1/tools/                  # Criar nova ferramenta
PUT /api/v1/tools/{id}              # Atualizar ferramenta (para implementar)
DELETE /api/v1/tools/{id}           # Deletar ferramenta (para implementar)
POST /api/v1/tools/{id}/test        # Testar ferramenta (para implementar)
```

#### Audit API
```python
GET /api/v1/audit/?search=termo&type=tipo   # Listar logs com filtros
POST /api/v1/audit/                          # Criar novo log
GET /api/v1/audit/export                    # Exportar logs (para implementar)
```

#### Settings API
```python
GET /api/v1/settings/               # Obter configurações
PUT /api/v1/settings/               # Atualizar configurações
```

### 7.2 APIs Existentes

Estas APIs já existiam no projeto original:

#### Agents API
```python
GET /api/v1/agents/                 # Listar agentes
POST /api/v1/agents/                # Criar novo agente
GET /api/v1/agents/{id}             # Obter agente
PUT /api/v1/agents/{id}             # Atualizar agente
DELETE /api/v1/agents/{id}          # Deletar agente
```

#### Chat API
```python
GET /api/v1/chat/                   # Listar sessões de chat
POST /api/v1/chat/                   # Criar nova sessão
POST /api/v1/chat/{session_id}/message # Enviar mensagem
```

#### Auth API
```python
POST /api/v1/auth/login              # Login
POST /api/v1/auth/register          # Registro
POST /api/v1/auth/logout            # Logout
POST /api/v1/auth/refresh           # Refresh token
```

---

## 8. Como Rodar o Projeto

### 8.1 Rodar Localmente (Desenvolvimento)

#### Opção A: Backend e Frontend Separados

**Backend (Python/FastAPI):**
```bash
cd /home/z/my-project/evo-ai

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor de desenvolvimento
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# API disponível em: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

**Frontend (Next.js):**
```bash
cd /home/z/my-project/evo-ai/frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Aplicação disponível em: http://localhost:3000
```

#### Opção B: Apenas Frontend (com backend simulado)

```bash
cd /home/z/my-project/evo-ai/frontend

# Instalar dependências
npm install

# Criar arquivo .env.local
NEXT_PUBLIC_API_URL=http://localhost:3000/api

# Iniciar servidor de desenvolvimento
npm run dev
```

### 8.2 Rodar com Docker

**Com Docker Compose (Recomendado):**
```bash
cd /home/z/my-project/evo-ai

# Construir e iniciar todos os serviços
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f evoai

# Parar serviços
docker-compose down

# Remover volumes (CUIDADO - apaga dados)
docker-compose down -v
```

**Serviços Iniciados:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Evolution API: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
- Nginx: http://localhost:80, https://localhost:443

---

## 9. Variáveis de Ambiente

### 9.1 Variáveis de Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://evoai:evoai_password@postgres:5432/evoai

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080  # 7 dias

# AI Configuration
AI_ENGINE=adk  # ou crewai
DEFAULT_MODEL=openai/gpt-4.1-nano

# Encryption
ENCRYPTION_KEY=your-encryption-key-change-this-in-production

# Email (SMTP)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@example.com

# Evolution API
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=your-evolution-api-key

# Integrations
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

TYPEBOT_URL=https://typebot.io
TYPEBOT_API_KEY=your-typebot-key

DIFY_URL=https://api.dify.ai
DIFY_API_KEY=your-dify-key

# Storage
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=evoai
S3_REGION=us-east-1

# Application
APP_NAME=Evo AI
APP_URL=http://localhost:3000
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Telemetry
ENABLE_TELEMETRY=true
```

### 9.2 Variáveis de Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Feature Flags
NEXT_PUBLIC_ENABLE_DARK_MODE=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Integrations
NEXT_PUBLIC_TYPEBOT_ENABLED=true
NEXT_PUBLIC_DIFY_ENABLED=true
NEXT_PUBLIC_EVOLUTION_ENABLED=true
```

---

## 10. Arquitetura do Sistema

### 10.1 Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx (80, 443)                    │
│                  ┌─────────────────────────┐               │
│                  │        Evo AI         │               │
│                  │  Frontend + Backend    │               │
│                  │  (Docker Container)    │               │
│                  └─────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Evo AI Backend (FastAPI)                │
│                  ┌─────────────────────────┐               │
│                  │      PostgreSQL       │               │
│                  │    (Database + ORM)     │               │
│                  └─────────────────────────┘               │
│                  ┌─────────────────────────┐               │
│                  │         Redis          │               │
│                  │   (Cache + Queues)      │               │
│                  └─────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Integrations
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Evolution API (WhatsApp)                    │
│                  ┌─────────────────────────┐               │
│                  │      Channels          │               │
│                  │  WhatsApp, Instagram,  │               │
│                  │  Email, SMS           │               │
│                  └─────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Fluxo de Dados

1. **Usuário** acessa o frontend via Nginx
2. **Frontend** faz chamadas REST ao backend
3. **Backend** processa e interage com:
   - PostgreSQL para persistência de dados
   - Redis para cache e filas
   - Evolution API para integração com canais
4. **Evolution API** envia/recebe mensagens via canais
5. **Backend** atualiza banco de dados e envia eventos via webhooks

### 10.3 Camadas de Arquitetura

**1. Camada de Apresentação (Frontend)**
- Next.js com App Router
- React Components (shadcn/ui)
- Tailwind CSS para estilização
- Axios para chamadas API

**2. Camada de Aplicação (Backend)**
- FastAPI como framework web
- Pydantic para validação
- SQLAlchemy ORM
- JWT para autenticação

**3. Camada de Serviços**
- Agent Service
- Chat Service
- Campaign Service
- Channel Service
- Contact Service
- Pipeline Service
- Tool Service
- Audit Service

**4. Camada de Acesso a Dados**
- PostgreSQL para dados relacionais
- Redis para cache e filas
- MinIO para armazenamento de arquivos

**5. Camada de Integrações**
- Evolution API (WhatsApp, Instagram, Email, SMS)
- Typebot (Workflows)
- Dify AI (Agentes)
- Langfuse (Tracing)

---

## 11. Integrações Existentes

### 11.1 Evolution API

**Documentação:** https://doc.evolution-api.com

**Canais Suportados:**
- **WhatsApp Baileys** - API baseada em WhatsApp Web (gratuita)
- **WhatsApp Cloud API** - API oficial da Meta (paga)
- **Instagram** - Em desenvolvimento
- **Messenger** - Em desenvolvimento
- **SMS** - Via Twilio (configurável)
- **Email** - Via SMTP (configurável)

**Endpoints Principais:**
- Conectar/Desconectar instância
- Enviar mensagem de texto
- Enviar mensagem de mídia
- Listar mensagens
- Obter status de mensagem
- Webhooks para eventos

### 11.2 Typebot

**Documentação:** https://typebot.io/docs

**Uso Sugerido:**
- Criar fluxos de conversação visuais
- Integrar como canal de atendimento
- Usar webhooks para eventos

### 11.3 Dify AI

**Documentação:** https://docs.dify.ai

**Uso Sugerido:**
- Criar agentes especializados
- Usar diferentes modelos LLM (GPT-4, Claude, etc.)
- Configurar prompts avançados
- Usar como backend para agents

### 11.4 Langfuse

**Documentação:** https://langfuse.com/docs

**Uso Sugerido:**
- Tracing de execuções de agentes
- Monitoramento de performance
- Debug de prompts
- Análise de custos de LLM

---

## 12. Bugs Conhecidos e Melhorias

### 12.1 Bugs Conhecidos

1. **Dados Simulados**
   - Todas as novas APIs retornam dados simulados em memória
   - Solução: Implementar integração real com banco de dados PostgreSQL

2. **Formulários de Criação Faltando**
   - As páginas têm botões de "Criar" mas os formulários não foram implementados
   - Solução: Criar componentes de formulário com react-hook-form e zod

3. **CRUD Incompleto**
   - Apenas endpoints GET e POST foram implementados
   - Solução: Implementar endpoints PUT e DELETE

4. **Gráficos Placeholders**
   - A seção de gráficos tem apenas placeholders visuais
   - Solução: Integrar Recharts ou Chart.js para visualizações reais

### 12.2 Melhorias Sugeridas

1. **Performance**
   - Implementar lazy loading para componentes
   - Otimizar imagens (lazy loading, WebP)
   - Usar React.memo para componentes pesados

2. **UX/UI**
   - Adicionar skeletons de loading
   - Melhorar responsividade mobile
   - Adicionar animações de transição
   - Implementar dark/light mode toggle

3. **Funcionalidades**
   - Implementar busca avançada com filtros
   - Adicionar ordenação (asc/desc)
   - Implementar exportação de dados (CSV, Excel, PDF)
   - Adicionar sistema de notificações em tempo real (WebSocket)
   - Implementar undo/redo em formulários

4. **Segurança**
   - Implementar rate limiting em APIs
   - Adicionar proteção CSRF
   - Implementar sanitização de entrada
   - Adicionar validação de permissões granulares
   - Criar sistema de backup de banco de dados

---

## 13. Conclusão

Este documento contém todas as informações necessárias para que outra IA possa dar continuidade ao projeto Evo AI Enhanced. Os principais pontos são:

1. **Estrutura Completa** - O projeto tem uma estrutura bem definida com frontend e backend separados
2. **9 Novas Páginas** - Dashboard, Pipelines, Channels, Contacts, Campaigns, Tools, Settings, Audit (admin)
3. **8 Novos Endpoints API** - Com dados simulados prontos para ser substituídos por banco de dados real
4. **Docker Completo** - Com multi-stage build e docker-compose com todos os serviços
5. **Documentação Detalhada** - Cada funcionalidade está documentada

### Próximos Passos Recomendados para Continuidade

1. **Implementar Banco de Dados Real** - Criar models, schemas e migrations
2. **Criar Formulários de Criação** - Para pipelines, canais, contatos, campanhas, ferramentas
3. **Conectar com Evolution API** - Implementar integração real com canais de comunicação
4. **Adicionar Gráficos Reais** - Integrar Recharts para visualizações
5. **Implementar CRUD Completo** - PUT e DELETE para todas as novas APIs
6. **Testes e Deploy** - Testes unitários, de integração e end-to-end

Boa sorte com a continuidade do projeto! 🚀

---

**Este documento foi criado por Z.ai Code**
**Data:** 2025-01-15
**Versão:** 1.0
**Baseado na implementação das funcionalidades do Evo AI Enhanced**

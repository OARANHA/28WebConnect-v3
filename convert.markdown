Evo AI - Agent Rules and Structure (Versão Completa)
Visão Geral do Projeto
"O Evo AI é uma plataforma completa de automação omnichannel que integra WhatsApp, Instagram, Email e SMS com agentes de IA baseados em FastAPI e Next.js. O projeto combina funcionalidades de CRM, automação de workflows, campanhas de mensagens em massa e integração com a Evolution API."
​

Tecnologias Principais
Backend
FastAPI: Framework web para construção da API com suporte assíncrono
​

SQLAlchemy: ORM para interação com banco de dados
​

Alembic: Sistema de migração de banco de dados
​

PostgreSQL: Banco de dados principal
​

Pydantic: Validação e serialização de dados
​

Uvicorn: Servidor ASGI para execução da aplicação
​

Redis: Gerenciamento de cache e sessões

JWT: Autenticação segura via tokens

Bcrypt: Hash seguro de senhas

SendGrid: Serviço de email para notificações

Jinja2: Motor de templates para renderização de emails

Frontend
Next.js 15: Framework com App Router
​
​

TypeScript: Linguagem tipada

Tailwind CSS: Framework de estilização

shadcn/ui: Biblioteca de componentes UI
​

Lucide React: Ícones

Radix UI: Componentes primitivos acessíveis

DevOps & Infraestrutura
Docker & Docker Compose: Containerização e orquestração

Nginx: Proxy reverso e balanceamento de carga

MinIO: Storage S3 compatível (versão RELEASE.2022-10-05T14-58-27Z - licença OK)

Evolution API: Integração com WhatsApp
​

Estrutura do Projeto
text
evo-ai/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin_routes.py          # Rotas administrativas
│   │   ├── agent_routes.py          # Gerenciamento de agentes
"│   │   ├── auth_routes.py           # Autenticação (login, registro)"
│   │   ├── chat_routes.py           # Interações de chat
│   │   ├── client_routes.py         # Gerenciamento de clientes
│   │   ├── mcp_server_routes.py     # Servidores MCP
│   │   ├── session_routes.py        # Sessões de chat
│   │   ├── tool_routes.py           # Ferramentas dos agentes
│   │   ├── dashboard_routes.py      # ✅ API de dashboard
│   │   ├── pipelines_routes.py      # ✅ Workflows de automação
│   │   ├── channels_routes.py       # ✅ Canais de comunicação
│   │   ├── contacts_routes.py       # ✅ CRM integrado
│   │   ├── campaigns_routes.py      # ✅ Campanhas de envio
│   │   ├── settings_routes.py       # ✅ Configurações globais
│   │   └── audit_routes.py          # ✅ Logs de auditoria
│   │
│   ├── config/
│   │   ├── database.py              # Configuração do banco
│   │   └── settings.py              # Configurações gerais
│   │
│   ├── core/
│   │   ├── middleware.py            # API Key middleware (legacy)
│   │   └── jwt_middleware.py        # Autenticação JWT
│   │
│   ├── models/
│   │   └── models.py                # Modelos SQLAlchemy
│   │
│   ├── schemas/
│   │   ├── schemas.py               # Schemas Pydantic principais
│   │   ├── chat.py                  # Schemas de chat
│   │   ├── user.py                  # Schemas de usuário
│   │   └── audit.py                 # Schemas de auditoria
│   │
│   ├── services/
│   │   ├── agent_service.py         # Lógica de negócio dos agentes
│   │   ├── agent_runner.py          # Execução de agentes
│   │   ├── auth_service.py          # Lógica de autenticação JWT
│   │   ├── audit_service.py         # Logs de auditoria
│   │   ├── client_service.py        # Lógica de clientes
│   │   ├── email_service.py         # Envio de emails
│   │   ├── mcp_server_service.py    # Servidores MCP
│   │   ├── session_service.py       # Sessões de chat
│   │   ├── tool_service.py          # Ferramentas
│   │   └── user_service.py          # Gerenciamento de usuários
│   │
│   ├── templates/
│   │   └── emails/
│   │       ├── base_email.html      # Template base
│   │       ├── verification_email.html
│   │       ├── password_reset.html
│   │       ├── welcome_email.html
│   │       └── account_locked.html
│   │
│   ├── tests/
│   │   ├── api/
│   │   ├── models/
│   │   └── services/
│   │
│   └── utils/
│       ├── logger.py                # Configuração de logging
"│       └── security.py              # Utilitários de segurança (JWT, hash)"
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Redirect para /dashboard
│   │   ├── dashboard/page.tsx       # ✅ Dashboard com métricas
│   │   ├── agents/page.tsx          # Gerenciamento de agentes
│   │   ├── pipelines/page.tsx       # ✅ Workflows visuais
│   │   ├── chat/page.tsx            # Interface de chat
│   │   ├── channels/page.tsx        # ✅ Canais de comunicação
│   │   ├── contacts/page.tsx        # ✅ CRM integrado
│   │   ├── campaigns/page.tsx       # ✅ Campanhas em massa
│   │   ├── tools/page.tsx           # ✅ Ferramentas customizadas
│   │   ├── shared-chat/page.tsx     # Showcase de agentes
│   │   ├── documentation/page.tsx   # Documentação
│   │   ├── mcp-servers/page.tsx     # Admin: Servidores MCP
│   │   ├── clients/page.tsx         # Admin: Clientes
│   │   ├── settings/page.tsx        # ✅ Admin: Configurações
│   │   └── audit/page.tsx           # ✅ Admin: Auditoria
│   │
│   └── components/
│       └── sidebar.tsx              # ✅ Sidebar atualizado
│
├── Dockerfile                       # ✅ Multi-stage build
├── docker-compose.yml               # ✅ Orquestração completa
├── .dockerignore                    # ✅ Arquivos ignorados
├── pyproject.toml                   # Gerenciamento de dependências
├── alembic.ini                      # Configuração do Alembic
└── .env.example                     # Variáveis de ambiente exemplo
Padrões de Código
Requisitos de Linguagem
"TODOS os comentários, docstrings e mensagens de log DEVEM ser escritos em inglês"

"Nomes de variáveis, funções e classes em inglês"

Mensagens de erro da API em inglês

Documentação (incluindo comentários inline) em inglês

Commits em inglês (Conventional Commits)

Configuração do Projeto
Dependências gerenciadas em pyproject.toml usando padrões modernos de empacotamento Python

Dependências de desenvolvimento como dependências opcionais em pyproject.toml

Única fonte de verdade para metadados do projeto em pyproject.toml

Sistema de build configurado para usar setuptools

Configuração do Pytest em pyproject.toml sob [tool.pytest.ini_options]

Formatação de código com Black configurado em pyproject.toml

Linting com Flake8 configurado em .flake8

Schemas (Pydantic)
Usar BaseModel como base para todos os schemas

Definir campos com tipos explícitos

Usar Optional para campos opcionais

Usar Field para validações e valores padrão

Implementar Config com from_attributes = True para modelos

Usar EmailStr para validação de email

Services
Tratamento de erros com SQLAlchemyError

Logging consistente com mensagens em inglês

Tipagem forte com Optional para retornos nulos

Documentação com docstrings

Rollback em caso de erro

Retornos padronizados

Usar transações para operações múltiplas

Templates de Email
Todos os templates estendem um template base

Templates escritos em inglês

Sistema de templates Jinja2

Estilização consistente usando template base comum

Design responsivo para compatibilidade mobile

Botões de call-to-action claros

Mecanismos de fallback para renderização falhada

Routes (FastAPI)
"Códigos de status apropriados (201 para criação, 204 para deleção)"

Tratamento de erros com HTTPException

Mensagens de erro em inglês

Paginação para endpoints de listagem

Validação de entrada com schemas

Autenticação JWT para rotas protegidas

Uso de funções assíncronas com async def
​

Migrations (Alembic)
Usar Alembic para gerenciamento de migrações
​

Nomes descritivos para migrações

Manter histórico de alterações

Usar CASCADE quando necessário para remover dependências

Autenticação e Segurança
Usar JWT para autenticação com OAuth2PasswordBearer

Tokens JWT com tempo de expiração definido em settings

"Access token contendo dados essenciais do usuário (is_admin, client_id, etc.)"

Verificação de propriedade de recursos baseada em client_id

Proteção de rotas administrativas com verificação de permissões

Sistema de verificação de email via tokens

Recuperação segura de senha com tokens de uso único

Bloqueio de conta após múltiplas tentativas de login falhadas

Auditoria
Registrar ações administrativas importantes

"Coleta automática de dados contextuais (IP, user-agent)"

Relacionamento com usuário que realizou a ação

Filtragem e consulta por diferentes critérios

Novas Funcionalidades Implementadas
📊 Dashboard
Rota Frontend: /dashboard

API Endpoints:

GET /api/v1/dashboard/stats - Estatísticas principais

GET /api/v1/dashboard/activity - Atividade recente

GET /api/v1/dashboard/charts/chat - Dados do gráfico de chat

GET /api/v1/dashboard/charts/contacts - Dados do gráfico de contatos

Recursos:

"Cards de métricas principais (Total Agents, Sessões de Chat, Contatos Ativos, Pipelines Ativos)"

Seção de gráficos (Chart.js/Recharts)

Atividade recente

Ações rápidas

🔀 Pipelines
Rota Frontend: /pipelines

API Endpoints:

GET /api/v1/pipelines/ - Listar pipelines

POST /api/v1/pipelines/ - Criar novo pipeline

Recursos:

Gerenciamento de workflows de automação visual

Status de pipelines (Ativo/Pausado)

Estatísticas de execuções

Botões para editar e executar pipelines

📱 Canais (Channels)
Rota Frontend: /channels

API Endpoints:

GET /api/v1/channels/ - Listar canais

POST /api/v1/channels/ - Criar novo canal

Recursos:

"Suporte para múltiplos canais: WhatsApp, Instagram, Email, SMS"
​

Status de conexão em tempo real

Estatísticas de mensagens por canal

Botões para conectar/desconectar canais

👥 Contatos (Contacts)
Rota Frontend: /contacts

API Endpoints:

GET /api/v1/contacts/?search=termo - Listar contatos com busca

POST /api/v1/contacts/ - Criar novo contato

Recursos:

CRM integrado completo

Sistema de tags para segmentação

"Busca avançada (nome, email, telefone)"

Histórico de mensagens por contato

🎯 Campanhas (Campaigns)
Rota Frontend: /campaigns

API Endpoints:

GET /api/v1/campaigns/ - Listar campanhas

POST /api/v1/campaigns/ - Criar nova campanha

Recursos:

Envio em massa de mensagens

"Estatísticas detalhadas (Enviados, Entregues, Abertos)"

"Suporte para diferentes canais (WhatsApp, Email)"

Sistema de agendamento

Controle de status (Em andamento/Agendada/Concluída/Pausada)

⚙️ Configurações (Settings)
Rota Frontend: /settings

API Endpoints:

GET /api/v1/settings/ - Obter configurações

PUT /api/v1/settings/ - Atualizar configurações

Recursos:

"Configurações gerais (Modo Escuro, Notificações, Sons)"

"Webhooks e integrações (Typebot, Dify AI, Evolution Bot)"

"Armazenamento (S3, MinIO)"

"Notificações (Email, Push, Resumo Diário)"

"Segurança (API Keys, Domínios Permitidos)"

🔧 Ferramentas (Tools)
Rota Frontend: /tools

API Endpoints:

GET /api/v1/tools/?search=termo - Listar ferramentas com busca

POST /api/v1/tools/ - Criar nova ferramenta

Recursos:

Ferramentas customizadas para agentes

Suporte para integrações externas

"Estatísticas de uso (último uso, execuções)"

Status de ferramenta (Ativa/Inativa)

Botão para testar ferramentas

📜 Auditoria (Audit)
Rota Frontend: /audit (Admin Only)

API Endpoints:

GET /api/v1/audit/?search=termo&type=tipo - Listar logs com filtros

POST /api/v1/audit/ - Criar novo log de auditoria

Recursos:

Logs completos de auditoria

Sistema de busca e filtros

"Classificação por tipo de ação (create, update, delete, execute, security)"

Ícones coloridos por tipo

Sistema de paginação

Exportação de logs

Estrutura da Navegação (Sidebar)
Menus Principais (Todos os Usuários)
📊 Dashboard - Visão geral com métricas

🤖 Agents - Gerenciamento de agentes AI

🔀 Pipelines - Workflows de automação visual

💬 Chat - Interface de chat com agentes

📱 Canais - Integração com múltiplos canais

👥 Contatos - CRM integrado

🎯 Campanhas - Envio em massa

🔧 Ferramentas - Ferramentas customizadas

🌐 Chat Compartilhado - Showcase de agentes

📚 Documentation - Documentação técnica

Menus de Admin
🖥️ MCP Servers - Gerenciamento de servidores MCP

💼 Clients - Gerenciamento de clientes

⚙️ Configurações - Configurações globais

📜 Auditoria - Logs de auditoria

Variáveis de Ambiente
Backend (.env)
bash
# Database
DATABASE_URL=postgresql://postgres:25hub2025@postgres:5432/evo_ai

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key

# AI
AI_ENGINE=adk

# Email
EMAIL_PROVIDER=smtp
SENDGRID_API_KEY=your-sendgrid-key

# Storage
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ENDPOINT=http://minio:9000

# Evolution API
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=your-evolution-api-key
Frontend (.env.local)
bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
Docker Compose - Serviços
Serviço	Porta	Descrição
"evoai (app)	3000, 8000	Frontend (Next.js) e Backend (FastAPI)"
postgres	5432	Banco de dados PostgreSQL 15
redis	6379	Cache Redis 7
"minio	9000, 9001	Storage S3 compatível (API: 9000, Console: 9001)"
evolution-api	8080	Integração com WhatsApp 
​
"nginx	80, 443	Reverse Proxy e Load Balancer"
Nota Importante sobre MinIO
"Por questões de licenciamento, usar a versão:"

text
minio:
  image: minio/minio:RELEASE.2022-10-05T14-58-27Z  # ✅ LICENÇA OK
Convenções
Nomes de variáveis e funções em inglês

Mensagens de log e erro em inglês

Documentação em inglês

"Conteúdo voltado ao usuário (emails, respostas) em inglês"

Indentação com 4 espaços

Máximo de 79 caracteres por linha

Regras de Commit
Usar formato Conventional Commits para todas as mensagens de commit:

Formato: <type>(<scope>): <description>

Tipos:

feat: Nova funcionalidade

fix: Correção de bug

docs: Mudanças na documentação

style: Mudanças de formatação (não afetam lógica)

refactor: Refatoração de código

perf: Melhorias de performance

test: Adição ou modificação de testes

chore: Mudanças no processo de build ou ferramentas auxiliares

Exemplos:

bash
feat(auth): add password reset functionality
fix(api): correct validation error in client registration
docs: update API documentation for new endpoints
refactor(services): improve error handling in authentication
Comandos Úteis
Makefile
bash
make run                          # Iniciar servidor de desenvolvimento
make run-prod                     # Iniciar servidor em produção
"make alembic-revision message=""description""  # Criar nova migração"
make alembic-upgrade              # Aplicar migrações pendentes
make alembic-downgrade            # Reverter última migração
make alembic-migrate              # Criar e aplicar nova migração
make alembic-reset                # Resetar banco ao estado inicial
make alembic-upgrade-cascade      # Forçar upgrade removendo dependências
make clear-cache                  # Limpar cache do projeto
make seed-all                     # Executar todos os seeders
make lint                         # Executar verificações de linting
make format                       # Formatar código com black
make install                      # Instalar projeto para desenvolvimento
make install-dev                  # Instalar com dependências de dev
Docker
bash
# Construir e iniciar todos os serviços
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f evoai

# Parar serviços
docker-compose down

# Remover volumes (CUIDADO!)
docker-compose down -v
Melhores Práticas
Sempre validar dados de entrada com Pydantic
​

Implementar logging apropriado

Tratar todos os erros possíveis

Manter consistência nos retornos

Documentar funções e classes

Seguir princípios SOLID

Manter testes atualizados

Proteger rotas com autenticação JWT

Usar variáveis de ambiente para configurações sensíveis

Implementar verificação de propriedade de recursos

Armazenar senhas apenas com hash seguro (bcrypt)

Implementar expiração apropriada para tokens

Usar herança de templates para layouts de email consistentes

Seguir padrões async/await para operações I/O
​

Segurança
Tokens JWT com tempo de vida limitado

Verificação de email com tokens de uso único

Hash seguro de senhas com bcrypt e salt aleatório

Sistema de auditoria para ações administrativas

Controle de acesso baseado em recursos

Separação clara entre usuários regulares e administradores

Validação estrita de entrada com Pydantic

Bloqueio de conta após múltiplas tentativas de login falhadas

HTTPS habilitado via Nginx (em produção)

API Keys para integrações externas

Domínios permitidos para CORS

Testes
Estrutura de Testes
text
tests/
├── api/
│   ├── test_auth_routes.py
│   ├── test_dashboard_routes.py
│   └── test_root.py
├── models/
│   └── test_models.py
└── services/
    ├── test_auth_service.py
    └── test_user_service.py
Comandos de Teste
bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src --cov-report=html

# Executar testes específicos
pytest tests/api/test_auth_routes.py
Próximos Passos
Implementar Banco de Dados Real:

Substituir dados simulados por queries reais ao PostgreSQL
​

Criar modelos SQLAlchemy para novas tabelas

Criar Migrations:

Usar Alembic para migrações do banco
​

Executar alembic upgrade head

Integrar com Evolution API:

Implementar chamadas reais à Evolution API
​

Configurar webhooks para eventos de WhatsApp

Adicionar Formulários de Criação:

Criar formulários com validação

Implementar componentes shadcn/ui
​

Adicionar Testes:

Testes unitários para componentes React

Testes de integração para APIs FastAPI

Testes end-to-end com Playwright

Deploy em Produção:

Configurar domínio personalizado

Configurar SSL/TLS no Nginx

"Configurar monitoramento (Sentry, Langfuse)"

Referências
Repositórios Base:

EvolutionAPI/evo-ai

EvolutionAPI/evolution-api

Documentação:

FastAPI Documentation

SQLAlchemy Documentation

Next.js Documentation

shadcn/ui Documentation

Autoria
Desenvolvido por: A.Aranha Code
Data: 2025-01-15
Baseado em: EvolutionAPI/evo-ai e EvolutionAPI/evolution-api
Licença: Conforme repositórios originais

"Este documento serve como guia completo para desenvolvimento, manutenção e extensão do projeto Evo AI, consolidando todas as regras, padrões e estruturas implementadas."

# 🎉 Evo AI - Versão Aprimorada com Novas Funcionalidades

Esta versão do Evo AI é para  inclui novas funcionalidades que estou buscando transfor em uma plataforma em uma **solução completa de automação omnichannel**.

---

## ✨ Novas Funcionalidades

### 📊 Dashboard
- **Rota:** `/dashboard`
- **API:** `/api/v1/dashboard/*`
- **Recursos:**
  - Cards de métricas principais (Total Agents, Sessões de Chat, Contatos Ativos, Pipelines Ativos)
  - Seção de gráficos (placeholders para Chart.js/Recharts)
  - Atividade recente
  - Ações rápidas

### 🔀 Pipelines
- **Rota:** `/pipelines`
- **API:** `/api/v1/pipelines/*`
- **Recursos:**
  - Gerenciamento de workflows de automação visual
  - Status de pipelines (Ativo/Pausado)
  - Estatísticas de execuções
  - Botões para editar e executar pipelines

### 📱 Canais (Channels)
- **Rota:** `/channels`
- **API:** `/api/v1/channels/*`
- **Recursos:**
  - Suporte para múltiplos canais: WhatsApp, Instagram, Email, SMS
  - Status de conexão em tempo real
  - Estatísticas de mensagens por canal
  - Botões para conectar/desconectar canais

### 👥 Contatos (Contacts)
- **Rota:** `/contacts`
- **API:** `/api/v1/contacts/*`
- **Recursos:**
  - CRM integrado completo
  - Sistema de tags para segmentação
  - Busca avançada (nome, email, telefone)
  - Histórico de mensagens por contato

### 🎯 Campanhas (Campaigns)
- **Rota:** `/campaigns`
- **API:** `/api/v1/campaigns/*`
- **Recursos:**
  - Envio em massa de mensagens
  - Estatísticas detalhadas (Enviados, Entregues, Abertos)
  - Suporte para diferentes canais (WhatsApp, Email)
  - Sistema de agendamento
  - Controle de status (Em andamento/Agendada/Concluída/Pausada)

### ⚙️ Configurações (Settings)
- **Rota:** `/settings`
- **API:** `/api/v1/settings/*`
- **Recursos:**
  - Configurações gerais (Modo Escuro, Notificações, Sons)
  - Webhooks e integrações (Typebot, Dify AI, Evolution Bot)
  - Armazenamento (S3, Minio)
  - Notificações (Email, Push, Resumo Diário)
  - Segurança (API Keys, Domínios Permitidos)

### 🔧 Ferramentas (Tools)
- **Rota:** `/tools`
- **API:** `/api/v1/tools/*`
- **Recursos:**
  - Ferramentas customizadas para agentes
  - Suporte para integrações externas
  - Estatísticas de uso (último uso, execuções)
  - Status de ferramenta (Ativa/Inativa)
  - Botão para testar ferramentas

### 📜 Auditoria (Audit)
- **Rota:** `/audit` (Admin Only)
- **API:** `/api/v1/audit/*`
- **Recursos:**
  - Logs completos de auditoria
  - Sistema de busca e filtros
  - Classificação por tipo de ação (create, update, delete, execute, security)
  - Ícones coloridos por tipo
  - Sistema de paginação
  - Exportação de logs

---

## 📁 Arquivos Modificados/Criados

### Frontend (`/frontend`)
```
components/
├── sidebar.tsx                    # ✅ Atualizado com novos menus

app/
├── page.tsx                        # ✅ Atualizado (redirect para /dashboard)
├── dashboard/page.tsx             # ✅ Novo
├── pipelines/page.tsx             # ✅ Novo
├── channels/page.tsx              # ✅ Novo
├── contacts/page.tsx              # ✅ Novo
├── campaigns/page.tsx             # ✅ Novo
├── settings/page.tsx              # ✅ Novo
├── tools/page.tsx                 # ✅ Novo
└── audit/page.tsx                 # ✅ Novo
```

### Backend (`/src/api`)
```
api/
├── dashboard_routes.py             # ✅ Novo
├── pipelines_routes.py             # ✅ Novo
├── channels_routes.py              # ✅ Novo
├── contacts_routes.py              # ✅ Novo
├── campaigns_routes.py             # ✅ Novo
├── tools_routes.py                 # ✅ Novo
├── audit_routes.py                # ✅ Novo
└── settings_routes.py             # ✅ Novo
```

### Docker
```
Dockerfile                          # ✅ Novo (multi-stage build)
docker-compose.yml                   # ✅ Novo (orquestração completa)
.dockerignore                        # ✅ Novo
```

---

## 🚀 Como Executar

### Sem Docker

#### Frontend
```bash
cd frontend
npm install
npm run dev

```

#### Backend
```bash
cd ..
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install -r requirements.txt
pip install -r backend/requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# API disponível em http://localhost:8000
```

### Com Docker

```bash
cd evo-ai

# Construir e iniciar todos os serviços
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f evoai

# Parar serviços
docker-compose down

# Remover volumes
docker-compose down -v
```

Os seguintes serviços serão iniciados:
- **Frontend (Next.js):** 
- **Backend (FastAPI):** http://localhost:8000
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379
- **MinIO Console:** http://localhost:9001
- **MinIO API:** http://localhost:9000
- **Evolution API:** http://localhost:8080
- **Nginx:** http://localhost:80, https://localhost:443

---

## 🔗 Novos Endpoints da API

### Dashboard
- `GET /api/v1/dashboard/stats` - Estatísticas
- `GET /api/v1/dashboard/activity` - Atividade recente
- `GET /api/v1/dashboard/charts/chat` - Dados do gráfico de chat
- `GET /api/v1/dashboard/charts/contacts` - Dados do gráfico de contatos

### Pipelines
- `GET /api/v1/pipelines/` - Listar pipelines
- `POST /api/v1/pipelines/` - Criar novo pipeline

### Channels
- `GET /api/v1/channels/` - Listar canais
- `POST /api/v1/channels/` - Criar novo canal

### Contacts
- `GET /api/v1/contacts/?search=termo` - Listar contatos com busca
- `POST /api/v1/contacts/` - Criar novo contato

### Campaigns
- `GET /api/v1/campaigns/` - Listar campanhas
- `POST /api/v1/campaigns/` - Criar nova campanha

### Tools
- `GET /api/v1/tools/?search=termo` - Listar ferramentas
- `POST /api/v1/tools/` - Criar nova ferramenta

### Audit
- `GET /api/v1/audit/?search=termo&type=tipo` - Listar logs com filtros
- `POST /api/v1/audit/` - Criar novo log

### Settings
- `GET /api/v1/settings/` - Obter configurações
- `PUT /api/v1/settings/` - Atualizar configurações

---

## 📊 Estrutura do Sidebar Atualizada

### Menus Principais (Todos os Usuários)
1. 📊 **Dashboard** - Visão geral com métricas
2. 🤖 **Agents** - Gerenciamento de agentes AI
3. 🔀 **Pipelines** - Workflows de automação visual
4. 💬 **Chat** - Interface de chat com agentes
5. 📱 **Canais** - Integração com múltiplos canais
6. 👥 **Contatos** - CRM integrado
7. 🎯 **Campanhas** - Envio em massa
8. 🔧 **Ferramentas** - Ferramentas customizadas
9. 🌐 **Chat Compartilhado** - Showcase de agentes
10. 📚 **Documentation** - Documentação técnica

### Menus de Admin
1. 🖥️ **MCP Servers** - Gerenciamento de servidores MCP
2. 💼 **Clients** - Gerenciamento de clientes
3. ⚙️ **Configurações** - Configurações globais
4. 📜 **Auditoria** - Logs de auditoria

---

## 🎨 Tecnologias Utilizadas

### Frontend
- **Framework:** Next.js 15 com App Router
- **Linguagem:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Ícones:** Lucide React

### Backend
- **Framework:** FastAPI (Python)
- **Linguagem:** Python 3.11+
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL 15
- **Cache:** Redis 7

### DevOps
- **Containerização:** Docker & Docker Compose
- **Proxy:** Nginx
- **Object Storage:** MinIO (S3 compatível)
- **WhatsApp Integration:** Evolution API

---

## 🔐 Segurança

- Autenticação JWT com middleware
- Proteção de rotas com verificações de permissão
- Logs de auditoria para todas as ações
- Validação de dados com Pydantic
- HTTPS habilitado via Nginx

---

## 📝 Variáveis de Ambiente

### Backend
```bash
DATABASE_URL=postgresql://postgres:25hub2025@postgres:5432/evo_ai
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET_KEY=your-jwt-secret-key
AI_ENGINE=adk
EMAIL_PROVIDER=smtp
ENCRYPTION_KEY=your-encryption-key
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:3000/api/v1
```

---

## 📄 Licença

Este projeto é licenciado sob a **Apache License 2.0**.

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

Para suporte, visite:
- Discord: https://evolution-api.com/discord
- WhatsApp: https://evolution-api.com/whatsapp
- Documentação: https://doc.evolution-api.com

---

**© 2025 Evolution API. Todos os direitos reservados.**

Desenvolvido com ❤️ pela equipe Evolution API.

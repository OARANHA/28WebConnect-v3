# Análise de Possibilidades de Novos Menus - Evo AI Sidebar

## 📋 Resumo Executivo

Este documento analisa as possibilidades de integração e adição de novos menus ao sidebar do **Evo AI** (frontend) considerando as funcionalidades do **Evo AI** (plataforma de agentes AI) e do **Evolution API** (plataforma de integração com múltiplos canais de comunicação).

---

## 🎯 Estrutura Atual do Sidebar

### Menus Atuais (Não-Admin)
- **Agents** (/agents) - Gerenciamento de agentes AI
- **Chat** (/chat) - Interface de chat com agentes
- **Documentation** (/documentation) - Documentação técnica

### Menus Atuais (Admin)
- **MCP Servers** (/mcp-servers) - Gerenciamento de servidores MCP
- **Clients** (/clients) - Gerenciamento de clientes
- **Documentation** (/documentation) - Documentação técnica

### Menu de Usuário (Ambos)
- **Profile** (/profile) - Perfil do usuário
- **Security** (/security) - Configurações de segurança
- **Logout** - Sair da aplicação

---

## 🚀 Novos Menus Sugeridos

### 1. 📊 Pipelines (Altamente Recomendado)

**Descrição:** Gerenciamento de pipelines de automação e fluxos de trabalho baseados em workflows.

**Justificativa:**
- O Evo AI já possui suporte a **Workflow Agents** com LangGraph
- Existe uma estrutura completa de workflows no frontend (`app/agents/workflows/`)
- Os workflows podem ser complexos e merecem uma seção dedicada
- Integração natural com agents AI existentes

**Funcionalidades Sugeridas:**
- Listar todos os pipelines/workflows
- Criar novos pipelines visuais
- Editar pipelines existentes
- Monitorar execução de pipelines
- Histórico de execuções
- Métricas de performance

**Ícone Sugerido:** `GitMerge` ou `Workflow`
**Rota:** `/pipelines`
**Backend Existente:** Workflow Agent já implementado

**Integração com Evolution API:**
- Pipelines podem incluir envio de mensagens via WhatsApp
- Automação de respostas baseadas em triggers
- Integração com Typebot, Dify, OpenAI

---

### 2. 📱 Canais (Channels) (Altamente Recomendado)

**Descrição:** Gerenciamento de canais de comunicação integrados (WhatsApp, Instagram, Messenger, Email, etc.)

**Justificativa:**
- Evolution API suporta múltiplos canais: WhatsApp Baileys, WhatsApp Cloud API, Instagram, Messenger (planejados)
- Integração nativa com Evo AI através de Evolution Bot
- Arquitetura de canais já existe no backend do Evolution API

**Funcionalidades Sugeridas:**
- Listar canais configurados
- Conectar novos canais (QR Code para WhatsApp, autenticação para Meta)
- Status de conexão (online/offline)
- Configurações por canal
- Webhooks de eventos
- Estatísticas de uso por canal

**Ícone Sugerido:** `MessageCircle` ou `Radio`
**Rota:** `/channels`
**Backend Existente:**
- `/src/api/integrations/channel/` no Evolution API
- Suporte para WhatsApp Baileys, WhatsApp Cloud API, Meta

**Estrutura de Canais Suportados:**
```
├── WhatsApp (Baileys)
├── WhatsApp Cloud API
├── Instagram (futuro)
├── Messenger (futuro)
├── SMS
├── Email
└── WebChat
```

---

### 3. 👥 Contatos (Contacts) (Recomendado)

**Descrição:** Gestão centralizada de contatos e leads de todos os canais integrados.

**Justificativa:**
- Evolution API já gerencia contatos de WhatsApp
- Necessidade de CRM integrado para gestão de relacionamentos
- Agentes AI precisam de contexto sobre contatos
- Unificação de contatos de múltiplos canais

**Funcionalidades Sugeridas:**
- Lista de contatos unificada
- Detalhes do contato (nome, telefone, email, foto)
- Histórico de conversas por contato
- Tags e segmentação de contatos
- Importação/exportação de contatos
- Integração com Agents AI (contexto personalizado)
- Informações personalizadas (custom fields)

**Ícone Sugerido:** `Users` ou `UserCircle2`
**Rota:** `/contacts`
**Backend Existente:**
- Tabela `contacts` no Evolution API
- Rotas de chat com informações de contato

---

### 4. 🎯 Campanhas (Campaigns) (Recomendado)

**Descrição:** Gerenciamento de campanhas de envio em massa via canais de comunicação.

**Justificativa:**
- Necessidade de envios em massa (broadcast) para WhatsApp
- Automação de marketing via canais digitais
- Integração com templates de mensagens
- Agentes AI podem personalizar mensagens de campanha

**Funcionalidades Sugeridas:**
- Criar campanhas de envio em massa
- Seleção de destinatários (lista de contatos/tags)
- Personalização de mensagens com variáveis
- Agendamento de envios
- Templates de mensagens (integrado com Evolution API)
- Monitoramento de delivery e status
- Análise de métricas (taxa de abertura, resposta)
- A/B testing de mensagens

**Ícone Sugerido:** `Megaphone` ou `Send`
**Rota:** `/campaigns`
**Backend Existente:**
- Tabela `templates` no Evolution API
- Suporte a templates de mensagens
- Webhooks para tracking

---

### 5. ⚙️ Configurações (Settings) (Altamente Recomendado)

**Descrição:** Configurações globais do sistema e integrações.

**Justificativa:**
- O menu "Security" é apenas para autenticação do usuário
- Necessidade de configurações de sistema em geral
- Integrações externas precisam de configuração centralizada

**Funcionalidades Sugeridas:**
- Configurações gerais da aplicação
- Configurações de integrações (Typebot, Dify, Chatwoot, etc.)
- Gerenciamento de Webhooks
- Configurações de notificações
- Configurações de API Keys (já existe no backend)
- Configurações de Langfuse (tracing/observability)
- Configurações de storage (S3/Minio)
- Preferências de tema e interface

**Ícone Sugerido:** `Settings` ou `Settings2`
**Rota:** `/settings`
**Backend Existente:**
- Tabela `settings` no Evolution API
- Múltiplas integrações configuráveis

---

### 6. 🔧 Ferramentas Customizadas (Custom Tools) (Recomendado)

**Descrição:** Gerenciamento de ferramentas customizadas que podem ser usadas pelos agentes.

**Justificativa:**
- O backend já possui `custom_tools.py` e `tool_service.py`
- MCP Servers já estão gerenciados, mas ferramentas customizadas merecem destaque
- Permite criar integrações específicas sem depender de MCP

**Funcionalidades Sugeridas:**
- Lista de ferramentas customizadas
- Criar nova ferramenta (definição de função)
- Editar ferramentas existentes
- Testar ferramentas
- Documentação automática
- Tags e categorização

**Ícone Sugerido:** `Wrench` ou `Tool`
**Rota:** `/tools`
**Backend Existente:**
- `/src/services/adk/custom_tools.py`
- `/src/api/tool_routes.py`

---

### 7. 📈 Dashboard / Analytics (Opcional)

**Descrição:** Painel de métricas e análises do uso da plataforma.

**Justificativa:**
- Insights sobre uso de agentes
- Métricas de performance
- Análise de sessões e conversas
- Monitoramento de canais e campanhas

**Funcionalidades Sugeridas:**
- Número de agentes ativos
- Sessões de chat por dia/semana/mês
- Performance dos agentes (tempo de resposta, tokens)
- Status dos canais
- Campanhas mais eficazes
- Uso de recursos (tokens, API calls)
- Gráficos e relatórios

**Ícone Sugerido:** `BarChart3` ou `LineChart`
**Rota:** `/dashboard` ou `/analytics`
**Backend Existente:**
- Serviço de monitor no Evolution API
- Langfuse integration para tracing

---

### 8. 💬 Chat Compartilhado (Shared Chat) (Já Existe, mas pode ser destacado)

**Descrição:** Área para compartilhar agentes de chat públicamente.

**Justificativa:**
- A rota `/shared-chat` já existe
- Pode ser adicionada ao sidebar principal para maior visibilidade
- Permite showcase de agentes

**Ícone Sugerido:** `Share2` ou `Globe`
**Rota:** `/shared-chat`
**Backend Existente:** Rota `/shared` em `agent_routes.py`

---

### 9. 🗂️ Auditoria / Logs (Admin Only) (Opcional)

**Descrição:** Logs de auditoria e atividades do sistema.

**Justificativa:**
- Backend já possui `audit_service.py` e rotas de admin
- Importante para segurança e compliance
- Rastrear ações de usuários

**Funcionalidades Sugeridas:**
- Lista de ações de usuários
- Filtros por usuário, ação, período
- Detalhes de cada ação
- Exportação de logs

**Ícone Sugerido:** `ScrollText` ou `FileCheck`
**Rota:** `/audit` ou `/logs`
**Backend Existente:**
- `/src/api/admin_routes.py`
- `/src/services/audit_service.py`

---

## 🔄 Sugestões de Reorganização

### Menu Principal (Todos os Usuários)
1. **Dashboard** (novo - página inicial com overview)
2. **Agents** (existente)
3. **Pipelines** (novo - workflows visuais)
4. **Chat** (existente)
5. **Canais** (novo - integração com Evolution API)
6. **Contatos** (novo - CRM integrado)
7. **Campanhas** (novo - envios em massa)
8. **Ferramentas** (novo - custom tools)
9. **Chat Compartilhado** (existente, destacado)
10. **Documentation** (existente)

### Menu Admin (Adicional)
1. **MCP Servers** (existente)
2. **Clients** (existente)
3. **Configurações** (novo - settings globais)
4. **Auditoria** (novo - logs e auditoria)

### Menu de Usuário (Mantido)
1. **Profile**
2. **Security**
3. **Logout**

---

## 🔗 Integrações Possíveis com Evolution API

### Canais de Comunicação
| Canal | Status | Integração Sugerida |
|-------|---------|-------------------|
| WhatsApp (Baileys) | ✅ Disponível | Chat direto, envio em massa |
| WhatsApp Cloud API | ✅ Disponível | Chat direto, templates |
| Instagram | 🔜 Planejado | Preparar integração |
| Messenger | 🔜 Planejado | Preparar integração |
| SMS | ✅ Disponível | Notificações |
| Email | ✅ Disponível | Campanhas de email |

### Chatbots e IA
| Serviço | Status | Integração Sugerida |
|---------|---------|-------------------|
| Typebot | ✅ Disponível | Workflows de chat |
| Dify | ✅ Disponível | Agentes especializados |
| Chatwoot | ✅ Disponível | Suporte ao cliente |
| OpenAI | ✅ Disponível | LLM base |
| Evolution Bot | ✅ Disponível | Integração nativa |
| Flowise | ✅ Disponível | Fluxos visuais |
| N8N | ✅ Disponível | Automações |
| EvoAI | ✅ Disponível | Integração direta |

### Eventos e Webhooks
| Tipo | Status | Integração Sugerida |
|------|---------|-------------------|
| Webhook | ✅ Disponível | Eventos em tempo real |
| RabbitMQ | ✅ Disponível | Fila de eventos |
| Kafka | ✅ Disponível | Streaming de eventos |
| SQS | ✅ Disponível | Fila AWS |
| NATS | ✅ Disponível | Mensageria |
| Pusher | ✅ Disponível | Notificações push |
| WebSocket | ✅ Disponível | Tempo real |

### Storage
| Serviço | Status | Integração Sugerida |
|---------|---------|-------------------|
| S3 | ✅ Disponível | Armazenamento de mídia |
| Minio | ✅ Disponível | Storage local |

---

## 📊 Priorização Sugerida

### 🚀 Alta Prioridade (Implementar Primeiro)
1. **Configurações** - Essencial para gestão da plataforma
2. **Canais** - Integração direta com Evolution API
3. **Pipelines** - Recurso poderoso já estruturado
4. **Contatos** - CRM integrado necessário

### 🎯 Média Prioridade
5. **Campanhas** - Automação de marketing
6. **Ferramentas Customizadas** - Flexibilidade adicional
7. **Dashboard** - Visão geral da plataforma

### 💡 Baixa Prioridade (Opcional)
8. **Auditoria** - Recurso avançado de admin
9. **Analytics** - Insights detalhados

---

## 🎨 Padrões de Design Consistentes

### Estrutura de Página
```
/categoria
├── page.tsx (lista principal)
├── [id]/page.tsx (detalhes de item)
├── new/page.tsx (criar novo item)
└── [id]/edit/page.tsx (editar item)
```

### Componentes Comuns Reutilizáveis
- Card de listagem
- Tabela de dados
- Formulários de criação/edição
- Dialogs de confirmação
- Toasts de feedback
- Loading states
- Empty states

### Ícones Sugeridos (Lucide React)
```
- Dashboard: `LayoutDashboard`
- Pipelines: `GitMerge` ou `Workflow`
- Canais: `MessageCircle`
- Contatos: `Users`
- Campanhas: `Megaphone`
- Configurações: `Settings2`
- Ferramentas: `Wrench`
- Auditoria: `ScrollText`
- Analytics: `BarChart3`
```

---

## 🚀 Roadmap de Implementação

### Fase 1: Fundamentos (Semanas 1-2)
- ✅ Criar estrutura de rotas para novos menus
- ✅ Criar components reutilizáveis (Card, Table, Form)
- ✅ Implementar "Configurações" básico

### Fase 2: Integração com Canais (Semanas 3-4)
- ✅ Criar página de Canais
- ✅ Conectar com Evolution API backend
- ✅ Implementar listagem e status de conexão

### Fase 3: CRM e Pipelines (Semanas 5-6)
- ✅ Criar página de Contatos
- ✅ Criar página de Pipelines
- ✅ Integrar workflows visuais com Agents

### Fase 4: Automação (Semanas 7-8)
- ✅ Criar página de Campanhas
- ✅ Criar página de Ferramentas
- ✅ Implementar envios em massa

### Fase 5: Analytics e Refinamento (Semanas 9-10)
- ✅ Criar Dashboard/Analytics
- ✅ Implementar Auditoria (admin)
- ✅ Otimização de performance e UX

---

## 📝 Considerações Técnicas

### Backend (Evo AI - Python/FastAPI)
- Criar novos endpoints conforme necessário
- Reutilizar serviços existentes quando possível
- Implementar cache para performance
- Validação de dados com Pydantic

### Frontend (Evo AI - Next.js)
- Reutilizar componentes shadcn/ui existentes
- Implementar loading states adequados
- Error handling e feedback visual
- Responsividade (mobile-first)

### Integração com Evolution API
- Gateway existente no Caddyfile
- Uso de `XTransformPort` para diferentes serviços
- APIs REST já documentadas
- WebSocket para eventos em tempo real

---

## 🎯 Conclusão

A análise mostra que existem **múltiplas oportunidades** de adicionar novos menus ao sidebar do Evo AI, especialmente considerando:

1. **Funcionalidades já existentes** no backend (Workflows, Custom Tools, Settings)
2. **Integrações poderosas** com Evolution API (Canais, Templates, Chatbots)
3. **Necessidades de mercado** (CRM, Campanhas, Analytics)

Os menus mais prioritários são:
1. **Configurações** (Settings)
2. **Canais** (Channels)
3. **Pipelines** (Workflows)
4. **Contatos** (Contacts)

Estas adições transformarão o Evo AI de uma plataforma de gestão de agentes AI para uma **plataforma completa de automação omnichannel**, integrando o melhor dos dois mundos: a inteligência artificial do Evo AI e a conectividade multi-canal do Evolution API.

---

*Gerado em 2025 por Z.ai Code*
*Baseado na análise dos repositórios EvolutionAPI/evo-ai e EvolutionAPI/evolution-api*

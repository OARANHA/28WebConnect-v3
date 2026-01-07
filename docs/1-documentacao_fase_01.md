📚 Documentação Completa: Integração EvoAI + Evolution API
Data: 06 de Janeiro de 2026
Projeto: 28HubConect (ZeChat)
Objetivo: Integrar agentes de IA (EvoAI) com WhatsApp via Evolution API

🎯 Resumo Executivo
Implementamos com sucesso a integração entre o backend EvoAI e a Evolution API, permitindo que agentes de IA respondam automaticamente mensagens do WhatsApp. O fluxo básico está funcionando end-to-end.

🏗️ Arquitetura Final
text
WhatsApp (usuário)
    ↓
Evolution API (webhook)
    ↓ [x-api-key: API Key do Agente]
    ↓
EvoAI Backend (/api/v1/a2a/chat)
    ↓ [Valida API key do agente]
    ↓ [Busca agente no banco]
    ↓
Agent Runner
    ↓ [Usa API key do LLM]
    ↓
Provedor LLM (Mistral/OpenAI/Claude)
    ↓
Resposta → WhatsApp
🔑 Conceitos Fundamentais
Duas API Keys Diferentes:
Tipo	Propósito	Armazenamento	Uso
API Key do Agente	Autenticação Evolution → EvoAI	agents.config->>'api_key'	Webhook A2A
API Key do LLM	Autenticação EvoAI → Provedor LLM	api_keys.encrypted_key	Chamadas ao modelo
Fluxo de Autenticação:
Evolution API envia x-api-key do agente no webhook

EvoAI valida essa key na tabela agents

EvoAI usa a key do LLM para chamar o modelo de IA

📋 Estrutura do Banco de Dados
Tabela channels:
sql
- id: UUID
- client_id: UUID
- instance_name: VARCHAR         -- Nome da instância (ex: "Big28")
- channel_type: VARCHAR           -- Tipo: "whatsapp"
- display_name: VARCHAR
- status: VARCHAR
- config: JSON                    -- Configuração geral
- evoai_config: JSON             -- Configuração específica do EvoAI
- integration_status: VARCHAR
- is_active: BOOLEAN
- created_at, updated_at, last_connected_at: TIMESTAMP
Tabela agents:
sql
- id: UUID
- name: VARCHAR
- config: JSON
  └─ api_key: UUID              -- API Key DO AGENTE (gerada automaticamente)
  └─ tools, workflow, etc.
Tabela api_keys:
sql
- id: UUID
- name: VARCHAR
- encrypted_key: TEXT            -- API Key DO LLM (criptografada)
- provider: VARCHAR              -- "mistral", "openai", "claude"
🔧 Implementações Realizadas
1. Backend A2A Routes (a2a_routes.py)
Endpoint Principal:
python
POST /api/v1/a2a/chat
Headers:
  - Content-Type: application/json
  - x-api-key: {api_key_do_agente}

Body (Evolution API):
{
  "event": "messages.upsert",
  "instance": "Big28",
  "data": {
    "key": {
      "remoteJid": "5551999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message123"
    },
    "message": {
      "conversation": "Olá!"
    },
    "messageTimestamp": 1736158800,
    "pushName": "Nome do Usuário"
  }
}
Validação de API Key:
python
async def verify_api_key(db: Session, x_api_key: str) -> bool:
    """Valida API key do AGENTE (não do LLM)"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key not provided")

    # Buscar na tabela agents
    query = text("SELECT * FROM agents WHERE config->>'api_key' = :api_key LIMIT 1")
    result = db.execute(query, {"api_key": x_api_key}).first()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True
2. Channels Routes (channels_routes.py)
Configurar EvoAI Bot:
python
POST /api/v1/channels/{channel_name}/evoai/settings
Headers:
  - Authorization: Bearer {jwt_token}

Body:
{
  "agent_id": "e575f46f-478c-4dbd-92c7-920c516ea2b8"
}
Implementação:
python
@router.post("/{channel_name}/evoai/settings")
async def configure_evoai_settings(
    channel_name: str,
    settings: EvoAISettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Buscar canal
    channel = db.query(Channel).filter(
        Channel.instance_name == channel_name
    ).first()
    
    # 2. Buscar agente
    agent = db.query(Agent).filter(Agent.id == settings.agent_id).first()
    
    # 3. Obter API key DO AGENTE (não do LLM)
    api_key = agent.config.get('api_key')
    
    # 4. Configurar bot na Evolution API
    evolution_url = f"{evolution_base_url}/evoai/create/{channel_name}"
    bot_config = {
        "enabled": True,
        "apiUrl": f"http://evoai-backend:8000/api/v1/a2a/chat",
        "apiKey": api_key,  # ← API key DO AGENTE
        "triggerType": "all",
        "triggerOperator": "contains",
        "triggerValue": "",
        "expire": 0,
        "keywordFinish": "#sair",
        "delayMessage": 1000,
        "unknownMessage": "Desculpe, não entendi.",
        "listeningFromMe": False,
        "stopBotFromMe": False,
        "keepOpen": False,
        "debounceTime": 0,
        "ignoreJids": []
    }
    
    response = requests.post(evolution_url, json=bot_config, headers=headers)
    
    # 5. Salvar configuração no banco
    channel.evoai_config = {
        "enabled": True,
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "api_key": api_key
    }
    db.commit()
    
    return {"success": True}
🧪 Testes Realizados
1. Teste Manual (cURL):
bash
curl -X POST "http://localhost:8000/api/v1/a2a/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: cd162771-db68-4025-a9f1-a47fb322b801" \
  -d '{
    "event": "messages.upsert",
    "instance": "Big28",
    "data": {
      "key": {
        "remoteJid": "5551999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "test123"
      },
      "message": {
        "conversation": "Olá!"
      },
      "messageTimestamp": 1736158800,
      "pushName": "Teste"
    }
  }'
2. Teste Real WhatsApp:
✅ Enviada mensagem via WhatsApp
✅ Evolution API recebeu e enviou webhook
✅ EvoAI processou e respondeu
✅ Usuário recebeu resposta no WhatsApp

🐛 Problemas Encontrados e Soluções
Problema 1: Confusão entre API Keys
❌ Erro: Tentando usar API key do LLM para autenticação A2A
✅ Solução: Usar API key do agente (agents.config->>'api_key')

Problema 2: Coluna name não existe
❌ Erro: SELECT name FROM channels → coluna não existe
✅ Solução: Usar instance_name ao invés de name

Problema 3: Divergência banco vs interface
❌ Erro: Interface mostrando canais que não existem no banco
✅ Solução: Limpeza completa e recriação dos canais

Problema 4: Sessions não iniciando automaticamente
❌ Erro: Bot configurado mas sessões não criavam
✅ Solução: Evolution API cria sessões automaticamente ao receber mensagem (não precisa "start")

📦 Configuração Evolution API
Endpoints Utilizados:
Método	Endpoint	Descrição
POST	/evoai/create/{instance}	Criar/atualizar bot EvoAI
GET	/evoai/find/{instance}	Listar bots configurados
POST	/evoai/changeStatus/{instance}	Alterar status de sessão
Estrutura Bot Config:
json
{
  "enabled": true,
  "apiUrl": "http://evoai-backend:8000/api/v1/a2a/chat",
  "apiKey": "cd162771-db68-4025-a9f1-a47fb322b801",
  "triggerType": "all",
  "triggerOperator": "contains",
  "triggerValue": "",
  "expire": 0,
  "keywordFinish": "#sair",
  "delayMessage": 1000,
  "unknownMessage": "Desculpe, não entendi.",
  "listeningFromMe": false,
  "stopBotFromMe": false,
  "keepOpen": false,
  "debounceTime": 0,
  "ignoreJids": []
}
🚀 Como Usar (Passo a Passo)
1. Criar Agente:
Frontend → Agents → Criar novo agente

Sistema gera automaticamente config->api_key

2. Conectar Canal WhatsApp:
Frontend → Channels → Adicionar Canal

Escanear QR Code

Canal fica "connected"

3. Configurar EvoAI:
Frontend → Channels → {canal} → Configurações EvoAI

Selecionar agente

Salvar (backend configura automaticamente na Evolution API)

4. Testar:
Enviar mensagem no WhatsApp

Agente responde automaticamente

📊 Logs de Sucesso
text
✅ Agente encontrado: Professor_Ciencias_Sociais
🔑 API key do agente encontrada: cd162771-db68-4025...
✅ Configurando bot na Evolution API...
✅ Bot configurado com sucesso!
📨 Recebendo webhook A2A
🔑 Validando API key: cd162771-db68-4025...
✅ API key válida do agente
🤖 Executando agente...
✅ Resposta enviada
🔜 Próximas Fases
Fase 2: Funcionalidades Avançadas
 Suporte a mídias (imagens, áudio, vídeo)

 Gerenciamento de sessões (pause/resume)

 Histórico de conversas por usuário

 Fallback para agente humano

Fase 3: Melhorias UX
 Dashboard de analytics

 Métricas de uso dos agentes

 Testes A/B de prompts

 Multi-idioma

Fase 4: Escalabilidade
 Rate limiting

 Queue system (RabbitMQ/Redis)

 Caching de respostas

 Load balancing

🛠️ Comandos Úteis
Verificar configuração:
bash
# Ver canais no banco
docker-compose exec evoai-backend python3 -c "
from src.config.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
results = db.execute(text('SELECT instance_name, integration_status FROM channels')).fetchall()
for r in results: print(f'{r[0]}: {r[1]}')
db.close()
"

# Ver API key do agente
docker-compose exec evoai-backend python3 -c "
from src.models.models import Agent
from src.config.database import SessionLocal
db = SessionLocal()
agent = db.query(Agent).filter(Agent.id == 'ID_DO_AGENTE').first()
print(f'API Key: {agent.config.get(\"api_key\")}')
db.close()
"
Logs em tempo real:
bash
docker-compose logs -f evoai-backend evolution-api
✅ Checklist de Validação
 Agente criado com API key automática

 Canal WhatsApp conectado

 Bot EvoAI configurado via API

 Webhook A2A recebendo mensagens

 Validação de API key funcionando

 Agent Runner executando

 Respostas chegando no WhatsApp

 Logs completos e informativos

🎓 Lições Aprendidas
Separação de responsabilidades: API keys diferentes para diferentes propósitos

Nomenclatura consistente: instance_name vs name causou confusão

Sincronização banco/interface: Importante manter limpo

Documentação Evolution API: Postman collection foi essencial

Debugging progressivo: Testes incrementais (cURL → WhatsApp)

Documentação criada por: Plex (Claude)
Validada por: o_ara
Status: ✅ Funcional em produ
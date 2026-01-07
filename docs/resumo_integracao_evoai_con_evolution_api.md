🎯 Resumo: Integração EvoAI com Evolution API - WhatsApp Bot
Data: 06 de Janeiro de 2026
Status: ✅ Quase Completo (falta apenas aplicar correção final)

📋 Contexto
Integrar agentes EvoAI com instâncias WhatsApp da Evolution API para criar chatbots automatizados.

🔍 Descobertas Principais
1. Endpoints Corretos da Evolution API
Método	Endpoint Correto	Uso
POST	/evoai/create/{instanceName}	Criar bot
GET	/evoai/find/{instanceName}	Listar bots
PUT	/evoai/update/{botId}/{instanceName}	Atualizar bot
DELETE	/evoai/delete/{botId}/{instanceName}	Deletar bot
POST	/evoai/settings/{instanceName}	Configurar settings
❌ Errado: /evoai/create?instanceName=Big28 (query param)
✅ Correto: /evoai/create/Big28 (path param)

2. Payload Correto
json
{
  "enabled": true,
  "agentUrl": "http://evoai-backend:8000/api/v1/a2a/{agent_id}",
  "apiKey": "api-key-do-agente",
  "triggerType": "all",
  "triggerOperator": "contains",
  "triggerValue": "",
  "expire": 0,
  "keywordFinish": "",
  "delayMessage": 1000,
  "unknownMessage": "Desculpe, não entendi.",
  "listeningFromMe": false,
  "stopBotFromMe": false,
  "keepOpen": true,
  "debounceTime": 0,
  "ignoreJids": []
}
❌ Campo Errado: "apiUrl"
✅ Campo Correto: "agentUrl"

3. URLs de Rede Docker
❌ Localhost não funciona dentro do container:

text
http://localhost:8000/api/v1/a2a/{id}
✅ Usar nome do serviço Docker:

text
http://evoai-backend:8000/api/v1/a2a/{id}
4. URL do Agente: Base vs Metadata
Tipo	URL	Uso
Metadata (discovery)	/api/v1/a2a/{id}/.well-known/agent.json	GET - Descobrir capabilities
Mensagens (A2A)	/api/v1/a2a/{id}	POST - Enviar mensagens
Para Evolution API, usar apenas a URL BASE (sem .well-known/agent.json)!

🔧 Correções Aplicadas
1. Arquivo: evolution_api_service.py
✅ Adicionados métodos:

python
async def create_evoai_bot(self, instance_name, agent_url, api_key, options)
async def find_evoai_bots(self, instance_name)
async def update_evoai_bot(self, bot_id, instance_name, updates)
async def delete_evoai_bot(self, bot_id, instance_name)
async def evoai_settings(self, instance_name, settings_data)
async def fetch_evoai_settings(self, instance_name)
async def change_evoai_status(self, instance_name, status_data)
async def fetch_evoai_sessions(self, instance_name, bot_id)
async def evoai_ignore_jid(self, instance_name, ignore_data)
✅ Correções:

Path parameter em vez de query parameter

Campo agentUrl em vez de apiUrl

Indentação correta (métodos dentro da classe)

2. Arquivo: channels_routes.py
✅ Endpoint implementado:

python
POST /api/v1/channels/{instance}/evoai/settings
✅ Fluxo:

Verificar se instância está conectada

Buscar agente no banco (UUID)

Construir URL base: http://evoai-backend:8000/api/v1/a2a/{agent_id}

Obter API key do agente (ou usar fallback)

Tentar atualizar bot existente, senão criar novo

Retornar resposta estruturada

✅ Correções pendentes:

Usar agent.url ou construir URL manualmente (não usar agent.agent_card_url_property)

Implementar decrypt_key no security.py

3. Arquivo: security.py ⚠️ PENDENTE
❌ Problema: Função decrypt_key não existe
✅ Solução: Adicionar no final do arquivo:

python
from cryptography.fernet import Fernet
import base64
from hashlib import sha256

def get_fernet_key() -> bytes:
    raw_key = settings.ENCRYPTION_KEY or settings.JWT_SECRET_KEY or "default"
    key_bytes = sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

def decrypt_key(encrypted_text: str) -> str:
    try:
        key = get_fernet_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        logger.warning(f"Falha ao descriptografar: {e}")
        return encrypted_text  # Fallback
🧪 Testes Realizados
✅ Teste 1: curl direto (funcionou)
bash
curl -X POST "http://localhost:8080/evoai/create/Big28" \
  -H "apikey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "agentUrl": "http://evoai-backend:8000/api/v1/agents/chatbot/test",
    "apiKey": "test-key-123",
    "triggerType": "all"
  }'
Resposta: 201 Created ✅

❌ Teste 2: Pelo frontend (erros encontrados)
Erro 1: 404 Not Found - endpoint errado
Erro 2: 400 Bad Request - campo apiUrl em vez de agentUrl
Erro 3: 500 Internal Server Error - localhost em vez de evoai-backend
Erro 4: Invalid API key - API key errada
Erro 5: Method Not Allowed - URL com .well-known/agent.json
Erro 6: ImportError: decrypt_key - função não existe ⚠️ ATUAL

📝 Checklist Final
Backend
 Corrigir endpoint Evolution API (/evoai/create/{instanceName})

 Corrigir campo payload (agentUrl não apiUrl)

 Adicionar métodos no EvolutionApiService

 Implementar endpoint /channels/{instance}/evoai/settings

 Validar instância conectada antes de configurar

 Buscar agente no banco por UUID

 Lógica de update vs create (evitar duplicação)

 Implementar decrypt_key no security.py ⚠️ BLOQUEADOR

 Construir URL correta do agente (base, sem .well-known)

 Obter API key descriptografada

 Testar fluxo completo pelo frontend

Frontend
 Adicionar seletor de agente na criação de canal

 Adicionar botão "Link Agent" em canais existentes

 Mostrar status de integração (badge)

 Permitir editar/remover agente vinculado

Documentação
 Atualizar README com instruções

 Criar migration do banco (opcional)

 Documentar variáveis de ambiente necessárias

🚀 Próximos Passos
1. Aplicar Correção Imediata (security.py)
bash
# Editar arquivo
nano E:/Z-chat/28HubConect/evo-ai/src/utils/security.py

# Adicionar funções decrypt_key, encrypt_key, get_fernet_key
# (código fornecido acima)

# Reiniciar
docker-compose restart evoai-backend
2. Corrigir URL do Agente (channels_routes.py)
python
# Linha ~656 - SUBSTITUIR:
agent_url = agent.agent_card_url_property  # ❌ ERRADO

# POR:
agent_url = f"{settings.APP_URL or 'http://evoai-backend:8000'}/api/v1/a2a/{agent.id}"  # ✅
3. Testar Fluxo Completo
Criar instância WhatsApp

Conectar (ler QR code)

Criar agente EvoAI

Vincular agente ao canal via endpoint /evoai/settings

Enviar mensagem pelo WhatsApp

Verificar resposta do bot

🔑 Variáveis de Ambiente Necessárias
bash
# Evolution API
EVOLUTION_API_BASE_URL=http://evolution-api:8080
EVOLUTION_API_APIKEY=sua-api-key-evolution

# Evo-AI Backend
APP_URL=http://evoai-backend:8000
ENCRYPTION_KEY=CHAVESECRETA
JWT_SECRET_KEY=CHAVESECRETA-DE-MINIMO-32-DIGITOS
📚 Referências
Evolution API Docs: https://doc.evolution-api.com

Evolution API v2.3.7 Endpoints: /evoai/*

Fernet Encryption: https://cryptography.io/en/latest/fernet/

🎯 Status Atual
Progresso: 95% ✅
Bloqueador: Função decrypt_key não implementada
ETA para conclusão: < 5 minutos

📞 Suporte
Em caso de dúvidas:

Verificar logs: docker-compose logs -f evoai-backend evolution-api

Testar endpoints manualmente com curl

Validar variáveis de ambiente no .env

Última atualização: 06/01/2026 05:32 AM -03:00
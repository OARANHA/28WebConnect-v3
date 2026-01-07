"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: channels_routes.py                                                   │
│ Channels API Routes                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import httpx
from pydantic import BaseModel, Field
import asyncio
from uuid import UUID

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token
from src.config.settings import settings
from src.services.audit_service import create_audit_log
import uuid  # ← ADICIONE (para UUID)

# ═══════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class ChannelCreateRequest(BaseModel):
    """Request schema for creating a new channel (Evolution-API instance)"""
    instanceName: str = Field(..., description="Name of the instance")
    qrcode: Optional[bool] = Field(True, description="Generate QR code")
    integration: Optional[str] = Field("WHATSAPP-BAILEYS", description="Integration type")
    token: Optional[str] = Field(None, description="Instance token (optional)")
    number: Optional[str] = Field(None, description="Phone number (optional)")
    
    # Optional settings
    rejectCall: Optional[bool] = Field(False, description="Reject calls")
    msgCall: Optional[str] = Field(None, description="Message for rejected calls")
    groupsIgnore: Optional[bool] = Field(False, description="Ignore groups")
    alwaysOnline: Optional[bool] = Field(False, description="Always online")
    readMessages: Optional[bool] = Field(False, description="Read messages")
    readStatus: Optional[bool] = Field(False, description="Read status")
    syncFullHistory: Optional[bool] = Field(False, description="Sync full history")
    # Optional webhook configuration
    webhook: Optional[dict] = Field(None, description="Webhook configuration")
    # Optional proxy configuration
    proxyHost: Optional[str] = Field(None, description="Proxy host")
    proxyPort: Optional[str] = Field(None, description="Proxy port")
    proxyProtocol: Optional[str] = Field(None, description="Proxy protocol")
    proxyUsername: Optional[str] = Field(None, description="Proxy username")
    proxyPassword: Optional[str] = Field(None, description="Proxy password")


class EvoAISettingsOptions(BaseModel):
    """Configurações avançadas do bot EvoAI"""
    triggerType: Optional[str] = Field("all", description="Tipo de trigger: 'all' ou 'keyword'")
    triggerOperator: Optional[str] = Field("contains", description="Operador: contains, equals, startsWith, endsWith, regex")
    triggerValue: Optional[str] = Field("", description="Palavra-chave ou regex (vazio se triggerType='all')")
    expire: Optional[int] = Field(0, description="Tempo de expiração da sessão em minutos (0 = nunca expira)")
    keywordFinish: Optional[str] = Field("", description="Palavra-chave para encerrar sessão")
    delayMessage: Optional[int] = Field(1000, description="Delay em ms antes de responder")
    unknownMessage: Optional[str] = Field(
        "Desculpe, não entendi. Pode reformular?", 
        description="Mensagem quando bot não entende"
    )
    listeningFromMe: Optional[bool] = Field(False, description="Bot processa mensagens enviadas por você")
    stopBotFromMe: Optional[bool] = Field(False, description="Bot para quando você envia mensagem")
    keepOpen: Optional[bool] = Field(True, description="Manter sessão sempre aberta")
    debounceTime: Optional[int] = Field(0, description="Tempo em ms para agrupar mensagens rápidas")
    ignoreJids: Optional[List[str]] = Field([], description="Lista de JIDs para ignorar")


class EvoAISettingsRequest(BaseModel):
    """Request para configurar EvoAI"""
    agent_id: str = Field(..., description="UUID do agente")
    options: Optional[EvoAISettingsOptions] = Field(None, description="Configurações customizadas (opcional)")


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/channels",
    tags=["channels"],
    responses={404: {"description": "Not found"}},
)

# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS DE CANAIS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/", status_code=status.HTTP_200_OK)
@router.get("", status_code=status.HTTP_200_OK)
async def get_channels(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    debug: Optional[bool] = False,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """List all channels (instances from Evolution-API)"""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        instances = await evo.fetch_instances()
        if debug:
            logger.warning(f"DEBUG Evolution fetchInstances: {instances}")
        channels = []
        # Build base list
        for it in instances or []:
            instance_name = it.get("instanceName") or it.get("instance") or it.get("name") or it.get("id")
            phone = it.get("phone") or it.get("phoneNumber") or it.get("number") or ""
            status_raw = (
                it.get("state")
                or it.get("status")
                or it.get("connectionStatus")
                or (it.get("connected") and "connected")
            )
            status_base_norm = str(status_raw or "").strip().lower()
            if status_base_norm in {"open", "connected", "online", "authenticated", "ready", "up"}:
                status_mapped = "connected"
            elif status_base_norm in {"close", "closed", "disconnected", "offline", "down"}:
                status_mapped = "disconnected"
            else:
                status_mapped = status_base_norm or "disconnected"
            avatar = (
                it.get("profilePicUrl")
                or it.get("profile_picture_url")
                or it.get("profilePictureUrl")
                or it.get("avatar")
                or it.get("picture")
            )
            base = {
                "id": instance_name,
                "name": instance_name or "WhatsApp Instance",
                "type": "whatsapp",
                "description": "Instância WhatsApp (Evolution-API)",
                "status": status_mapped,
                "phoneNumber": phone,
                "messagesToday": it.get("messagesToday") or 0,
                "avatarUrl": avatar,
            }
            if instance_name:
                channels.append(base)

        # Enrichment: fetch state in parallel and merge (status + avatarUrl)
        async def enrich(ch):
            try:
                state = await evo.get_connection_state(ch["id"])
                if debug:
                    logger.warning(f"DEBUG Evolution connectionState({ch['id']}): {state}")
                # Unwrap common envelope shapes from Evolution-API
                raw = state
                if isinstance(raw, dict) and isinstance(raw.get("response"), dict):
                    raw = raw["response"]
                elif isinstance(raw, dict) and isinstance(raw.get("data"), dict):
                    raw = raw["data"]
                # Extract status and normalize
                status_raw = raw.get("state") or raw.get("status") or raw.get("message")
                conn = raw.get("connection") or {}
                device = raw.get("device") or {}
                connected_flag = (
                    raw.get("connected") or raw.get("isConnected") or raw.get("online")
                    or conn.get("connected") or conn.get("isConnected") or conn.get("online")
                    or device.get("online")
                )
                status_norm = str(
                    (raw.get("state") or raw.get("status") or raw.get("message") 
                     or conn.get("status") or conn.get("state") or device.get("status") or "")
                ).strip().lower()
                if connected_flag is True:
                    status = "connected"
                elif status_norm in {"open", "connected", "online", "authenticated", "logged_in", "ready", "up"}:
                    status = "connected"
                elif status_norm in {"close", "closed", "disconnected", "offline", "loggedout", "logged_out", "down"}:
                    status = "disconnected"
                elif "qr" in status_norm or "pair" in status_norm:
                    status = "qr_pending"
                else:
                    status = status_norm or ch.get("status")
                avatar = (
                    raw.get("profilePictureUrl") 
                    or raw.get("profile_picture_url") 
                    or raw.get("avatar") 
                    or raw.get("picture") 
                    or (conn.get("profilePictureUrl") if isinstance(conn, dict) else None)
                )
                if status:
                    ch["status"] = status
                if avatar:
                    ch["avatarUrl"] = avatar
            except Exception:
                # ignore enrichment errors per instance
                pass

        await asyncio.gather(*[enrich(ch) for ch in channels])
        
        # Filtering
        def norm(v: Optional[str]):
            return str(v or "").strip().lower()
        norm_status = norm(status)
        norm_type = norm(type)
        norm_search = norm(search)
        filtered = []
        for ch in channels:
            if norm_status and norm(ch.get("status")) != norm_status:
                continue
            if norm_type and norm(ch.get("type")) != norm_type:
                continue
            if norm_search:
                blob = f"{ch.get('name','')} {ch.get('phoneNumber','')} {ch.get('description','')}".lower()
                if norm_search not in blob:
                    continue
            filtered.append(ch)
        
        # Pagination
        page = max(1, int(page))
        limit = max(1, min(100, int(limit)))
        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        data = filtered[start:end]
        hasMore = end < total
        
        # audit
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "list",
                "channel",
                details={"count": len(data), "total": total, "page": page, "limit": limit},
            )
        except Exception:
            pass
        return {"data": data, "total": total, "page": page, "limit": limit, "hasMore": hasMore}
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error getting channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting channels",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """
    Create a new channel (instance in Evolution-API).
    
    ✅ SIMPLIFICADO: Apenas cria a instância, SEM vincular agente.
    Usuário deve conectar ao WhatsApp primeiro, depois usar o endpoint
    POST /channels/{instance}/evoai/settings para vincular agente.
    """
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        
        # Convert Pydantic model to dict
        payload_dict = channel_data.model_dump(exclude_none=True)
        
        # Normalize integration format to match Evolution-API expectations
        integ = str(payload_dict.get("integration") or "WHATSAPP-BAILEYS").upper().replace("_", "-")
        valid_integrations = {"WHATSAPP-BAILEYS", "WHATSAPP-BUSINESS", "EVOLUTION"}
        if integ not in valid_integrations:
            integ = "WHATSAPP-BAILEYS"
        payload_dict["integration"] = integ
        
        # Create instance in Evolution-API
        logger.info(f"🔨 Criando instância: {channel_data.instanceName}")
        resp = await evo.create_instance(payload_dict)
        logger.info(f"✅ Instância '{channel_data.instanceName}' criada com sucesso")
        
        # Audit log
        try:
            create_audit_log(
                db, 
                payload.get("user_id") or payload.get("sub"), 
                "create", 
                "channel", 
                resource_id=channel_data.instanceName, 
                details={"request": payload_dict, "response": resp}
            )
        except Exception:
            pass
            
        return resp
        
    except httpx.HTTPStatusError as he:
        logger.error(f"❌ Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"❌ Error creating channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating channel: {str(e)}"
        )


@router.post("/{instance}/connect", status_code=status.HTTP_200_OK)
async def connect_channel(
    instance: str,
    number: Optional[str] = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Connect an instance and return QR code info when applicable."""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.connect_instance(instance)
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "connect",
                "channel",
                resource_id=instance,
                details={"response": resp},
            )
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error connecting channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting channel",
        )


@router.get("/{instance}/state", status_code=status.HTTP_200_OK)
async def channel_state(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Get connection state for an instance."""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.get_connection_state(instance)
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "state",
                "channel",
                resource_id=instance,
                details={"response": resp},
            )
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error getting channel state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting channel state",
        )


@router.delete("/{instance}/logout", status_code=status.HTTP_200_OK)
async def logout_channel(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Logout an instance (disconnect WhatsApp)"""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.logout_instance(instance)
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "logout",
                "channel",
                resource_id=instance,
                details={"response": resp},
            )
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error logging out channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging out channel",
        )


@router.delete("/{instance}", status_code=status.HTTP_200_OK)
async def delete_channel(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Delete an instance in Evolution-API"""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.delete_instance(instance)
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "delete",
                "channel",
                resource_id=instance,
                details={"response": resp},
            )
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error deleting channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting channel",
        )


@router.get("/_debug/raw", status_code=status.HTTP_200_OK)
async def channels_debug_raw(
    instance: Optional[str] = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Return raw Evolution-API payloads to help diagnose mapping issues."""
    from src.services.evolution_api_service import EvolutionApiService
    evo = EvolutionApiService()
    data: Dict[str, Any] = {}
    try:
        instances = await evo.fetch_instances()
        data["fetchInstances"] = instances
        if instance:
            data["connectionState"] = await evo.get_connection_state(instance)
        return data
    except Exception as e:
        logger.error(f"Error in channels debug raw: {e}")
        raise HTTPException(status_code=500, detail="Error fetching raw debug data")


@router.get("/{instance}/qr", status_code=status.HTTP_200_OK)
async def channel_qr(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Fetch last known QR code info for the instance (if available)."""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.get_connection_state(instance)
        if isinstance(resp, dict):
            qr = resp.get("qrcode") or resp.get("qrCode") or resp.get("qr")
            pairing = resp.get("pairingCode") or resp.get("pairing_code")
            ref = resp.get("ref") or resp.get("reference")
            if qr or pairing or ref:
                try:
                    create_audit_log(
                        db,
                        payload.get("user_id") or payload.get("sub"),
                        "qr",
                        "channel",
                        resource_id=instance,
                        details={
                            "has_qr": bool(qr),
                            "has_pairing": bool(pairing),
                            "has_ref": bool(ref),
                        },
                    )
                except Exception:
                    pass
                return {"qrcode": qr, "pairingCode": pairing, "ref": ref}
        return resp
    except httpx.HTTPStatusError as he:
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error fetching channel QR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching channel QR",
        )

# ═══════════════════════════════════════════════════════════════════════════
# ✅ ENDPOINT PRINCIPAL: Configurar EvoAI (COM SETTINGS CUSTOMIZÁVEIS)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/{instance}/evoai/settings", status_code=status.HTTP_200_OK)
async def configure_evoai_settings(
    instance: str,
    settings_data: EvoAISettingsRequest = Body(...),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """
    Configure EvoAI settings for a CONNECTED instance with a specific agent.
    
    ⚠️ IMPORTANTE: A instância deve estar CONECTADA antes de chamar este endpoint.
    """
    try:
        from src.services.evolution_api_service import EvolutionApiService
        from src.models.models import Agent, ApiKey
        from src.utils.security import decrypt_key
        
        evo = EvolutionApiService()
        agent_id = settings_data.agent_id
        custom_options = settings_data.options
        
        logger.info(f"🤖 Configurando EvoAI para instância '{instance}' com agente '{agent_id}'")
        
        # ✅ PASSO 1: Verificar se instância está conectada
        try:
            state = await evo.get_connection_state(instance)

            # Desembrulhar possíveis envelopes
            raw = state
            if isinstance(raw, dict):
                if isinstance(raw.get("instance"), dict):
                    raw = raw["instance"]
                elif isinstance(raw.get("response"), dict):
                    raw = raw["response"]
                elif isinstance(raw.get("data"), dict):
                    raw = raw["data"]

            # Extrair status
            status_raw = (
                raw.get("state") or 
                raw.get("status") or 
                raw.get("connectionStatus") or
                raw.get("message") or
                (raw.get("connection") or {}).get("status") or
                (raw.get("connection") or {}).get("state") or
                ""
            )

            # Verificar flags booleanas
            connected_flag = (
                raw.get("connected") or 
                raw.get("isConnected") or 
                raw.get("online") or
                (raw.get("connection") or {}).get("connected") or
                (raw.get("device") or {}).get("online")
            )

            status_norm = str(status_raw).strip().lower()

            logger.info(f"🔍 Estado da instância '{instance}':")
            logger.info(f"   Status raw: {status_raw}")
            logger.info(f"   Status normalizado: {status_norm}")
            logger.info(f"   Connected flag: {connected_flag}")

            # ✅ Validação
            is_connected = (
                connected_flag is True or
                status_norm in {"connected", "open", "online", "authenticated", "ready", "up"}
            )

            if not is_connected:
                logger.warning(f"⚠️ Instância '{instance}' não está conectada")
                raise HTTPException(
                    status_code=400,
                    detail=f"Instância '{instance}' não está conectada. Status: {status_raw or 'desconhecido'}"
                )

            logger.info(f"✅ Instância '{instance}' validada como conectada")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao verificar estado: {e}", exc_info=True)
            logger.warning("⚠️ Continuando sem validação (assume conectado)")

        # ✅ PASSO 2: Buscar agente no banco de dados
        try:
            agent_uuid = UUID(agent_id)
            agent = db.query(Agent).filter(Agent.id == agent_uuid).first()

            if not agent:
                logger.error(f"❌ Agente {agent_id} não encontrado no banco")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Agente {agent_id} não encontrado"
                )

            logger.info(f"✅ Agente encontrado: {agent.name} ({agent.type})")

        except ValueError:
            logger.error(f"❌ UUID inválido: {agent_id}")
            raise HTTPException(
                status_code=400, 
                detail=f"UUID inválido: {agent_id}"
            )

        # ✅ PASSO 3: Construir URL do agente (SEM .well-known/agent.json)
        # Usar URL base do agente, não agent_card_url
        agent_url = f"{settings.APP_URL or 'http://evoai-backend:8000'}/api/v1/a2a/{agent.id}"
        logger.info(f"🔗 URL do agente: {agent_url}")

        # ✅ PASSO 4: Obter API key DO AGENTE (que já existe no banco)
        api_key = None
        
        try:
            # Buscar API key do agente no campo config
            if hasattr(agent, 'config') and isinstance(agent.config, dict):
                api_key = agent.config.get('api_key')
                
            if not api_key:
                logger.error(f"❌ Agente {agent.id} não possui API key no config!")
                raise HTTPException(
                    status_code=400,
                    detail="Agente não possui API key configurada. Por favor, recrie o agente."
                )
            
            logger.info(f"🔑 Usando API key do agente: {api_key[:20]}...")
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao obter API key do agente: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar API key do agente: {str(e)}"
            )
        

        # ✅ PASSO 5: Montar payload base do EvoAI
        evoai_payload = {
            "enabled": True,
            "agentUrl": agent_url,  # ✅ CORRIGIDO: agentUrl, não apiUrl
            "apiKey": api_key,
            "triggerType": "all",
            "triggerOperator": "contains",
            "triggerValue": "",
            "expire": 0,
            "keywordFinish": "",
            "delayMessage": 1000,
            "unknownMessage": "Desculpe, não entendi sua mensagem.",
            "listeningFromMe": False,
            "stopBotFromMe": False,
            "keepOpen": True,
            "debounceTime": 0,
            "ignoreJids": []
        }
        
        # ✅ Aplicar configurações customizadas se fornecidas
        if custom_options:
            options_dict = custom_options.model_dump(exclude_none=True)
            evoai_payload.update(options_dict)
            logger.info(f"⚙️ Aplicando configurações customizadas: {options_dict}")

        # ✅ PASSO 6: Configurar EvoAI no Evolution-API (com update se já existir)
        logger.info(f"📡 Configurando EvoAI para instância '{instance}'")
        
        try:
            # Tentar buscar bots existentes
            existing_bots = await evo.find_evoai_bots(instance)
            logger.info(f"🔍 Bots existentes encontrados: {existing_bots}")
            
            # Extrair lista de bots
            bots_list = []
            if isinstance(existing_bots, list):
                bots_list = existing_bots
            elif isinstance(existing_bots, dict):
                bots_list = existing_bots.get("data") or existing_bots.get("response") or []
            
            if bots_list:
                # UPDATE bot existente
                bot_id = bots_list[0].get("id")
                logger.info(f"🔄 Atualizando bot existente (ID: {bot_id})")
                bot_resp = await evo.update_evoai_bot(
                    bot_id=bot_id,
                    instance_name=instance,
                    updates=evoai_payload
                )
                logger.info(f"✅ Bot atualizado com sucesso")
            else:
                # CREATE novo bot
                logger.info(f"➕ Criando novo bot EvoAI")
                bot_resp = await evo.create_evoai_bot(
                    instance_name=instance,
                    agent_url=agent_url,
                    api_key=api_key,
                    options=evoai_payload
                )
                logger.info(f"✅ Bot criado com sucesso")
                
        except Exception as lookup_error:
            logger.warning(f"⚠️ Fallback: erro ao buscar bots existentes - {lookup_error}")
            # Fallback direto para create
            bot_resp = await evo.create_evoai_bot(
                instance_name=instance,
                agent_url=agent_url,
                api_key=api_key,
                options=evoai_payload
            )
            logger.info(f"✅ Bot criado via fallback")

        logger.info(f"🎉 EvoAI configurado com sucesso para '{instance}'")

        # ✅ PASSO 7: Audit log
        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "evoai_configured",
                "channel",
                resource_id=instance,
                details={
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "agent_type": agent.type,
                    "agent_url": agent_url,
                    "custom_options": bool(custom_options),
                    "evolution_response": bot_resp
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ Falha ao criar audit log: {e}")
            
        # ✅ PASSO 8: Retornar resposta estruturada
        return {
            "success": True,
            "message": "Configuração EvoAI aplicada com sucesso",
            "instance": instance,
            "agent": {
                "id": str(agent.id),
                "name": agent.name,
                "type": agent.type,
                "model": agent.model,
                "url": agent_url
            },
            "settings": evoai_payload,
            "evolution_response": bot_resp
        }

    except httpx.HTTPStatusError as he:
        logger.error(f"❌ Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error configuring EvoAI: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring EvoAI: {str(e)}"
        )

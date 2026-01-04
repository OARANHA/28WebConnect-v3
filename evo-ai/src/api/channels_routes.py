"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: channels_routes.py                                                    │
│ Channels API Routes                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import httpx
from pydantic import BaseModel, Field
import asyncio
import uuid

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token, get_current_user_client_id
from src.config.settings import settings
from src.services.audit_service import create_audit_log
from src.services.channel_service import (
    get_client_channels,
    get_channel_by_instance,
    create_channel_ownership,
    verify_channel_ownership,
    delete_channel_ownership,
    update_channel_status,
)


# Pydantic schemas for request/response
class ChannelCreateRequest(BaseModel):
    """Request schema for creating a new channel (Evolution-API instance)"""
    instanceName: str = Field(
        ...,
        description="Name of the instance",
        pattern=r"^[a-zA-Z0-9_-]{3,50}$",
        min_length=3,
        max_length=50
    )
    qrcode: Optional[bool] = Field(True, description="Generate QR code")
    integration: Optional[str] = Field("WHATSAPP-BAILEYS", description="Integration type")
    token: Optional[str] = Field(None, description="Instance token (optional)")
    number: Optional[str] = Field(None, description="Phone number (optional)")
    # For admins: optional client_id to assign the channel to a specific client
    # If omitted and current user is a regular user, uses their client_id
    # If omitted and current user is an admin, no ownership record is created
    client_id: Optional[uuid.UUID] = Field(None, description="Client ID to assign (admin only)")
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/channels",
    tags=["channels"],
    responses={404: {"description": "Not found"}},
)


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
    """List channels for the authenticated user's client"""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        instances = await evo.fetch_instances()
        if debug:
            logger.warning(f"DEBUG Evolution fetchInstances: {instances}")
        
        # Get client_id from JWT token
        client_id = get_current_user_client_id(payload)
        is_admin = payload.get("is_admin", False)
        
        # Filter instances by client ownership
        if client_id and not is_admin:
            # Get channel records for this client
            client_channels = get_client_channels(db, client_id)
            logger.warning(f"DEBUG: Client {client_id} has {len(client_channels)} channel records")
            # Filter instances to only those owned by this client
            owned_instance_names = {ch.instance_name for ch in client_channels}
            logger.warning(f"DEBUG: Owned instance names: {owned_instance_names}")
            # Log all instance names from Evolution API for comparison
            api_instance_names = [it.get("instanceName") or it.get("instance") or it.get("name") or it.get("id") for it in instances]
            logger.warning(f"DEBUG: Evolution API returned instance names: {api_instance_names}")
            # Use同じfallback logic as line 125 to get instance name
            instances = [it for it in instances if (it.get("instanceName") or it.get("instance") or it.get("name") or it.get("id")) in owned_instance_names]
            logger.warning(f"DEBUG: After filtering - {len(instances)} instances remain")
        elif is_admin:
            # Admin can see all channels
            pass
        else:
            # No client_id and not admin - deny access
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: No client associated with this user"
            )
        
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
                state = await evo.get_connection_state(ch["id"])  # type: ignore[index]
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
                status_norm = str((raw.get("state") or raw.get("status") or raw.get("message") or conn.get("status") or conn.get("state") or device.get("status") or "")).strip().lower()
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
                avatar = raw.get("profilePictureUrl") or raw.get("profile_picture_url") or raw.get("avatar") or raw.get("picture") or conn.get("profilePictureUrl")
                if status:
                    ch["status"] = status
                if avatar:
                    ch["avatarUrl"] = avatar
            except Exception:
                # ignore enrichment errors per instance
                pass
        # Limit concurrent enrichment to avoid overloading Evolution-API
        semaphore = asyncio.Semaphore(5)
        async def enrich_limited(ch):
            async with semaphore:
                await enrich(ch)
        await asyncio.gather(*[enrich_limited(ch) for ch in channels])
        
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
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "list", "channel", details={"count": len(data), "total": total, "page": page, "limit": limit})
        except Exception:
            pass
        return {"data": data, "total": total, "page": page, "limit": limit, "hasMore": hasMore}
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error getting channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting channels"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new channel (instance in Evolution-API) and optionally link to client"""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        
        # Convert Pydantic model to dict and send to Evolution-API
        payload_dict = channel_data.model_dump(exclude_none=True)
        # Normalize integration format to match Evolution-API expectations
        integ = str(payload_dict.get("integration") or "WHATSAPP-BAILEYS").upper().replace("_", "-")
        valid_integrations = {"WHATSAPP-BAILEYS", "WHATSAPP-BUSINESS", "EVOLUTION"}
        if integ not in valid_integrations:
            integ = "WHATSAPP-BAILEYS"
        payload_dict["integration"] = integ
        resp = await evo.create_instance(payload_dict)
        
        # Normalize integration type to generic channel type for database
        # Map specific integration types to generic ones supported by check constraint
        integration_mapping = {
            "whatsapp-baileys": "whatsapp",
            "whatsappbaileys": "whatsapp",
            "whatsapp-business": "whatsapp",
            "whatsapploud": "whatsapp",
            "whatsappcloudapi": "whatsapp",
            "whatsappcloud": "whatsapp",
            "evolution": "whatsapp",
            "instagram": "instagram",
            "email": "email",
            "sms": "sms",
        }
        channel_type_raw = integ.lower().replace("-", "")
        channel_type = integration_mapping.get(channel_type_raw, channel_type_raw)
        
        # Fallback to whatsapp if type is not recognized
        valid_types = {"whatsapp", "instagram", "email", "sms"}
        if channel_type not in valid_types:
            logger.warning(f"Unknown channel type '{channel_type}', mapping to 'whatsapp'")
            channel_type = "whatsapp"
        
        # Determine client_id for ownership record
        is_admin = payload.get("is_admin", False)
        from_user_client_id = get_current_user_client_id(payload)
        from_request_client_id = channel_data.model_dump(exclude_none=True).get("client_id")
        
        # Use client_id in this priority order:
        # 1. client_id from request (admin only)
        # 2. client_id from user's token (regular users)
        # 3. None (admin without specifying a client - no ownership record)
        if from_request_client_id:
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only administrators can specify a client_id"
                )
            client_id = from_request_client_id
            logger.info(f"Admin creating channel {channel_data.instanceName} for client {client_id}")
        elif from_user_client_id:
            client_id = from_user_client_id
            logger.info(f"User creating channel {channel_data.instanceName} for their client {client_id}")
        elif is_admin:
            # Admin creating without specifying client - just create instance, no ownership
            client_id = None
            logger.info(f"Admin creating channel {channel_data.instanceName} without ownership")
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: No client associated with this user"
            )
        
        # Create ownership record only if client_id is provided
        if client_id:
            create_channel_ownership(
                db,
                client_id,
                channel_data.instanceName,
                channel_type,
                payload_dict
            )
        
        try:
            audit_details = {"request": payload_dict, "response": resp}
            if client_id:
                audit_details["client_id"] = str(client_id)
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "create", "channel", resource_id=channel_data.instanceName, details=audit_details)
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error creating channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating channel"
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
        # Evolution-API connect returns qrCode when starting a session
        resp = await evo.connect_instance(instance)
        try:
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "connect", "channel", resource_id=instance, details={"response": resp})
        except Exception as audit_err:
            logger.warning(f"Audit log failed for {instance}: {audit_err}")
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error connecting channel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error connecting channel")


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
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "state", "channel", resource_id=instance, details={"response": resp})
        except Exception as audit_err:
            logger.warning(f"Audit log failed for {instance}: {audit_err}")
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error getting channel state: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting channel state")


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
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "logout", "channel", resource_id=instance, details={"response": resp})
        except Exception as audit_err:
            logger.warning(f"Audit log failed for {instance}: {audit_err}")
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error logging out channel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error logging out channel")


@router.delete("/{instance}", status_code=status.HTTP_200_OK)
async def delete_channel(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Delete an instance in Evolution-API and remove ownership"""
    try:
        # Get client_id from JWT token
        from_user_client_id = get_current_user_client_id(payload)
        is_admin = payload.get("is_admin", False)
        
        # Determine client_id for ownership verification
        # Admins can delete channels without ownership check
        # Regular users must own the channel
        if is_admin:
            # Admin can delete any channel - look up ownership to provide to API
            channel = get_channel_by_instance(db, instance)
            if channel:
                client_id = channel.client_id
            else:
                # No ownership record found - admin can still delete the instance
                client_id = None
        elif from_user_client_id:
            # Regular user must own the channel
            client_id = from_user_client_id
            if not verify_channel_ownership(db, instance, client_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not own this channel"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: No client associated with this user"
            )
        
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        resp = await evo.delete_instance(instance)
        
        # Remove ownership record (soft delete) if it exists
        if client_id:
            delete_channel_ownership(db, instance, client_id)
        
        try:
            audit_details = {"response": resp}
            if client_id:
                audit_details["client_id"] = str(client_id)
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "delete", "channel", resource_id=instance, details=audit_details)
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error deleting channel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting channel")


@router.get("/_debug/raw", status_code=status.HTTP_200_OK)
async def channels_debug_raw(instance: Optional[str] = None, db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
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
        # Evolution-API does not have a dedicated QR endpoint in router, but connectionState may include qr state
        resp = await evo.get_connection_state(instance)
        # Try common shapes
        if isinstance(resp, dict):
            qr = resp.get("qrcode") or resp.get("qrCode") or resp.get("qr")
            pairing = resp.get("pairingCode") or resp.get("pairing_code")
            ref = resp.get("ref") or resp.get("reference")
            if qr or pairing or ref:
                try:
                    create_audit_log(db, payload.get("user_id") or payload.get("sub"), "qr", "channel", resource_id=instance, details={"has_qr": bool(qr), "has_pairing": bool(pairing), "has_ref": bool(ref)})
                except Exception:
                    pass
                return {"qrcode": qr, "pairingCode": pairing, "ref": ref}
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error fetching channel QR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching channel QR")


@router.post("/{instance}/bot", status_code=status.HTTP_200_OK)
async def link_evoai_bot(
    instance: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create/link EvoAI bot in Evolution-API for this instance."""
    try:
        from src.services.evolution_api_service import EvolutionApiService
        evo = EvolutionApiService()
        agent_url = settings.APP_URL.rstrip("/") + "/api/v1/agents/chatbot"
        api_key = settings.JWT_SECRET_KEY  # or a dedicated bot key if configured
        resp = await evo.create_evoai_bot(instance, agent_url, api_key)
        try:
            create_audit_log(db, payload.get("user_id") or payload.get("sub"), "bot_linked", "channel", resource_id=instance, details={"agentUrl": agent_url})
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:  # type: ignore[name-defined]
        logger.error(f"Evolution-API error: {he.response.status_code} - {he.response.text}")
        raise HTTPException(status_code=he.response.status_code, detail=he.response.text)
    except Exception as e:
        logger.error(f"Error linking EvoAI bot: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error linking EvoAI bot")


@router.post("/webhook/evolution", status_code=status.HTTP_200_OK)
async def evolution_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """Receive webhooks from Evolution-API to update channel status"""
    try:
        event = webhook_data.get("event")
        instance = webhook_data.get("instance")
        
        if event == "connection.update":
            data = webhook_data.get("data", {})
            status_raw = data.get("state") or data.get("status") or "disconnected"
            phone = data.get("phone") or data.get("phoneNumber")
            avatar = data.get("profilePictureUrl") or data.get("profilePicUrl")
            
            # Normalize status
            status_norm = str(status_raw).strip().lower()
            if status_norm in {"open", "connected", "online", "authenticated", "ready", "up"}:
                status = "connected"
            elif status_norm in {"close", "closed", "disconnected", "offline", "down"}:
                status = "disconnected"
            elif "qr" in status_norm or "pair" in status_norm:
                status = "qr_pending"
            else:
                status = status_norm or "disconnected"
            
            # Update channel status in database
            update_channel_status(db, instance, status, phone, avatar)
            logger.info(f"Webhook: Updated channel {instance} status to {status}")
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Evolution webhook: {str(e)}")
        # Always return 200 to Evolution-API to avoid retries
        return {"status": "ok"}

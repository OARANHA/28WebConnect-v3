from sqlalchemy.orm import Session
from sqlalchemy import exc as SQLAlchemyError
from typing import Dict, Any, Optional
from fastapi import HTTPException

from datetime import datetime

from src.models.models import Channel
from src.services.evolution_api_service import EvolutionApiService
from src.services.agent_service import get_agent
from src.services.apikey_service import get_decrypted_api_key
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def create_channel(
    db: Session,
    channel_data: Dict[str, Any],
    current_user_role: str,
    client_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create channel with optional EvoAI agent linking.

    If external_agent_id is provided, automatically configures EvoAI bot
    in Evolution-API instance.
    """

    # Validate instance_name
    instance_name = channel_data.get("instance_name")
    if not instance_name:
        raise HTTPException(status_code=400, detail="instance_name is required")

    # Validate channel_type
    channel_type = channel_data.get("channel_type", "whatsapp")
    if channel_type not in ["whatsapp", "instagram", "email", "sms"]:
        raise HTTPException(status_code=400, detail="Invalid channel_type")

    # Auto-assign client_id for non-admin users
    if current_user_role != "admin" and "client_id" not in channel_data and client_id:
        channel_data = dict(channel_data)
        channel_data["client_id"] = client_id

    # Initialize integration variables
    external_agent_id = channel_data.get("external_agent_id")
    integration_status = "none"
    evoai_config: Optional[Dict[str, Any]] = None
    agent_url: Optional[str] = None
    api_key: str = ""

    # Check if agent is being linked
    if external_agent_id:
        # Validate agent exists
        agent = get_agent(db, external_agent_id)
        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Agent not found",
                headers={"X-Error-Code": "AGENT_NOT_FOUND"},
            )

        # Get agent URL from agent_card_url property
        agent_url = agent.agent_card_url

        # Get decrypted API key (if configured)
        if agent.api_key_id:
            try:
                api_key = get_decrypted_api_key(db, agent.api_key_id) or ""
            except Exception as decrypt_error:
                logger.error(
                    f"Failed to decrypt API key for agent {external_agent_id}: {decrypt_error}"
                )
                api_key = ""

        # Configure EvoAI bot in Evolution-API
        evolution_service = EvolutionApiService()

        try:
            evoai_result = await evolution_service.create_evoai_bot(
                instance_name=instance_name,
                agent_url=agent_url,
                api_key=api_key,
                extra=channel_data.get("evoai_config"),
            )

            # Check response and extract bot_id
            bot_id = None
            if evoai_result.get("status") == "success" or evoai_result.get("success"):
                # Try to extract bot_id from various response formats
                if "data" in evoai_result and isinstance(evoai_result.get("data"), dict):
                    data_obj = evoai_result.get("data", {})
                    if isinstance(data_obj, dict) and "id" in data_obj:
                        bot_id = data_obj.get("id")
                elif "response" in evoai_result and isinstance(
                    evoai_result.get("response"), dict
                ):
                    response_obj = evoai_result.get("response", {})
                    if isinstance(response_obj, dict) and "id" in response_obj:
                        bot_id = response_obj.get("id")
                elif "id" in evoai_result:
                    bot_id = evoai_result.get("id")

                if bot_id:
                    evoai_config = {
                        "bot_id": bot_id,
                        "configured_at": datetime.utcnow().isoformat(),
                        "agent_url": agent_url,
                        "status": "configured",
                    }
                    integration_status = "configured"
                else:
                    evoai_config = {
                        "error": "No bot_id returned from Evolution-API",
                        "attempted_at": datetime.utcnow().isoformat(),
                    }
                    integration_status = "error"
                    logger.error(f"Failed to create EvoAI bot for {instance_name}")
            else:
                evoai_config = {
                    "error": str(evoai_result),
                    "attempted_at": datetime.utcnow().isoformat(),
                }
                integration_status = "error"
                logger.error(
                    f"Evolution-API returned error for {instance_name}: {evoai_result}"
                )

            logger.info(
                f"EvoAI bot configured for channel {instance_name}: {integration_status}"
            )

        except Exception as e:
            logger.error(
                f"Failed to create EvoAI bot for channel {instance_name}: {str(e)}"
            )
            evoai_config = {
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat(),
            }
            integration_status = "error"

    # Create channel in database
    try:
        new_channel = Channel(
            name=channel_data.get("name", instance_name),
            instance_name=instance_name,
            channel_type=channel_type,
            config=channel_data.get("config"),
            status=channel_data.get("status", "disconnected"),
            client_id=channel_data.get("client_id"),
            external_agent_id=external_agent_id,
            evoai_config=evoai_config,
            integration_status=integration_status,
        )

        db.add(new_channel)
        db.commit()
        db.refresh(new_channel)

        logger.info(
            f"Channel created: {instance_name} with integration status: {integration_status}"
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating channel {instance_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create channel")

    return channel_to_dict(new_channel)


async def update_channel_integration(
    db: Session,
    channel_id: str,
    external_agent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Link or unlink an agent to an existing channel.
    """

    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    integration_status = "none"
    evoai_config: Optional[Dict[str, Any]] = None
    agent_url: Optional[str] = None
    api_key: str = ""

    # If linking agent
    if external_agent_id:
        # Validate agent exists
        agent = get_agent(db, external_agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Get agent URL
        agent_url = agent.agent_card_url

        # Get decrypted API key
        if agent.api_key_id:
            try:
                api_key = get_decrypted_api_key(db, agent.api_key_id) or ""
            except Exception as decrypt_error:
                logger.error(f"Failed to decrypt API key: {decrypt_error}")
                api_key = ""

        # Configure EvoAI bot
        evolution_service = EvolutionApiService()
        try:
            evoai_result = await evolution_service.create_evoai_bot(
                instance_name=channel.instance_name,
                agent_url=agent_url,
                api_key=api_key,
            )

            bot_id = None
            if evoai_result.get("status") == "success" or evoai_result.get("success"):
                if "data" in evoai_result and isinstance(evoai_result.get("data"), dict):
                    data_obj = evoai_result.get("data", {})
                    if isinstance(data_obj, dict) and "id" in data_obj:
                        bot_id = data_obj.get("id")
                elif "response" in evoai_result and isinstance(
                    evoai_result.get("response"), dict
                ):
                    response_obj = evoai_result.get("response", {})
                    if isinstance(response_obj, dict) and "id" in response_obj:
                        bot_id = response_obj.get("id")
                elif "id" in evoai_result:
                    bot_id = evoai_result.get("id")

                if bot_id:
                    evoai_config = {
                        "bot_id": bot_id,
                        "configured_at": datetime.utcnow().isoformat(),
                        "agent_url": agent_url,
                        "status": "configured",
                    }
                    integration_status = "configured"
                else:
                    integration_status = "error"
                    logger.error(f"No bot_id returned for {channel.instance_name}")
            else:
                integration_status = "error"
                logger.error(
                    f"Evolution-API error for {channel.instance_name}: {evoai_result}"
                )

        except Exception as e:
            logger.error(f"Failed to configure EvoAI bot: {str(e)}")
            integration_status = "error"

        # Update channel
        channel.external_agent_id = external_agent_id
        channel.evoai_config = evoai_config
        channel.integration_status = integration_status

    # If unlinking agent (external_agent_id is None)
    else:
        # Delete EvoAI bot from Evolution-API if exists
        if channel.evoai_config and channel.evoai_config.get("bot_id"):
            evolution_service = EvolutionApiService()
            try:
                await evolution_service.delete_evoai_bot(
                    instance_name=channel.instance_name,
                    evoai_id=channel.evoai_config.get("bot_id"),
                )
                logger.info(
                    f"Deleted EvoAI bot {channel.evoai_config.get('bot_id')} from {channel.instance_name}"
                )
            except Exception as e:
                logger.error(f"Failed to delete EvoAI bot: {str(e)}")

        channel.external_agent_id = None
        channel.evoai_config = None
        channel.integration_status = "none"

    try:
        db.commit()
        db.refresh(channel)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating channel integration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update channel")

    return channel_to_dict(channel)


def channel_to_dict(channel: Channel) -> Dict[str, Any]:
    """Convert Channel model to dictionary with all fields."""
    return {
        "id": str(channel.id),
        "name": channel.name,
        "instance_name": channel.instance_name,
        "channel_type": channel.channel_type,
        "config": channel.config,
        "status": channel.status,
        "client_id": str(channel.client_id) if channel.client_id else None,
        "external_agent_id": str(channel.external_agent_id)
        if channel.external_agent_id
        else None,
        "integration_status": channel.integration_status,
        "evoai_config": channel.evoai_config,
        "created_at": channel.created_at.isoformat() if channel.created_at else None,
        "updated_at": channel.updated_at.isoformat() if channel.updated_at else None,
    }

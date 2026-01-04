"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: channel_service.py                                                 │
│ Channel Service - Business logic for channel management                      │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from sqlalchemy.orm import Session
from src.models.models import Channel, Client
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


def get_client_channels(
    db: Session, 
    client_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[Channel]:
    """
    Get all active channels for a specific client
    
    Args:
        db: Database session
        client_id: Client UUID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Channel objects
    """
    try:
        return db.query(Channel).filter(
            Channel.client_id == client_id,
            Channel.is_active == True
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting client channels: {str(e)}")
        raise


def get_channel_by_instance(db: Session, instance_name: str) -> Optional[Channel]:
    """
    Get channel by instance name
    
    Args:
        db: Database session
        instance_name: Evolution-API instance name
        
    Returns:
        Channel object or None
    """
    try:
        return db.query(Channel).filter(
            Channel.instance_name == instance_name,
            Channel.is_active == True
        ).first()
    except Exception as e:
        logger.error(f"Error getting channel by instance: {str(e)}")
        raise


def create_channel_ownership(
    db: Session, 
    client_id: uuid.UUID, 
    instance_name: str, 
    channel_type: str = "whatsapp",
    config: dict = None
) -> Channel:
    """
    Create channel ownership record
    
    Args:
        db: Database session
        client_id: Client UUID
        instance_name: Evolution-API instance name
        channel_type: Type of channel (whatsapp, instagram, email, sms)
        config: Configuration JSON
        
    Returns:
        Created Channel object
    """
    try:
        channel = Channel(
            client_id=client_id,
            instance_name=instance_name,
            channel_type=channel_type,
            display_name=instance_name,
            config=config or {}
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)
        logger.info(f"Created channel ownership: {instance_name} for client {client_id}")
        return channel
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating channel ownership: {str(e)}")
        raise


def update_channel_status(
    db: Session, 
    instance_name: str, 
    status: str, 
    phone_number: str = None, 
    avatar_url: str = None
) -> Optional[Channel]:
    """
    Update channel status from Evolution-API webhook
    
    Args:
        db: Database session
        instance_name: Evolution-API instance name
        status: New status (connected, disconnected, qr_pending, error)
        phone_number: Phone number (optional)
        avatar_url: Avatar URL (optional)
        
    Returns:
        Updated Channel object or None
    """
    try:
        channel = get_channel_by_instance(db, instance_name)
        if channel:
            channel.status = status
            if phone_number:
                channel.phone_number = phone_number
            if avatar_url:
                channel.avatar_url = avatar_url
            if status == "connected":
                from datetime import datetime
                channel.last_connected_at = datetime.utcnow()
            db.commit()
            db.refresh(channel)
            logger.info(f"Updated channel status: {instance_name} -> {status}")
            return channel
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating channel status: {str(e)}")
        raise


def verify_channel_ownership(
    db: Session, 
    instance_name: str, 
    client_id: uuid.UUID
) -> bool:
    """
    Verify if a channel belongs to a client
    
    Args:
        db: Database session
        instance_name: Evolution-API instance name
        client_id: Client UUID
        
    Returns:
        True if channel belongs to client, False otherwise
    """
    try:
        channel = db.query(Channel).filter(
            Channel.instance_name == instance_name,
            Channel.client_id == client_id,
            Channel.is_active == True
        ).first()
        return channel is not None
    except Exception as e:
        logger.error(f"Error verifying channel ownership: {str(e)}")
        raise


def delete_channel_ownership(
    db: Session, 
    instance_name: str, 
    client_id: uuid.UUID
) -> bool:
    """
    Soft delete channel ownership (mark as inactive)
    
    Args:
        db: Database session
        instance_name: Evolution-API instance name
        client_id: Client UUID
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        channel = db.query(Channel).filter(
            Channel.instance_name == instance_name,
            Channel.client_id == client_id,
            Channel.is_active == True
        ).first()
        
        if channel:
            channel.is_active = False
            db.commit()
            logger.info(f"Deleted channel ownership: {instance_name} for client {client_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting channel ownership: {str(e)}")
        raise


def get_all_channels(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[Channel]:
    """
    Get all active channels (admin only)
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Channel objects
    """
    try:
        return db.query(Channel).filter(
            Channel.is_active == True
        ).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting all channels: {str(e)}")
        raise

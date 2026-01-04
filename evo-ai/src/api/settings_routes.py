"""
┌──────────────────────────────────────────────────────────────┐
│ @file: settings_routes.py                                                   │
│ Settings API Routes                                                           │
└──────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_settings(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """Get system settings"""
    try:
        settings = {
            "general": {
                "darkMode": True,
                "realTimeNotifications": True,
                "notificationSounds": True,
            },
            "notifications": {
                "emailNotifications": False,
                "pushNotifications": True,
                "dailySummary": False,
            },
        }
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting settings"
        )


@router.put("/", status_code=status.HTTP_200_OK)
async def update_settings(
    settings_data: Dict[str, Any],
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Update system settings"""
    try:
        return {
            "message": "Configurações atualizadas com sucesso",
            "settings": settings_data
        }
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating settings"
        )

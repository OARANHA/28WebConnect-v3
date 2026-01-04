"""
┌──────────────────────────────────────────────────────────────────────┐
│ @file: campaigns_routes.py                                                   │
│ Campaigns API Routes                                                           │
└──────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/campaigns",
    tags=["campaigns"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_campaigns(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """List all campaigns"""
    try:
        campaigns = [
            {
                "id": 1,
                "name": "Promoção de Natal",
                "description": "Campanha de promoções de fim de ano",
                "status": "running",
                "type": "whatsapp",
                "recipients": 1250,
                "sent": 875,
                "delivered": 820,
                "opened": 645,
                "scheduled": "2025-01-15 10:00",
            },
            {
                "id": 2,
                "name": "Lançamento de Produto",
                "description": "Anúncio do novo produto premium",
                "status": "scheduled",
                "type": "email",
                "recipients": 3400,
                "sent": 0,
                "delivered": 0,
                "opened": 0,
                "scheduled": "2025-01-20 09:00",
            },
        ]
        return campaigns
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting campaigns"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new campaign"""
    try:
        new_campaign = {
            "id": len(campaign_data) + 1,
            **campaign_data,
            "status": "scheduled",
            "sent": 0,
            "delivered": 0,
            "opened": 0,
        }
        return {
            "message": "Campanha criada com sucesso",
            "campaign": new_campaign
        }
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating campaign"
        )

"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: dashboard_routes.py                                                   │
│ Dashboard API Routes                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_dashboard_stats(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """Get dashboard statistics"""
    try:
        stats = {
            "totalAgents": 24,
            "chatSessions": 1234,
            "activeContacts": 5678,
            "activePipelines": 12,
            "agentGrowth": 2,
            "chatGrowth": 18,
            "contactGrowth": 201,
            "pipelineGrowth": 3,
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting dashboard stats"
        )


@router.get("/activity", status_code=status.HTTP_200_OK)
async def get_dashboard_activity(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """Get dashboard recent activity"""
    try:
        activity = [
            {"action": "Novo agente criado", "time": "Há 2 horas", "user": "João Silva"},
            {"action": "Pipeline 'Vendas' atualizado", "time": "Há 4 horas", "user": "Maria Santos"},
            {"action": "Canal WhatsApp conectado", "time": "Há 6 horas", "user": "Pedro Costa"},
            {"action": "Campanha 'Promoção' iniciada", "time": "Há 1 dia", "user": "Ana Rodrigues"},
        ]
        return activity
    except Exception as e:
        logger.error(f"Error getting dashboard activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting dashboard activity"
        )


@router.get("/charts/chat", status_code=status.HTTP_200_OK)
async def get_chat_chart_data(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """Get chat activity chart data"""
    try:
        data = [
            {"date": "2025-01-09", "sessions": 145},
            {"date": "2025-01-10", "sessions": 189},
            {"date": "2025-01-11", "sessions": 167},
            {"date": "2025-01-12", "sessions": 234},
            {"date": "2025-01-13", "sessions": 198},
            {"date": "2025-01-14", "sessions": 201},
            {"date": "2025-01-15", "sessions": 178},
        ]
        return data
    except Exception as e:
        logger.error(f"Error getting chat chart data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting chat chart data"
        )


@router.get("/charts/contacts", status_code=status.HTTP_200_OK)
async def get_contacts_chart_data(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """Get contacts growth chart data"""
    try:
        data = [
            {"month": "2024-08", "contacts": 4100},
            {"month": "2024-09", "contacts": 4350},
            {"month": "2024-10", "contacts": 4620},
            {"month": "2024-11", "contacts": 4980},
            {"month": "2024-12", "contacts": 5400},
            {"month": "2025-01", "contacts": 5678},
        ]
        return data
    except Exception as e:
        logger.error(f"Error getting contacts chart data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting contacts chart data"
        )

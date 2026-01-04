"""
┌──────────────────────────────────────────────────────────────┐
│ @file: pipelines_routes.py                                                  │
│ Pipelines API Routes                                                          │
└──────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/pipelines",
    tags=["pipelines"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_pipelines(db: Session = Depends(get_db), payload: dict = Depends(get_jwt_token)):
    """List all pipelines"""
    try:
        pipelines = [
            {
                "id": 1,
                "name": "Pipeline de Vendas",
                "description": "Fluxo de atendimento automatizado para vendas",
                "status": "active",
                "lastRun": "Há 2 horas",
                "executions": 156,
            },
            {
                "id": 2,
                "name": "Suporte Técnico",
                "description": "Triagem automática de tickets de suporte",
                "status": "active",
                "lastRun": "Há 30 minutos",
                "executions": 423,
            },
            {
                "id": 3,
                "name": "Onboarding de Novos Clients",
                "description": "Sequência de boas-vindas automatizada",
                "status": "paused",
                "lastRun": "Há 1 dia",
                "executions": 89,
            },
        ]
        return pipelines
    except Exception as e:
        logger.error(f"Error getting pipelines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting pipelines"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new pipeline"""
    try:
        new_pipeline = {
            "id": len(pipeline_data) + 1,
            **pipeline_data,
            "status": "paused",
            "lastRun": "Nunca",
            "executions": 0,
        }
        return {
            "message": "Pipeline criado com sucesso",
            "pipeline": new_pipeline
        }
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating pipeline"
        )

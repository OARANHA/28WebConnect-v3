"""
┌──────────────────────────────────────────────────────────────────────┐
│ @file: tools_routes.py                                                       │
│ Tools API Routes                                                              │
└──────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/tools",
    tags=["tools"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_tools(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """List all tools with optional search"""
    try:
        tools = [
            {
                "id": 1,
                "name": "Calculadora de Preços",
                "description": "Calcula preços baseado em parâmetros personalizados",
                "type": "custom",
                "lastUsed": "Há 2 horas",
                "executions": 156,
                "status": "active",
            },
            {
                "id": 2,
                "name": "Validador de CPF",
                "description": "Valida números de CPF brasileiros",
                "type": "custom",
                "lastUsed": "Há 4 horas",
                "executions": 423,
                "status": "active",
            },
        ]

        # Apply search filter
        if search:
            search_lower = search.lower()
            tools = [
                tool for tool in tools
                if search_lower in tool["name"].lower()
                or search_lower in tool["description"].lower()
            ]

        return tools
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting tools"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new tool"""
    try:
        new_tool = {
            "id": len(tool_data) + 1,
            **tool_data,
            "lastUsed": "Nunca",
            "executions": 0,
            "status": "inactive",
        }
        return {
            "message": "Ferramenta criada com sucesso",
            "tool": new_tool
        }
    except Exception as e:
        logger.error(f"Error creating tool: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating tool"
        )

"""
┌──────────────────────────────────────────────────────────────┐
│ @file: audit_routes.py                                                     │
│ Audit API Routes                                                             │
└──────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/audit",
    tags=["audit"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_audit_logs(
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """List all audit logs with optional filters"""
    try:
        logs = [
            {
                "id": 1,
                "action": "Criou novo agente",
                "entity": "Agent: Assistente de Vendas",
                "user": "João Silva",
                "timestamp": "2025-01-15 14:32:15",
                "type": "create",
                "ip": "192.168.1.100",
            },
            {
                "id": 2,
                "action": "Atualizou configuração",
                "entity": "Settings: Webhook URL",
                "user": "Maria Santos",
                "timestamp": "2025-01-15 14:28:42",
                "type": "update",
                "ip": "192.168.1.101",
            },
            {
                "id": 3,
                "action": "Deletou contato",
                "entity": "Contact: Test User",
                "user": "Pedro Costa",
                "timestamp": "2025-01-15 14:15:30",
                "type": "delete",
                "ip": "192.168.1.102",
            },
            {
                "id": 4,
                "action": "Falha de autenticação",
                "entity": "Auth: Login",
                "user": "unknown",
                "timestamp": "2025-01-15 13:45:11",
                "type": "security",
                "ip": "203.0.113.42",
            },
        ]

        # Apply search filter
        if search:
            search_lower = search.lower()
            logs = [
                log for log in logs
                if search_lower in log["action"].lower()
                or search_lower in log["user"].lower()
                or search_lower in log["entity"].lower()
            ]

        # Apply type filter
        if type:
            logs = [log for log in logs if log["type"] == type]

        return {
            "logs": logs,
            "total": len(logs)
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting audit logs"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    log_data: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new audit log entry"""
    try:
        new_log = {
            "id": len(log_data) + 1,
            **log_data,
            "timestamp": new_log_data.get("timestamp"),
        }

        return {
            "message": "Log de auditoria criado",
            "log": new_log
        }
    except Exception as e:
        logger.error(f"Error creating audit log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating audit log"
        )

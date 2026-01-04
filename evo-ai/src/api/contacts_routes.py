"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: contacts_routes.py                                                   │
│ Contacts API Routes                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/contacts",
    tags=["contacts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_contacts(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """List all contacts with optional search"""
    try:
        contacts = [
            {
                "id": 1,
                "name": "João Silva",
                "phone": "+55 11 98765-4321",
                "email": "joao.silva@email.com",
                "tags": ["cliente-vip", "recorrente"],
                "lastContact": "Há 2 horas",
                "messages": 45,
            },
            {
                "id": 2,
                "name": "Maria Santos",
                "phone": "+55 11 12345-6789",
                "email": "maria.santos@email.com",
                "tags": ["lead", "prospecção"],
                "lastContact": "Há 1 dia",
                "messages": 23,
            },
        ]

        # Apply search filter
        if search:
            search_lower = search.lower()
            contacts = [
                contact for contact in contacts
                if search_lower in contact["name"].lower()
                or search_lower in contact["email"].lower()
                or search in contact["phone"]
            ]

        return contacts
    except Exception as e:
        logger.error(f"Error getting contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting contacts"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token)
):
    """Create a new contact"""
    try:
        new_contact = {
            "id": len(contact_data) + 1,
            **contact_data,
            "lastContact": "Agora",
            "messages": 0,
        }
        return {
            "message": "Contato criado com sucesso",
            "contact": new_contact
        }
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating contact"
        )

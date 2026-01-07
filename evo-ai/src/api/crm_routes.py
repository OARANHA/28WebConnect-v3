"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes (Original) / OARANHA (CRM Routes)                    │
│ @file: crm_routes.py                                                         │
│ CRM API Routes - Endpoints para gerenciamento de CRM                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ @description:                                                                 │
│ Rotas RESTful para:                                                           │
│ - Gerenciamento de Leads                                                    │
│ - Gerenciamento de Contatos                                                 │
│ - Gerenciamento de Pipelines                                                │
│ - Gerenciamento de Deals                                                    │
│ - Kanban Board                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token
from src.services.audit_service import create_audit_log
from src.services.crm_service import CRMService
from src.schemas.crm_schemas import (
    LeadCreateRequest,
    LeadUpdateRequest,
    LeadResponse,
    ContactCreateRequest,
    ContactUpdateRequest,
    ContactResponse,
    PipelineCreateRequest,
    PipelineUpdateRequest,
    PipelineResponse,
    DealCreateRequest,
    DealUpdateRequest,
    DealResponse,
    KanbanCardCreateRequest,
    KanbanCardUpdateRequest,
    KanbanCardResponse,
    PaginatedResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/crm",
    tags=["crm"],
    responses={404: {"description": "Not found"}},
)


# ═══════════════════════════════════════════════════════════════════════════
# LEADS
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/leads", status_code=status.HTTP_200_OK)
async def list_leads(
    page: int = Query(1, ge=1, description="Página (começa em 1)"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    search: Optional[str] = Query(None, description="Buscar por nome, email, etc"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Listar todos os leads com filtros e paginação"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado no token",
            )

        leads, total = CRMService.list_leads(
            db,
            client_id=UUID(client_id),
            page=page,
            limit=limit,
            status=status,
            search=search,
        )

        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "list",
                "crm_lead",
                details={"page": page, "limit": limit, "total": total, "count": len(leads)},
            )
        except Exception:
            pass

        return {
            "data": [LeadResponse.model_validate(lead) for lead in leads],
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": (page * limit) < total,
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar leads",
        )


@router.post("/leads", status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✨ Criar novo lead"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado no token",
            )

        lead = CRMService.create_lead(
            db, client_id=UUID(client_id), data=lead_data.model_dump()
        )

        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "create",
                "crm_lead",
                resource_id=str(lead.id),
                details={"name": lead.name, "email": lead.email},
            )
        except Exception:
            pass

        return LeadResponse.model_validate(lead)
    except Exception as e:
        logger.error(f"❌ Erro ao criar lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar lead",
        )


@router.get("/leads/{lead_id}", status_code=status.HTTP_200_OK)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🔍 Obter detalhes de um lead"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado no token",
            )

        lead = CRMService.get_lead(db, lead_id=lead_id, client_id=UUID(client_id))
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead não encontrado",
            )

        return LeadResponse.model_validate(lead)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar lead",
        )


@router.put("/leads/{lead_id}", status_code=status.HTTP_200_OK)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✏️  Atualizar um lead"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado no token",
            )

        lead = CRMService.update_lead(
            db,
            lead_id=lead_id,
            client_id=UUID(client_id),
            data=lead_data.model_dump(exclude_none=True),
        )
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead não encontrado",
            )

        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "update",
                "crm_lead",
                resource_id=str(lead.id),
                details={"updated_fields": list(lead_data.model_dump(exclude_none=True).keys())},
            )
        except Exception:
            pass

        return LeadResponse.model_validate(lead)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar lead",
        )


@router.delete("/leads/{lead_id}", status_code=status.HTTP_200_OK)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🗑️  Deletar um lead"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado no token",
            )

        deleted = CRMService.delete_lead(db, lead_id=lead_id, client_id=UUID(client_id))
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead não encontrado",
            )

        try:
            create_audit_log(
                db,
                payload.get("user_id") or payload.get("sub"),
                "delete",
                "crm_lead",
                resource_id=str(lead_id),
            )
        except Exception:
            pass

        return {"message": "Lead deletado com sucesso", "id": str(lead_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar lead",
        )


# ═══════════════════════════════════════════════════════════════════════════
# CONTACTS
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/contacts", status_code=status.HTTP_200_OK)
async def list_contacts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Listar todos os contatos"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        contacts, total = CRMService.list_contacts(
            db,
            client_id=UUID(client_id),
            page=page,
            limit=limit,
            search=search,
        )

        return {
            "data": [ContactResponse.model_validate(contact) for contact in contacts],
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": (page * limit) < total,
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar contatos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar contatos",
        )


@router.post("/contacts", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✨ Criar novo contato"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        contact = CRMService.create_contact(
            db, client_id=UUID(client_id), data=contact_data.model_dump()
        )

        return ContactResponse.model_validate(contact)
    except Exception as e:
        logger.error(f"❌ Erro ao criar contato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar contato",
        )


@router.get("/contacts/{contact_id}", status_code=status.HTTP_200_OK)
async def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🔍 Obter detalhes de um contato"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        contact = CRMService.get_contact(db, contact_id=contact_id, client_id=UUID(client_id))
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contato não encontrado",
            )

        return ContactResponse.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar contato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar contato",
        )


@router.put("/contacts/{contact_id}", status_code=status.HTTP_200_OK)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✏️  Atualizar um contato"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        contact = CRMService.update_contact(
            db,
            contact_id=contact_id,
            client_id=UUID(client_id),
            data=contact_data.model_dump(exclude_none=True),
        )
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contato não encontrado",
            )

        return ContactResponse.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar contato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar contato",
        )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_200_OK)
async def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🗑️  Deletar um contato"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deleted = CRMService.delete_contact(db, contact_id=contact_id, client_id=UUID(client_id))
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contato não encontrado",
            )

        return {"message": "Contato deletado com sucesso", "id": str(contact_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar contato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar contato",
        )


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINES
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/pipelines", status_code=status.HTTP_200_OK)
async def list_pipelines(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Listar todos os pipelines"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        pipelines, total = CRMService.list_pipelines(
            db,
            client_id=UUID(client_id),
            page=page,
            limit=limit,
        )

        return {
            "data": [PipelineResponse.model_validate(p) for p in pipelines],
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": (page * limit) < total,
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar pipelines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar pipelines",
        )


@router.post("/pipelines", status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✨ Criar novo pipeline"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        pipeline = CRMService.create_pipeline(
            db, client_id=UUID(client_id), data=pipeline_data.model_dump()
        )

        return PipelineResponse.model_validate(pipeline)
    except Exception as e:
        logger.error(f"❌ Erro ao criar pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar pipeline",
        )


@router.get("/pipelines/{pipeline_id}", status_code=status.HTTP_200_OK)
async def get_pipeline(
    pipeline_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🔍 Obter detalhes de um pipeline"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        pipeline = CRMService.get_pipeline(
            db, pipeline_id=pipeline_id, client_id=UUID(client_id)
        )
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline não encontrado",
            )

        return PipelineResponse.model_validate(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar pipeline",
        )


@router.put("/pipelines/{pipeline_id}", status_code=status.HTTP_200_OK)
async def update_pipeline(
    pipeline_id: UUID,
    pipeline_data: PipelineUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✏️  Atualizar um pipeline"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        pipeline = CRMService.update_pipeline(
            db,
            pipeline_id=pipeline_id,
            client_id=UUID(client_id),
            data=pipeline_data.model_dump(exclude_none=True),
        )
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline não encontrado",
            )

        return PipelineResponse.model_validate(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar pipeline",
        )


# ═══════════════════════════════════════════════════════════════════════════
# DEALS
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/deals", status_code=status.HTTP_200_OK)
async def list_deals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    pipeline_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Listar todos os deals"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deals, total = CRMService.list_deals(
            db,
            client_id=UUID(client_id),
            page=page,
            limit=limit,
            pipeline_id=UUID(pipeline_id) if pipeline_id else None,
            stage=stage,
            search=search,
        )

        return {
            "data": [DealResponse.model_validate(deal) for deal in deals],
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": (page * limit) < total,
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar deals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar deals",
        )


@router.post("/deals", status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✨ Criar novo deal"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deal = CRMService.create_deal(
            db, client_id=UUID(client_id), data=deal_data.model_dump()
        )

        return DealResponse.model_validate(deal)
    except Exception as e:
        logger.error(f"❌ Erro ao criar deal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar deal",
        )


@router.get("/deals/{deal_id}", status_code=status.HTTP_200_OK)
async def get_deal(
    deal_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🔍 Obter detalhes de um deal"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deal = CRMService.get_deal(db, deal_id=deal_id, client_id=UUID(client_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal não encontrado",
            )

        return DealResponse.model_validate(deal)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar deal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar deal",
        )


@router.put("/deals/{deal_id}", status_code=status.HTTP_200_OK)
async def update_deal(
    deal_id: UUID,
    deal_data: DealUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✏️  Atualizar um deal"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deal = CRMService.update_deal(
            db,
            deal_id=deal_id,
            client_id=UUID(client_id),
            data=deal_data.model_dump(exclude_none=True),
        )
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal não encontrado",
            )

        return DealResponse.model_validate(deal)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar deal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar deal",
        )


@router.delete("/deals/{deal_id}", status_code=status.HTTP_200_OK)
async def delete_deal(
    deal_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🗑️  Deletar um deal"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deleted = CRMService.delete_deal(db, deal_id=deal_id, client_id=UUID(client_id))
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal não encontrado",
            )

        return {"message": "Deal deletado com sucesso", "id": str(deal_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar deal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar deal",
        )


# ═══════════════════════════════════════════════════════════════════════════
# KANBAN
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/kanban", status_code=status.HTTP_200_OK)
async def list_kanban_cards(
    pipeline_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Listar cards do kanban"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        cards = CRMService.list_kanban_cards(
            db,
            client_id=UUID(client_id),
            pipeline_id=UUID(pipeline_id) if pipeline_id else None,
        )

        return {
            "data": [KanbanCardResponse.model_validate(card) for card in cards],
            "total": len(cards),
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar kanban cards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar kanban cards",
        )


@router.post("/kanban", status_code=status.HTTP_201_CREATED)
async def create_kanban_card(
    card_data: KanbanCardCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✨ Criar card no kanban"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        card = CRMService.create_kanban_card(
            db, client_id=UUID(client_id), data=card_data.model_dump()
        )

        return KanbanCardResponse.model_validate(card)
    except Exception as e:
        logger.error(f"❌ Erro ao criar kanban card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar kanban card",
        )


@router.get("/kanban/{card_id}", status_code=status.HTTP_200_OK)
async def get_kanban_card(
    card_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🔍 Obter detalhes de um kanban card"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        card = CRMService.get_kanban_card(db, card_id=card_id, client_id=UUID(client_id))
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kanban card não encontrado",
            )

        return KanbanCardResponse.model_validate(card)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar kanban card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar kanban card",
        )


@router.put("/kanban/{card_id}", status_code=status.HTTP_200_OK)
async def update_kanban_card(
    card_id: UUID,
    card_data: KanbanCardUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """✏️  Atualizar um kanban card"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        card = CRMService.update_kanban_card(
            db,
            card_id=card_id,
            client_id=UUID(client_id),
            data=card_data.model_dump(exclude_none=True),
        )
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kanban card não encontrado",
            )

        return KanbanCardResponse.model_validate(card)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar kanban card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar kanban card",
        )


@router.delete("/kanban/{card_id}", status_code=status.HTTP_200_OK)
async def delete_kanban_card(
    card_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """🗑️  Deletar um kanban card"""
    try:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id não encontrado",
            )

        deleted = CRMService.delete_kanban_card(
            db, card_id=card_id, client_id=UUID(client_id)
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kanban card não encontrado",
            )

        return {"message": "Kanban card deletado com sucesso", "id": str(card_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar kanban card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar kanban card",
        )

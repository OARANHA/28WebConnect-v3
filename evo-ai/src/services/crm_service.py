"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes (Original) / OARANHA (CRM Service)                   │
│ @file: crm_service.py                                                        │
│ CRM Service: Lógica de negócio para CRM                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ @description:                                                                 │
│ Serviço centralizado para todas as operações de CRM                          │
│ - Gerenciamento de leads                                                    │
│ - Gerenciamento de contatos                                                 │
│ - Gerenciamento de pipelines e deals                                        │
│ - Kanban board                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
"""

import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.models.crm_models import (
    Lead,
    Contact,
    Pipeline,
    Deal,
    KanbanCard,
)

logger = logging.getLogger(__name__)


class CRMService:
    """
    Serviço centralizado para gerenciamento de CRM.
    Encapsula toda a lógica de negócio para leads, contatos, deals e kanban.
    """

    # ════════════════════════════════
    # LEADS
    # ════════════════════════════════

    @staticmethod
    def create_lead(db: Session, client_id: UUID, data: Dict[str, Any]) -> Lead:
        """✨ Criar novo lead"""
        logger.info(f"✨ Criando novo lead para cliente {client_id}")
        lead = Lead(
            client_id=client_id,
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            company=data.get("company"),
            source=data.get("source"),
            status=data.get("status", "novo"),
            value=data.get("value", 0.0),
            description=data.get("description"),
            tags=data.get("tags", []),
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        logger.info(f"✅ Lead '{lead.name}' criado com ID {lead.id}")
        return lead

    @staticmethod
    def get_lead(db: Session, lead_id: UUID, client_id: UUID) -> Optional[Lead]:
        """🔍 Buscar lead por ID"""
        return db.query(Lead).filter(
            and_(Lead.id == lead_id, Lead.client_id == client_id)
        ).first()

    @staticmethod
    def list_leads(
        db: Session,
        client_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Lead], int]:
        """📑 Listar leads com filtros"""
        query = db.query(Lead).filter(Lead.client_id == client_id)

        if status:
            query = query.filter(Lead.status == status)

        if search:
            query = query.filter(
                or_(
                    Lead.name.ilike(f"%{search}%"),
                    Lead.email.ilike(f"%{search}%"),
                    Lead.phone.ilike(f"%{search}%"),
                    Lead.company.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        leads = (
            query.order_by(desc(Lead.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return leads, total

    @staticmethod
    def update_lead(
        db: Session, lead_id: UUID, client_id: UUID, data: Dict[str, Any]
    ) -> Optional[Lead]:
        """✏️  Atualizar lead"""
        lead = CRMService.get_lead(db, lead_id, client_id)
        if not lead:
            return None

        logger.info(f"✍️  Atualizando lead {lead_id}")
        for key, value in data.items():
            if value is not None and hasattr(lead, key):
                setattr(lead, key, value)

        db.commit()
        db.refresh(lead)
        logger.info(f"✅ Lead {lead_id} atualizado")
        return lead

    @staticmethod
    def delete_lead(db: Session, lead_id: UUID, client_id: UUID) -> bool:
        """🗑️  Deletar lead"""
        lead = CRMService.get_lead(db, lead_id, client_id)
        if not lead:
            return False

        logger.info(f"🗑️  Deletando lead {lead_id}")
        db.delete(lead)
        db.commit()
        logger.info(f"✅ Lead {lead_id} deletado")
        return True

    # ════════════════════════════════
    # CONTACTS
    # ════════════════════════════════

    @staticmethod
    def create_contact(db: Session, client_id: UUID, data: Dict[str, Any]) -> Contact:
        """✨ Criar novo contato"""
        logger.info(f"✨ Criando novo contato para cliente {client_id}")
        contact = Contact(
            client_id=client_id,
            lead_id=data.get("lead_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            company=data.get("company"),
            department=data.get("department"),
            position=data.get("position"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            country=data.get("country"),
            notes=data.get("notes"),
            social_media=data.get("social_media", {}),
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        logger.info(f"✅ Contato '{contact.first_name}' criado com ID {contact.id}")
        return contact

    @staticmethod
    def get_contact(db: Session, contact_id: UUID, client_id: UUID) -> Optional[Contact]:
        """🔍 Buscar contato por ID"""
        return db.query(Contact).filter(
            and_(Contact.id == contact_id, Contact.client_id == client_id)
        ).first()

    @staticmethod
    def list_contacts(
        db: Session,
        client_id: UUID,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[Contact], int]:
        """📑 Listar contatos com filtros"""
        query = db.query(Contact).filter(Contact.client_id == client_id)

        if search:
            query = query.filter(
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.phone.ilike(f"%{search}%"),
                    Contact.company.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        contacts = (
            query.order_by(desc(Contact.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return contacts, total

    @staticmethod
    def update_contact(
        db: Session, contact_id: UUID, client_id: UUID, data: Dict[str, Any]
    ) -> Optional[Contact]:
        """✏️  Atualizar contato"""
        contact = CRMService.get_contact(db, contact_id, client_id)
        if not contact:
            return None

        logger.info(f"✍️  Atualizando contato {contact_id}")
        for key, value in data.items():
            if value is not None and hasattr(contact, key):
                setattr(contact, key, value)

        db.commit()
        db.refresh(contact)
        logger.info(f"✅ Contato {contact_id} atualizado")
        return contact

    @staticmethod
    def delete_contact(db: Session, contact_id: UUID, client_id: UUID) -> bool:
        """🗑️  Deletar contato"""
        contact = CRMService.get_contact(db, contact_id, client_id)
        if not contact:
            return False

        logger.info(f"🗑️  Deletando contato {contact_id}")
        db.delete(contact)
        db.commit()
        logger.info(f"✅ Contato {contact_id} deletado")
        return True

    # ════════════════════════════════
    # PIPELINES
    # ════════════════════════════════

    @staticmethod
    def create_pipeline(
        db: Session, client_id: UUID, data: Dict[str, Any]
    ) -> Pipeline:
        """✨ Criar novo pipeline"""
        logger.info(f"✨ Criando novo pipeline para cliente {client_id}")
        pipeline = Pipeline(
            client_id=client_id,
            name=data.get("name"),
            description=data.get("description"),
            stages=data.get("stages"),  # Se None, usa default
            order=data.get("order", 0),
        )
        db.add(pipeline)
        db.commit()
        db.refresh(pipeline)
        logger.info(f"✅ Pipeline '{pipeline.name}' criado com ID {pipeline.id}")
        return pipeline

    @staticmethod
    def get_pipeline(
        db: Session, pipeline_id: UUID, client_id: UUID
    ) -> Optional[Pipeline]:
        """🔍 Buscar pipeline por ID"""
        return db.query(Pipeline).filter(
            and_(Pipeline.id == pipeline_id, Pipeline.client_id == client_id)
        ).first()

    @staticmethod
    def list_pipelines(
        db: Session,
        client_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[List[Pipeline], int]:
        """📑 Listar pipelines"""
        query = db.query(Pipeline).filter(
            and_(Pipeline.client_id == client_id, Pipeline.is_active == True)
        )

        total = query.count()
        pipelines = (
            query.order_by(Pipeline.order)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return pipelines, total

    @staticmethod
    def update_pipeline(
        db: Session, pipeline_id: UUID, client_id: UUID, data: Dict[str, Any]
    ) -> Optional[Pipeline]:
        """✏️  Atualizar pipeline"""
        pipeline = CRMService.get_pipeline(db, pipeline_id, client_id)
        if not pipeline:
            return None

        logger.info(f"✍️  Atualizando pipeline {pipeline_id}")
        for key, value in data.items():
            if value is not None and hasattr(pipeline, key):
                setattr(pipeline, key, value)

        db.commit()
        db.refresh(pipeline)
        logger.info(f"✅ Pipeline {pipeline_id} atualizado")
        return pipeline

    # ════════════════════════════════
    # DEALS
    # ════════════════════════════════

    @staticmethod
    def create_deal(db: Session, client_id: UUID, data: Dict[str, Any]) -> Deal:
        """✨ Criar novo deal"""
        logger.info(f"✨ Criando novo deal para cliente {client_id}")
        deal = Deal(
            client_id=client_id,
            pipeline_id=data.get("pipeline_id"),
            contact_id=data.get("contact_id"),
            title=data.get("title"),
            description=data.get("description"),
            value=data.get("value"),
            probability=data.get("probability", 50),
            expected_close_date=data.get("expected_close_date"),
            stage=data.get("stage"),
            owner_id=data.get("owner_id"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
        db.add(deal)
        db.commit()
        db.refresh(deal)
        logger.info(f"✅ Deal '{deal.title}' criado com ID {deal.id}")
        return deal

    @staticmethod
    def get_deal(db: Session, deal_id: UUID, client_id: UUID) -> Optional[Deal]:
        """🔍 Buscar deal por ID"""
        return db.query(Deal).filter(
            and_(Deal.id == deal_id, Deal.client_id == client_id)
        ).first()

    @staticmethod
    def list_deals(
        db: Session,
        client_id: UUID,
        page: int = 1,
        limit: int = 20,
        pipeline_id: Optional[UUID] = None,
        stage: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Deal], int]:
        """📑 Listar deals com filtros"""
        query = db.query(Deal).filter(Deal.client_id == client_id)

        if pipeline_id:
            query = query.filter(Deal.pipeline_id == pipeline_id)

        if stage:
            query = query.filter(Deal.stage == stage)

        if search:
            query = query.filter(Deal.title.ilike(f"%{search}%"))

        total = query.count()
        deals = (
            query.order_by(desc(Deal.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return deals, total

    @staticmethod
    def update_deal(
        db: Session, deal_id: UUID, client_id: UUID, data: Dict[str, Any]
    ) -> Optional[Deal]:
        """✏️  Atualizar deal"""
        deal = CRMService.get_deal(db, deal_id, client_id)
        if not deal:
            return None

        logger.info(f"✍️  Atualizando deal {deal_id}")
        for key, value in data.items():
            if value is not None and hasattr(deal, key):
                setattr(deal, key, value)

        db.commit()
        db.refresh(deal)
        logger.info(f"✅ Deal {deal_id} atualizado")
        return deal

    @staticmethod
    def delete_deal(db: Session, deal_id: UUID, client_id: UUID) -> bool:
        """🗑️  Deletar deal"""
        deal = CRMService.get_deal(db, deal_id, client_id)
        if not deal:
            return False

        logger.info(f"🗑️  Deletando deal {deal_id}")
        db.delete(deal)
        db.commit()
        logger.info(f"✅ Deal {deal_id} deletado")
        return True

    # ════════════════════════════════
    # KANBAN CARDS
    # ════════════════════════════════

    @staticmethod
    def create_kanban_card(
        db: Session, client_id: UUID, data: Dict[str, Any]
    ) -> KanbanCard:
        """✨ Criar card no kanban"""
        logger.info(f"✨ Criando kanban card para cliente {client_id}")
        card = KanbanCard(
            client_id=client_id,
            deal_id=data.get("deal_id"),
            title=data.get("title"),
            column=data.get("column"),
            position=data.get("position", 0),
            metadata=data.get("metadata", {}),
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        logger.info(f"✅ Kanban card criado com ID {card.id}")
        return card

    @staticmethod
    def get_kanban_card(
        db: Session, card_id: UUID, client_id: UUID
    ) -> Optional[KanbanCard]:
        """🔍 Buscar kanban card"""
        return db.query(KanbanCard).filter(
            and_(KanbanCard.id == card_id, KanbanCard.client_id == client_id)
        ).first()

    @staticmethod
    def list_kanban_cards(
        db: Session,
        client_id: UUID,
        pipeline_id: Optional[UUID] = None,
    ) -> List[KanbanCard]:
        """📑 Listar cards do kanban"""
        query = db.query(KanbanCard).filter(KanbanCard.client_id == client_id)

        if pipeline_id:
            # Filtrar por deals do pipeline
            query = query.join(Deal).filter(Deal.pipeline_id == pipeline_id)

        return query.order_by(KanbanCard.position).all()

    @staticmethod
    def update_kanban_card(
        db: Session, card_id: UUID, client_id: UUID, data: Dict[str, Any]
    ) -> Optional[KanbanCard]:
        """✏️  Atualizar kanban card"""
        card = CRMService.get_kanban_card(db, card_id, client_id)
        if not card:
            return None

        logger.info(f"✍️  Atualizando kanban card {card_id}")
        for key, value in data.items():
            if value is not None and hasattr(card, key):
                setattr(card, key, value)

        db.commit()
        db.refresh(card)
        logger.info(f"✅ Kanban card {card_id} atualizado")
        return card

    @staticmethod
    def delete_kanban_card(db: Session, card_id: UUID, client_id: UUID) -> bool:
        """🗑️  Deletar kanban card"""
        card = CRMService.get_kanban_card(db, card_id, client_id)
        if not card:
            return False

        logger.info(f"🗑️  Deletando kanban card {card_id}")
        db.delete(card)
        db.commit()
        logger.info(f"✅ Kanban card {card_id} deletado")
        return True

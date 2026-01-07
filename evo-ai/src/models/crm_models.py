"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes (Original) / OARANHA (CRM Implementation)            │
│ @file: crm_models.py                                                         │
│ CRM Models: Leads, Contatos, Deals, Kanban                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ @description:                                                                 │
│ Modelos de dados para gerenciamento de CRM                                   │
│ - Lead: Contatos prospecto                                                   │
│ - Contact: Contatos gerais                                                   │
│ - Deal: Negócios/Oportunidades                                               │
│ - Pipeline: Estágios de vendas                                               │
│ - KanbanBoard: Quadro visual com cards                                        │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from sqlalchemy import (
    Column,
    String,
    UUID,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    CheckConstraint,
    Boolean,
    Float,
    Integer,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from src.config.database import Base
import uuid


class Lead(Base):
    """
    Modelo para representar leads/prospectos no CRM.
    
    Campos:
    - id: UUID único do lead
    - client_id: Referência ao cliente
    - name: Nome do prospect
    - email: Email do prospect
    - phone: Telefone do prospect
    - company: Empresa do prospect
    - source: Origem do lead (website, referência, etc)
    - status: Status atual (novo, qualificado, proposta enviada, etc)
    - value: Valor estimado da oportunidade
    - description: Descrições/Notas sobre o lead
    - tags: Tags para categorização
    - contact_date: Data do último contato
    - created_at: Data de criação
    - updated_at: Data de última atualização
    """
    __tablename__ = "crm_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    company = Column(String(255), nullable=True)
    source = Column(String(100), nullable=True)  # website, referência, ads, etc
    status = Column(
        String(50),
        nullable=False,
        default="novo",
        index=True
    )  # novo, qualificado, proposta_enviada, convertido, perdido
    value = Column(Float, nullable=True, default=0.0)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=[], nullable=False)  # ["tag1", "tag2"]
    contact_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="crm_leads")

    __table_args__ = (
        CheckConstraint(
            "status IN ('novo', 'qualificado', 'proposta_enviada', 'convertido', 'perdido')",
            name="check_lead_status",
        ),
    )


class Contact(Base):
    """
    Modelo para representar contatos gerais no CRM.
    
    Campos:
    - id: UUID único do contato
    - client_id: Referência ao cliente
    - lead_id: Referência ao lead associado (opcional)
    - first_name: Primeiro nome
    - last_name: Sobrenome
    - email: Email do contato
    - phone: Telefone do contato
    - company: Empresa do contato
    - department: Departamento na empresa
    - position: Cargo/Posição
    - address: Endereço
    - city: Cidade
    - state: Estado/Provincia
    - zip_code: CEP
    - country: País
    - notes: Notas gerais
    - social_media: Links de redes sociais
    - created_at: Data de criação
    - updated_at: Data de última atualização
    """
    __tablename__ = "crm_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    lead_id = Column(
        UUID(as_uuid=True), ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True
    )
    first_name = Column(String(255), nullable=False, index=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(255), nullable=True, index=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    social_media = Column(JSON, default={}, nullable=False)  # {"linkedin": "url", "twitter": "url"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="crm_contacts")
    lead = relationship("Lead", backref="contacts")


class Pipeline(Base):
    """
    Modelo para representar pipelines/estágios de vendas.
    
    Campos:
    - id: UUID único
    - client_id: Referência ao cliente
    - name: Nome do pipeline (ex: "Vendas", "Suporte")
    - description: Descrição do pipeline
    - stages: JSON com array de estágios e suas cores/ordem
    - order: Ordem de exibição
    - is_active: Se está ativo ou arquivado
    - created_at: Data de criação
    - updated_at: Data de última atualização
    """
    __tablename__ = "crm_pipelines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stages = Column(
        JSON,
        default=[
            {"id": "novo", "name": "Novo", "color": "#3B82F6"},
            {"id": "qualificado", "name": "Qualificado", "color": "#10B981"},
            {"id": "proposta", "name": "Proposta Enviada", "color": "#F59E0B"},
            {"id": "negociacao", "name": "Negociação", "color": "#8B5CF6"},
            {"id": "fechado", "name": "Fechado", "color": "#059669"},
        ],
        nullable=False,
    )
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="crm_pipelines")
    deals = relationship("Deal", back_populates="pipeline", cascade="all, delete-orphan")


class Deal(Base):
    """
    Modelo para representar deals/negócios/oportunidades.
    
    Campos:
    - id: UUID único do deal
    - client_id: Referência ao cliente
    - pipeline_id: Referência ao pipeline
    - contact_id: Referência ao contato
    - title: Título do negócio
    - description: Descrição do negócio
    - value: Valor do deal
    - probability: Probabilidade de fechamento (0-100)
    - expected_close_date: Data esperada de fechamento
    - stage: Estágio atual no pipeline
    - owner_id: ID do responsável (user_id)
    - tags: Tags para categorização
    - metadata: Dados customizados em JSON
    - created_at: Data de criação
    - updated_at: Data de última atualização
    """
    __tablename__ = "crm_deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    pipeline_id = Column(
        UUID(as_uuid=True), ForeignKey("crm_pipelines.id", ondelete="CASCADE"), nullable=False
    )
    contact_id = Column(
        UUID(as_uuid=True), ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True
    )
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    value = Column(Float, nullable=False, default=0.0)
    probability = Column(Integer, default=50)  # 0-100
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    stage = Column(String(100), nullable=False, index=True)  # Referência ao stage.id do pipeline
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    tags = Column(JSON, default=[], nullable=False)
    metadata = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="crm_deals")
    pipeline = relationship("Pipeline", back_populates="deals")
    contact = relationship("Contact", backref="deals")
    owner = relationship("User", backref="crm_deals")


class KanbanCard(Base):
    """
    Modelo para representar cards do Kanban (normalmente linked a Deals).
    
    Campos:
    - id: UUID único
    - deal_id: Referência ao deal
    - client_id: Referência ao cliente
    - title: Título do card
    - column: Coluna do kanban (referência ao stage)
    - position: Posição na coluna (order)
    - metadata: Dados adicionais (attachments, checklists, etc)
    - created_at: Data de criação
    - updated_at: Data de última atualização
    """
    __tablename__ = "crm_kanban_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(
        UUID(as_uuid=True), ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=False
    )
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False)
    column = Column(String(100), nullable=False, index=True)  # Stage ID
    position = Column(Integer, default=0)
    metadata = Column(JSON, default={}, nullable=False)  # attachments, checklists, etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="crm_kanban_cards")
    deal = relationship("Deal", backref="kanban_cards")

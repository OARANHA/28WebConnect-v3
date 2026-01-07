"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes (Original) / OARANHA (CRM Implementation)            │
│ @file: crm_schemas.py                                                        │
│ CRM Schemas: Pydantic models para validação                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ @description:                                                                 │
│ Schemas Pydantic para Request/Response de CRM                               │
│ Incluindo validações, tipos e documentação                                   │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ═══════════════════════════════════════════════════════════════════════════
# LEADS
# ═══════════════════════════════════════════════════════════════════════════

class LeadCreateRequest(BaseModel):
    """Schema para criar um novo lead"""
    name: str = Field(..., min_length=1, max_length=255, description="Nome do prospect")
    email: Optional[str] = Field(None, description="Email do prospect")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone do prospect")
    company: Optional[str] = Field(None, max_length=255, description="Empresa do prospect")
    source: Optional[str] = Field(None, description="Origem do lead (website, referência, ads, etc)")
    status: Optional[str] = Field(
        "novo",
        description="Status do lead (novo, qualificado, proposta_enviada, convertido, perdido)"
    )
    value: Optional[float] = Field(0.0, description="Valor estimado da oportunidade")
    description: Optional[str] = Field(None, description="Notas/Descrição do lead")
    tags: Optional[List[str]] = Field([], description="Tags para categorização")

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['novo', 'qualificado', 'proposta_enviada', 'convertido', 'perdido']
        if v not in valid_statuses:
            raise ValueError(f'Status deve ser um de: {valid_statuses}')
        return v


class LeadUpdateRequest(BaseModel):
    """Schema para atualizar um lead"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome do prospect")
    email: Optional[str] = Field(None, description="Email do prospect")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone do prospect")
    company: Optional[str] = Field(None, max_length=255, description="Empresa do prospect")
    source: Optional[str] = Field(None, description="Origem do lead")
    status: Optional[str] = Field(None, description="Status do lead")
    value: Optional[float] = Field(None, description="Valor estimado")
    description: Optional[str] = Field(None, description="Notas/Descrição")
    tags: Optional[List[str]] = Field(None, description="Tags")


class LeadResponse(BaseModel):
    """Schema de resposta para lead"""
    id: UUID
    client_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    source: Optional[str]
    status: str
    value: float
    description: Optional[str]
    tags: List[str]
    contact_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# CONTACTS
# ═══════════════════════════════════════════════════════════════════════════

class ContactCreateRequest(BaseModel):
    """Schema para criar um novo contato"""
    first_name: str = Field(..., min_length=1, max_length=255, description="Primeiro nome")
    last_name: Optional[str] = Field(None, max_length=255, description="Sobrenome")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    company: Optional[str] = Field(None, max_length=255, description="Empresa")
    department: Optional[str] = Field(None, max_length=100, description="Departamento")
    position: Optional[str] = Field(None, max_length=100, description="Cargo/Posição")
    address: Optional[str] = Field(None, max_length=255, description="Endereço")
    city: Optional[str] = Field(None, max_length=100, description="Cidade")
    state: Optional[str] = Field(None, max_length=100, description="Estado/Província")
    zip_code: Optional[str] = Field(None, max_length=20, description="CEP")
    country: Optional[str] = Field(None, max_length=100, description="País")
    notes: Optional[str] = Field(None, description="Notas gerais")
    social_media: Optional[Dict[str, str]] = Field({}, description="Links de redes sociais")
    lead_id: Optional[UUID] = Field(None, description="ID do lead associado")


class ContactUpdateRequest(BaseModel):
    """Schema para atualizar um contato"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None)
    social_media: Optional[Dict[str, str]] = Field(None)


class ContactResponse(BaseModel):
    """Schema de resposta para contato"""
    id: UUID
    client_id: UUID
    lead_id: Optional[UUID]
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    department: Optional[str]
    position: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    notes: Optional[str]
    social_media: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

class PipelineStageSchema(BaseModel):
    """Schema para um estágio do pipeline"""
    id: str = Field(..., description="ID único do estágio")
    name: str = Field(..., description="Nome do estágio")
    color: Optional[str] = Field("#3B82F6", description="Cor em hex")


class PipelineCreateRequest(BaseModel):
    """Schema para criar um novo pipeline"""
    name: str = Field(..., min_length=1, max_length=255, description="Nome do pipeline")
    description: Optional[str] = Field(None, description="Descrição do pipeline")
    stages: Optional[List[PipelineStageSchema]] = Field(
        None,
        description="Estágios customizados (opcional)"
    )
    order: Optional[int] = Field(0, description="Ordem de exibição")


class PipelineUpdateRequest(BaseModel):
    """Schema para atualizar um pipeline"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    stages: Optional[List[PipelineStageSchema]] = Field(None)
    order: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)


class PipelineResponse(BaseModel):
    """Schema de resposta para pipeline"""
    id: UUID
    client_id: UUID
    name: str
    description: Optional[str]
    stages: List[Dict[str, Any]]
    order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# DEALS
# ═══════════════════════════════════════════════════════════════════════════

class DealCreateRequest(BaseModel):
    """Schema para criar um novo deal"""
    pipeline_id: UUID = Field(..., description="ID do pipeline")
    title: str = Field(..., min_length=1, max_length=255, description="Título do negócio")
    description: Optional[str] = Field(None, description="Descrição do negócio")
    value: float = Field(..., gt=0, description="Valor do deal")
    probability: Optional[int] = Field(50, ge=0, le=100, description="Probabilidade 0-100")
    expected_close_date: Optional[datetime] = Field(None, description="Data esperada de fechamento")
    stage: str = Field(..., description="Estágio no pipeline")
    contact_id: Optional[UUID] = Field(None, description="ID do contato associado")
    owner_id: Optional[UUID] = Field(None, description="ID do responsável")
    tags: Optional[List[str]] = Field([], description="Tags")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Dados customizados")


class DealUpdateRequest(BaseModel):
    """Schema para atualizar um deal"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    value: Optional[float] = Field(None, gt=0)
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = Field(None)
    stage: Optional[str] = Field(None)
    contact_id: Optional[UUID] = Field(None)
    owner_id: Optional[UUID] = Field(None)
    tags: Optional[List[str]] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)


class DealResponse(BaseModel):
    """Schema de resposta para deal"""
    id: UUID
    client_id: UUID
    pipeline_id: UUID
    contact_id: Optional[UUID]
    title: str
    description: Optional[str]
    value: float
    probability: int
    expected_close_date: Optional[datetime]
    stage: str
    owner_id: Optional[UUID]
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# KANBAN CARDS
# ═══════════════════════════════════════════════════════════════════════════

class KanbanCardCreateRequest(BaseModel):
    """Schema para criar um card no kanban"""
    deal_id: UUID = Field(..., description="ID do deal")
    title: str = Field(..., min_length=1, max_length=255, description="Título do card")
    column: str = Field(..., description="Coluna/Stage ID")
    position: Optional[int] = Field(0, description="Posição na coluna")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Dados adicionais")


class KanbanCardUpdateRequest(BaseModel):
    """Schema para atualizar um card do kanban"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    column: Optional[str] = Field(None)
    position: Optional[int] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)


class KanbanCardResponse(BaseModel):
    """Schema de resposta para kanban card"""
    id: UUID
    deal_id: UUID
    client_id: UUID
    title: str
    column: str
    position: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# LIST RESPONSES (with pagination)
# ═══════════════════════════════════════════════════════════════════════════

class PaginatedResponse(BaseModel):
    """Schema para resposta paginada genérica"""
    data: List[Any]
    total: int
    page: int
    limit: int
    hasMore: bool

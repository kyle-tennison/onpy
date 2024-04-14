"""Models for OnShape API payloads & responses"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ApiModel(BaseModel):

    model_config = ConfigDict(extra="ignore")


class UserReference(ApiModel):
    """Represents a reference to a user"""

    href: str
    id: str
    name: str


class Document(ApiModel):
    """Represents surface-level document information"""

    createdAt: datetime
    createdBy: UserReference
    href: str
    id: str
    name: str
    owner: UserReference


class DocumentsResponse(ApiModel):
    """Response model of GET /documents"""

    items: list[Document]

class DocumentCreateRequest(ApiModel):
    """Request model of POST /documents"""

    name: str
    description: str|None

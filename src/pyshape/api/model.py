"""Models for OnShape API payloads & responses"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Protocol


class NameIdFetchable(Protocol):
    name: str | None
    id: str | None


class ApiModel(BaseModel):

    model_config = ConfigDict(extra="ignore")


class UserReference(ApiModel):
    """Represents a reference to a user"""

    href: str
    id: str
    name: str


class Workspace(ApiModel):
    """Represents an instance of OnShape's workspace versioning"""

    name: str
    id: str


class Document(ApiModel):
    """Represents surface-level document information"""

    createdAt: datetime
    createdBy: UserReference
    href: str
    id: str
    name: str
    owner: UserReference
    defaultWorkspace: Workspace


class DocumentsResponse(ApiModel):
    """Response model of GET /documents"""

    items: list[Document]


class DocumentCreateRequest(ApiModel):
    """Request model of POST /documents"""

    name: str
    description: str | None


class Element(ApiModel):
    """Represents an OnShape element"""

    angleUnits: str | None
    areaUnits: str | None
    lengthUnits: str | None
    massUnits: str | None
    volumeUnits: str | None
    elementType: str
    id: str
    name: str

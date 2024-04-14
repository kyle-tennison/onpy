"""Models for OnShape API payloads & responses"""

from pydantic import BaseModel, field
from datetime import datetime

class ApiModel(BaseModel): ...

class UserReference(ApiModel):
    """Represents a reference to a user"""
    href: str 
    id: str 
    name: str 
    viewRef: str 
    image: str 
    state: int 
    jsonType: str


class Document(ApiModel):
    canMove: bool
    createdAt: datetime
    createdBy: UserReference
    description: str 
    href: str 
    id: str 
    name: str 
    owner: UserReference
    projectId: str 

    
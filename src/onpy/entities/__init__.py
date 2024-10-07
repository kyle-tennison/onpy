"""Onshape entity interface."""

from onpy.entities.entities import BodyEntity, EdgeEntity, Entity, FaceEntity, VertexEntity
from onpy.entities.filter import EntityFilter

__all__ = [
    "EntityFilter",
    "Entity",
    "VertexEntity",
    "EdgeEntity",
    "FaceEntity",
    "BodyEntity",
]

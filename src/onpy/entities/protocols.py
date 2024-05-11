"""Traits that an entity can implement"""

from textwrap import dedent
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from abc import abstractmethod
from onpy.util.misc import unwrap

if TYPE_CHECKING:
    from onpy.entities import VertexEntity, EdgeEntity, FaceEntity, BodyEntity


@runtime_checkable
class FaceEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of face entities"""

    @abstractmethod
    def _face_entities(self) -> list["FaceEntity"]:
        """Converts the current object into a list of face entities"""
        ...


@runtime_checkable
class VertexEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of vertex entities"""

    @abstractmethod
    def _vertex_entities(self) -> list["VertexEntity"]:
        """Converts the current object into a list of vertex entities"""
        ...


@runtime_checkable
class EdgeEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of edge entities"""

    @abstractmethod
    def _edge_entities(self) -> list["EdgeEntity"]:
        """Converts the current object into a list of edge entities"""
        ...


@runtime_checkable
class BodyEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of body entities"""

    @abstractmethod
    def _body_entities(self) -> list["BodyEntity"]:
        """Converts the current object into a list of body entities"""
        ...

"""Protocols/traits that different objects can display.

This system was inspired by Rust's trait system, which is similar to Python's
Protocol system. Sometimes, we want to be able to target an object
that is not directly an entity—such as wanting to extrude the total area of
a sketch. We can do this by making the Sketch object implement the
FaceEntityConversable trait, which allows it to convert itself into a set
of face entities. The same can be done for all other entity types. The
underlying traits are defined here.

OnPy - May 2024 - Kyle Tennison

"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from onpy.entities import BodyEntity, EdgeEntity, FaceEntity, VertexEntity


@runtime_checkable
class FaceEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of face entities."""

    @abstractmethod
    def _face_entities(self) -> list["FaceEntity"]:
        """Convert the current object into a list of face entities."""
        ...


@runtime_checkable
class VertexEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of vertex entities."""

    @abstractmethod
    def _vertex_entities(self) -> list["VertexEntity"]:
        """Convert the current object into a list of vertex entities."""
        ...


@runtime_checkable
class EdgeEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of edge entities."""

    @abstractmethod
    def _edge_entities(self) -> list["EdgeEntity"]:
        """Convert the current object into a list of edge entities."""
        ...


@runtime_checkable
class BodyEntityConvertible(Protocol):
    """A protocol used for items that can be converted into a list of body entities."""

    @abstractmethod
    def _body_entities(self) -> list["BodyEntity"]:
        """Convert the current object into a list of body entities."""
        ...

"""Interface to OnShape Entities.

In OnShape, there are four types of entities:
 - Vertex Entities
 - Line Entities
 - Face Entities
 - Body Entities

Different features can create different entities; e.g., an Extrude will create
a BodyEntity. The different entity types, along with their base class, are
defined here.

OnPy - May 2024 - Kyle Tennison

"""

from typing import override

from onpy.entities.protocols import (
    BodyEntityConvertible,
    EdgeEntityConvertible,
    FaceEntityConvertible,
    VertexEntityConvertible,
)


class Entity:
    """A generic OnShape entity."""

    def __init__(self, transient_id: str) -> None:
        """Construct an entity from its transient id."""
        self.transient_id = transient_id

    @classmethod
    def as_featurescript(cls) -> str:
        """Convert the EntityType variant into a Featurescript expression."""
        msg = "An entity of unknown type should never be parsed into featurescript"
        raise NotImplementedError(
            msg,
        )

    @staticmethod
    def match_string_type(string: str) -> type["Entity"]:
        """Match a string to the corresponding entity class."""
        match = {
            "VERTEX": VertexEntity,
            "EDGE": EdgeEntity,
            "FACE": FaceEntity,
            "BODY": BodyEntity,
        }.get(string.upper())

        if match is None:
            msg = f"'{string}' is not a valid entity type"
            raise TypeError(msg)

        return match

    def __str__(self) -> str:
        """Pretty string representation of the entity."""
        return repr(self)

    def __repr__(self) -> str:
        """Printable representation of the entity."""
        return f"{self.__class__.__name__}({self.transient_id})"


class VertexEntity(Entity, VertexEntityConvertible):
    """An entity that is a vertex."""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return "EntityType.VERTEX"

    @override
    def _vertex_entities(self) -> list["VertexEntity"]:
        return [self]


class EdgeEntity(Entity, EdgeEntityConvertible):
    """An entity that is an edge."""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return "EntityType.EDGE"

    @override
    def _edge_entities(self) -> list["EdgeEntity"]:
        return [self]


class FaceEntity(Entity, FaceEntityConvertible):
    """An entity that is a face."""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return "EntityType.FACE"

    @override
    def _face_entities(self) -> list["FaceEntity"]:
        return [self]


class BodyEntity(Entity, BodyEntityConvertible):
    """An entity that is a body."""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return "EntityType.BODY"

    @override
    def _body_entities(self) -> list["BodyEntity"]:
        return [self]

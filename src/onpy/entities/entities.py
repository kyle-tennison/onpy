"""Interface to OnShape entities"""

from abc import ABC
from enum import Enum
from typing import override
from onpy.entities.protocols import (
    FaceEntityConvertible,
    VertexEntityConvertible,
    BodyEntityConvertible,
    EdgeEntityConvertible,
)


class Entity:
    """A generic OnShape entity"""

    def __init__(self, transient_id: str):
        self.transient_id = transient_id

    @classmethod
    def as_featurescript(cls) -> str:
        """Converts the EntityType variant into a Featurescript expression"""
        raise NotImplementedError(
            "An entity of unknown type should never be parsed into featurescript"
        )

    @property
    def as_query(self) -> str:
        """Featurescript expression to convert into query of self"""
        return '{ "queryType" : QueryType.TRANSIENT, "transientId" : "TRANSIENT_ID" } as Query'.replace(
            "TRANSIENT_ID", self.transient_id
        )

    @property
    def as_entity(self) -> str:
        """Featurescript expression to get a reference to this entity"""
        return f"evaluateQuery(context, {self.as_query})[0] "

    @staticmethod
    def match_string_type(string: str) -> type["Entity"]:
        """Matches a string to the corresponding entity class"""

        match = {
            "VERTEX": VertexEntity,
            "EDGE": EdgeEntity,
            "FACE": FaceEntity,
            "BODY": BodyEntity,
        }.get(string.upper())

        if match is None:
            raise TypeError(f"'{string}' is not a valid entity type")

        return match

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"{self.__class__.__name__}({self.transient_id})"


class VertexEntity(Entity, VertexEntityConvertible):
    """An entity that is a vertex"""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return f"EntityType.VERTEX"

    @override
    def _vertex_entities(self) -> list["VertexEntity"]:
        return [self]


class EdgeEntity(Entity, EdgeEntityConvertible):
    """An entity that is an edge"""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return f"EntityType.EDGE"

    @override
    def _edge_entities(self) -> list["EdgeEntity"]:
        return [self]


class FaceEntity(Entity, FaceEntityConvertible):
    """An entity that is a face"""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return f"EntityType.FACE"

    @override
    def _face_entities(self) -> list["FaceEntity"]:
        return [self]


class BodyEntity(Entity, BodyEntityConvertible):
    """An entity that is a body"""

    @classmethod
    @override
    def as_featurescript(cls) -> str:
        return f"EntityType.BODY"

    @override
    def _body_entities(self) -> list["BodyEntity"]:
        return [self]

"""Interface to OnShape entities"""

from enum import Enum
from typing import override
from onpy.features.base import Extrudable

class Entity(Extrudable):
    """Base class for OnShape entities"""

    def __init__(self, transient_id: str):
        self.transient_id = transient_id

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

    @property
    @override
    def _extrusion_query(self) -> list[str]:
        return [self.transient_id]

    @property
    @override
    def _extrusion_parameter_bt_type(self) -> str:
        return "BTMIndividualQuery-138"

    @property
    @override
    def _extrusion_query_key(self) -> str:
        return "deterministicIds"

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        """NOTE: for debugging purposes"""
        return f"Entity({self.transient_id})"
    

class EntityType(Enum):
    """Used to differentiate entity types"""

    VERTEX = "vertex"
    EDGE = "edge"
    FACE = "face"
    BODY = "body"

    def as_featurescript(self) -> str:
        """Converts the EntityType variant into a Featurescript expression"""
        return f"EntityType.{self.name}"

    @staticmethod
    def parse_type(input: str) -> "EntityType":
        """Parses a string into the corresponding enum variant

        Raises:
            KeyError if the input cannot be matched to a variant
        """

        input = input.lower()

        if input.lower() not in EntityType:
            raise KeyError(
                f"'{input}' is not a valid entity type. Options are: VERTEX, EDGE, FACE, BODY"
            )
        else:
            return EntityType[input]

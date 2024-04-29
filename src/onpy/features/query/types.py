"""Wrapping for various OnShape query types"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from textwrap import dedent
from typing import override
from onpy.util.misc import UnitSystem


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


class QueryType(ABC):
    """Used to represent the type of a query"""

    @abstractmethod
    def inject_featurescript(self, q_to_filter: str) -> str:
        """The featurescript to inject to create a Query object of this type

        Args:
            q_to_filter: The internal query to filter
        """
        ...

    @staticmethod
    def make_point_vector(point: tuple[float, float, float], units: UnitSystem) -> str:
        """Makes a point into a dimensioned Featurescript vector

        Args:
            point: The point to convert
            units: The UnitSystem to dimension with

        Returns:
            The Featurescript expression for the point with units
        """
        return f"(vector([{point[0]}, {point[1]}, {point[2]}]) * {units.fs_name})"

    @classmethod
    def make_line(
        cls,
        origin: tuple[float, float, float],
        direction: tuple[float, float, float],
        units: UnitSystem,
    ) -> str:
        """Makes a Featurescript line

        Args:
            origin: The origin of the line
            direction: The direction of the line
            units: The UnitSystem to dimension with

        Returns:
            The Featurescript expression for the point with units
        """
        return f'({{"origin": {cls.make_point_vector(origin, units)}, "direction": vector([{direction[0]}, {direction[1]}, {direction[2]}]) }} as Line)'

    @staticmethod
    def add_units(value: int | float, units: UnitSystem) -> str:
        """Adds units to a number for Featurescript

        Args:
            value: The value to add units to
            units: The UnitSystem to dimension with

        Returns:
            The Featurescript expression for the value with units
        """
        return f"({value}*{units.fs_name})"


@dataclass
class qContainsPoint(QueryType):
    """Wraps the OnShape qContainsPoint query"""

    point: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qContainsPoint({q_to_filter}, {self.make_point_vector(self.point, self.units)})"


@dataclass
class qClosestTo(QueryType):
    """Wraps the OnShape qClosestTo query"""

    point: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qClosestTo({q_to_filter}, {self.make_point_vector(self.point, self.units)})"


@dataclass
class qLargest(QueryType):
    """Wraps the OnShape qLargest query"""

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qLargest({q_to_filter})"


@dataclass
class qSmallest(QueryType):
    """Wraps the OnShape qSmallest query"""

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qSmallest({q_to_filter})"


@dataclass
class qWithinRadius(QueryType):
    """Wraps the OnShape qWithinRadius query"""

    point: tuple[float, float, float]
    radius: float
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qWithinRadius({q_to_filter})"


@dataclass
class qIntersectsLine(QueryType):
    """Wraps the OnShape qIntersectsLine query"""

    line_origin: tuple[float, float, float]
    line_direction: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qIntersectsLine({q_to_filter}, {self.make_line(self.line_origin, self.line_direction, self.units)})"


@dataclass
class qEntityType(QueryType):
    """Wraps the OnShape qEntityType query"""

    entity_type: EntityType

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qEntityType({q_to_filter}, {self.entity_type.as_featurescript()})"

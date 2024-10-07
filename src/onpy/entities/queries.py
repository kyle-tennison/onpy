"""Python wrappings of OnShape queries.

The queries used by entities.py are defined here. They are used to filter
entities.

OnPy - May 2024 - Kyle Tennison

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from onpy.entities import Entity
from onpy.util.misc import UnitSystem


class QueryType(ABC):
    """Used to represent the type of a query."""

    @abstractmethod
    def inject_featurescript(self, q_to_filter: str) -> str:
        """Generate featurescript that will create a Query object of this type.

        Args:
            q_to_filter: The internal query to filter

        """
        ...

    @staticmethod
    def make_point_vector(point: tuple[float, float, float], units: UnitSystem) -> str:
        """Make a point into a dimensioned Featurescript vector.

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
        """Make a Featurescript line.

        Args:
            origin: The origin of the line
            direction: The direction of the line
            units: The UnitSystem to dimension with

        Returns:
            The Featurescript expression for the point with units

        """
        return f'({{"origin": {cls.make_point_vector(origin, units)}, "direction": vector([{direction[0]}, {direction[1]}, {direction[2]}]) }} as Line)'  # noqa: E501

    @staticmethod
    def add_units(value: float, units: UnitSystem) -> str:
        """Add units to a number for Featurescript.

        Args:
            value: The value to add units to
            units: The UnitSystem to dimension with

        Returns:
            The Featurescript expression for the value with units

        """
        return f"({value}*{units.fs_name})"


@dataclass
class qContainsPoint(QueryType):
    """Wrap the OnShape qContainsPoint query."""

    point: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qContainsPoint({q_to_filter}, {self.make_point_vector(self.point, self.units)})"


@dataclass
class qClosestTo(QueryType):
    """Wrap the OnShape qClosestTo query."""

    point: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qClosestTo({q_to_filter}, {self.make_point_vector(self.point, self.units)})"


@dataclass
class qLargest(QueryType):
    """Wrap the OnShape qLargest query."""

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qLargest({q_to_filter})"


@dataclass
class qSmallest(QueryType):
    """Wrap the OnShape qSmallest query."""

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qSmallest({q_to_filter})"


@dataclass
class qWithinRadius(QueryType):
    """Wrap the OnShape qWithinRadius query."""

    point: tuple[float, float, float]
    radius: float
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qWithinRadius({q_to_filter})"


@dataclass
class qIntersectsLine(QueryType):
    """Wrap the OnShape qIntersectsLine query."""

    line_origin: tuple[float, float, float]
    line_direction: tuple[float, float, float]
    units: UnitSystem

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qIntersectsLine({q_to_filter}, {self.make_line(self.line_origin, self.line_direction, self.units)})"  # noqa: E501


@dataclass
class qEntityType(QueryType):
    """Wrap the OnShape qEntityType query."""

    entity_type: type[Entity]

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qEntityFilter({q_to_filter}, {self.entity_type.as_featurescript()})"

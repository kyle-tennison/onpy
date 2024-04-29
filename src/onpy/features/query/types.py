"""Wrapping for various OnShape query types"""

from abc import ABC, abstractmethod
from typing import override
from onpy.util.misc import UnitSystem


class QueryType(ABC):
    """Used to represent the type of a query"""

    @abstractmethod
    def inject_featurescript(self, q_to_filter: str) -> str:
        """The featurescript to inject to create a Query object of this type
        
        Args:
            q_to_filter: The internal query to filter
        """
        ...


class qContainsPoint(QueryType):

    def __init__(self, point: tuple[float, float, float], units: UnitSystem):

        self.point = point 
        self.units = units

    @property
    def point_vector(self) -> str:
        """The Featurescript compatible definition of the point to query"""
        return f"vector([{self.point[0]}, {self.point[1]}, {self.point[2]}]) * {self.units.fs_name}"

    @override
    def inject_featurescript(self, q_to_filter: str) -> str:
        return f"qContainsPoint({q_to_filter}, {self.point_vector})"
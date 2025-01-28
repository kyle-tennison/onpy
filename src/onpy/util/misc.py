"""Miscellaneous Tools.

Misc tools should go here

OnPy - May 2024 - Kyle Tennison

"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Self

from onpy.api.schema import NameIdFetchable
from onpy.util.exceptions import OnPyParameterError


def find_by_name_or_id[T: NameIdFetchable](
    target_id: str | None, name: str | None, items: list[T]
) -> T | None:
    """Given a list of values and a name & id, find the first match.

    Only the name or id needs to be provided.

    Args:
        target_id: The id to search for
        name: The name to search for
        items: A list of items to search through

    Returns:
        The matching item, if found. Returns None if no match is found.

    Raises:
        OnPyParameterError if neither the id nor name were provided.

    """
    if name is None and target_id is None:
        msg = "A name or id is required to fetch"
        raise OnPyParameterError(msg)

    if len(items) == 0:
        return None

    candidate: T | None = None

    if name:
        filtered = [i for i in items if i.name == name]
        if len(filtered) > 1:
            msg = f"Duplicate names '{name}'. Use id instead to fetch."
            raise OnPyParameterError(msg)
        if len(filtered) == 0:
            return None

        candidate = filtered[0]

    if target_id:
        for i in items:
            if i.id == target_id:
                candidate = i
                break

    return candidate


def unwrap_type[T](target: object, expected_type: type[T]) -> T:
    """Return the object if the type matches. Raises error otherwise."""
    if isinstance(target, expected_type):
        return target
    msg = (
        f"Failed to unwrap type. Got {type(target).__name__}, expected {expected_type.__name__}",
    )
    raise TypeError(msg)


def unwrap[T](target: T | None, message: str | None = None, default: T | None = None) -> T:
    """Take the object out of an Option[T].

    Args:
        target: The object to unwrap
        message: An optional message to show on error
        default: An optional value to use instead of throwing an error

    Returns:
        The object of the value, if it is not None. Returns the default if the
        object is None and a default value is provided

    Raises:
        TypeError if the object is None and no default value is provided.

    """
    if target is not None:
        return target
    if default is not None:
        return default
    raise TypeError(message if message else "Failed to unwrap")


class UnitSystem(Enum):
    """Enumeration of available OnShape unit systems for length."""

    INCH = "inch"
    METRIC = "metric"

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Get corresponding enum variant from string.

        Raises:
            TypeError if the string does not match the expected type

        """
        string = string.lower()

        if string not in UnitSystem:
            msg = f"'{string}' is not a valid unit system"
            raise TypeError(msg)
        return cls(string)

    @property
    def extension(self) -> str:
        """Get the extension of the unit; e.g., 'in' for inches."""
        return {UnitSystem.INCH: "in", UnitSystem.METRIC: "m"}[self]

    @property
    def fs_name(self) -> str:
        """The featurescript name of the unit system."""
        return {UnitSystem.INCH: "inch", UnitSystem.METRIC: "meter"}[self]


@dataclass
class Point2D:
    """Represents a 2D point."""

    x: float
    y: float

    def __mul__(self, value: float) -> "Point2D":
        """Multiply a point by a scalar."""
        return Point2D(x=self.x * value, y=self.y * value)

    def __truediv__(self, value: float) -> "Point2D":
        """Divide a point by a scalar."""
        return Point2D(x=self.x / value, y=self.y / value)

    def __add__(self, other: "Point2D") -> "Point2D":
        """Add two points together."""
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point2D") -> "Point2D":
        """Subtract one point from another."""
        return Point2D(self.x - other.x, self.y - other.y)

    def __eq__(self, other: object) -> bool:
        """Check if two points are equal."""
        if isinstance(other, Point2D):
            return self.x == other.x and self.y == other.y
        return False

    @classmethod
    def from_pair(cls, pair: tuple[float, float]) -> Self:
        """Create a point from an ordered pair."""
        return cls(*pair)

    @property
    def as_tuple(self) -> tuple[float, float]:
        """The point as an ordered pair tuple."""
        return (self.x, self.y)

    @staticmethod
    def approx(point1: "Point2D", point2: "Point2D", error: float = 1e-8) -> bool:
        """Check if two points are approximately equal."""
        distance = math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)
        return distance < error

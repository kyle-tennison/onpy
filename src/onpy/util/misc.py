"""

Miscellaneous Tools

Misc tools should go here

OnPy - May 2024 - Kyle Tennison

"""

from enum import Enum
import math
from typing import Self
from dataclasses import dataclass

from onpy.api.model import NameIdFetchable
from onpy.util.exceptions import OnPyParameterError


def find_by_name_or_id[
    T: NameIdFetchable
](id: str | None, name: str | None, items: list[T]) -> T | None:
    """Given a list of values and a name & id, find the first match. Only the
    name or id needs to be provided.

    Args:
        id: The id to search for
        name: The name to search for
        items: A list of items to search through

    Returns:
        The matching item, if found. Returns None if no match is found.

    Raises:
        OnPyParameterError if neither the id nor name were provided.
    """

    if name is None and id is None:
        raise OnPyParameterError("A name or id is required to fetch")

    if len(items) == 0:
        return None

    candidate: T | None = None

    if name:
        filtered = [i for i in items if i.name == name]
        if len(filtered) > 1:
            raise OnPyParameterError(
                f"Duplicate names '{name}'. Use id instead to fetch."
            )
        if len(filtered) == 0:
            return None

        candidate = filtered[0]

    if id:
        for i in items:
            if i.id == id:
                candidate = i
                break

    return candidate


def unwrap_type[T](object: object, expected_type: type[T]) -> T:
    """Returns the object if the type matches. Raises error otherwise."""

    if isinstance(object, expected_type):
        return object
    else:
        raise TypeError(
            "Failed to unwrap type. Got %s, expected %s"
            % (type(object).__name__, expected_type.__name__)
        )


def unwrap[
    T
](object: T | None, message: str | None = None, default: T | None = None) -> T:
    """Takes the object out of an Option[T].

    Args:
        object: The object to unwrap
        message: An optional message to show on error
        default: An optional value to use instead of throwing an error

    Returns:
        The object of the value, if it is not None. Returns the default if the
        object is None and a default value is provided

    Raises
        TypeError if the object is None and no default value is provided.
    """

    if object is not None:
        return object
    else:
        if default is not None:
            return default
        else:
            raise TypeError(message if message else "Failed to unwrap")


class UnitSystem(Enum):
    INCH = "inch"
    METRIC = "metric"

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Gets corresponding enum variant from string

        Raises:
            TypeError if the string does not match the expected type
        """

        string = string.lower()

        if string not in UnitSystem:
            raise TypeError(f"'{string}' is not a valid unit system")
        else:
            return cls(string)

    @property
    def extension(self) -> str:
        """Gets the extension of the unit; e.g., 'in' for inches."""

        return {UnitSystem.INCH: "in", UnitSystem.METRIC: "m"}[self]

    @property
    def fs_name(self) -> str:
        """The featurescript name of the unit system"""

        return {UnitSystem.INCH: "inch", UnitSystem.METRIC: "meter"}[self]


@dataclass
class Point2D:
    """Represents a 2D point"""

    x: float
    y: float

    def __mul__(self, value: float) -> "Point2D":
        return Point2D(x=self.x * value, y=self.y * value)

    def __truediv__(self, value: float) -> "Point2D":
        return Point2D(x=self.x / value, y=self.y / value)

    def __add__(self, other: "Point2D") -> "Point2D":
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point2D") -> "Point2D":
        return Point2D(self.x - other.x, self.y - other.y)

    def __eq__(self, other: "Point2D") -> bool:
        return self.x == other.x and self.y == other.y

    @classmethod
    def from_pair(cls, tuple: tuple[float, float]) -> Self:
        return cls(*tuple)

    @property
    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @staticmethod
    def approx(point1: "Point2D", point2: "Point2D", error: float = 1e-8) -> bool:
        """Checks if two points are approximately equal"""
        distance = math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)
        return distance < error

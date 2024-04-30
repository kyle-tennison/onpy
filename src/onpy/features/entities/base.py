"""Abstract base class for feature entities"""

from abc import ABC, abstractmethod
import math
import uuid
import onpy.api.model as model
from typing import Self, TYPE_CHECKING
from onpy.util.misc import Point2D

if TYPE_CHECKING:
    from onpy.features.base import Feature


class Entity(ABC):

    @abstractmethod
    def to_model(self) -> model.FeatureEntity:
        """Convert the entity into the corresponding model"""
        ...

    @property
    @abstractmethod
    def _feature(self) -> "Feature":
        """A reference to the """
        ...

    def generate_entity_id(self) -> str:
        """Generates a random entity id"""
        return str(uuid.uuid4()).replace("-", "")
    
    # TODO: there needs to be reorganization to differentiate between sketch entities and other entities
    @abstractmethod
    def translate(self, x: float = 0, y:float =0) -> Self:
        """Linear translation of the entity
        
        Args:
            x: The distance to translate along the x-axis
            y: The distance to translate along the y-axis

        Returns:
            A new sketch object
        """
        ...

    @abstractmethod
    def rotate(self, origin: tuple[float, float], theta:float ) -> Self:
        """Rotates the entity about a point
        
        Args:
            origin: The point to rotate about
            theta: The degrees to rotate by. Positive is ccw

        Returns:
            A new sketch object
        """
        ...

    @abstractmethod
    def mirror(self, line_start: tuple[float, float], line_end: tuple[float, float]) -> Self:
        """Mirror the entity about a line
        
        Args:
            line_start: The starting point of the line
            line_end: The ending point of the line

        Returns:
            A new sketch object
        """
        ...

    @staticmethod # TODO: make these use Point2D
    def _mirror_point(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> tuple[float, float]:
        """Mirrors the point across a line
        
        Args:
            point: The point to mirror
            line_start: The point where the line starts
            line_end: The point where the line ends

        Returns:
            The mirrored point
        """

        # calculate the angle of the line
        angle = math.atan2(line_end[1] - line_start[1], line_end[0] - line_start[0])
        line_angle_x = angle if angle >= 0 else angle + math.pi
        point_angle = math.atan2(point[1] - line_start[1], point[0] - line_start[0])
        diff_angle = point_angle - line_angle_x
        distance = abs(math.sin(diff_angle) * math.sqrt((point[0] - line_start[0])**2 + (point[1] - line_start[1])**2))
        new_x = point[0] + 2 * distance * math.cos(diff_angle)
        new_y = point[1] + 2 * distance * math.sin(diff_angle)

        return new_x, new_y
    
    @staticmethod
    def _rotate_point(point: Point2D, pivot: Point2D, degrees: float) -> Point2D:
        """Rotates a point about another point
        
        Args:
            point: The point to rotate
            pivot: The pivot to rotate about
            degrees: The degrees to rotate by

        Returns:
            The rotated point
        """

        dx = point.x - pivot.x 
        dy = point.y - pivot.y

        radius = math.sqrt( dx**2 + dy**2)
        start_angle = math.atan2(dy,dx)
        end_angle = start_angle + math.radians(degrees)

        new_x = math.cos(end_angle)
        new_y = math.sin(end_angle)

        return Point2D(new_x, new_y)



    
    def _replace_entity(self, new_entity: "Entity") -> None:
        """Replaces the existing entity with a new entity and refreshes the
        feature

        Args:
            new_entity: The entity to replace with
        """

        self._feature.entities.remove(self)
        self._feature.entities.append(new_entity)
        self._feature._update_feature()


    def __str__(self) -> str:
        return repr(self)

    @abstractmethod
    def __repr__(self) -> str: ...

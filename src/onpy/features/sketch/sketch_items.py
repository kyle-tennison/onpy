"""Various items that can belong to a sketch.

As a user builds a sketch, they are adding sketch items. This is importantly
different from adding entities--which they are also adding. Sketch items
*cannot* be queried or used for any type of other feature; they are internal
to the sketch. Entities, on the other hand, are derived from the way sketch
items are added; these can be queried and used in other features.

OnPy - May 2024 - Kyle Tennison

"""

import copy
import math
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self, override

import numpy as np
from loguru import logger

from onpy.api import schema
from onpy.util.exceptions import OnPyParameterError
from onpy.util.misc import Point2D, UnitSystem

if TYPE_CHECKING:
    from onpy.features import Sketch


class SketchItem(ABC):
    """Represents an item that the user added to the sketch. *Not* the same
    as an entity.
    """

    @property
    @abstractmethod
    def sketch(self) -> "Sketch":
        """A reference to the owning sketch."""

    @abstractmethod
    def to_model(self) -> schema.ApiModel:
        """Convert the item into the corresponding api schema."""
        ...

    @abstractmethod
    def translate(self, x: float = 0, y: float = 0) -> Self:
        """Linear translation of the entity.

        Args:
            x: The distance to translate along the x-axis
            y: The distance to translate along the y-axis

        Returns:
            A new sketch object

        """
        ...

    @abstractmethod
    def rotate(self, origin: tuple[float, float], theta: float) -> Self:
        """Rotates the entity about a point.

        Args:
            origin: The point to rotate about
            theta: The degrees to rotate by. Positive is ccw

        Returns:
            A new sketch object

        """
        ...

    @abstractmethod
    def mirror(
        self,
        line_start: tuple[float, float],
        line_end: tuple[float, float],
    ) -> Self:
        """Mirror the entity about a line.

        Args:
            line_start: The starting point of the line
            line_end: The ending point of the line

        Returns:
            A new entity object

        """
        ...

    @staticmethod
    def _mirror_point(
        point: Point2D,
        line_start: Point2D,
        line_end: Point2D,
    ) -> Point2D:
        """Mirrors the point across a line.

        Args:
            point: The point to mirror
            line_start: The point where the line starts
            line_end: The point where the line ends

        Returns:
            The mirrored point

        """
        q_i = np.array(line_start.as_tuple)
        q_j = np.array(line_end.as_tuple)
        p_0 = np.array(point.as_tuple)

        a = q_i[1] - q_j[1]
        b = q_j[0] - q_i[0]
        c = -(a * q_i[0] + b * q_i[1])

        p_k = (
            np.array([[b**2 - a**2, -2 * a * b], [-2 * a * b, a**2 - b**2]]) @ p_0
            - 2 * c * np.array([a, b])
        ) / (a**2 + b**2)

        return Point2D.from_pair(p_k)

    @staticmethod
    def _rotate_point(point: Point2D, pivot: Point2D, degrees: float) -> Point2D:
        """Rotates a point about another point.

        Args:
            point: The point to rotate
            pivot: The pivot to rotate about
            degrees: The degrees to rotate by

        Returns:
            The rotated point

        """
        dx = point.x - pivot.x
        dy = point.y - pivot.y

        radius = math.sqrt(dx**2 + dy**2)
        start_angle = math.atan2(dy, dx)
        end_angle = start_angle + math.radians(degrees)

        new_x = radius * math.cos(end_angle)
        new_y = radius * math.sin(end_angle)

        return Point2D(new_x, new_y)

    def _replace_entity(self, new_entity: "SketchItem") -> None:
        """Replace the existing entity with a new entity and refreshes the
        feature.

        Args:
            new_entity: The entity to replace with

        """
        self.sketch._items.remove(self)
        self.sketch._items.add(new_entity)
        self.sketch._update_feature()

    def clone(self) -> Self:
        """Create a copy of the entity."""
        logger.debug(f"Created a close of {self}")

        new_entity = copy.copy(self)
        self.sketch._items.add(new_entity)
        return new_entity

    def linear_pattern(
        self,
        num_steps: int,
        x_step: float,
        y_step: float,
    ) -> list[Self]:
        """Create a linear pattern of the sketch entity.

        Args:
            num_steps: The number of steps to make. Does not include original entity
            x_step: The x distance to translate per step
            y_step: The y distance to translate per step

        Returns:
            A list of the entities that compose the linear pattern, including the
            original item.

        """
        logger.debug(f"Creating a linear pattern of {self} for {num_steps}")

        entities: list[Self] = [self]

        for _ in range(num_steps):
            entities.append(entities[-1].clone().translate(x_step, y_step))

        return entities

    def circular_pattern(
        self,
        origin: tuple[float, float],
        num_steps: int,
        theta: float,
    ) -> list[Self]:
        """Create a circular pattern of the sketch entity about a point.

        Args:
            origin: The origin of the circular rotation
            num_steps: The number of steps to make. Does not include original entity
            theta: The degrees to rotate per step

        Returns:
            A list of entities that compose the circular pattern, including the
            original item.

        """
        logger.debug(f"Creating a circular pattern of {self} for {num_steps}")

        entities: list[Self] = [self]

        for _ in range(num_steps):
            entities.append(entities[-1].clone().rotate(origin, theta))

        return entities

    def _generate_entity_id(self) -> str:
        """Generate a random entity id."""
        return str(uuid.uuid4()).replace("-", "")

    def __str__(self) -> str:
        """Pretty representation of the sketch item."""
        return repr(self)

    @abstractmethod
    def __repr__(self) -> str:
        """Printable representation of the sketch item."""
        ...


class SketchCircle(SketchItem):
    """A sketch circle."""

    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        units: UnitSystem,
        direction: tuple[float, float] = (1, 0),
        *,
        clockwise: bool = False,
    ) -> None:
        """Args:
        sketch: A reference to the owning sketch
        radius: The radius of the arc
        center: The centerpoint of the arc
        units: The unit system to use
        direction: An optional direction to specify. Defaults to +x axis
        clockwise: Whether or not the arc is clockwise. Defaults to false.

        """
        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.units = units
        self.direction = Point2D.from_pair(direction)
        self.clockwise = clockwise
        self.entity_id = self._generate_entity_id()

    @override
    def to_model(self) -> schema.SketchCurveEntity:
        return schema.SketchCurveEntity(
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xCenter": self.center.x,
                "yCenter": self.center.y,
                "xDir": self.direction.x,
                "yDir": self.direction.y,
                "clockwise": self.clockwise,
            },
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
        )

    @property
    @override
    def sketch(self) -> "Sketch":
        """A reference to the owning sketch."""
        return self._sketch

    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchCircle":
        new_center = self._rotate_point(self.center, Point2D.from_pair(origin), theta)
        new_entity = SketchCircle(
            sketch=self.sketch,
            radius=self.radius,
            center=new_center,
            units=self.units,
            direction=self.direction.as_tuple,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def translate(self, x: float = 0, y: float = 0) -> "SketchCircle":
        if self._sketch._client.units is UnitSystem.INCH:
            x *= 0.0254
            y *= 0.0254

        new_center = Point2D(self.center.x + x, self.center.y + y)
        new_entity = SketchCircle(
            sketch=self.sketch,
            radius=self.radius,
            center=new_center,
            units=self.units,
            direction=self.direction.as_tuple,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def mirror(
        self,
        line_start: tuple[float, float],
        line_end: tuple[float, float],
    ) -> "SketchCircle":
        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end)

        # to avoid confusion
        del line_start
        del line_end

        new_center = self._mirror_point(self.center, mirror_start, mirror_end)

        new_entity = SketchCircle(
            sketch=self.sketch,
            radius=self.radius,
            center=new_center,
            units=self.units,
            direction=self.direction.as_tuple,
            clockwise=self.clockwise,
        )

        self._replace_entity(new_entity)
        return new_entity

    @override
    def __repr__(self) -> str:
        return f"Circle(radius={self.radius}, center={self.center})"


class SketchLine(SketchItem):
    """A straight sketch line segment."""

    def __init__(
        self,
        sketch: "Sketch",
        start_point: Point2D,
        end_point: Point2D,
        units: UnitSystem,
    ) -> None:
        """Args:
        sketch: A reference to the owning sketch
        start_point: The starting point of the line
        end_point: The ending point of the line
        units: The unit system to use.

        """
        self._sketch = sketch
        self.start = start_point
        self.end = end_point
        self.units = units
        self.entity_id = self._generate_entity_id()

    @property
    def dx(self) -> float:
        """The x-component of the line."""
        return self.end.x - self.start.x

    @property
    def dy(self) -> float:
        """The y-component of the line."""
        return self.end.y - self.start.y

    @property
    def length(self) -> float:
        """The length of the line."""
        return abs(math.sqrt(self.dx**2 + self.dy**2))

    @property
    def theta(self) -> float:
        """The angle of the line relative to the x-axis."""
        return math.atan2(self.dy, self.dx)

    @property
    def direction(self) -> Point2D:
        """A vector pointing in the direction of the line."""
        return Point2D(math.cos(self.theta), math.sin(self.theta))

    @property
    @override
    def sketch(self) -> "Sketch":
        """A reference to the owning sketch."""
        return self._sketch

    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchLine":
        new_start = self._rotate_point(
            self.start,
            Point2D.from_pair(origin),
            degrees=theta,
        )
        new_end = self._rotate_point(self.end, Point2D.from_pair(origin), degrees=theta)

        new_entity = SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def mirror(
        self,
        line_start: tuple[float, float],
        line_end: tuple[float, float],
    ) -> "SketchLine":
        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end)

        new_start = self._mirror_point(self.start, mirror_start, mirror_end)
        new_end = self._mirror_point(self.end, mirror_start, mirror_end)

        new_entity = SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def translate(self, x: float = 0, y: float = 0) -> "SketchLine":
        if self._sketch._client.units is UnitSystem.INCH:
            x *= 0.0254
            y *= 0.0254

        new_start = Point2D(self.start.x + x, self.start.y + y)
        new_end = Point2D(self.end.x + x, self.end.y + y)

        new_entity = SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def to_model(self) -> schema.SketchCurveSegmentEntity:
        return schema.SketchCurveSegmentEntity(
            entityId=self.entity_id,
            startPointId=f"{self.entity_id}.start",
            endPointId=f"{self.entity_id}.end",
            startParam=0,
            endParam=self.length,
            geometry={
                "btType": "BTCurveGeometryLine-117",
                "pntX": self.start.x,
                "pntY": self.start.y,
                "dirX": self.direction.x,
                "dirY": self.direction.y,
            },
        )

    @override
    def __repr__(self) -> str:
        return f"Line(start={self.start}, end={self.end})"


class SketchArc(SketchItem):
    """A sketch arc."""

    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        theta_interval: tuple[float, float],
        units: UnitSystem,
        direction: tuple[float, float] = (1, 0),
        *,
        clockwise: bool = False,
    ) -> None:
        """Args:
        sketch: A reference to the owning sketch
        radius: The radius of the arc
        center: The centerpoint of the arc
        theta_interval: The theta interval, in degrees
        units: The unit system to use
        direction: An optional direction to specify. Defaults to +x axis
        clockwise: Whether or not the arc is clockwise. Defaults to false.

        """
        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.theta_interval = theta_interval
        self.direction = direction
        self.clockwise = clockwise
        self.entity_id = self._generate_entity_id()
        self.units = units

    @property
    @override
    def sketch(self) -> "Sketch":
        """A reference to the owning sketch."""
        return self._sketch

    @override
    def mirror(
        self,
        line_start: tuple[float, float],
        line_end: tuple[float, float],
    ) -> "SketchArc":
        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end)

        # to avoid confusion
        del line_start
        del line_end

        start_point = Point2D(
            self.radius * math.cos(self.theta_interval[0]) + self.center.x,
            self.radius * math.sin(self.theta_interval[0]) + self.center.y,
        )

        start_point = self._mirror_point(start_point, mirror_start, mirror_end)
        new_center = self._mirror_point(self.center, mirror_start, mirror_end)

        arc_start_vector = np.array(
            [start_point.x - new_center.x, start_point.y - new_center.y],
        )
        mirror_line_vector = np.array(
            [mirror_end.x - mirror_start.x, mirror_end.y - mirror_start.y],
        )

        angle_offset = 2 * math.acos(
            np.dot(arc_start_vector, mirror_line_vector)
            / (np.linalg.norm(arc_start_vector) * np.linalg.norm(mirror_line_vector)),
        )

        d_theta = self.theta_interval[1] - self.theta_interval[0]

        new_theta = (
            (self.theta_interval[0] - angle_offset - d_theta),
            (self.theta_interval[0] - angle_offset),
        )

        new_entity = SketchArc(
            sketch=self._sketch,
            radius=self.radius,
            center=new_center,
            theta_interval=new_theta,
            units=self.units,
            direction=self.direction,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def translate(self, x: float = 0, y: float = 0) -> "SketchArc":
        if self._sketch._client.units is UnitSystem.INCH:
            x *= 0.0254
            y *= 0.0254

        new_center = Point2D(self.center.x + x, self.center.y + y)
        new_entity = SketchArc(
            sketch=self._sketch,
            radius=self.radius,
            center=new_center,
            theta_interval=self.theta_interval,
            units=self.units,
            direction=self.direction,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchArc":
        pivot = Point2D.from_pair(origin)

        start_point = Point2D(
            self.radius * math.cos(self.theta_interval[0]) + self.center.x,
            self.radius * math.sin(self.theta_interval[0]) + self.center.y,
        )
        end_point = Point2D(
            self.radius * math.cos(self.theta_interval[1]) + self.center.x,
            self.radius * math.sin(self.theta_interval[1]) + self.center.y,
        )

        new_center = self._rotate_point(self.center, pivot, theta)
        start_point = self._rotate_point(start_point, pivot, theta)
        end_point = self._rotate_point(end_point, pivot, theta)

        new_entity = SketchArc.three_point_with_midpoint(
            sketch=self._sketch,
            center=new_center,
            radius=self.radius,
            endpoint_1=start_point,
            endpoint_2=end_point,
            units=self.units,
            direction=self.direction,
            clockwise=self.clockwise,
        )

        self._replace_entity(new_entity)
        return new_entity

    @override
    def to_model(self) -> schema.SketchCurveSegmentEntity:
        return schema.SketchCurveSegmentEntity(
            startPointId=f"{self.entity_id}.start",
            endPointId=f"{self.entity_id}.end",
            startParam=self.theta_interval[0],
            endParam=self.theta_interval[1],
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xcenter": self.center.x,
                "ycenter": self.center.y,
                "xdir": self.direction[0],
                "ydir": self.direction[1],
            },
        )

    @classmethod
    def three_point_with_midpoint(
        cls,
        sketch: "Sketch",
        center: Point2D,
        radius: float | None,
        endpoint_1: Point2D,
        endpoint_2: Point2D,
        units: UnitSystem,
        direction: tuple[float, float] = (1, 0),
        *,
        clockwise: bool = False,
    ) -> "SketchArc":
        """Construct a new instance of a SketchArc using endpoints instead
        of a theta interval.

        Args:
            sketch: A reference to the owning sketch
            radius: The radius of the arc. If unprovided, it will be solved for
            center: The centerpoint of the arc
            endpoint_1: One of the endpoints of the arc
            endpoint_2: The other endpoint of the arc
            units: The unit system to use
            direction: An optional direction to specify. Defaults to +x axis
            clockwise: Whether or not the arc is clockwise. Defaults to false

        Returns:
            A new SketchArc instance

        """
        # verify that a valid arc can be found
        if not math.isclose(
            math.sqrt((center.x - endpoint_1.x) ** 2 + (center.y - endpoint_1.y) ** 2),
            math.sqrt((center.x - endpoint_2.x) ** 2 + (center.y - endpoint_2.y) ** 2),
        ):
            msg = "No valid arc can be created from provided endpoints"
            raise OnPyParameterError(msg)

        # find radius
        radius_from_endpoints = math.sqrt(
            (center.x - endpoint_1.x) ** 2 + (center.y - endpoint_1.y) ** 2,
        )
        if radius is None:
            radius = radius_from_endpoints
        elif not math.isclose(radius, radius_from_endpoints):
            msg = "Endpoints do not match the provided radius"
            raise OnPyParameterError(msg)

        # create line vectors from center to endpoints
        vec_1 = Point2D(endpoint_1.x - center.x, endpoint_1.y - center.y)
        vec_2 = Point2D(endpoint_2.x - center.x, endpoint_2.y - center.y)

        # measure the angle of these segments
        theta_1 = math.atan2(vec_1.y, vec_1.x) % (2 * math.pi)
        theta_2 = math.atan2(vec_2.y, vec_2.x) % (2 * math.pi)

        # calculate the difference in angles
        diff_theta = abs(theta_1 - theta_2)

        # Choose the smaller arc
        if diff_theta <= math.pi:
            # if the difference is less than or equal to pi, choose the smaller arc
            if clockwise:
                # for clockwise arcs, choose the larger angle as the starting point
                theta_start = max(theta_1, theta_2)
                theta_end = min(theta_1, theta_2)
            else:
                # for counterclockwise arcs, choose the smaller angle as the
                # starting point
                theta_start = min(theta_1, theta_2)
                theta_end = max(theta_1, theta_2)
        elif clockwise:
            # for clockwise arcs, choose the smaller angle as the starting point
            theta_start = min(theta_1, theta_2)
            theta_end = max(theta_1, theta_2)
        else:
            # for counterclockwise arcs, choose the larger angle as the
            # starting point
            theta_start = max(theta_1, theta_2)
            theta_end = min(theta_1, theta_2)

        # create theta interval
        theta_interval = (theta_start, theta_end)

        # create an arc using this interval
        return SketchArc(
            sketch=sketch,
            radius=radius,
            center=center,
            theta_interval=theta_interval,
            units=units,
            direction=direction,
            clockwise=clockwise,
        )

    @override
    def __repr__(self) -> str:
        return (
            f"Arc(center={self.center}, radius={self.radius}, "
            f"interval={self.theta_interval[0]}<θ<{self.theta_interval[1]})"
        )

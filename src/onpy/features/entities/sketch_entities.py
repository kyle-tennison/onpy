"""Various entities that might appear in a sketch"""

import math
from typing import TYPE_CHECKING, override

import numpy as np
from onpy.features.entities.base import Entity
import onpy.api.model as model
from onpy.util.misc import UnitSystem, Point2D

if TYPE_CHECKING:
    from onpy.features import Sketch


class SketchCircle(Entity):
    """A sketch circle"""

    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        units: UnitSystem,
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ):
        """
        Args:
            sketch: A reference to the owning sketch
            radius: The radius of the arc
            center: The centerpoint of the arc
            units: The unit system to use
            dir: An optional dir to specify. Defaults to +x axis
            clockwise: Whether or not the arc is clockwise. Defaults to false
        """

        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.units = units
        self.dir = Point2D.from_pair(dir)
        self.clockwise = clockwise
        self.entity_id = self.generate_entity_id()

    @override
    def to_model(self) -> model.SketchCurveEntity:

        return model.SketchCurveEntity(
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xcenter": self.center.x,
                "ycenter": self.center.y,
                "xdir": self.dir.x,
                "ydir": self.dir.y,
                "clockwise": self.clockwise,
            },
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
        )

    @property
    @override
    def _feature(self) -> "Sketch":
        return self._sketch

    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchCircle":
        new_center = self._rotate_point(self.center, Point2D.from_pair(origin), theta)
        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def translate(self, x: float, y: float) -> "SketchCircle":

        if self._sketch._client.units is UnitSystem.INCH:
            x *= 0.0254
            y *= 0.0254

        new_center = Point2D(self.center.x + x, self.center.y + y)
        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise,
        )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def mirror(
        self, line_start: tuple[float, float], line_end: tuple[float, float]
    ) -> "SketchCircle":
        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end)

        # to avoid confusion
        del line_start
        del line_end

        new_center = self._mirror_point(self.center, mirror_start, mirror_end)

        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise,
        )

        self._replace_entity(new_entity)
        return new_entity

    @override
    def __repr__(self) -> str:
        return f"Circle(radius={self.radius}, center={self.center})"


class SketchLine(Entity):
    """A straight sketch line segment"""

    def __init__(
        self,
        sketch: "Sketch",
        start_point: Point2D,
        end_point: Point2D,
        units: UnitSystem,
    ) -> None:
        """
        Args:
            sketch: A reference to the owning sketch
            start_point: The starting point of the line
            end_point: The ending point of the line
            units: The unit system to use
        """

        self._sketch = sketch
        self.start = start_point
        self.end = end_point
        self.units = units
        self.entity_id = self.generate_entity_id()

    @property
    def dx(self) -> float:
        """The x-component of the line"""
        return self.end.x - self.start.x

    @property
    def dy(self) -> float:
        """The y-component of the line"""
        return self.end.y - self.start.y

    @property
    def length(self) -> float:
        """The length of the line"""
        return abs(math.sqrt(self.dx**2 + self.dy**2))

    @property
    def theta(self) -> float:
        """The angle of the line relative to the x-axis"""
        return math.atan2(self.dy, self.dx)

    @property
    def dir(self) -> Point2D:
        """A vector pointing in the direction of the line"""
        return Point2D(math.cos(self.theta), math.sin(self.theta))

    @property
    @override
    def _feature(self):
        return self._sketch

    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchLine":
        new_start = self._rotate_point(
            self.start, Point2D.from_pair(origin), degrees=theta
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
        self, line_start: tuple[float, float], line_end: tuple[float, float]
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
    def to_model(self) -> model.SketchCurveSegmentEntity:
        return model.SketchCurveSegmentEntity(
            entityId=self.entity_id,
            startPointId=f"{self.entity_id}.start",
            endPointId=f"{self.entity_id}.end",
            startParam=0,
            endParam=self.length,
            geometry={
                "btType": "BTCurveGeometryLine-117",
                "pntX": self.start.x,
                "pntY": self.start.y,
                "dirX": self.dir.x,
                "dirY": self.dir.y,
            },
        )

    @override
    def __repr__(self) -> str:
        return f"Line(start={self.start}, end={self.end})"


class SketchArc(Entity):
    """A sketch arc"""

    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        theta_interval: tuple[float, float],
        units: UnitSystem,
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ):
        """
        Args:
            sketch: A reference to the owning sketch
            radius: The radius of the arc
            center: The centerpoint of the arc
            theta_interval: The theta interval, in degrees
            units: The unit system to use
            dir: An optional dir to specify. Defaults to +x axis
            clockwise: Whether or not the arc is clockwise. Defaults to false
        """

        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.theta_interval = theta_interval
        self.dir = dir
        self.clockwise = clockwise
        self.entity_id = self.generate_entity_id()
        self.units = units

    @property
    @override
    def _feature(self):
        return self._sketch

    @override
    def mirror(
        self, line_start: tuple[float, float], line_end: tuple[float, float]
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
            [start_point.x - new_center.x, start_point.y - new_center.y]
        )
        mirror_line_vector = np.array(
            [mirror_end.x - mirror_start.x, mirror_end.y - mirror_start.y]
        )

        angle_offset = 2 * math.acos(
            np.dot(arc_start_vector, mirror_line_vector)
            / (np.linalg.norm(arc_start_vector) * np.linalg.norm(mirror_line_vector))
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
            dir=self.dir,
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
            dir=self.dir,
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
            dir=self.dir,
            clockwise=self.clockwise,
        )

        # d_theta = self.theta_interval[1] - self.theta_interval[0]

        # arc_start_vector = np.array(
        #     [start_point.x - new_center.x, start_point.y - new_center.y]
        # )
        # x_axis = np.array([1, 0])

        # angle_start = math.acos(
        #     np.dot(arc_start_vector, x_axis) / np.linalg.norm(arc_start_vector)
        # )

        # new_theta = (angle_start, angle_start + d_theta)

        # new_entity = SketchArc(
        #     sketch=self._sketch,
        #     radius=self.radius,
        #     center=new_center,
        #     theta_interval=new_theta,
        #     units=self.units,
        #     dir=self.dir,
        #     clockwise=self.clockwise,
        # )
        self._replace_entity(new_entity)
        return new_entity

    @override
    def to_model(self) -> model.SketchCurveSegmentEntity:
        return model.SketchCurveSegmentEntity(
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
                "xdir": self.dir[0],
                "ydir": self.dir[1],
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
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ) -> "SketchArc":
        """Constructs a new instance of a SketchArc using endpoints instead
        of a theta interval

        Args:
            sketch: A reference to the owning sketch
            radius: The radius of the arc. If unprovided, it will be solved for
            center: The centerpoint of the arc
            endpoint_1: One of the endpoints of the arc
            endpoint_2: The other endpoint of the arc
            units: The unit system to use
            dir: An optional dir to specify. Defaults to +x axis
            clockwise: Whether or not the arc is clockwise. Defaults to false

        Returns:
            A new SketchArc instance
        """

        # verify that a valid arc can be found
        assert math.isclose(
            math.sqrt((center.x - endpoint_1.x) ** 2 + (center.y - endpoint_1.y) ** 2),
            math.sqrt((center.x - endpoint_2.x) ** 2 + (center.y - endpoint_2.y) ** 2),
        ), "No valid arc can be created from provided endpoints"

        # find radius
        radius_from_endpoints = math.sqrt(
            (center.x - endpoint_1.x) ** 2 + (center.y - endpoint_1.y) ** 2
        )
        if radius is None:
            radius = radius_from_endpoints
        else:
            assert math.isclose(
                radius, radius_from_endpoints
            ), "Endpoints do not match the provided radius"

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
                # for counterclockwise arcs, choose the smaller angle as the starting point
                theta_start = min(theta_1, theta_2)
                theta_end = max(theta_1, theta_2)
        else:
            # if the difference is greater than pi, choose the larger arc
            if clockwise:
                # for clockwise arcs, choose the smaller angle as the starting point
                theta_start = min(theta_1, theta_2)
                theta_end = max(theta_1, theta_2)
            else:
                # for counterclockwise arcs, choose the larger angle as the starting point
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
            dir=dir,
            clockwise=clockwise,
        )

    @override
    def __repr__(self) -> str:
        return f"Arc(center={self.center}, radius={self.radius}, interval={self.theta_interval[0]}<θ<{self.theta_interval[1]})"

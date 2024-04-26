"""Various entities that might appear in a sketch"""

from enum import Enum
import math
from typing import override
from pyshape.features.entities.base import Entity
import pyshape.api.model as model
from pyshape.util.misc import UnitSystem, Point2D


class SketchCircle(Entity):

    def __init__(
        self,
        radius: float,
        center: Point2D,
        units: UnitSystem,
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ):

        self.radius = radius
        self.center = center
        self.units = units
        self.dir = dir
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
                "xdir": self.dir[0],
                "ydir": self.dir[1],
                "clockwise": self.clockwise,
            },
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
        )

class SketchLine(Entity):

    def __init__(self,
                 start_point: Point2D,
                 end_point: Point2D,
                 units: UnitSystem
                 ) -> None:
        
        self.start = start_point
        self.end = end_point
        self.units = units
        self.entity_id = self.generate_entity_id()

        dx = self.end.x - self.start.x 
        dy = self.end.y - self.start.y

        length = math.sqrt(dx ** 2 + dy ** 2)
        theta = math.atan2(dy, dx)
        unit_direction = Point2D(math.cos(theta), math.sin(theta))

        if units is UnitSystem.INCH:
            length *= 0.0254

        self.length = abs(length) 
        self.dir = unit_direction

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
                "dirX": self.start.x + self.dir.x,
                "dirY": self.start.y + self.dir.y
            }
        )
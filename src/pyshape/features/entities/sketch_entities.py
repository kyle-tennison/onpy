"""Various entities that might appear in a sketch"""


from enum import Enum
from pyshape.features.entities.base import Entity
import pyshape.api.model as model

class SketchCircle(Entity):

    def __init__(self, radius: float, center: tuple[float, float], dir: tuple[float, float] = (1, 0), clockwise: bool = False):

        self.radius = radius 
        self.center = center 
        self.dir = dir 
        self.clockwise = clockwise 

    def to_model(self) -> model.SketchCurveEntity:

        return model.SketchCurveEntity(
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xcenter": self.center[0],
                "ycenter": self.center[1],
                "xdir": self.dir[0],
                "ydir": self.dir[1],
                "clockwise": self.clockwise
            },
            centerId="circle-entity.center",
            entityId="circle-entity",
        )
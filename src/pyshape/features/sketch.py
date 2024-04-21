"""Interface to OnShape Sketches"""

from typing import TYPE_CHECKING
from pyshape.features.base import Feature

if TYPE_CHECKING:
    from pyshape.api.model import ApiModel
    from pyshape.elements.partstudio import PartStudio
    from pyshape.document import Document
    from pyshape.features.plane import Plane

class Sketch(Feature):

    def __init__(self, partstudio: "PartStudio", plane: "Plane", name: str = "New Sketch") -> None:
        self.plane = plane
        self._partstudio = partstudio
        self._name = name
        self._sketch_id: str|None = None

    @property
    def partstudio(self) -> "PartStudio":
        return self._partstudio
    
    @property
    def id(self) -> str|None:
        return self._sketch_id
    
    @property
    def name(self) -> str:
        return self._name
    
    
    def __str__(self) -> str:
        return repr(self)
    
    def __repr__(self) -> str:
        return f"<Sketch on {self.plane}>"

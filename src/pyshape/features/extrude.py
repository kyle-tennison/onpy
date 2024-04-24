"""OnShape extrusion feature"""

from typing import TYPE_CHECKING, override
from pyshape.api.model import Feature, FeatureAddResponse
from pyshape.features.base import Feature, Extrudable
import pyshape.api.model as model

if TYPE_CHECKING:
    from pyshape.elements.partstudio import PartStudio


class Extrude(Feature):

    def __init__(self, partstudio: "PartStudio", target: Extrudable, distance: float, name: str="Extrusion") -> None:
        self.target = target
        self._id: str|None = None 
        self._partstudio = partstudio
        self._name = name

    @property
    @override
    def id(self) -> str|None:
        return self._id 
    
    @property
    @override
    def partstudio(self) -> "PartStudio":
        return self._partstudio
    
    @property
    @override
    def name(self) -> str:
        return self._name 
    
    def _to_model(self) -> Feature:
        raise NotImplementedError()
    
    def _load_response(self, response: FeatureAddResponse) -> None:
        raise NotImplementedError()
